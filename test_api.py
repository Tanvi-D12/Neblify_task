"""
Sample test script demonstrating how to use the Deel AI Challenge API.
Run this after starting the server with: python run.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint."""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def test_match_users(transaction_id: str):
    """Test the user matching endpoint."""
    print("\n" + "="*60)
    print(f"TEST: Match Users for Transaction ID: {transaction_id}")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/match-users/{transaction_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nTotal Matches: {data['total_number_of_matches']}")
            print("\nTop Matches:")
            for user in data['users'][:5]:  # Show top 5
                print(f"  - User ID: {user['id']}, Match Metric: {user['match_metric']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def test_semantic_search(query: str):
    """Test the semantic similarity search endpoint."""
    print("\n" + "="*60)
    print(f"TEST: Semantic Search for Query: '{query}'")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/search-similar-descriptions",
            params={"query": query}
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nTotal Tokens Used: {data['total_number_of_tokens_used']}")
            print(f"Total Matches: {len(data['transactions'])}")
            print("\nTop Matches (by similarity):")
            for trans in data['transactions'][:5]:  # Show top 5
                print(f"  - Transaction ID: {trans['id']}, Embedding Score: {trans['embedding']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DEEL AI CHALLENGE - API TEST SUITE")
    print("="*60)
    print("\nMake sure the server is running: python run.py")
    
    # Give user time to read the message
    time.sleep(1)
    
    # Test health check
    test_health_check()
    
    # Test Task 1 - Match Users (with different transaction IDs)
    test_match_users("caqjJtrI")  # Example from the CSV
    test_match_users("AcwQVVtq")
    test_match_users("invalid_id")  # Test error handling
    
    # Test Task 2 - Semantic Search (with different queries)
    test_semantic_search("liam johnson payment")
    test_semantic_search("transfer money")
    test_semantic_search("salary payment contractor")
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60)
    print("\nFor interactive testing, visit: http://localhost:8000/docs")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API server.")
        print("Please make sure the server is running with: python run.py")
