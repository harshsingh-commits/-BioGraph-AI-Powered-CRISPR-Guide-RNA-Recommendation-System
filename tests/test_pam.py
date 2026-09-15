from agents.pam_finder import pam_finder


def test_pam_finder_returns_ngg_positions():
    result = pam_finder({"sequence": "AAAGGTAACCGG"})
    assert result["pam_positions"] == [2, 9]
    assert result["pam_count"] == 2
