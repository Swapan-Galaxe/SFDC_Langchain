# Salesforce AI Assistant

AI-powered system to prioritize leads, score opportunities, and generate personalized follow-up actions using OpenAI GPT-4 and Salesforce APIs.

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

3. Run Streamlit UI:
```bash
streamlit run app.py
```

4. Access: http://localhost:8502

## Core Files

- **app.py**: Streamlit web interface with visualizations
- **salesforce_agent.py**: Salesforce data fetching and AI scoring
- **prioritization_simple.py**: Lead/opportunity prioritization logic

## Features

- Real-time Salesforce data access via SOQL
- AI-powered lead prioritization (0-100 scoring)
- Opportunity conversion likelihood scoring
- Personalized follow-up action generation
- Interactive visualizations & dashboards
- Modern gradient UI design
