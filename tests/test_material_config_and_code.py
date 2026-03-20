"""
Test unitari per MaterialConfigLoader e compute_material_code.
Verifica formula evaluation, chain dependencies, override, e hash del codice.
"""

import json
import uuid
from pathlib import Path

import pytest

# ── MaterialConfigLoader ──────────────────────────────────────────────────────


class TestMaterialConfigLoader:
    """Test per MaterialConfigLoader (formula eval, schema loading, override)."""

    @pytest.fixture(autouse=True)
    def reset_cache(self):
        """Invalida la cache prima di ogni test."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        MaterialConfigLoader.reload()
        yield
        MaterialConfigLoader.reload()

    def test_load_families_returns_list(self):
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        families = MaterialConfigLoader.load_families()
        assert isinstance(families, list)
        assert len(families) >= 4
        keys = [f["key"] for f in families]
        assert "calcestruzzo" in keys
        assert "acciaio" in keys

    def test_get_norms_for_calcestruzzo(self):
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        norms = MaterialConfigLoader.get_norms_for_family("calcestruzzo")
        assert isinstance(norms, list)
        assert len(norms) >= 1
        norm_keys = [n["key"] for n in norms]
        assert "NTC2018" in norm_keys

    def test_get_norm_schema_calcestruzzo_ntc2018(self):
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
        assert schema is not None
        assert "parametri_input" in schema
        assert "parametri_derivati" in schema
        input_keys = [f["key"] for f in schema["parametri_input"]]
        assert "f_ck" in input_keys

    def test_compute_derived_E_formula(self):
        """Verifica che E calcestruzzo NTC2018 sia calcolato correttamente."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
        # C25/30: f_ck = 254.9 kg/cm² (25 MPa)
        material = {"f_ck": 254.9, "nu": 0.2}
        derived = MaterialConfigLoader.compute_derived(material, schema)
        # E calcestruzzo C25/30 ≈ 30000 MPa ≈ 305000-315000 kg/cm²
        assert "E" in derived, "E deve essere presente nei derivati"
        E = derived["E"]
        assert isinstance(E, (int, float))
        assert 200000 < E < 450000, f"E fuori range realistico: {E}"

    def test_compute_derived_chain_dependency(self):
        """Verifica che la dipendenza a catena E→G funzioni."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
        material = {"f_ck": 254.9, "nu": 0.2}
        derived = MaterialConfigLoader.compute_derived(material, schema)
        if "G" in derived and "E" in derived:
            # G ≈ E / (2 * (1 + nu)) = E / 2.4
            expected_G = derived["E"] / (2.0 * (1.0 + 0.2))
            assert abs(derived["G"] - expected_G) < 10, f"G={derived['G']} ≠ {expected_G}"

    def test_compute_derived_respects_override(self):
        """Un campo con _override=True non deve essere sovrascritto dai derivati."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
        # Imposta E manualmente con override
        material = {"f_ck": 254.9, "nu": 0.2, "E": 999999.0, "E_override": True}
        derived = MaterialConfigLoader.compute_derived(material, schema)
        # E deve rimanere 999999 perché override è attivo
        if "E" in derived:
            assert derived["E"] == 999999.0, "Override dovrebbe impedire il ricalcolo di E"

    def test_compute_derived_formula_error_handled(self):
        """Un errore in una formula non deve far crashare l'intera computazione."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("calcestruzzo", "NTC2018")
        # f_ck mancante → E non calcolabile, ma non deve sollevare eccezione
        material = {"nu": 0.2}
        try:
            derived = MaterialConfigLoader.compute_derived(material, schema)
            # OK se non crasha; warnings possibili
            assert isinstance(derived, dict)
        except Exception as exc:
            pytest.fail(f"compute_derived ha sollevato eccezione inaspettata: {exc}")

    def test_get_norm_schema_nonexistent_family_returns_none_or_raises(self):
        """Famiglia non esistente deve restituire None o sollevare un'eccezione."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        try:
            result = MaterialConfigLoader.get_norm_schema("famiglia_inesistente", "NTC2018")
            # Se non solleva, deve restituire None
            assert result is None
        except Exception:
            pass  # Qualsiasi eccezione è accettata

    def test_compute_derived_acciaio_f_yd(self):
        """Verifica f_yd = f_yk / gamma_s per acciaio NTC2018."""
        from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader

        schema = MaterialConfigLoader.get_norm_schema("acciaio", "NTC2018")
        if schema is None:
            pytest.skip("Schema acciaio NTC2018 non disponibile")
        # B450C: f_yk = 4589 kg/cm² (450 MPa), gamma_s = 1.15
        material = {"f_yk": 4589.0}
        derived = MaterialConfigLoader.compute_derived(material, schema)
        if "f_yd" in derived:
            expected = 4589.0 / 1.15
            assert abs(derived["f_yd"] - expected) < 5.0, f"f_yd={derived['f_yd']} ≠ {expected}"


# ── compute_material_code ─────────────────────────────────────────────────────


class TestComputeMaterialCode:
    """Test per il calcolo automatico del codice materiale (UUID5 hash)."""

    def _get_func(self):
        from src.ui.qt.material_editor.logic.material_repository import compute_material_code

        return compute_material_code

    def test_returns_string(self):
        fn = self._get_func()
        code = fn({"f_ck": 25.0, "descrizione": "Test"})
        assert isinstance(code, str)
        assert len(code) > 0

    def test_deterministic(self):
        """Lo stesso input produce sempre lo stesso codice."""
        fn = self._get_func()
        data = {"f_ck": 25.0, "gamma_c": 1.5, "descrizione": "C25/30"}
        assert fn(data) == fn(data)

    def test_different_data_different_code(self):
        fn = self._get_func()
        data1 = {"f_ck": 25.0}
        data2 = {"f_ck": 30.0}
        assert fn(data1) != fn(data2)

    def test_id_and_codice_excluded(self):
        """I campi 'id' e 'codice' non influenzano il codice calcolato."""
        fn = self._get_func()
        data_base = {"f_ck": 25.0, "descrizione": "C25"}
        data_with_id = {"f_ck": 25.0, "descrizione": "C25", "id": "abc123"}
        data_with_codice = {"f_ck": 25.0, "descrizione": "C25", "codice": "OLD123"}
        assert fn(data_base) == fn(data_with_id)
        assert fn(data_base) == fn(data_with_codice)

    def test_override_fields_excluded(self):
        """I campi _override non influenzano il codice."""
        fn = self._get_func()
        data1 = {"f_ck": 25.0}
        data2 = {"f_ck": 25.0, "E_override": True, "G_override": False}
        assert fn(data1) == fn(data2)

    def test_valid_uuid_format(self):
        """Il codice deve essere un UUID valido."""
        fn = self._get_func()
        code = fn({"f_ck": 25.0})
        # UUID5 ha formato xxxx-xxxx-xxxx-xxxx-xxxx
        try:
            parsed = uuid.UUID(code)
            assert parsed.version == 5
        except ValueError:
            pytest.fail(f"Codice non è un UUID valido: {code}")


# ── MaterialRepository auto-codice ────────────────────────────────────────────


class TestMaterialRepositoryAutoCode:
    """Test per l'auto-generazione del codice in add_material e update_material."""

    def _make_repo(self):
        from src.ui.qt.material_editor.logic.material_repository import MaterialRepository

        return MaterialRepository()

    def test_add_material_auto_assigns_codice(self):
        repo = self._make_repo()
        initial_count = len(repo.materials)
        repo.add_material({"f_ck": 25.0, "descrizione": "C25"})
        assert len(repo.materials) == initial_count + 1
        mat = repo.materials[-1]
        assert "codice" in mat
        assert mat["codice"] not in (None, "")

    def test_add_material_keeps_existing_codice(self):
        repo = self._make_repo()
        initial_count = len(repo.materials)
        repo.add_material(
            {
                "f_ck": 25.0,
                "codice": "CUSTOM-CODE-123",
                "descrizione": "C25",
            }
        )
        assert len(repo.materials) == initial_count + 1
        mat = repo.materials[-1]
        assert mat["codice"] == "CUSTOM-CODE-123"

    def test_update_material_recomputes_codice_if_empty(self):
        repo = self._make_repo()
        repo.add_material({"f_ck": 25.0, "codice": "OLD"})
        idx = len(repo.materials) - 1
        # Aggiorna svuotando il codice → deve essere ricalcolato
        repo.update_material(idx, {"f_ck": 30.0, "codice": ""})
        mat = repo.materials[idx]
        assert mat["codice"] not in (None, "")
        # Non deve essere "OLD" né vuoto
        assert mat["codice"] != "OLD"
