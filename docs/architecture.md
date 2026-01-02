# Architecture Documentation

## Overview

The Pharmacy AI Agent is a Python-based application that provides an AI-powered assistant for pharmacy operations. The system enables users to search for medications, check stock availability, and verify prescription requirements through a natural language interface.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐
│   Gradio UI     │  User Interface Layer
└────────┬────────┘
         │
┌────────▼────────┐
│  Agent Layer    │  OpenAI API Integration
│  (streaming.py) │  Function Calling & Streaming
└────────┬────────┘
         │
┌────────▼────────┐
│  Tools Layer    │  Business Logic
│  (tools/)       │  Tool Functions
└────────┬────────┘
         │
┌────────▼────────┐
│ Database Layer │  Data Access
│  (db.py)        │  JSON Storage
└────────┬────────┘
         │
┌────────▼────────┐
│  Models Layer   │  Data Validation
│  (models/)      │  Pydantic Models
└─────────────────┘
```

## Component Overview

### 1. Models Layer (`app/models/`)

**Purpose (Why):**
Provides type-safe data models using Pydantic for validation and serialization. Ensures data integrity throughout the application.

**Components:**
- `user.py`: User model representing pharmacy customers
- `medication.py`: Medication model with Stock nested model
- `prescription.py`: Prescription model linking users to medications

**Key Features:**
- Automatic validation using Pydantic
- Type hints for all fields
- JSON serialization support
- Required field validation (active_ingredients, dosage_instructions)

### 2. Database Layer (`app/database/`)

**Purpose (Why):**
Manages JSON-based database operations, providing a simple file-based storage solution for the pharmacy data.

**Components:**
- `db.py`: DatabaseManager class for database operations

**Key Features:**
- Load/save JSON database
- Query by ID (users, medications)
- Search medications by name (fuzzy matching)
- Get prescriptions by user
- Automatic caching for performance

### 3. Tools Layer (`app/tools/`)

**Purpose (Why):**
Implements business logic functions that can be called by the AI agent through OpenAI function calling. Each tool provides a specific capability for the pharmacy assistant.

**Components:**
- `medication_tools.py`: Medication search functionality
- `inventory_tools.py`: Stock availability checking
- `prescription_tools.py`: Prescription requirement verification
- `registry.py`: Tool registration and execution routing

**Key Features:**
- OpenAI function calling compatible
- Comprehensive error handling
- Safe fallback values for errors
- Module-level caching for DatabaseManager
- Input validation and normalization

### 4. Agent Layer (`app/agent/`)

**Purpose (Why):**
Integrates with OpenAI API to provide conversational AI capabilities with real-time text streaming. Handles function calling, streaming, and message processing. The agent is stateless and supports both Hebrew and English as required by the project specifications.

**Components:**
- `streaming.py`: StreamingAgent class for real-time streaming responses
- `__init__.py`: Module exports for agent usage

**Key Features:**
- Stateless design (no state between conversations)
- Real-time text streaming (required by project specifications)
- Function calling support with tool integration
- Bilingual support (Hebrew/English)
- Seamless tool call handling during streaming
- **Parallel tool execution**: Independent tools execute concurrently using ThreadPoolExecutor for improved performance
- **Order preservation**: Tool results maintain original order expected by OpenAI API
- **Error isolation**: One tool's failure doesn't prevent other tools from completing

### 5. Security Layer (`app/security/`)

**Purpose (Why):**
Provides security and compliance features including rate limiting and audit logging. Ensures system stability, prevents abuse, and maintains complete traceability of all operations for compliance and debugging.

**Components:**
- `rate_limiter.py`: RateLimiter class for controlling tool execution frequency
- `audit_logger.py`: AuditLogger class for comprehensive audit trail
- `correlation.py`: Correlation ID generation for request tracking

**Key Features:**
- **Thread-safe rate limiting**: Prevents DoS attacks and resource exhaustion with configurable limits
- **Thread-safe audit logging**: Complete traceability of all operations with correlation IDs
- **Concurrent execution support**: All security components are thread-safe for parallel tool execution
- **Configurable limits**: Rate limits configurable via environment variables
- **Structured logging**: JSON-based audit logs for easy analysis

### 6. UI Layer (`app/main.py`)

**Purpose (Why):**
Provides the user interface using Gradio, enabling web-based interaction with the AI agent.

**Components:**
- `main.py`: Application entry point and Gradio interface

**Key Features:**
- Chat interface
- Streaming support
- Tool call visualization
- Bilingual UI

## Data Flow

### Medication Search Flow

```
User Query → Agent → get_medication_by_name() → DatabaseManager → Medication Model → Response
```

### Stock Check Flow

```
User Query → Agent → check_stock_availability() → DatabaseManager → Medication Model → Stock Info → Response
```

### Prescription Check Flow

```
User Query → Agent → check_prescription_requirement() → DatabaseManager → Medication Model → Prescription Info → Response
```

### Parallel Tool Execution Flow

When multiple independent tools are requested simultaneously, they execute in parallel:

```
User Query → Agent → [Tool 1, Tool 2, Tool 3] (parallel execution)
                    ↓
            ThreadPoolExecutor (max_workers=5)
                    ↓
        [Result 1, Result 2, Result 3] (order preserved)
                    ↓
            Combined Response
```

**Benefits:**
- **Performance**: Up to 33% faster execution for multi-tool scenarios
- **Order Preservation**: Results maintain original tool call order
- **Error Isolation**: One tool's failure doesn't affect others
- **Thread-Safety**: RateLimiter and AuditLogger use locks for safe concurrent access

## Design Principles

### 1. Type Safety
- All functions use full type hints
- Pydantic models for data validation
- Type checking throughout the codebase

### 2. Error Handling
- Comprehensive error handling in all tools
- Safe fallback values (e.g., requires_prescription=True on errors)
- Structured error responses

### 3. Performance
- Module-level caching for DatabaseManager
- Efficient database queries
- Minimal redundant operations
- **Parallel tool execution**: Independent tools execute concurrently using ThreadPoolExecutor, reducing total execution time by up to 33% for multi-tool scenarios
- **Thread-safe components**: RateLimiter and AuditLogger use threading.Lock for safe concurrent access

### 4. Maintainability
- Clear separation of concerns
- Modular design
- Comprehensive documentation
- DRY principles (helper functions)

### 5. Safety
- Safe defaults for prescription requirements
- Required field validation
- Input sanitization
- **Thread-safety**: Critical components (RateLimiter, AuditLogger) are thread-safe for parallel execution
- **Rate limiting**: Prevents resource exhaustion and infinite loops with configurable limits

## Technology Stack

- **Python 3.11+**: Core language
- **Pydantic 2.5+**: Data validation and models
- **OpenAI API 1.3+**: AI agent capabilities
- **Gradio 4.0+**: Web interface
- **pytest 7.4+**: Testing framework

## File Structure

```
Wond/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── agent/                  # Agent implementation
│   │   ├── __init__.py
│   │   └── streaming.py        # StreamingAgent class (parallel execution)
│   ├── database/               # Database management
│   │   ├── __init__.py
│   │   └── db.py              # DatabaseManager
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── medication.py
│   │   └── prescription.py
│   ├── tools/                  # Tool functions
│   │   ├── __init__.py
│   │   ├── medication_tools.py
│   │   ├── inventory_tools.py
│   │   ├── prescription_tools.py
│   │   └── registry.py
│   ├── security/               # Security components
│   │   ├── __init__.py
│   │   ├── rate_limiter.py    # Thread-safe rate limiting
│   │   ├── audit_logger.py    # Thread-safe audit logging
│   │   └── correlation.py     # Correlation ID generation
│   └── prompts/                # System prompts
│       └── __init__.py
├── data/
│   └── database.json           # JSON database
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── database_schema.json
│   └── database_structure_design.md
├── tests/                      # Test suite
├── Dockerfile
├── requirements.txt
└── README.md
```

## Logging

The application uses Python's standard logging module with module-level loggers:

- **ERROR**: Critical errors (red)
- **WARNING**: Warnings (orange)
- **INFO**: General information (white)
- **DEBUG**: Debug information (light green)

All modules configure their own logger:
```python
import logging
logger = logging.getLogger(__name__)
```

## Security Considerations

1. **API Keys**: Stored in environment variables, never in code
2. **Input Validation**: All inputs validated before processing
3. **Safe Defaults**: Prescription requirements default to "required" on errors
4. **No Medical Advice**: Agent explicitly prohibited from giving medical advice
5. **Rate Limiting**: Thread-safe rate limiting prevents DoS attacks and resource exhaustion
6. **Audit Logging**: Thread-safe audit logging ensures complete traceability of all operations
7. **Thread-Safety**: Critical security components use threading.Lock to prevent race conditions

## Future Enhancements

1. Database migration to SQL database
2. User authentication
3. Prescription management
4. Order processing
5. Analytics and reporting



