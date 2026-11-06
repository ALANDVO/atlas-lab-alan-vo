"""
GWAS Catalog service for fetching region data.
"""
import httpx
from typing import Optional
from pydantic import BaseModel, Field


class GWASVariant(BaseModel):
    """Single variant association from GWAS Catalog."""
    variant_id: str = Field(..., description="Variant identifier (rsID or chr:pos)")
    chromosome: str = Field(..., description="Chromosome")
    position: int = Field(..., description="Genomic position (GRCh38)")
    p_value: float = Field(..., description="P-value for association")
    beta: Optional[float] = Field(None, description="Effect size (beta coefficient)")
    se: Optional[float] = Field(None, description="Standard error")
    trait: str = Field(..., description="Reported trait")
    study_accession: str = Field(..., description="GWAS Catalog study accession")
    gene: Optional[str] = Field(None, description="Mapped gene")


class GWASRegionResponse(BaseModel):
    """Response for GWAS Catalog region query."""
    variants: list[GWASVariant] = Field(default_factory=list)
    region: str = Field(..., description="Queried region (chr:start-end)")
    total_results: int = Field(..., description="Total variants found")
    query_time_ms: int = Field(..., description="Query execution time in milliseconds")


class GWASService:
    """Service for querying GWAS Catalog REST API."""
    
    BASE_URL = "https://www.ebi.ac.uk/gwas/rest/api"
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
        p_value_threshold: float = 5e-8,
        max_results: int = 1000
    ) -> GWASRegionResponse:
        """
        Fetch GWAS Catalog associations for a genomic region.
        
        Args:
            chromosome: Chromosome (e.g., "1", "X", "MT")
            start: Start position (1-based, inclusive)
            end: End position (1-based, inclusive)
            p_value_threshold: Maximum p-value to include
            max_results: Maximum number of results to return
            
        Returns:
            GWASRegionResponse with variant associations
        """
        import time
        start_time = time.perf_counter()
        
        # Normalize chromosome
        chrom = chromosome.upper().replace("CHR", "")
        region = f"{chrom}:{start}-{end}"
        
        client = await self._get_client()
        
        # GWAS Catalog API: /singleNucleotidePolymorphisms?chr=1&bp=1000000-2000000
        params = {
            "chr": chrom,
            "bp": f"{start}-{end}",
            "pval": p_value_threshold,
            "size": max_results,
        }
        
        try:
            response = await client.get("/singleNucleotidePolymorphisms", params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            # Return empty response on error, don't raise
            return GWASRegionResponse(
                variants=[],
                region=region,
                total_results=0,
                query_time_ms=int((time.perf_counter() - start_time) * 1000)
            )
        
        variants = []
        # Parse the nested response structure
        embedded = data.get("_embedded", {})
        snps = embedded.get("singleNucleotidePolymorphisms", [])
        
        for snp in snps[:max_results]:
            try:
                # Extract variant info
                variant_id = snp.get("variantId", "")
                chr_name = snp.get("chromosomeName", chrom)
                pos = snp.get("chromosomalPosition", 0)
                
                # Get strongest association
                associations = snp.get("associations", [])
                if not associations:
                    continue
                    
                assoc = associations[0]
                p_val = assoc.get("pvalueMantissa", 1.0) * (10 ** assoc.get("pvalueExponent", 0))
                
                if p_val > p_value_threshold:
                    continue
                
                # Get trait
                trait = assoc.get("trait", "Unknown")
                if "efoTraits" in assoc and assoc["efoTraits"]:
                    trait = assoc["efoTraits"][0].get("trait", trait)
                
                # Get study
                study = assoc.get("study", {})
                study_accession = study.get("accessionId", "")
                
                # Get gene
                gene = None
                if "genes" in assoc and assoc["genes"]:
                    gene = assoc["genes"][0].get("geneName")
                
                variants.append(GWASVariant(
                    variant_id=variant_id,
                    chromosome=chr_name,
                    position=pos,
                    p_value=p_val,
                    beta=assoc.get("beta"),
                    se=assoc.get("standardError"),
                    trait=trait,
                    study_accession=study_accession,
                    gene=gene,
                ))
            except (KeyError, TypeError, ValueError):
                # Skip malformed entries
                continue
        
        query_time_ms = int((time.perf_counter() - start_time) * 1000)
        
        return GWASRegionResponse(
            variants=variants,
            region=region,
            total_results=len(variants),
            query_time_ms=query_time_ms,
        )


gwas_service = GWASService()
