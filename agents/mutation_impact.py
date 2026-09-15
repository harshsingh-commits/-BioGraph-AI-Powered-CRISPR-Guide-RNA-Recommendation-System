def mutation_impact(state):
    impacts = []
    for item in state.get("ranked_guides", []):
        frame_offset = item.get("guide_start", 0) % 3
        consequence = (
            "In-frame indel (position heuristic)"
            if frame_offset == 0
            else "Frameshift risk (position heuristic)"
        )
        impacts.append(
            {
                "guide": item["guide"],
                "consequence": consequence,
                "frame_offset": frame_offset,
                "model": "coding-frame heuristic",
            }
        )
    return {"mutation_impacts": impacts}
