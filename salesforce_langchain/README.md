# Salesforce LangChain AI System

AI-powered system to prioritize leads, score opportunities, and generate personalized follow-up actions using LangChain and Salesforce APIs.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Test with real data:
```bash
python test_real_data.py
```

4. Run full workflow:
```bash
python real_workflow.py
```

## Core Files

- **salesforce_agent.py**: Main LangChain agent with Salesforce tools
- **prioritization.py**: Lead scoring, opportunity analysis, visualizations
- **test_real_data.py**: Real Salesforce data testing
- **real_workflow.py**: Complete production workflow
- **example.py**: Basic usage demonstration

## Features

- Real-time Salesforce data access via SOQL
- AI-powered lead prioritization (0-100 scoring)
- Opportunity conversion likelihood scoring
- Personalized follow-up action generation
- Interactive visualizations & dashboards
- LangChain agent for natural language queries
