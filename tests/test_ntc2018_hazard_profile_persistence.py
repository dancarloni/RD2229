from src.codes.ntc2018.spectrum_paste_service import build_profile
from verification_project import VerificationProject


def test_profile_roundtrip(tmp_path):
    proj = VerificationProject()
    proj.new_project()

    raw = "Operatività 0.5 0.25 0.3 0.4"
    profile = build_profile(
        class_of_use="II", vita_nominale_years=50, vr_years=100, site_label="Test", raw_paste=raw
    )
    proj.seismic_inputs.ntc2018_hazard_profile = profile

    file = tmp_path / "proj.jsonp"
    proj.save_to_file(str(file))

    # load into new project
    loaded = VerificationProject()
    loaded.load_from_file(str(file))
    loaded_profile = loaded.seismic_inputs.ntc2018_hazard_profile
    assert loaded_profile is not None
    assert loaded_profile.raw_paste == raw
    assert loaded_profile.class_of_use == "II"
    assert len(loaded_profile.parsed_rows) == 1
    row = loaded_profile.parsed_rows[0]
    assert row.limit_state_label.lower().startswith("operativ")
