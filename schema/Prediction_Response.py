from pydantic import BaseModel,Field


class PredictionDetail(BaseModel):
    Predicted_class: str =Field(...,
                                description="The Perediction class of Premium.",
                                example="Low")
    Confidence_Score: float= Field(...,
                                   description="Confidence Score of Predicted Label.",
                                   example="0.5 in range 0-1")
    Class_Probabilities: dict[str, float] = Field(...,
                                                  description="All output classes Probabilities.",
                                                  example="high:0.5,medium:0.3,low:0.2")

class PredictionResponse(BaseModel):
    Prediction: PredictionDetail

