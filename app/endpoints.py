"""API endpoints for Task 1 and Task 2."""

from fastapi import APIRouter, HTTPException, Query
from app.models import Task1Response, Task2Response
from app.services import UserMatcher, SemanticSearcher

router = APIRouter()


@router.get("/match-users/{transaction_id}", response_model=Task1Response)
async def match_users(transaction_id: str):
    """
    Task 1: Match users to a transaction based on description.
    
    Takes a transaction ID and returns users whose names match the transaction description,
    sorted by relevance. Handles typos, partial names, and casing issues using fuzzy matching.
    
    Args:
        transaction_id: The ID of the transaction to match
    
    Returns:
        Task1Response with matched users and match metrics (0-1)
    """
    try:
        matches, total_count = UserMatcher.match_users(transaction_id)
        return Task1Response(
            users=matches,
            total_number_of_matches=total_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error matching users: {str(e)}"
        )


@router.get("/search-similar-descriptions", response_model=Task2Response)
async def search_similar_descriptions(query: str = Query(..., min_length=1)):
    """
    Task 2: Find transactions with semantically similar descriptions.
    
    Takes a text query and returns transactions with descriptions that are semantically similar,
    using pre-trained language model embeddings. Results are sorted by relevance.
    
    Args:
        query: The text query to find similar descriptions for
    
    Returns:
        Task2Response with matching transactions, embedding scores, and token count
    """
    try:
        matches, tokens_used = SemanticSearcher.search_transactions(query)
        return Task2Response(
            transactions=matches,
            total_number_of_tokens_used=tokens_used
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching descriptions: {str(e)}"
        )
