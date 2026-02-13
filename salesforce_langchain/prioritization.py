from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
import matplotlib.pyplot as plt
import pandas as pd

class LeadPrioritizer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
    def prioritize_leads(self, leads):
        scored_leads = []
        for lead in leads:
            score = self._calculate_score(lead)
            scored_leads.append({**lead, 'priority_score': score})
        return sorted(scored_leads, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_score(self, lead):
        prompt = PromptTemplate(
            input_variables=["lead"],
            template="""Analyze this lead and return ONLY a number 0-100:
{lead}
Consider: Rating, Status, LeadSource, Company size indicators.
Score only:"""
        )
        response = self.llm.invoke(prompt.format(lead=json.dumps(lead)))
        try:
            return int(''.join(filter(str.isdigit, response.content[:3])))
        except:
            return 50

class OpportunityScorer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
    def score_opportunities(self, opportunities):
        scored_opps = []
        for opp in opportunities:
            score = self._calculate_score(opp)
            scored_opps.append({**opp, 'conversion_score': score})
        return sorted(scored_opps, key=lambda x: x['conversion_score'], reverse=True)
    
    def _calculate_score(self, opp):
        prompt = PromptTemplate(
            input_variables=["opportunity"],
            template="""Score this opportunity 0-100 for close likelihood:
{opportunity}
Consider: Amount, StageName, Probability, CloseDate proximity.
Score only:"""
        )
        response = self.llm.invoke(prompt.format(opportunity=json.dumps(opp)))
        try:
            return int(''.join(filter(str.isdigit, response.content[:3])))
        except:
            return 50

class FollowUpGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        
    def generate_actions(self, record, record_type="lead"):
        prompt = PromptTemplate(
            input_variables=["record", "type"],
            template="""Generate 3 specific follow-up actions for this {type}:
{record}

Format as numbered list with actionable steps."""
        )
        response = self.llm.invoke(prompt.format(record=json.dumps(record), type=record_type))
        return response.content

class SalesVisualizer:
    @staticmethod
    def plot_lead_scores(scored_leads):
        df = pd.DataFrame(scored_leads)
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(df)), df['priority_score'], color='skyblue')
        plt.title('Lead Priority Scores')
        plt.xlabel('Leads')
        plt.ylabel('Priority Score (0-100)')
        plt.xticks(range(len(df)), [f"{lead['Name'][:10]}..." for lead in scored_leads], rotation=45)
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_opportunity_scores(scored_opps):
        df = pd.DataFrame(scored_opps)
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Amount'], df['conversion_score'], s=100, alpha=0.7, c='green')
        plt.title('Opportunity Amount vs Conversion Score')
        plt.xlabel('Amount ($)')
        plt.ylabel('Conversion Score (0-100)')
        for i, opp in enumerate(scored_opps):
            plt.annotate(opp['Name'][:10], (opp['Amount'], opp['conversion_score']))
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def dashboard(scored_leads, scored_opps):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Lead scores
        lead_df = pd.DataFrame(scored_leads[:10])
        ax1.barh(range(len(lead_df)), lead_df['priority_score'], color='lightblue')
        ax1.set_title('Top 10 Lead Scores')
        ax1.set_xlabel('Priority Score')
        ax1.set_yticks(range(len(lead_df)))
        ax1.set_yticklabels([f"{lead['Name'][:15]}" for lead in scored_leads[:10]])
        
        # Opportunity pipeline
        opp_df = pd.DataFrame(scored_opps[:10])
        ax2.scatter(opp_df['Amount'], opp_df['conversion_score'], s=80, alpha=0.7, c='orange')
        ax2.set_title('Top 10 Opportunities')
        ax2.set_xlabel('Amount ($)')
        ax2.set_ylabel('Conversion Score')
        
        plt.tight_layout()
        plt.show()
