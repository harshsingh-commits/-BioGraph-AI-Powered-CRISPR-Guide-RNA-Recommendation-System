from agents.ranking_engine import ranking_engine


def test_ranking_prefers_efficiency_and_low_risk():
    result = ranking_engine(
        {
            "efficiency_scores": [
                {"guide": "A", "efficiency": 90, "gc_content": 50},
                {"guide": "B", "efficiency": 95, "gc_content": 55},
            ],
            "risk_report": [
                {"guide": "A", "risk": "LOW", "off_targets": 0},
                {"guide": "B", "risk": "HIGH", "off_targets": 4},
            ],
        }
    )
    assert result["ranked_guides"][0]["guide"] == "A"
    assert result["ranked_guides"][0]["final_score"] == 94
