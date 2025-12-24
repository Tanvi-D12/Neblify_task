"""Business logic services for matching and semantic search."""

import os
import csv
from typing import List, Dict, Tuple
from rapidfuzz import fuzz
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import settings


class DataLoader:
    """Load and cache data from CSV files."""
    
    _users_cache: Dict[str, str] = None
    _transactions_cache: Dict[str, str] = None
    
    @classmethod
    def get_users(cls) -> Dict[str, str]:
        """Load users from CSV. Returns {id: name}."""
        if cls._users_cache is not None:
            return cls._users_cache
        
        cls._users_cache = {}
        csv_path = settings.DATA_USERS_PATH
        
        if not os.path.exists(csv_path):
            return cls._users_cache
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row and 'id' in row and 'name' in row:
                    cls._users_cache[row['id']] = row['name']
        
        return cls._users_cache
    
    @classmethod
    def get_transactions(cls) -> Dict[str, str]:
        """Load transactions from CSV. Returns {id: description}."""
        if cls._transactions_cache is not None:
            return cls._transactions_cache
        
        cls._transactions_cache = {}
        csv_path = settings.DATA_TRANSACTIONS_PATH
        
        if not os.path.exists(csv_path):
            return cls._transactions_cache
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row and 'id' in row and 'description' in row:
                    cls._transactions_cache[row['id']] = row['description']
        
        return cls._transactions_cache


class UserMatcher:
    """Fuzzy match users based on transaction descriptions."""
    
    # Thresholds for different matching strategies
    EXACT_MATCH_THRESHOLD = 100
    PARTIAL_MATCH_THRESHOLD = 80
    FUZZY_MATCH_THRESHOLD = 70
    
    @staticmethod
    def match_users(transaction_id: str) -> Tuple[List[Dict], int]:
        """
        Find users matching a transaction description.
        
        Returns:
            Tuple of (matches list, total count) where matches contain id and match_metric
        """
        transactions = DataLoader.get_transactions()
        users = DataLoader.get_users()
        
        # Validate transaction exists
        if transaction_id not in transactions:
            return [], 0
        
        description = transactions[transaction_id].strip().lower()
        
        if not description or not users:
            return [], 0
        
        # Split description into potential name tokens
        tokens = description.split()
        matches = {}
        
        for user_id, user_name in users.items():
            user_name_lower = user_name.strip().lower()
            
            # Strategy 1: Exact match on full name
            if user_name_lower == description:
                matches[user_id] = 1.0
                continue
            
            # Strategy 2: Token-based matching (any token matches full user name)
            if user_name_lower in tokens:
                matches[user_id] = 0.95
                continue
            
            # Strategy 3: Partial name match (user name in description)
            if user_name_lower in description:
                # Calculate ratio based on name length to description length
                ratio = len(user_name_lower) / len(description)
                matches[user_id] = 0.85 + (ratio * 0.1)
                continue
            
            # Strategy 4: Fuzzy token matching (token in description contains user name)
            best_token_score = 0
            for token in tokens:
                token_score = fuzz.token_sort_ratio(user_name_lower, token) / 100.0
                if token_score > best_token_score:
                    best_token_score = token_score
            
            if best_token_score >= UserMatcher.FUZZY_MATCH_THRESHOLD / 100.0:
                matches[user_id] = best_token_score
                continue
            
            # Strategy 5: Full fuzzy matching on entire description
            full_score = fuzz.token_sort_ratio(user_name_lower, description) / 100.0
            
            if full_score >= UserMatcher.FUZZY_MATCH_THRESHOLD / 100.0:
                matches[user_id] = full_score
        
        # Sort by match_metric (descending)
        sorted_matches = sorted(
            matches.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        result = [
            {"id": user_id, "match_metric": round(score, 2)}
            for user_id, score in sorted_matches
        ]
        
        return result, len(result)


class SemanticSearcher:
    """Perform semantic similarity search using embeddings."""
    
    _model = None
    
    @classmethod
    def get_model(cls):
        """Load sentence transformer model (lazy loading)."""
        if cls._model is None:
            cls._model = SentenceTransformer(settings.MODEL_NAME)
        return cls._model
    
    @staticmethod
    def search_transactions(query: str) -> Tuple[List[Dict], int]:
        """
        Find transactions with similar descriptions using semantic search.
        
        Returns:
            Tuple of (matches list, total token count) where matches contain id and embedding score
        """
        transactions = DataLoader.get_transactions()
        
        if not transactions:
            return [], 0
        
        model = SemanticSearcher.get_model()
        
        # Generate embeddings for query
        query_embedding = model.encode(query, convert_to_tensor=False)
        
        # Count tokens in input query
        # Using simple whitespace tokenization as approximation
        tokens_used = len(query.split())
        
        # Generate embeddings for all transaction descriptions
        transaction_ids = list(transactions.keys())
        descriptions = [transactions[tid] for tid in transaction_ids]
        
        description_embeddings = model.encode(descriptions, convert_to_tensor=False)
        
        # Calculate cosine similarity between query and each description
        matches = {}
        
        for idx, (trans_id, description) in enumerate(zip(transaction_ids, descriptions)):
            # Cosine similarity
            similarity = np.dot(query_embedding, description_embeddings[idx]) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(description_embeddings[idx]) + 1e-10
            )
            
            # Normalize to 0-1 range (cosine similarity is -1 to 1)
            normalized_similarity = (similarity + 1) / 2
            
            if normalized_similarity > settings.SIMILARITY_THRESHOLD:  # Only include relevant results
                matches[trans_id] = round(normalized_similarity, 2)
        
        # Sort by embedding score (descending)
        sorted_matches = sorted(
            matches.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        result = [
            {"id": trans_id, "embedding": score}
            for trans_id, score in sorted_matches
        ]
        
        return result, tokens_used
