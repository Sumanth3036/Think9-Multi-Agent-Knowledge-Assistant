CONFIDENCE_THRESHOLD = 80


class ConfidenceGate:
    def __init__(self, threshold=CONFIDENCE_THRESHOLD):
        self.threshold = threshold

    def evaluate(self, confidence, categories):
        if "legal" in categories:
            return {
                "status": "pending_review",
                "reason": "Legal answers require human approval.",
            }

        if confidence < self.threshold:
            return {
                "status": "pending_review",
                "reason": (
                    f"Confidence score {confidence} is below "
                    f"the threshold of {self.threshold}."
                ),
            }

        return {
            "status": "approved",
            "reason": "Answer meets the confidence requirements.",
        }