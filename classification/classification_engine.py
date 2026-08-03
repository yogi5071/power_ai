from classification.classification_result import ClassificationResult
from classification.dimension import Dimension


class Classifier:

    def classify(self, question: str) -> ClassificationResult:

        question = question.lower()

        if "battery" in question:

            intent = "battery"

        else:

            intent = "unknown"

        return ClassificationResult(

            intent=intent,

            dimension=Dimension.UNKNOWN,

            value=None,

            confidence=0.0,

            found=False

        )