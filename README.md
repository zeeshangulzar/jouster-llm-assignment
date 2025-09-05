# LLM Knowledge Extractor

A simple FastAPI application that uses OpenAI's GPT-4o-mini to analyze text and extract structured information.

## Features

- **Text Analysis**: Processes unstructured text input
- **Summary Generation**: Creates 1-2 sentence summaries using GPT-4o-mini
- **Metadata Extraction**: Extracts title, topics, sentiment, keywords, and confidence score
- **Keyword Extraction**: Custom implementation to find 3 most frequent nouns
- **Database Storage**: SQLite database for persistence
- **Search API**: Search analyses by topic or keyword
- **Error Handling**: Handles empty input and LLM API failures
- **Token Authentication**: Simple API key authentication for all endpoints
- **Docker Support**: Containerized application
- **Basic Testing**: Simple test for keyword extraction
- **Batch Processing**: Process multiple texts at once (up to 10)

## Setup

### Option 1: Docker (Recommended)

1. Set up environment variables:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export API_TOKEN="your_api_token_here"
```

2. Run with Docker Compose:
```bash
docker-compose up --build
```

### Option 2: Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export API_TOKEN="your_api_token_here"  # Optional: defaults to "demo-token-123"
```

3. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Testing

Run the simple test:
```bash
python test.py
```

## API Endpoints

- `POST /analyze` - Analyze text and return structured data
- `POST /analyze/batch` - Analyze multiple texts at once (up to 10)
- `GET /search?topic=xyz` - Search analyses by topic
- `GET /search?keyword=xyz` - Search analyses by keyword
- `GET /search` - Get all analyses

### Example Usage

**Analyze text:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-token-123" \
  -d '{"text": "Your text here"}'
```

**Analyze multiple texts:**
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-token-123" \
  -d '{"texts": ["Text 1", "Text 2", "Text 3"]}'
```

**Search analyses:**
```bash
curl -H "Authorization: Bearer demo-token-123" \
  "http://localhost:8000/search?topic=healthcare"
```

## Authentication

All API endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Bearer <your-token>
```

- **Default token**: `demo-token-123` (for testing)
- **Custom token**: Set `API_TOKEN` environment variable
- **Error responses**: 401 Unauthorized for invalid/missing tokens

## Design Choices

**Architecture & Framework Selection**: I chose FastAPI as the web framework because it provides automatic API documentation, built-in request/response validation through Pydantic models, and excellent async support. The modular structure separates concerns with dedicated files for database operations (`database.py`), LLM integration (`llm_service.py`), text processing (`text_processing.py`), and data models (`models.py`), making the codebase maintainable and testable.

**LLM Integration Strategy**: I implemented a single API call approach where GPT-4o-mini extracts both summary and structured metadata (title, topics, sentiment) in one request, then supplements it with custom keyword extraction and confidence scoring. This reduces API costs and latency compared to multiple calls, while the custom keyword extraction using regex and frequency counting provides more control over the keyword selection process.

**Database Design**: I selected SQLite for simplicity and portability, storing metadata as JSON text to maintain flexibility without complex schema migrations. The search functionality uses simple LIKE queries on the JSON metadata, which works well for the expected scale but could become inefficient with large datasets.

**Authentication & Security**: I implemented a simple Bearer token authentication system with a default demo token, prioritizing ease of testing and development over enterprise-grade security features.

## Trade-offs Made Due to Time Constraints

**Limited Error Handling**: While I included basic error handling for empty inputs and LLM API failures, I didn't implement comprehensive retry logic, rate limiting, or detailed error logging that would be necessary for production use.

**Simple Search Implementation**: The search functionality uses basic SQL LIKE queries instead of full-text search or more sophisticated indexing, which limits search quality and performance as the dataset grows.

**Basic Testing**: I only included a simple test for keyword extraction missing comprehensive unit tests, integration tests, and performance benchmarks that would ensure code quality and reliability.

**Minimal Configuration**: The application uses hardcoded values for many parameters (like the 10-text batch limit, confidence scoring formula, and stop words list) instead of a proper configuration management system.

**No Caching or Optimization**: I didn't implement response caching, database connection pooling, or other performance optimizations that would be important for handling larger workloads efficiently.
