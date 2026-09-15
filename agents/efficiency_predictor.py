import os


def efficiency_predictor(state):

    scores = []
    scoring_model = os.getenv("BIOGRAPH_SCORING_MODEL", "gc_heuristic")

    for guide in state["candidate_guides"]:

        gc = guide.count("G") + guide.count("C")

        gc_content = (gc / len(guide)) * 100
        gc_penalty = abs(gc_content - 50) * 1.5
        homopolymer_penalty = max((guide.count(base * 4) for base in "ACGT"), default=0) * 5
        score = round(max(0, min(100, 100 - gc_penalty - homopolymer_penalty)), 2)

        scores.append(
            {
                "guide": guide,
                "efficiency": score,
                "gc_content": round(gc_content, 2),
                "scoring_model": scoring_model,
            }
        )

    return {
        "efficiency_scores": scores,
        "scoring_model": scoring_model,
    }
