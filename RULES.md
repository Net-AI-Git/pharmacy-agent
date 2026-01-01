# Project Rules

This file defines all rules, requirements, and restrictions for the AI Agent - Pharmacy Assistant project.

---

## Required Requirements

### 1. AI Agent
- **Required**: Implement AI Agent based on GPT-5 with real-time text streaming
- **Required**: The Agent must be stateless (no state preservation)
- **Required**: The Agent must support Hebrew and English
- **Required**: The Agent must support streaming

### 2. Tools
- **Required**: Design and implement tools for the Agent
- **Minimum Required**: At least 3 different tools
- **Required**: Each tool must include:
  - Name and purpose
  - Inputs (parameters, types)
  - Output schema (fields, types)
  - Error handling
  - Fallback behavior

### 3. Database
- **Required**: Create a synthetic database with:
  - 10 users
  - 5 medications

### 4. UI (User Interface)
- **Required**: Interface for interaction with the Agent
- **Required**: Display tool calls in the interface

### 5. Multi-Step Flows
- **Required**: Design and implement at least 3 different multi-step flows
- **Required**: Each flow must cover all steps from request initiation to resolution

### 6. Evaluation Plan
- **Required**: Provide an evaluation plan for the Agent

### 7. Docker
- **Required**: Wrap the project in a Dockerfile

---

## Allowed

### Programming Languages
- **Allowed**: Python, JavaScript, TypeScript or Go (Backend)
- **Allowed**: Any language (Frontend - no limitation)

### Use of AI Assistants
- **Allowed**: Collaboration with AI assistants (Claude Code, Codex, etc.) during development
- **Condition**: Must be prepared to explain the code and answer questions about implementation decisions

### Additional Tools
- **Allowed**: Add additional tools beyond the minimum 3, if justified

### Additional Requirements
- **Allowed**: Propose and add additional requirements if they are important for production readiness

---

## Forbidden

### Frameworks
- **Strictly Forbidden**: Use of Langchain or similar frameworks
- **Required**: Use OpenAI API Vanilla only

### Agent Behavior
- **Strictly Forbidden**: Providing medical advice
- **Strictly Forbidden**: Encouragement to purchase
- **Strictly Forbidden**: Diagnosis

### README
- **Forbidden**: Use of LLM for writing README.md
- **Required**: Write README.md yourself

---

## Agent Requirements

The Agent must meet all of the following requirements (minimum):

1. **Required**: Provide factual information about medications
2. **Required**: Explain dosage and usage instructions
3. **Required**: Confirm prescription requirements
4. **Required**: Check availability in stock
5. **Required**: Identify active ingredients
6. **Forbidden**: Medical advice, encouragement to purchase, diagnosis
7. **Required**: Redirect to healthcare professional or general resources for advice requests
8. **Required**: Support for streaming

---

## Tool Documentation Requirements

Each tool must include complete documentation:

1. **Name and purpose**
2. **Inputs** (parameters, types)
3. **Output schema** (fields, types)
4. **Error handling**
5. **Fallback behavior**

### Example of Required Tool:
- `get_medication_by_name`: Inputs, outputs, example responses, error handling, fallback logic

---

## Deliverables

In a public GitHub repository, provide:

1. **README.md**
   - Explanation of the project and its architecture
   - Explanation of how to run Docker
   - **Required**: Write it yourself, not using LLM

2. **Multi-Step Flow**
   - Demonstration of three multi-step flows

3. **Evidence**
   - 2-3 screenshots of conversations

4. **Evaluation Plan**
   - Plan for evaluating Agent flows

---

## Evaluation Criteria

The project will be evaluated according to:

1. **Tool/API Design** - Clarity of tool and API design
2. **Prompt Quality** - Quality of prompts and integration of API usage
3. **Multi-Step Interaction Handling** - Multi-step interaction handling
4. **Policy Adherence** - Policy adherence
5. **Testing Rigor** - Testing rigor
   - Coverage in Hebrew
   - Multiple variations per flow
6. **Quality and Completeness of Flow Designs** - Quality and completeness of flow designs

---

## Testing Requirements

- **Required**: Tests in Hebrew
- **Required**: Multiple variations per flow
- **Required**: Full coverage of all flows

---

## Flow Design Requirements

Each multi-step flow must include:

1. **Definition** - Definition of the flow
2. **Sequence Description** - Description of the expected sequence
3. **Usage Description** - Description of how the Agent will use functions and respond

---

## Architecture Guidelines

### Context
- The company is developing an AI-powered pharmacist assistant for a retail pharmacy chain
- The Agent serves customers through chat
- The Agent uses data from the pharmacy's internal systems
- Customers ask about medications, stock availability, prescription requirements, and safe usage

### Workflows
The Agent should handle workflows through tools:
- Prescription management
- Inventory control
- Customer service

---

## Summary

### What Must Be Done:
- AI Agent with GPT-5, streaming, stateless, Hebrew+English
- At least 3 well-documented tools
- Database: 10 users, 5 medications
- UI with tool calls display
- At least 3 multi-step flows
- Evaluation plan
- Dockerfile
- README.md (written by yourself)
- Screenshots (2-3)
- Tests in Hebrew with variations

### What Is Allowed:
- Python/JS/TS/Go (Backend), any language (Frontend)
- Collaboration with AI assistants (with ability to explain)
- Additional tools beyond minimum
- Additional requirements for production readiness

### What Is Forbidden:
- Langchain or similar frameworks
- Medical advice
- Encouragement to purchase
- Diagnosis
- Use of LLM for writing README

---

**Last Updated**: 2024
**Version**: 1.0
