from fastapi import APIRouter

router = APIRouter()


@router.get("/gwas/region")
async def fetch_gwas_region():
    return {"message": "GWAS Catalog region fetch - not yet implemented"}


@router.get("/eqtl/region")
async def fetch_eqtl_region():
    return {"message": "eQTL Catalogue region fetch - not yet implemented"}


@router.post("/ld/compute")
async def compute_ld():
    return {"message": "LD computation from 1000 Genomes - not yet implemented"}


@router.post("/locuscompare/render")
async def render_locus_compare():
    return {"message": "Locus compare 4-panel plot rendering - not yet implemented"}


@router.post("/locuscompare/workflow")
async def locus_compare_workflow():
    return {"message": "End-to-end locus compare workflow - not yet implemented"}