def evaluate_guides(predictions, labels):
    predicted = {item.get("guide") for item in predictions if item.get("risk") == "LOW"}
    expected = {item.get("guide") for item in labels if item.get("is_safe")}
    true_positive = len(predicted & expected)
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(expected) if expected else 0.0
    quality = (
        sum(item.get("final_score", 0) for item in predictions) / len(predictions)
        if predictions
        else 0.0
    )
    off_target_rate = (
        sum(item.get("off_targets", 0) > 0 for item in predictions) / len(predictions)
        if predictions
        else 0.0
    )
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "guide_quality": round(quality, 2),
        "off_target_rate": round(off_target_rate, 4),
        "sample_size": len(predictions),
    }


def compare_guides(first, second):
    fields = ["efficiency", "final_score", "off_targets", "risk", "gc_content"]
    return {
        "guide_a": {field: first.get(field) for field in fields},
        "guide_b": {field: second.get(field) for field in fields},
        "winner": (
            first.get("guide")
            if first.get("final_score", 0) >= second.get("final_score", 0)
            else second.get("guide")
        ),
    }
