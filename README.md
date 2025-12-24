# Neblify - Transaction Matching & Semantic Search API

# Overview

Neblify is a FastAPI-based solution for intelligent transaction-to-user matching and semantic search, addressing three core tasks:

1. **Task 1**: Match users to a transaction based on the transaction ID
2. **Task 2**: Find transactions with semantically similar descriptions using language model embeddings  
3. **Task 3**: Production considerations and scalability strategies

---

# Project Structure

```

├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application entry point
│   ├── endpoints.py          # API route handlers
│   ├── services.py           # Business logic (matching, search)
│   └── models.py             # Pydantic request/response schemas
├── data/
│   ├── users.csv             # User data (id, name)
│   └── transactions.csv      # Transaction data (id, amount, description)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

# Setup & Installation

# Prerequisites
- Python 3.8+
- pip or conda

# Installation Steps

1. **Navigate to project directory:**
   ```bash
   cd Neblify_Task
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional):**
   ```bash
   # Copy the example .env file
   cp .env.example .env
   
   # Edit .env to customize settings (optional)
   ```
   
   Available environment variables in `.env`:
   - `API_HOST` - Server host (default: 0.0.0.0)
   - `API_PORT` - Server port (default: 8000)
   - `API_RELOAD` - Enable auto-reload (default: true)
   - `DATA_USERS_PATH` - Path to users CSV (default: data/users.csv)
   - `DATA_TRANSACTIONS_PATH` - Path to transactions CSV (default: data/transactions.csv)
   - `MODEL_NAME` - Sentence transformer model (default: all-MiniLM-L6-v2)
   - `SIMILARITY_THRESHOLD` - Semantic search threshold (default: 0.3)
   - `LOG_LEVEL` - Logging level (default: INFO)

5. **Ensure CSV files are present:**
   - `data/users.csv` (columns: id, name)
   - `data/transactions.csv` (columns: id, amount, description)

---

## Running the API

### Start the Server

```bash
python run.py
```

The API will be available at `http://localhost:8000`

**Alternative (using uvicorn directly):**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Demo Video

Watch the API in action:

<video width="100%" controls>
  <source src="demo.mp4" type="video/mp4">
   Your browser does not support the video tag.
</video>

---

# API Endpoints

# Task 1: Match Users to Transaction
**Endpoint:** `GET /match-users/{transaction_id}`

**Description:** Takes a transaction ID as input and returns the users which could be considered to match the transaction. This endpoint is used to match users with their payments.

**Features:**
- Accounts for edge cases such as typos
- Checks both inexact and exact matches
- Input names consist of latin alphabet characters
- Users are sorted in order of relevance
- Includes a metric of "how well each transaction matches"

**Parameters:**
- `transaction_id` (path parameter): The ID of the transaction to match

**Response:**
```json
{
  "users": [
    { "id": "user_123", "match_metric": 0.95 },
    { "id": "user_456", "match_metric": 0.78 }
  ],
  "total_number_of_matches": 2
}
```

**Example:**
```bash
curl "http://localhost:8000/match-users/caqjJtrI"
```

---

### Task 2: Search Similar Descriptions
**Endpoint:** `GET /search-similar-descriptions?query=payment`

**Description:** Takes a string as input and returns all transactions which have "similar" descriptions to this string in a semantical way. Uses language model embeddings for semantic similarity.

**Features:**
- Uses language model embeddings for semantic understanding
- Transactions are sorted in order of relevance
- Includes the total number of input tokens used to create the embeddings
- Accounts for semantic similarity, not just keyword matching

**Parameters:**
- `query` (query parameter): Text query to find semantically similar descriptions for

**Response:**
```json
{
  "transactions": [
    { "id": "txn_101", "embedding": 0.87 },
    { "id": "txn_202", "embedding": 0.72 }
  ],
  "total_number_of_tokens_used": 10
}
```

**Example:**
```bash
curl "http://localhost:8000/search-similar-descriptions?query=payment+from+contractor"
```

---

### Health Check
**Endpoint:** `GET /health`

**Description:** Simple health check endpoint.

**Response:**
```json
{ "status": "healthy" }
```

---

## Task 1: User Matching Approach

### Strategy

The fuzzy matching implementation uses a **multi-tier matching strategy** that progressively handles more complex matching scenarios:

1. **Exact Match (Score: 1.0)**
   - Transaction description exactly matches user name (case-insensitive)

2. **Token Match (Score: 0.95)**
   - Any whitespace-separated token in description exactly matches the user name

3. **Partial Match (Score: 0.85+)**
   - User name appears as substring in description
   - Score adjusted by name-to-description length ratio

4. **Fuzzy Token Matching (Score: 0.70-0.90)**
   - Each token in description is compared to user name
   - Uses Levenshtein distance ratio for typo tolerance
   - Captures variations like "Jhn" → "John"

5. **Full Fuzzy Matching (Score: 0.70+)**
   - Entire description compared to user name
   - Token sort ratio normalizes word order

### Why This Approach

- **Handles typos:** Fuzzy matching catches misspellings and abbreviations
- **Case-insensitive:** Works regardless of capitalization
- **Partial names:** Identifies users even when description contains multiple names
- **Relevance ranking:** Multi-tier scoring ensures most relevant matches appear first
- **Efficient:** Early exits on exact matches avoid unnecessary comparisons

### Libraries Used

- **rapidfuzz**: Industry-standard fuzzy string matching library
  - Uses optimized Levenshtein distance
  - Token-sort ratio handles word order variations
  - C++ backend for performance

### Limitations

1. **Single Name Matching**: Assumes user names are single tokens or can be extracted as such
   - Limitation: Complex names like "Mary Jane Smith" may not match "Mary" alone
   - Mitigation: Could tokenize names and match partial user names

2. **Latin Characters Only**: Solution assumes names contain only Latin alphabet characters
   - Limitation: Won't work for names with diacritics (José, Müller) or non-Latin scripts
   - Mitigation: Add Unicode normalization (NFD) for accent handling

3. **No Contextual Understanding**: Pure string matching without semantic understanding
   - Limitation: Won't understand "John Smith" ≠ "Smith & Co"
   - Mitigation: Could add NLP-based entity extraction for organization names

4. **Typo Tolerance Threshold**: Current threshold (70%) might be too loose or strict
   - Limitation: May have false positives/negatives depending on threshold tuning
   - Mitigation: Could implement confidence scoring with configurable thresholds

5. **No Learning**: Matching rules are static, not adaptive
   - Limitation: Won't improve from false positives/negatives
   - Mitigation: Could add user feedback loop to retrain model

---

## Task 2: Semantic Search Approach

### Strategy

The semantic search implementation uses **pre-trained sentence transformers** to generate dense embeddings:

1. **Model Selection**: `all-MiniLM-L6-v2`
   - Lightweight (22M parameters) but effective for semantic similarity
   - Pre-trained on 215M sentence pairs
   - Handles domain-agnostic text well

2. **Embedding Generation**
   - Converts both query and transaction descriptions into 384-dimensional vectors
   - Captures semantic meaning, not just keyword matching

3. **Similarity Computation**
   - Computes cosine similarity between query and each transaction embedding
   - Normalizes similarity from [-1, 1] to [0, 1] range
   - Filters results with similarity > 0.3 threshold

4. **Token Counting**
   - Counts input tokens for cost/monitoring purposes
   - Uses whitespace tokenization for simplicity

### Why This Approach

- **Semantic Understanding**: Captures meaning beyond exact keywords
  - "salary payment" matches "employee compensation" 
- **Language Model Quality**: Pre-trained on large corpus, generalizes well
- **Efficiency**: Small model suitable for real-time inference
- **Normalized Scores**: 0-1 range makes scores interpretable
- **Extensible**: Can easily swap models for different domains

### Libraries Used

- **sentence-transformers**: Semantic similarity using transformer-based models
  - Built on HuggingFace transformers
  - Efficient similarity computation
  - Pre-trained on various tasks

- **numpy**: Efficient numerical operations for embeddings
  - Fast cosine similarity computation

### Limitations

1. **Model Specificity**: `all-MiniLM-L6-v2` is general-purpose
   - Limitation: May not be optimal for financial/payment domain
   - Mitigation: Could use domain-specific models or fine-tune on payment data

2. **Semantic Ambiguity**: Model doesn't understand context
   - Limitation: "bank transfer" could mean moving money or financial institution
   - Mitigation: Could provide domain context or use multi-stage retrieval

3. **Similarity Threshold**: Fixed threshold (0.3) may miss relevant results
   - Limitation: Threshold selection is arbitrary
   - Mitigation: Could make threshold configurable or use dynamic percentile ranking

4. **Embedding Dimensionality**: 384 dimensions may compress information loss
   - Limitation: Larger models use more memory/compute
   - Mitigation: Could use larger models (e.g., `all-mpnet-base-v2`) if resources permit

5. **Token Counting**: Simplified whitespace-based counting
   - Limitation: Doesn't match actual tokenizer used by model
   - Mitigation: Could use model's actual tokenizer (requires loading additional objects)

6. **One-way Similarity**: Doesn't consider bidirectional similarity
   - Limitation: Query might not be as "relevant" to transaction as transaction is to query
   - Mitigation: Could implement bidirectional similarity checks

---

## Testing

### Manual Testing via Curl

```bash
# Test health check
curl http://localhost:8000/health

# Test Task 1 - User matching
curl "http://localhost:8000/match-users/1"

# Test Task 2 - Semantic search
curl "http://localhost:8000/search-similar-descriptions?query=contractor+payment"
```

### Using Python Requests

```python
import requests

# Task 1
response = requests.get("http://localhost:8000/match-users/1")
print(response.json())

# Task 2
response = requests.get("http://localhost:8000/search-similar-descriptions?query=payment")
print(response.json())
```

---

## Task 3: Production Roadmap

### Infrastructure & Scalability

| Component | Current | Production |
|-----------|---------|-----------|
| **Data Storage** | CSV (in-memory) | PostgreSQL + Redis cache |
| **Model Serving** | Single-threaded | GPU-accelerated + batch processing |
| **API Server** | Synchronous | Async with Gunicorn/multiple workers |
| **Caching** | Python-level | Redis for embeddings & results |
| **Deployment** | Local | Docker + Kubernetes |

**Key Changes:**
- Replace CSV with PostgreSQL for scalability and persistence
- Add Redis for caching embeddings (reduces compute by ~80%)
- Use GPU acceleration for embedding generation (10-50x faster)
- Implement async database queries and batch endpoints

### Reliability Improvements

- **Logging**: Structured logging with correlation IDs for debugging
- **Monitoring**: Track latency, error rates, cache hit rates with OpenTelemetry
- **Circuit Breaker**: Graceful fallbacks if embedding service fails
- **Input Validation**: Stricter validation, error handling, and sanitization
- **Health Checks**: Extended health checks for database and cache connectivity

### Advanced Features

```python
# Batch API endpoints
POST /batch/match-users          # Process multiple transactions
POST /batch/search-descriptions  # Bulk semantic search

# Admin utilities
GET /admin/cache-stats           # Monitor cache performance
POST /admin/clear-cache          # Invalidate cached embeddings

# Export capabilities
GET /embeddings/transaction/{id} # Retrieve embeddings for analysis
```

### Performance Optimizations

1. **Hybrid Search**: Combine keyword matching (Elasticsearch) + semantic search
2. **Model Improvements**: 
   - Fine-tune embeddings on payment domain data
   - Use domain-specific models for better accuracy
   - Implement re-ranking for top-k results
3. **Advanced Matching**:
   - Add phonetic matching (Soundex) for name variations
   - NLP-based entity recognition for organization names
   - Confidence scoring with explainability

### Security & Operations

| Area | Implementation |
|------|-----------------|
| **Authentication** | API keys or JWT tokens |
| **Rate Limiting** | Token bucket algorithm |
| **Data Privacy** | Encryption at rest, PII masking |
| **Versioning** | Pin dependencies, automated security updates |
| **Model Versioning** | Track model versions, A/B testing capability |

### Deployment Architecture

```bash
# Production deployment options

# Option 1: Docker (containerized)
docker build -t neblify-api .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://... neblify-api

# Option 2: Kubernetes (cloud-native)
kubectl apply -f deployment.yaml  # Multi-replica setup with autoscaling

# Option 3: Serverless
# Deploy as AWS Lambda/Google Cloud Functions with API Gateway
```

### Estimated Improvements

| Metric | Current | Production |
|--------|---------|-----------|
| **Query Latency** | 200-500ms | 50-100ms (with caching) |
| **Throughput** | ~10 req/s | 100+ req/s |
| **Memory Usage** | ~500MB | ~2GB (with Redis) |
| **Cost/1M requests** | N/A | ~$50-100 (assuming $0.00005 per inference) |

---

## Code Quality

### Principles Followed

✓ **DRY (Don't Repeat Yourself)**: Reusable DataLoader, modular services  
✓ **SOLID Principles**: Single responsibility, loose coupling  
✓ **Type Hints**: Full type annotations for IDE support and documentation  
✓ **Error Handling**: Try-catch with meaningful error messages  
✓ **Caching**: Lazy loading and result caching for efficiency  
✓ **Documentation**: Docstrings for all functions and classes  
✓ **Code Organization**: Separated concerns (models, services, endpoints)  
✓ **Clean Code**: Meaningful variable names, clear logic flow  

---

## Troubleshooting

### ImportError: No module named 'fastapi'
```bash
pip install -r requirements.txt
```

### Connection refused on localhost:8000
- Ensure server is running: `python -m uvicorn app.main:app --reload`
- Check if port 8000 is available

### Transaction ID not found
- Verify transaction ID exists in `data/transactions.csv`
- Check CSV format and encoding (should be UTF-8)

### Slow embedding generation
- First run loads the model (slow)
- Subsequent queries use cached model (fast)
- Consider GPU acceleration for production

### Empty results from matching/search
- Check CSV data and ensure descriptions/names are populated
- Verify similarity thresholds haven't filtered all results
- Try broader query strings

---

## Future Enhancements

1. **Machine Learning Model**: Train on historical matches to improve accuracy
2. **Spell Checker**: Correct misspellings before matching
3. **Multi-language Support**: Handle non-Latin characters and translations
4. **Active Learning**: Learn from user feedback to improve matching
5. **Explanation Features**: Provide reasoning for why matches were selected
6. **Custom Models**: Fine-tune embeddings on payment domain
7. **Real-time Updates**: WebSocket support for live matching results
8. **Analytics**: Dashboard for matching performance and accuracy metrics

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104.1 | Web framework |
| uvicorn | 0.24.0 | ASGI server |
| pydantic | 2.5.0 | Data validation |
| rapidfuzz | 3.6.0 | Fuzzy string matching |
| sentence-transformers | 2.2.2 | Semantic embeddings |
| numpy | 1.24.3 | Numerical operations |
| torch | 2.0.1 | Deep learning framework |

---

## License

This solution is created for Neblify and is provided as-is for evaluation purposes.

---

## Questions?

For questions or issues, refer to the API documentation at `/docs` once the server is running.
