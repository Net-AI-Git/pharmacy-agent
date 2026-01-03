# Setup and Usage Guide

## Overview

This guide provides step-by-step instructions for setting up, running, and using the Pharmacy AI Agent application.

## Prerequisites

- **Python 3.11+**: Required Python version
- **pip**: Python package manager
- **OpenAI API Key**: Required for AI agent functionality
- **Docker** (optional): For containerized deployment

## Installation

### Step 1: Clone or Navigate to Project

```bash
cd Wond
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `gradio>=4.0.0`: Web interface
- `openai>=1.3.0`: OpenAI API client
- `pydantic>=2.5.0`: Data validation
- `python-dotenv>=1.0.0`: Environment variable management
- `pytest>=7.4.0`: Testing framework

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_api_key_here
```

**Note:** Never commit the `.env` file to version control. A `.env.example` file is provided as a template.

### Step 5: Verify Database

Ensure the database file exists at `data/database.json`. The file should contain:
- Users data
- Medications data
- Prescriptions data

See `docs/database_documentation.md` for the expected structure.

## Running the Application

### Local Development

**Option 1: Direct Python Execution**

```bash
python main.py
```

**Option 2: Using Gradio**

The application will start a Gradio web interface. Access it at:
- **Local**: `http://localhost:7860`
- **Network**: `http://0.0.0.0:7860`

### Docker Deployment

#### Prerequisites

1. **Install Docker Desktop**:
   - Download from: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop
   - Verify Docker is running (icon should be green)

2. **Prepare .env file**:
   - Copy `.env.example` to `.env`
   - Add your `OPENAI_API_KEY`

#### Step 1: Build Docker Image

Build the Docker image from the project root:

```bash
docker build -t pharmacy-agent .
```

**Verification:**
- Ensure build completes successfully
- No errors during build
- Image is created (check with `docker images`)

#### Step 2: Run Container

Run the container with one of the following methods:

**Option 1: Using environment variable directly**
```bash
docker run -p 7860:7860 -e OPENAI_API_KEY=your_api_key_here pharmacy-agent
```

**Option 2: Using .env file**
```bash
docker run -p 7860:7860 --env-file .env pharmacy-agent
```

**Verification:**
- Application starts successfully
- Open browser at `http://localhost:7860`
- Test functionality:
  - Streaming responses
  - Tool calls
  - All multi-step flows

#### Important Notes

1. **Port 7860**: The application runs on port 7860. If the port is in use, you can change it:
   ```bash
   docker run -p 8080:7860 -e OPENAI_API_KEY=your_key pharmacy-agent
   ```
   Then access at `http://localhost:8080`

2. **Environment Variables**: If you have additional environment variables (e.g., `ENVIRONMENT`, `RATE_LIMIT_PER_MINUTE`), add them:
   ```bash
   docker run -p 7860:7860 -e OPENAI_API_KEY=your_key -e ENVIRONMENT=prod pharmacy-agent
   ```

3. **Data**: The container includes the `data/` directory with `database.json`, so the application can access the database.

4. **Logs**: To view logs:
   ```bash
   docker logs <container_id>
   ```

#### Troubleshooting Docker Issues

**Docker not recognized:**
- Ensure Docker Desktop is running
- Try restarting the terminal
- Try restarting Docker Desktop

**Port already in use:**
- Change the port in `docker run` (e.g., `-p 8080:7860`)
- Or stop the application running on port 7860

**API Key error:**
- Verify `OPENAI_API_KEY` is passed correctly
- Check it's valid in `.env` file

**Database error:**
- Ensure `data/` directory is included in build
- Verify `database.json` exists

## Usage

### Basic Usage

1. **Start the application** (see Running the Application above)
2. **Open the web interface** in your browser
3. **Type your question** in the chat interface
4. **Receive response** from the AI agent

### Example Queries

#### Medication Search

**Hebrew:**
- "תספר לי על אקמול"
- "מה זה פרצטמול?"
- "אני מחפש תרופה לכאב ראש"

**English:**
- "Tell me about Acetaminophen"
- "What is Paracetamol?"
- "I'm looking for a headache medication"

#### Stock Availability

**Hebrew:**
- "האם יש לכם אקמול במלאי?"
- "כמה יחידות של פרצטמול יש לכם?"

**English:**
- "Do you have Acetaminophen in stock?"
- "How many units of Paracetamol do you have?"

#### Prescription Requirements

**Hebrew:**
- "האם אקמול דורש מרשם?"
- "אני צריך אנטיביוטיקה, האם צריך מרשם?"

**English:**
- "Does Acetaminophen require a prescription?"
- "I need antibiotics, do I need a prescription?"

### Multi-Step Flows

The agent supports complex multi-step interactions:

#### Flow 1: Stock Check
1. User asks about medication availability
2. Agent searches for medication by name
3. Agent checks stock availability
4. Agent provides complete information

**Example:**
```
User: "האם יש לכם אקמול במלאי?"
Agent: [Searches for "אקמול"] → [Checks stock] → "אקמול זמין במלאי. יש לנו 150 יחידות."
```

#### Flow 2: Prescription + Stock Check
1. User asks about prescription requirement
2. Agent searches for medication
3. Agent checks prescription requirement
4. Agent checks stock availability
5. Agent provides complete information

**Example:**
```
User: "אני צריך אנטיביוטיקה, האם צריך מרשם?"
Agent: [Searches] → [Checks prescription] → [Checks stock] → 
       "אמוקסיצילין דורש מרשם רופא. התרופה זמינה במלאי."
```

#### Flow 3: Complete Medication Information
1. User asks for medication information
2. Agent searches for medication
3. Agent retrieves all details
4. Agent checks prescription requirement
5. Agent provides comprehensive information

**Example:**
```
User: "תספר לי על אקמול"
Agent: [Searches] → [Retrieves details] → [Checks prescription] →
       "אקמול (Acetaminophen) הוא משכך כאבים ומפחית חום.
       רכיב פעיל: Paracetamol 500mg
       מינון: 500-1000mg כל 4-6 שעות, מקסימום 4g ביום
       לא דורש מרשם רופא.
       זמין במלאי: 150 יחידות."
```

## Agent Usage

### Using StreamingAgent

The application uses `StreamingAgent` for real-time text streaming responses. Here's how to use it:

```python
from app.agent import StreamingAgent

# Initialize the agent
agent = StreamingAgent(model="gpt-5")

# Stream response in real-time
user_message = "Tell me about Acamol"
for chunk in agent.stream_response(user_message):
    print(chunk, end="", flush=True)
```

### StreamingAgent with Conversation History

```python
from app.agent import StreamingAgent
from typing import List, Dict

# Initialize the agent
agent = StreamingAgent()

# Maintain conversation history within a session
conversation_history: List[Dict[str, str]] = []

# First message
user_message_1 = "What is Acamol?"
response_1 = ""
for chunk in agent.stream_response(user_message_1):
    response_1 += chunk
    print(chunk, end="", flush=True)

# Add to history
conversation_history.append({"role": "user", "content": user_message_1})
conversation_history.append({"role": "assistant", "content": response_1})

# Follow-up message with context
user_message_2 = "Does it require a prescription?"
for chunk in agent.stream_response(user_message_2, conversation_history):
    print(chunk, end="", flush=True)
```

**Note:** The agent is stateless - conversation history is only maintained within a single session. Each new session starts fresh.

## Tool Usage

### Direct Tool Execution

You can also use tools directly in Python code:

```python
from app.tools.medication_tools import get_medication_by_name
from app.tools.inventory_tools import check_stock_availability
from app.tools.prescription_tools import check_prescription_requirement

# Search medication
result = get_medication_by_name("Acamol", language="he")
print(result)

# Check stock
result = check_stock_availability("med_001", quantity=10)
print(result)

# Check prescription requirement
result = check_prescription_requirement("med_001")
print(result)
```

### Tool Registry

```python
from app.tools.registry import get_tools_for_openai, execute_tool

# Get tools for OpenAI
tools = get_tools_for_openai()

# Execute tool
result = execute_tool(
    "get_medication_by_name",
    {"name": "Acamol", "language": "he"}
)
```

## Database Management

### Loading Database

```python
from app.database.db import DatabaseManager

db = DatabaseManager()
data = db.load_db()
```

### Querying Database

```python
# Get medication by ID
medication = db.get_medication_by_id("med_001")

# Get user by ID
user = db.get_user_by_id("user_001")

# Get prescriptions by user
prescriptions = db.get_prescriptions_by_user("user_001")

# Search medications by name
medications = db.search_medications_by_name("Acamol", language="he")
```

### Saving Database

```python
# Modify data
data = db.load_db()
data['users'].append(new_user)

# Save changes
db.save_db(data)
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_medication_tools.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pytest --cov=app tests/
```

## Troubleshooting

### Common Issues

#### 1. Database File Not Found

**Error:**
```
FileNotFoundError: Database file not found: data/database.json
```

**Solution:**
- Ensure `data/database.json` exists
- Check file path is correct
- Verify file permissions

#### 2. OpenAI API Key Not Set

**Error:**
```
OpenAI API key not found
```

**Solution:**
- Create `.env` file with `OPENAI_API_KEY=your_key`
- Verify environment variable is loaded
- Check API key is valid

#### 3. Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'app'
```

**Solution:**
- Ensure you're in the project root directory
- Verify virtual environment is activated
- Check all dependencies are installed

#### 4. Port Already in Use

**Error:**
```
Address already in use
```

**Solution:**
- Change port in `main.py`: `app.launch(server_port=7861)`
- Or stop the process using port 7860

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|-----------|
| `OPENAI_API_KEY` | OpenAI API key for AI agent | Yes |

### Application Settings

Modify settings in `app/main.py`:
- Server port (default: 7860)
- Server host (default: 0.0.0.0)
- Gradio theme and styling

## Best Practices

1. **Environment Variables**: Never commit `.env` file to version control
2. **Database Backups**: Regularly backup `data/database.json`
3. **Error Handling**: Always handle errors gracefully
4. **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
5. **Testing**: Run tests before deploying changes
6. **Documentation**: Keep documentation up to date

## Performance Tips

1. **Database Caching**: DatabaseManager uses internal caching - load once, use many times
2. **Tool Caching**: Tools cache DatabaseManager instance - improves performance
3. **Minimize API Calls**: Cache OpenAI responses when possible
4. **Optimize Queries**: Use specific queries instead of broad searches

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Input Validation**: All inputs are validated before processing
3. **Safe Defaults**: Prescription requirements default to "required" on errors
4. **No Medical Advice**: Agent explicitly prohibited from giving medical advice

## Support

For issues or questions:
1. Check this documentation
2. Review error logs
3. Check GitHub issues (if applicable)
4. Contact project maintainers

## Next Steps

1. Review `docs/architecture.md` for system architecture
2. Read `docs/api_documentation.md` for API details
3. Check `docs/api_documentation.md` for tool usage and API details
4. See `docs/models_documentation.md` for data models



