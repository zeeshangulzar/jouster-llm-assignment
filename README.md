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
