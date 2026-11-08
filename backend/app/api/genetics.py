from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.services.genetics.gwas import gwas_service, GWASRegionResponse
from app.services.genetics.eqtl import eqtl_service, EQTLRegionResponse
from app.services.genetics.ld import ld_service, LDMatrixResponse
from app.services.genetics.locuscompare import (
    locuscompare_service, 
    LocusCompareRequest, 
    LocusCompareResponse,
    LocusCompareFrontendRequest
)

router = APIRouter()


class RegionRequest(BaseModel):
    chromosome: str = Field(..., description="Chromosome (e.g., 1, X)")
    start: int = Field(..., ge=1, description="Start position (1-based)")
    end: int = Field(..., ge=1, description="End position (1-based)")


class LocusCompareFrontendResponse(BaseModel):
    """Response format expected by frontend."""
    plot_url: str
    exposure_count: int
    outcome_count: int
    palindromic_excluded: int
    ld_computed: bool

@router.post("/gwas/region", response_model=GWASRegionResponse)
async def fetch_gwas_region(request: RegionRequest):
    """Fetch GWAS Catalog associations for a genomic region."""
    try:
        return await gwas_service.fetch_region(
            chromosome=request.chromosome,
            start=request.start,
            end=request.end,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GWAS fetch failed: {str(e)}")


@router.post("/eqtl/region", response_model=EQTLRegionResponse)
async def fetch_eqtl_region(request: RegionRequest):
    """Fetch eQTL Catalogue associations for a genomic region."""
    try:
        return await eqtl_service.fetch_region(
            chromosome=request.chromosome,
            start=request.start,
            end=request.end,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"eQTL fetch failed: {str(e)}")


@router.post("/ld/compute", response_model=LDMatrixResponse)
async def compute_ld(request: RegionRequest):
    """Compute LD matrix from 1000 Genomes reference panel."""
    try:
        return await ld_service.compute_ld(
            chromosome=request.chromosome,
            start=request.start,
            end=request.end,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LD computation failed: {str(e)}")


@router.post("/locuscompare/render", response_model=LocusCompareResponse)
async def render_locus_compare(request: LocusCompareRequest):
    """Render locus compare 4-panel plot data."""
    try:
        return await locuscompare_service.run_workflow(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Locus compare failed: {str(e)}")


@router.post("/locuscompare/workflow", response_model=LocusCompareResponse)
async def locus_compare_workflow(request: LocusCompareRequest):
    """Execute end-to-end locus compare workflow."""
    try:
        return await locuscompare_service.run_workflow(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@router.post("/locuscompare", response_model=LocusCompareFrontendResponse)
async def locus_compare_frontend(request: LocusCompareFrontendRequest):
    """
    Frontend-compatible locus compare endpoint.
    Accepts sentinel SNP and window, returns plot URL and summary counts.
    """
    try:
        # Convert frontend request to internal format
        internal_request = await locuscompare_service._frontend_to_internal(request)
        
        # Run workflow
        result = await locuscompare_service.run_workflow(internal_request)
        
        # Build frontend-compatible response
        return LocusCompareFrontendResponse(
            plot_url=f"/api/v1/genetics/locuscompare/plot?region={internal_request.region}",
            exposure_count=result.gwas_data.total_results,
            outcome_count=result.eqtl_data.total_results,
            palindromic_excluded=0,  # Placeholder
            ld_computed=len(result.ld_data.ld_matrix) > 0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Locus compare failed: {str(e)}")
