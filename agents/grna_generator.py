def grna_generator(state):
    sequence = state["sequence"]

    guides = []
    guide_metadata = []
    seen_guides = set()

    for pos in state["pam_positions"]:

        start = max(0, pos - 20)

        guide = sequence[start:pos]

        if len(guide) == 20 and guide not in seen_guides:
            guides.append(guide)
            guide_metadata.append(
                {
                    "guide": guide,
                    "guide_start": start,
                    "guide_end": pos,
                    "pam": sequence[pos : pos + 3],
                    "pam_position": pos,
                }
            )
            seen_guides.add(guide)

        if len(guides) == 100:
            break

    return {
        "candidate_guides": guides,
        "guide_metadata": guide_metadata,
        "optimization_attempts": state.get("optimization_attempts", 0) + 1,
    }
