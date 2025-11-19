# VaultAI Architecture

## Overview

VaultAI Integration Layer follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  Health, Exit Ready, Facilitator, CRM, Analytics Routes │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Service Layer                           │
│  Domain-specific business logic for each module          │
│  - ExitReadyService                                      │
│  - FacilitatorService                                    │
│  - CRMService                                            │
│  - AnalyticsService                                      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                   LLM Layer                              │
│  LLMRouter: Intelligent provider selection               │
│  LLMClients: Provider-specific implementations           │
│    - LocalOpenAICompatibleClient                         │
│    - OpenAICompatibleClient                              │
│    - AzureOpenAIClient                                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Core Infrastructure                        │
│  - Configuration (Pydantic Settings)                     │
│  - Database (Async SQLAlchemy)                           │
│  - Authentication (API Key)                              │
│  - Security (PII Redaction)                              │
│  - Logging (Structured JSON)                             │
└──────────────────────────────────────────────────────────┘
```

## Design Principles

### 1. Provider Agnosticism

**Goal**: Support any LLM provider without code changes.

**Implementation**:
- Abstract `LLMClient` interface
- Configuration-driven provider selection
- OpenAI-compatible API as common denominator
- No vendor SDKs (use httpx for all HTTP calls)

**Benefits**:
- Easy to switch providers
- Multi-provider deployments
- Vendor independence

### 2. Stateless Architecture

**VaultAI does NOT**:
- Store business transaction data
- Mutate upstream module databases
- Maintain user session state
- Implement business workflows

**VaultAI DOES**:
- Accept inputs via HTTP requests
- Generate AI outputs
- Log requests for audit/analytics
- Store prompt templates
- Maintain optional document embeddings

**Benefits**:
- Horizontal scalability
- Clear separation of concerns
- Simpler deployment
- Cache-friendly

### 3. Domain Separation

Each Capitalink module has a dedicated service:

```python
ExitReadyService  → /api/v1/vaultai/exit-ready/*
FacilitatorService → /api/v1/vaultai/facilitator/*
CRMService        → /api/v1/vaultai/crm/*
AnalyticsService  → /api/v1/vaultai/analytics/*
```

**Rationale**:
- Different modules may require different providers
- Prompt engineering is domain-specific
- Easier to evolve independently
- Clear ownership and responsibility

### 4. Security by Design

**Layers of security**:

1. **API Key Authentication**
   - All endpoints require valid API key
   - Service-level identification

2. **PII Detection & Redaction**
   - Automatic scanning for sensitive data
   - Configurable redaction patterns
   - Logged detections for compliance

3. **Provider Isolation**
   - Confidential data → local provider
   - General tasks → cloud providers
   - Configurable routing rules

4. **Audit Logging**
   - All requests logged with metadata
   - Request/response tracking
   - Usage analytics

## Data Flow

### Example: Generate Investment Teaser

```
1. External Module (Exit Ready)
   ↓ HTTP POST with API key
2. FastAPI Router (exit_ready_router.py)
   ↓ Validates API key, parses request
3. Exit Ready Service (exit_ready.py)
   ↓ Builds prompt from template
4. LLM Router (router.py)
   ↓ Selects provider (local for confidential data)
5. LLM Client (client.py)
   ↓ HTTP POST to LLM provider
6. LLM Provider (vLLM, OpenAI, etc.)
   ↓ Generates completion
7. LLM Client
   ↓ Parses response, extracts usage
8. Exit Ready Service
   ↓ Detects PII, logs request
9. Database (llm_logs table)
   ↓ Async insert
10. FastAPI Router
    ↓ Returns response to client
11. External Module
```

## Database Schema

### Core Tables

**1. prompt_templates**
- Stores reusable prompt templates
- Supports versioning
- Domain and task type classification
- Placeholder substitution

**2. llm_logs**
- Tracks all LLM requests/responses
- Usage metrics (tokens, latency)
- Status and error tracking
- PII detection results

**3. documents**
- Stores documents for RAG
- Content hashing for deduplication
- Metadata and categorization
- Processing status

**4. embeddings**
- Vector embeddings of document chunks
- pgvector for similarity search
- Links to source documents
- Model and provider tracking

### Indexing Strategy

**High-cardinality indexes**:
- `llm_logs.request_id` (unique lookups)
- `llm_logs.created_at` (time-range queries)
- `documents.external_id` (integration keys)

**Composite indexes**:
- `(domain, task_type, created_at)` for analytics
- `(provider, status, created_at)` for monitoring
- `(document_id, chunk_index)` for chunk retrieval

**Vector indexes**:
- IVFFlat or HNSW for embedding similarity

## LLM Provider System

### LLMRouter

**Responsibilities**:
- Provider selection based on task type
- Load balancing (future)
- Fallback on provider failure
- Configuration management

**Provider Selection Logic**:

```python
def provider_for_task(task_type):
    if task_type.startswith("exit_ready_"):
        return "local"  # Confidential business data
    elif task_type.startswith("facilitator_"):
        return "local"  # Negotiation context
    elif task_type.startswith("crm_"):
        return "default"  # General matching
    elif task_type.startswith("analytics_"):
        return "default"  # Insights generation
    else:
        return "default"
```

### LLMClient Hierarchy

```
LLMClient (Abstract)
├── OpenAICompatibleClient
│   └── LocalOpenAICompatibleClient
└── AzureOpenAIClient
```

**Adding new providers**:
1. Extend `LLMClient`
2. Implement `chat()` and `embed()` methods
3. Register in `LLMRouter._initialize_providers()`
4. Add configuration to Settings

## Request Lifecycle

### 1. Request Reception

```python
@router.post("/teaser")
async def generate_teaser(
    request: TeaserRequest,
    service_id: str = Depends(get_current_service),
):
```

- FastAPI validates request schema
- API key authentication via dependency
- Service identifier extracted

### 2. Service Processing

```python
async def generate_teaser(request, service_id):
    # Build prompt from template
    system_prompt = "You are an expert..."
    user_prompt = f"Company: {request.company_name}..."

    # Create LLM request
    llm_request = LLMRequest(
        messages=[
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ],
        temperature=0.7,
        max_tokens=800,
    )
```

- Domain-specific logic
- Prompt construction
- Parameter selection

### 3. LLM Routing

```python
response = await llm_router.chat(
    request=llm_request,
    task_type="exit_ready_teaser",
)
```

- Provider selection
- Request routing
- Retry logic

### 4. Provider Communication

```python
async def chat(self, messages, **params):
    # Build HTTP request
    payload = {
        "model": self.config.model,
        "messages": [msg.dict() for msg in messages],
        "temperature": params.get("temperature", 0.7),
    }

    # Send with retry
    for attempt in range(self.config.max_retries):
        try:
            response = await self.client.post(
                "/v1/chat/completions",
                headers=self._build_headers(),
                json=payload,
            )
            return self._parse_response(response)
        except Exception as e:
            await self._wait_before_retry(attempt)
```

- HTTP request construction
- Retry with exponential backoff
- Response parsing

### 5. Post-Processing

```python
# Detect PII
pii_detected = detect_pii(response.content)

# Log request
await self._log_request(
    request_id=uuid4(),
    task_type="teaser",
    service_id=service_id,
    messages=llm_request.messages,
    response=response,
    pii_detected=pii_detected,
)

# Return to client
return TeaserResponse(
    teaser=response.content,
    word_count=len(response.content.split()),
    pii_detected=pii_detected,
)
```

- PII detection
- Async logging
- Response construction

## Async Architecture

### Benefits

- **Non-blocking I/O**: Handle multiple requests concurrently
- **Database pooling**: Efficient connection management
- **HTTP requests**: Parallel LLM calls
- **High throughput**: 100+ requests/min per instance

### Implementation

```python
# Async database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Async HTTP client
client = httpx.AsyncClient(
    base_url=config.base_url,
    timeout=config.timeout,
)

# Async service methods
async def generate_teaser(self, request, service_id):
    response = await llm_router.chat(...)
    await self._log_request(...)
```

## Error Handling

### Levels

1. **HTTP Client Errors** → Retry with exponential backoff
2. **Provider Errors** → Log and propagate
3. **Service Errors** → Catch, log, return error response
4. **API Errors** → Global exception handler

### Example

```python
try:
    response = await client.post(...)
except httpx.HTTPStatusError as e:
    # Retry up to max_retries
    if attempt < max_retries - 1:
        await asyncio.sleep(2 ** attempt)
        continue
    else:
        raise Exception(f"Failed after {max_retries} attempts")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## Scalability

### Horizontal Scaling

- **Stateless design**: Any instance can handle any request
- **No sticky sessions**: Load balancer can use round-robin
- **Database pooling**: Efficient resource usage
- **Independent providers**: LLM calls don't block each other

### Deployment Options

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  VaultAI    │     │  VaultAI    │     │  VaultAI    │
│  Instance 1 │     │  Instance 2 │     │  Instance 3 │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       └──────────────┬────────────────────────┘
                      │
              ┌───────▼───────┐
              │ Load Balancer │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │   PostgreSQL  │
              └───────────────┘
```

### Performance Targets

- **Latency**: < 2s for typical requests (depends on LLM)
- **Throughput**: 100+ requests/min per instance
- **Availability**: 99.9% uptime
- **Database**: < 50ms query time

## Observability

### Logging

**Structured JSON logs**:
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "app.services.exit_ready",
  "message": "Generating teaser for Acme Corp",
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "service_id": "exit_ready_module"
}
```

**Log aggregation** (future):
- ELK Stack
- CloudWatch Logs
- Datadog

### Metrics

Track in `llm_logs` table:
- Request count by domain, task type, provider
- Token usage (cost tracking)
- Latency percentiles (p50, p95, p99)
- Error rates

### Alerting

Monitor:
- Provider availability
- Error rate spikes
- Latency degradation
- Database connection pool saturation

## Future Enhancements

### 1. Streaming Responses

```python
@router.post("/teaser/stream")
async def generate_teaser_stream(...):
    async for chunk in llm_router.chat_stream(...):
        yield chunk
```

### 2. Batch Processing

```python
@router.post("/batch")
async def process_batch(requests: List[LLMRequest]):
    tasks = [llm_router.chat(req) for req in requests]
    return await asyncio.gather(*tasks)
```

### 3. Caching

```python
@lru_cache(maxsize=1000)
async def get_cached_response(prompt_hash):
    # Check cache before calling LLM
    pass
```

### 4. Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_api_key)

@app.post("/teaser")
@limiter.limit("10/minute")
async def generate_teaser(...):
    pass
```

### 5. Provider Load Balancing

```python
def select_provider(task_type):
    # Check provider health
    # Distribute load evenly
    # Avoid overloaded providers
    pass
```

## Security Considerations

### Data Classification

| Data Type | Provider | Rationale |
|-----------|----------|-----------|
| Company financials | Local | Confidential |
| Deal terms | Local | Sensitive |
| Negotiation context | Local | Privileged |
| General matching | Cloud | Non-sensitive |
| Public market data | Cloud | Public |

### Compliance

- **GDPR**: PII detection and redaction
- **SOC 2**: Audit logging of all requests
- **Data residency**: Local providers for EU data

### Best Practices

1. **Never log raw API keys** - Only log key prefixes
2. **Redact PII in logs** - Before writing to database
3. **Encrypt in transit** - HTTPS for all connections
4. **Rotate API keys** - Regular key rotation
5. **Least privilege** - API keys scoped to specific services

---

**Related Documents**:
- [API Usage](api_usage.md)
- [Development Guide](development.md)
- [Deployment Guide](deployment.md)
