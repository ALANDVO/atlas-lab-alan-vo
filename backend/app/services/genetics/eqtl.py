"""
eQTL Catalogue service for fetching region data.
"""
import httpx
from typing import Optional
from pydantic import BaseModel, Field


class EQTLVariant(BaseModel):
    """Single variant association from eQTL Catalogue."""
    variant_id: str = Field(..., description="Variant identifier")
    chromosome: str = Field(..., description="Chromosome")
    position: int = Field(..., description="Genomic position (GRCh38)")
    p_value: float = Field(..., description="P-value for association")
    beta: Optional[float] = Field(None, description="Effect size")
    se: Optional[float] = Field(None, description="Standard error")
    gene_id: str = Field(..., description="Ensembl gene ID")
    gene_symbol: str = Field(..., description="Gene symbol")
    tissue: str = Field(..., description="Tissue/cell type")
    study_id: str = Field(..., description="Study identifier")
    qtl_group: str = Field(..., description="QTL group (e.g., eQTL, sQTL)")


class EQTLRegionResponse(BaseModel):
    """Response for eQTL Catalogue region query."""
    variants: list[EQTLVariant] = Field(default_factory=list)
    region: str = Field(..., description="Queried region (chr:start-end)")
    total_results: int = Field(..., description="Total variants found")
    query_time_ms: int = Field(..., description="Query execution time in milliseconds")


class EQTLService:
    """Service for querying eQTL Catalogue REST API."""
    
    BASE_URL = "https://www.ebi.ac.uk/eqtl/api"
    DEFAULT_TIMEOUT = 30.0
    
    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                timeout=httpx.Timeout(self.timeout),
                headers={"Accept": "application/json"}
            )
        return self._client
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def fetch_region(
        self,
        chromosome: str,
        start: int,
        end: int,
        gene_id: Optional[str] = None,
        tissue: Optional[str] = None,
        max_results: int = 1000
    ) -> EQTLRegionResponse:
        """
        Fetch eQTL Catalogue associations for a genomic region.
        
        Args:
            chromosome: Chromosome (e.g., "1", "X", "MT")
            start: Start position (1-based, inclusive)
            end: End position (1-based, inclusive)
            gene_id: Optional Ensembl gene ID filter
            tissue: Optional tissue filter
            max_results: Maximum number of results to return
            
        Returns:
            EQTLRegionResponse with variant associations
        """
        import time
        start_time = time.perf_counter()
        
        chrom = chromosome.upper().replace("CHR", "")
        region = f"{chrom}:{start}-{end}"
        
        client = await self._get_client()
        
        # eQTL Catalogue API uses /v2/associations endpoint with region filter
        params = {
            "chromosome": chrom,
            "bpStart": start,
            "bpEnd": end,
            "size": max_results,
        }
        
        if gene_id:
            params["geneId"] = gene_id
        if tissue:
            params["tissueLabel"] = tissue
        
        try:
            response = await client.get("/v2/associations", params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError:
            return EQTLRegionResponse(
                variants=[],
                region=region,
                total_results=0,
                query_time_ms=int((time.perf_counter() - start_time) * 1000)
            )
        
        variants = []
        # Parse response - eQTL Catalogue returns a list directly or wrapped
        associations = data if isinstance(data, list) else data.get("associations", [])
        
        for assoc in associations[:max_results]:
            try:
                variant_id = assoc.get("variantId", "")
                chr_name = assoc.get("chromosome", chrom)
                pos = assoc.get("position", 0)
                p_val = assoc.get("pValue", 1.0)
                
                variants.append(EQTLVariant(
                    variant_id=variant_id,
                    chromosome=chr_name,
                    position=pos,
                    p_value=p_val,
                    beta=assoc.get("beta"),
                    se=assoc.get("standardError"),
                    gene_id=assoc.get("geneId", ""),
                    gene_symbol=assoc.get("geneSymbol", ""),
                    tissue=assoc.get("tissueLabel", ""),
                    study_id=assoc.get("studyId", ""),
                    qtl_group=assoc.get("qtlGroup", "eQTL"),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        
        query_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        return EQTLRegionResponse(
            variants=variants,
            region=region,
            total_results=len(variants),
            query_time_ms=query_time_ms,
        )


eqtl_service = EQTLService()
