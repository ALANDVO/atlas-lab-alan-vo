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
                data={},
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
