from src.gui.ntc2018_selector import list_available_codes


def test_norm_selector_lists_codes():
    codes = list_available_codes()
    assert isinstance(codes, list)
    assert 'NTC2018' in codes
