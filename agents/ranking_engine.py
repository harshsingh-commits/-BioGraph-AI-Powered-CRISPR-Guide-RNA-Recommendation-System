RISK_SCORES = {
    "LOW": 0,
    "MEDIUM": 50,
    "HIGH": 100,
}


def ranking_engine(state):
    risk_by_guide = {item["guide"]: item for item in state.get("risk_report", [])}
    efficiency_by_guide = {item["guide"]: item for item in state.get("efficiency_scores", [])}
    metadata_by_guide = {item["guide"]: item for item in state.get("guide_metadata", [])}
    ranked_guides = []

    for guide, efficiency_item in efficiency_by_guide.items():
        risk_item = risk_by_guide.get(guide, {})
        risk = risk_item.get("risk", "HIGH")
        risk_score = RISK_SCORES.get(risk, 100)
        efficiency = float(efficiency_item.get("efficiency", 0))
        final_score = round((efficiency * 0.6) + ((100 - risk_score) * 0.4), 2)
        ranked_guides.append(
            {
                "rank": 0,
                "guide": guide,
                "efficiency": efficiency,
                "risk": risk,
                "risk_score": risk_score,
                "gc_content": float(efficiency_item.get("gc_content", 0)),
                "off_targets": int(risk_item.get("off_targets", 0)),
                "final_score": final_score,
                "guide_start": metadata_by_guide.get(guide, {}).get("guide_start", 0),
                "guide_end": metadata_by_guide.get(guide, {}).get("guide_end", 0),
                "pam_position": metadata_by_guide.get(guide, {}).get("pam_position", 0),
            }
        )

    ranked_guides.sort(key=lambda item: item["final_score"], reverse=True)
    for rank, item in enumerate(ranked_guides, start=1):
        item["rank"] = rank

    explanation = None
    if ranked_guides:
        top = ranked_guides[0]
        explanation = (
            f"Guide {top['guide']} ranked first with {top['efficiency']:.2f}% efficiency, "
            f"{top['gc_content']:.2f}% GC, {top['off_targets']} off-target hits, "
            f"{top['risk']} risk, and a final score of {top['final_score']:.2f}."
        )
    return {"ranked_guides": ranked_guides, "recommendation_explanation": explanation}
