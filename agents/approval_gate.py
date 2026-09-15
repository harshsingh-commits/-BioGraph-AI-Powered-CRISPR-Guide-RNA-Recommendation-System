from langgraph.types import interrupt


def approval_gate(state):
    if not state.get("approval_required", False):
        return {"approval_status": "not_requested"}

    ranked_guides = state.get("ranked_guides", [])
    recommendation = ranked_guides[0] if ranked_guides else None
    response = interrupt(
        {
            "type": "guide_approval",
            "message": "Approve the top-ranked guide RNA for experimental planning?",
            "recommendation": recommendation,
        }
    )
    approved = response if isinstance(response, bool) else response.get("approved", False)
    return {"approval_status": "approved" if approved else "rejected"}
