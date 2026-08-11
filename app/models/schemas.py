"""HTTP request and response schemas for the Think9 Brain API."""

from typing import List

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)


class DecisionResponse(BaseModel):
    question: str
    answer: str
    confidence: int
    categories: List[str]
    sources: List[str]
    status: str
    review_required: bool
    decision_id: int


class ReviewQueueResponse(BaseModel):
    """Pending decisions returned by the review queue endpoint."""

    decisions: List[DecisionResponse]
