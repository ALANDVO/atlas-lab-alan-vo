"""
Tests for statistical genetics services.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.services.genetics.gwas import gwas_service, GWASVariant, GWASRegionResponse
from app.services.genetics.eqtl import eqtl_service, EQTLVariant, EQTLRegionResponse
from app.services.genetics.ld import ld_service, LDVariant, LDMatrixResponse
from app.services.genetics.locuscompare import locuscompare_service, LocusCompareRequest, LocusCompareResponse


class TestGWASService:
    """Test GWAS Catalog service."""

    @pytest.mark.asyncio
    async def test_fetch_region_mock(self):
        """Test GWAS region fetch with mocked response."""
        mock_response = {
            "_embedded": {
                "singleNucleotidePolymorphisms": [
                    {
                        "variantId": "rs12345",
                        "chromosomeName": "1",
                        "chromosomalPosition": 1000000,
                        "associations": [
                            {
                                "pvalueMantissa": 1.2,
                                "pvalueExponent": -10,
                                "beta": 0.15,
                                "standardError": 0.02,
                                "trait": "Type 2 diabetes",
                                "efoTraits": [{"trait": "Type 2 diabetes"}],
                                "study": {"accessionId": "GCST123456"},
                                "genes": [{"geneName": "TCF7L2"}]
                            }
                        ]
                    }
                ]
            }
        }

        with patch.object(gwas_service, '_get_client') as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.get.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            result = await gwas_service.fetch_region("1", 1000000, 2000000)

            assert isinstance(result, GWASRegionResponse)
            assert result.region == "1:1000000-2000000"
            assert len(result.variants) == 1
            assert result.variants[0].variant_id == "rs12345"
            assert result.variants[0].p_value == 1.2e-10
            assert result.variants[0].gene == "TCF7L2"
            assert result.total_results == 1
            assert result.query_time_ms >= 0

    @pytest.mark.asyncio
    async def test_fetch_region_empty(self):
        """Test GWAS region fetch with empty response."""
        mock_response = {"_embedded": {"singleNucleotidePolymorphisms": []}}

        with patch.object(gwas_service, '_get_client') as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.get.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            result = await gwas_service.fetch_region("1", 1000000, 2000000)

            assert isinstance(result, GWASRegionResponse)
            assert len(result.variants) == 0
            assert result.total_results == 0


class TestEQTLService:
    """Test eQTL Catalogue service."""

    @pytest.mark.asyncio
    async def test_fetch_region_mock(self):
        """Test eQTL region fetch with mocked response."""
        mock_response = [
            {
                "variantId": "rs67890",
                "chromosome": "1",
                "position": 1500000,
                "pValue": 2.5e-8,
                "beta": 0.2,
                "standardError": 0.03,
                "geneId": "ENSG00000123456",
                "geneSymbol": "TESTGENE",
                "tissueLabel": "Whole Blood",
                "studyId": "eqtl_study_1",
                "qtlGroup": "eQTL"
            }
        ]

        with patch.object(eqtl_service, '_get_client') as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.get.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            result = await eqtl_service.fetch_region("1", 1000000, 2000000)

            assert isinstance(result, EQTLRegionResponse)
            assert result.region == "1:1000000-2000000"
            assert len(result.variants) == 1
            assert result.variants[0].variant_id == "rs67890"
            assert result.variants[0].gene_symbol == "TESTGENE"
            assert result.variants[0].tissue == "Whole Blood"
            assert result.total_results == 1


class TestLDService:
    """Test LD computation service."""

    @pytest.mark.asyncio
    async def test_compute_ld_mock(self):
        """Test LD computation with mocked Ensembl response."""
        mock_variants = [
            {"id": "rs111", "start": 1000000},
            {"id": "rs222", "start": 1001000},
            {"id": "rs333", "start": 1002000},
        ]

        with patch.object(ld_service, '_get_client') as mock_client:
            mock_async_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_variants
            mock_response_obj.raise_for_status = MagicMock()
            mock_async_client.get.return_value = mock_response_obj
            mock_client.return_value = mock_async_client

            result = await ld_service.compute_ld("1", 1000000, 1003000, population="EUR", max_variants=10)

            assert isinstance(result, LDMatrixResponse)
            assert result.region == "1:1000000-1003000"
            assert result.population == "EUR"
            assert len(result.variants) == 3
            assert len(result.ld_matrix) == 3
            assert len(result.ld_matrix[0]) == 3
            # Diagonal should be 1.0
            assert result.ld_matrix[0][0] == 1.0
            assert result.ld_matrix[1][1] == 1.0
            assert result.ld_matrix[2][2] == 1.0
            # Off-diagonal should be < 1.0
            assert result.ld_matrix[0][1] < 1.0
            assert result.query_time_ms >= 0


class TestLocusCompareService:
    """Test locus compare workflow service."""

    @pytest.mark.asyncio
    async def test_run_workflow_mock(self):
        """Test end-to-end locus compare workflow with mocked services."""
        request = LocusCompareRequest(region="1:1000000-1003000")

        # Mock GWAS response
        mock_gwas = GWASRegionResponse(
            variants=[
                GWASVariant(
                    variant_id="rs123",
                    chromosome="1",
                    position=1001000,
                    p_value=1e-10,
                    trait="Test trait",
                    study_accession="GCST001",
                    gene="GENE1"
                )
            ],
            region="1:1000000-1003000",
            total_results=1,
            query_time_ms=100
        )

        # Mock eQTL response
        mock_eqtl = EQTLRegionResponse(
            variants=[
                EQTLVariant(
                    variant_id="rs123",
                    chromosome="1",
                    position=1001000,
                    p_value=1e-8,
                    gene_id="ENSG001",
                    gene_symbol="GENE1",
                    tissue="Blood",
                    study_id="eqtl1",
                    qtl_group="eQTL"
                )
            ],
            region="1:1000000-1003000",
            total_results=1,
            query_time_ms=100
        )

        # Mock LD response
        mock_ld = LDMatrixResponse(
            variants=[
                LDVariant(variant_id="rs123", chromosome="1", position=1001000, allele_frequency=0.3)
            ],
            ld_matrix=[[1.0]],
            region="1:1000000-1003000",
            population="EUR",
            query_time_ms=100
        )

        with patch.object(gwas_service, 'fetch_region', return_value=mock_gwas), \
             patch.object(eqtl_service, 'fetch_region', return_value=mock_eqtl), \
             patch.object(ld_service, 'compute_ld', return_value=mock_ld):

            result = await locuscompare_service.run_workflow(request)

            assert isinstance(result, LocusCompareResponse)
            assert result.region == "1:1000000-1003000"
            assert len(result.panels) == 4
            assert result.panels[0].panel_type == "gwas"
            assert result.panels[1].panel_type == "eqtl"
            assert result.panels[2].panel_type == "ld"
            assert result.panels[3].panel_type == "combined"
            assert result.gwas_data.total_results == 1
            assert result.eqtl_data.total_results == 1
            assert result.ld_data.population == "EUR"
            assert result.workflow_time_ms >= 0


class TestGeneticsAPI:
    """Test genetics API endpoints."""

    @pytest.fixture
    async def client(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

    @pytest.fixture
    async def demo_token(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/demo-login", follow_redirects=False)
        cookies = response.headers.get("set-cookie", "")
        import re
        match = re.search(r'access_token=([^;]+)', cookies)
        if match:
            return match.group(1)
        return "demo-access-token"

    @pytest.mark.asyncio
    async def test_gwas_region_endpoint(self, client: AsyncClient, demo_token: str):
        """Test GWAS region endpoint."""
        with patch.object(gwas_service, 'fetch_region') as mock_fetch:
            mock_fetch.return_value = GWASRegionResponse(
                variants=[],
                region="1:1000000-2000000",
                total_results=0,
                query_time_ms=50
            )
            response = await client.post(
                "/api/v1/genetics/gwas/region",
                json={"chromosome": "1", "start": 1000000, "end": 2000000},
                cookies={"access_token": demo_token}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["region"] == "1:1000000-2000000"

    @pytest.mark.asyncio
    async def test_locus_compare_workflow_endpoint(self, client: AsyncClient, demo_token: str):
        """Test locus compare workflow endpoint."""
        with patch.object(locuscompare_service, 'run_workflow') as mock_workflow:
            from app.services.genetics.locuscompare import LocusCompareResponse, LocusComparePanel
            from app.services.genetics.gwas import GWASRegionResponse
            from app.services.genetics.eqtl import EQTLRegionResponse
            from app.services.genetics.ld import LDMatrixResponse

            mock_workflow.return_value = LocusCompareResponse(
                region="1:1000000-1003000",
                panels=[
                    LocusComparePanel(panel_type="gwas", title="GWAS", data={}, plot_config={}),
                    LocusComparePanel(panel_type="eqtl", title="eQTL", data={}, plot_config={}),
                    LocusComparePanel(panel_type="ld", title="LD", data={}, plot_config={}),
                    LocusComparePanel(panel_type="combined", title="Combined", data={}, plot_config={}),
                ],
                gwas_data=GWASRegionResponse(variants=[], region="1:1000000-1003000", total_results=0, query_time_ms=50),
                eqtl_data=EQTLRegionResponse(variants=[], region="1:1000000-1003000", total_results=0, query_time_ms=50),
                ld_data=LDMatrixResponse(variants=[], ld_matrix=[], region="1:1000000-1003000", population="EUR", query_time_ms=50),
                workflow_time_ms=200,
                gwas_time_ms=50,
                eqtl_time_ms=50,
                ld_time_ms=50,
            )
            response = await client.post(
                "/api/v1/genetics/locuscompare/workflow",
                json={"region": "1:1000000-1003000"},
                cookies={"access_token": demo_token}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["region"] == "1:1000000-1003000"
            assert len(data["panels"]) == 4

    @pytest.mark.asyncio
    async def test_locus_compare_invalid_region(self, client: AsyncClient, demo_token: str):
        """Test locus compare with invalid region format."""
        response = await client.post(
            "/api/v1/genetics/locuscompare/workflow",
            json={"region": "invalid"},
            cookies={"access_token": demo_token}
        )
        assert response.status_code == 400
