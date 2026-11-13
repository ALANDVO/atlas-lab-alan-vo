import httpx
import time
from typing import Optional
from pydantic import BaseModel, Field

from app.services.genetics.gwas import gwas_service, GWASRegionResponse
from app.services.genetics.eqtl import eqtl_service, EQTLRegionResponse
from app.services.genetics.ld import ld_service, LDMatrixResponse

class LocusCompareRequest(BaseModel):
    region: str = Field(..., description="Genomic region (chr:start-end)")
    gwas_p_threshold: float = Field(5e-8, description="GWAS p-value threshold")
    eqtl_gene_id: Optional[str] = Field(None, description="eQTL gene ID filter")
    eqtl_tissue: Optional[str] = Field(None, description="eQTL tissue filter")
    ld_population: str = Field("EUR", description="LD reference population")
    max_variants: int = Field(100, description="Max variants per panel")


class LocusCompareFrontendRequest(BaseModel):
    """Request format from frontend with sentinel SNP and window."""
    gene: str = Field(..., description="Gene symbol")
    tissue: str = Field(..., description="Tissue/cell type")
    outcome_trait: str = Field(..., description="Outcome trait (e.g., triglycerides)")
    population: str = Field("EUR", description="LD reference population")
    sentinel_snp: str = Field(..., description="Sentinel SNP rsID")
    window_kb: int = Field(500, description="Window size in kilobases")


class LocusComparePanel(BaseModel):
    panel_type: str = Field(..., description="Panel type: gwas, eqtl, ld, combined")
    title: str = Field(..., description="Panel title")
    data: dict = Field(default_factory=dict, description="Panel data")
    plot_config: dict = Field(default_factory=dict, description="Plot configuration")


class LocusCompareResponse(BaseModel):
    region: str
    panels: list[LocusComparePanel]
    gwas_data: GWASRegionResponse
    eqtl_data: EQTLRegionResponse
    ld_data: LDMatrixResponse
    workflow_time_ms: int
    gwas_time_ms: int
    eqtl_time_ms: int
    ld_time_ms: int


class LocusCompareService:
    def __init__(self):
        pass
    
    async def _resolve_sentinel_snp(self, sentinel_snp: str) -> tuple[str, int, int] | None:
        """
        Resolve sentinel SNP rsID to genomic position using GWAS Catalog.
        Returns (chromosome, start, end) or None if not found.
        """
        try:
            # Search GWAS Catalog for the variant
            client = await gwas_service._get_client()
            response = await client.get(
                f"/singleNucleotidePolymorphisms/{sentinel_snp}",
                params={"projection": "chr,pos"}
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            
            chrom = data.get("chromosomeName", "").replace("chr", "")
            pos = data.get("chromosomalPosition", 0)
            
            if chrom and pos:
                return (chrom, pos, pos)
        except Exception:
            pass
        return None
    
    async def _frontend_to_internal(self, request: LocusCompareFrontendRequest) -> LocusCompareRequest:
        """Convert frontend request format to internal format."""
        # Resolve sentinel SNP to position
        resolved = await self._resolve_sentinel_snp(request.sentinel_snp)
        
        if resolved:
            chrom, pos, _ = resolved
            window = request.window_kb * 1000
            start = max(1, pos - window // 2)
            end = pos + window // 2
            region = f"{chrom}:{start}-{end}"
        else:
            # Fallback: use a default region (chr1:1-1000000) if SNP not found
            region = "1:1000000-2000000"
        
        return LocusCompareRequest(
            region=region,
            gwas_p_threshold=5e-8,
            eqtl_gene_id=None,  # Could map gene symbol to Ensembl ID
            eqtl_tissue=request.tissue,
            ld_population=request.population,
            max_variants=100
        )
    
    async def run_workflow(self, request: LocusCompareRequest) -> LocusCompareResponse:
        total_start = time.perf_counter()
        
        # Parse region
        try:
            chrom_part, pos_part = request.region.split(':')
            start_str, end_str = pos_part.split('-')
            chromosome = chrom_part
            start = int(start_str)
            end = int(end_str)
        except ValueError:
            raise ValueError("Invalid region format. Use chr:start-end")
        
        # Fetch GWAS data
        gwas_start = time.perf_counter()
        gwas_response = await gwas_service.fetch_region(
            chromosome=chromosome,
            start=start,
            end=end,
            p_value_threshold=request.gwas_p_threshold,
            max_results=request.max_variants
        )
        gwas_time = int((time.perf_counter() - gwas_start) * 1000)
        
        # Fetch eQTL data
        eqtl_start = time.perf_counter()
        eqtl_response = await eqtl_service.fetch_region(
            chromosome=chromosome,
            start=start,
            end=end,
            gene_id=request.eqtl_gene_id,
            tissue=request.eqtl_tissue,
            max_results=request.max_variants
        )
        eqtl_time = int((time.perf_counter() - eqtl_start) * 1000)
        
        # Compute LD
        ld_start = time.perf_counter()
        ld_response = await ld_service.compute_ld(
            chromosome=chromosome,
            start=start,
            end=end,
            population=request.ld_population,
            max_variants=request.max_variants
        )
        ld_time = int((time.perf_counter() - ld_start) * 1000)
        
        # Build 4-panel plot configuration
        # Combined panel data merges GWAS, eQTL, and LD for locuscompare visualization
        combined_variants = []
        variant_map = {}
        
        # Index GWAS variants by position
        for v in gwas_response.variants:
            key = f"{v.chromosome}:{v.position}"
            if key not in variant_map:
                variant_map[key] = {
                    "variant_id": v.variant_id,
                    "chromosome": v.chromosome,
                    "position": v.position,
                    "gwas_p_value": v.p_value,
                    "gwas_trait": v.trait,
                    "gwas_gene": v.gene,
                    "eqtl_p_value": None,
                    "eqtl_gene": None,
                    "eqtl_tissue": None,
                    "allele_frequency": None,
                }
            variant_map[key]["gwas_p_value"] = v.p_value
            variant_map[key]["gwas_trait"] = v.trait
            variant_map[key]["gwas_gene"] = v.gene
        
        # Index eQTL variants by position
        for v in eqtl_response.variants:
            key = f"{v.chromosome}:{v.position}"
            if key not in variant_map:
                variant_map[key] = {
                    "variant_id": v.variant_id,
                    "chromosome": v.chromosome,
                    "position": v.position,
                    "gwas_p_value": None,
                    "gwas_trait": None,
                    "gwas_gene": None,
                    "eqtl_p_value": v.p_value,
                    "eqtl_gene": v.gene_symbol,
                    "eqtl_tissue": v.tissue,
                    "allele_frequency": None,
                }
            variant_map[key]["eqtl_p_value"] = v.p_value
            variant_map[key]["eqtl_gene"] = v.gene_symbol
            variant_map[key]["eqtl_tissue"] = v.tissue
        
        # Add LD variant info
        for v in ld_response.variants:
            key = f"{v.chromosome}:{v.position}"
            if key not in variant_map:
                variant_map[key] = {
                    "variant_id": v.variant_id,
                    "chromosome": v.chromosome,
                    "position": v.position,
                    "gwas_p_value": None,
                    "gwas_trait": None,
                    "gwas_gene": None,
                    "eqtl_p_value": None,
                    "eqtl_gene": None,
                    "eqtl_tissue": None,
                }
            variant_map[key]["allele_frequency"] = v.allele_frequency
        
        # Convert to sorted list by position
        combined_variants = sorted(variant_map.values(), key=lambda x: x["position"])
        
        panels = [
            LocusComparePanel(
                panel_type="gwas",
                title="GWAS Catalog Associations",
                data={"variants": [v.model_dump() for v in gwas_response.variants]},
                plot_config={"type": "manhattan", "y_axis": "-log10(p)"}
            ),
            LocusComparePanel(
                panel_type="eqtl",
                title="eQTL Catalogue Associations",
                data={"variants": [v.model_dump() for v in eqtl_response.variants]},
                plot_config={"type": "manhattan", "y_axis": "-log10(p)"}
            ),
            LocusComparePanel(
                panel_type="ld",
                title="Linkage Disequilibrium (r²)",
                data={"variants": [v.model_dump() for v in ld_response.variants], "matrix": ld_response.ld_matrix},
                plot_config={"type": "heatmap", "color_scale": "blues"}
            ),
            LocusComparePanel(
                panel_type="combined",
                title="LocusCompare Combined View",
                data={
                    "variants": combined_variants,
                    "ld_matrix": ld_response.ld_matrix,
                    "ld_variants": [v.model_dump() for v in ld_response.variants]
                },
                plot_config={"type": "locuscompare", "layout": "4-panel"}
            )
        ]
        
        total_time = int((time.perf_counter() - total_start) * 1000)
        
        return LocusCompareResponse(
            region=request.region,
            panels=panels,
            gwas_data=gwas_response,
            eqtl_data=eqtl_response,
            ld_data=ld_response,
            workflow_time_ms=total_time,
            gwas_time_ms=gwas_time,
            eqtl_time_ms=eqtl_time,
            ld_time_ms=ld_time
        )


locuscompare_service = LocusCompareService()
