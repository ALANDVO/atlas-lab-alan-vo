"""
Genetics services package.
"""
from app.services.genetics.gwas import gwas_service
from app.services.genetics.eqtl import eqtl_service
from app.services.genetics.ld import ld_service
from app.services.genetics.locuscompare import locuscompare_service

__all__ = [
    "gwas_service",
    "eqtl_service",
    "ld_service",
    "locuscompare_service",
]
