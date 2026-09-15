def chromosome_scan(state):
    chromosome = state["chromosome"]
    locations_by_guide = {
        item.get("guide", ""): item.get("locations", [])
        for item in state.get("off_target_results", [])
    }
    hits = sum(
        1
        for locations in locations_by_guide.values()
        for location in locations
        if location.get("reference") == chromosome
    )
    return {"chromosome_scan_results": [{"chromosome": chromosome, "off_target_hits": hits}]}
