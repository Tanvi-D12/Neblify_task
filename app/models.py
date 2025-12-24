"""Pydantic models for request/response schemas."""

from pydantic import BaseModel
from typing import List


class UserMatch(BaseModel):
    """User match result with relevance metric."""
    id: str
    match_metric: float


class Task1Response(BaseModel):
    """Response schema for user matching endpoint."""
    users: List[UserMatch]
    total_number_of_matches: int


class TransactionMatch(BaseModel):
    """Transaction match result with embedding distance."""
    id: str
    embedding: float


class Task2Response(BaseModel):
    """Response schema for semantic similarity endpoint."""
    transactions: List[TransactionMatch]
    total_number_of_tokens_used: int
