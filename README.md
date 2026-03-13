# LLM-Powered Prompt Router for Intent Classification

## Project Overview
This is a Python-based backend service that intelligently routes user messages to specialized AI "experts." It uses a two-step LLM orchestration pattern:
1. **Classification:** A fast LLM call (GPT-4o-mini via GitHub Models) identifies the user's intent.
2. **Routing:** Based on the intent, the system selects a specialized persona (Code, Data, Writing, or Career) to generate a high-quality response.

## Setup & Installation

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- A GitHub Personal Access Token (PAT) with `models:read` permissions.

### Environment Configuration
1. Create a `.env` file in the root directory.
2. Add your token:
   
```env
   GITHUB_TOKEN=your_github_token_here
```
## Running the Application 
### Using Docker
Build and run the container with a single command
```
docker-compose up --build
```

### Using Local Python
1. Create a virtual environment: python -m venv venv
2. Activate it: venv\Scripts\activate 
3. Install dependencies : pip install openai
4. Run the app: python main.py

## Project Structure
- **main.py**: Core logic for classification, routing, and logging.

- **prompts.py**: Dictionary containing the four specialized expert system prompts.

- **route_log.jsonl**: Log file tracking all intent classifications and responses.

- **Dockerfile & docker-compose.yml**: Containerization configuration.

## System Design:
### The "Classify-then-Respond" Pattern
The application avoids "monolithic prompts" (one giant prompt trying to do everything) by using a modular routing pattern. This increases accuracy and reduces costs by using a smaller model for simple logic and specialized personas for complex tasks

## 1. Intent Classification (classify_intent)
This is the "traffic controller" of the service.

- **Prompt Engineering**: We use Few-Shot/Structured Prompting to force the LLM to output only JSON. This ensures our Python code can reliably "read" the decision.

- **Structured Output:** By using response_format={ "type": "json_object" }, we prevent the AI from adding conversational filler like "Sure, here is your classification," which would break the code.

- **Graceful Degradation:** If the API fails or the LLM returns gibberish, the function uses a try-except block to return a default unclear intent rather than crashing the whole system.

## 2. Expert Routing (route_and_respond)
Once the intent is known, this function acts as a Dispatcher.

- Expert Personas: Instead of hardcoding prompts, we pull from prompts.py. Each persona (Code, Data, Writing, Career) has specific constraints (e.g., the Code Expert is forbidden from "conversational chatter").

- Confidence Filtering: To ensure quality, if the Classifier's confidence score is below 0.5, the system automatically triggers the "Unclear" logic to ask the user for more detail, preventing the AI from "hallucinating" a wrong answer.

## 3. Observability & Logging (log_request)
For production AI systems, you must know what happened after the fact.

- JSON Lines (.jsonl): We use this format because it is stream-friendly. Unlike a standard JSON list, you can add new lines to a .jsonl file without reading the whole file into memory, making it highly efficient for long-term logging.

## Demon Video
[Video](https://drive.google.com/file/d/1RL7Fsa5oh2Dcti8GD9hvJFGdL-OGcHOY/view?usp=sharing)