def risk_assessor(state):

    risks = []

    for item in state["off_target_results"]:

        off_targets = item["off_targets"]

        if off_targets == 0:
            risk = "LOW"

        elif off_targets <= 5:
            risk = "MEDIUM"

        else:
            risk = "HIGH"

        risks.append(
            {
                "guide": item["guide"],
                "risk": risk,
                "off_targets": off_targets,
            }
        )

    return {"risk_report": risks}
