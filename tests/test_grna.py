from agents.grna_generator import grna_generator


def test_grna_generator_extracts_twenty_base_guides():
    sequence = "A" * 20 + "AGG"
    result = grna_generator({"sequence": sequence, "pam_positions": [20]})
    assert result["candidate_guides"] == ["A" * 20]
    assert result["guide_metadata"][0]["pam_position"] == 20
