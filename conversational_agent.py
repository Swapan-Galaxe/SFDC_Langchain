from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from salesforce_agent import SalesforceAgent
from prioritization_simple import LeadPrioritizer, OpportunityScorer, FollowUpGenerator
import os
import json

class ConversationalSalesAgent:
    def __init__(self, sf_username, sf_password, sf_token):
        self.sf_agent = SalesforceAgent(sf_username, sf_password, sf_token, limit=50)
        self.prioritizer = LeadPrioritizer()
        self.scorer = OpportunityScorer()
        self.followup_gen = FollowUpGenerator()
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        # Create agent with tools
        self.agent = self._create_agent()
    
    def _create_agent(self):
        @tool
        def get_top_leads(n: int = 5) -> str:
            """Get top N prioritized leads with their scores. Use this when user asks about best leads or top leads."""
            leads = self.sf_agent.get_leads()
            scored = self.prioritizer.prioritize_leads(leads)[:n]
            
            result = f"Top {n} Leads:\n"
            for i, lead in enumerate(scored, 1):
                result += f"{i}. {lead['Name']} ({lead['Company']}) - Score: {lead['priority_score']}\n"
            return result
        
        @tool
        def get_top_opportunities(n: int = 5) -> str:
            """Get top N opportunities with conversion scores. Use this when user asks about best opportunities or deals."""
            opps = self.sf_agent.get_opportunities()
            scored = self.scorer.score_opportunities(opps)[:n]
            
            result = f"Top {n} Opportunities:\n"
            for i, opp in enumerate(scored, 1):
                result += f"{i}. {opp['Name']} - ${opp['Amount']:,.0f} - Score: {opp['conversion_score']}\n"
            return result
        
        @tool
        def search_lead_by_name(name: str) -> str:
            """Search for a specific lead by name and get their details and score."""
            leads = self.sf_agent.get_leads()
            scored = self.prioritizer.prioritize_leads(leads)
            
            for lead in scored:
                if name.lower() in lead['Name'].lower():
                    return json.dumps({
                        "Name": lead['Name'],
                        "Company": lead['Company'],
                        "Email": lead.get('Email', 'N/A'),
                        "Status": lead.get('Status', 'N/A'),
                        "Score": lead['priority_score']
                    }, indent=2)
            return f"Lead '{name}' not found"
        
        @tool
        def generate_followup_for_lead(lead_name: str) -> str:
            """Generate personalized follow-up actions for a specific lead by name."""
            leads = self.sf_agent.get_leads()
            scored = self.prioritizer.prioritize_leads(leads)
            
            for lead in scored:
                if lead_name.lower() in lead['Name'].lower():
                    return self.followup_gen.generate_actions(lead, "lead")
            return f"Lead '{lead_name}' not found"
        
        @tool
        def compare_leads(lead1_name: str, lead2_name: str) -> str:
            """Compare two leads and explain which one is better and why."""
            leads = self.sf_agent.get_leads()
            scored = self.prioritizer.prioritize_leads(leads)
            
            found_leads = []
            for lead in scored:
                if lead1_name.lower() in lead['Name'].lower() or lead2_name.lower() in lead['Name'].lower():
                    found_leads.append(lead)
            
            if len(found_leads) < 2:
                return "Could not find both leads for comparison"
            
            comparison = f"Comparison:\n"
            comparison += f"1. {found_leads[0]['Name']} - Score: {found_leads[0]['priority_score']}\n"
            comparison += f"2. {found_leads[1]['Name']} - Score: {found_leads[1]['priority_score']}\n"
            return comparison
        
        @tool
        def get_pipeline_summary() -> str:
            """Get quick pipeline summary with key metrics."""
            leads = self.sf_agent.get_leads()
            opps = self.sf_agent.get_opportunities()
            scored_leads = self.prioritizer.prioritize_leads(leads)
            scored_opps = self.scorer.score_opportunities(opps)
            
            total_value = sum(o['Amount'] for o in scored_opps if o['Amount'])
            avg_lead_score = sum(l['priority_score'] for l in scored_leads) / len(scored_leads)
            avg_opp_score = sum(o['conversion_score'] for o in scored_opps) / len(scored_opps)
            
            return f"""📊 Quick Pipeline Summary:
- Total Leads: {len(leads)} (Avg Score: {avg_lead_score:.1f})
- Total Opportunities: {len(opps)}
- Pipeline Value: ${total_value:,.0f}
- Avg Opportunity Score: {avg_opp_score:.1f}"""
        
        @tool
        def get_opportunity_summary(opportunity_name: str) -> str:
            """Get comprehensive summary and analysis for a specific opportunity by name."""
            opps = self.sf_agent.get_opportunities()
            scored = self.scorer.score_opportunities(opps)
            
            for opp in scored:
                if opportunity_name.lower() in opp['Name'].lower():
                    summary = f"""📊 COMPREHENSIVE OPPORTUNITY ANALYSIS

🏢 Opportunity: {opp['Name']}
💰 Amount: ${opp['Amount']:,.0f}
📈 Stage: {opp.get('StageName', 'N/A')}
📅 Close Date: {opp.get('CloseDate', 'N/A')}
🎯 AI Conversion Score: {opp['conversion_score']}/100
📊 Probability: {opp.get('Probability', 'N/A')}%

💡 INSIGHTS:
- Score Ranking: #{scored.index(opp) + 1} out of {len(scored)} opportunities
- Risk Level: {'Low' if opp['conversion_score'] >= 75 else 'Medium' if opp['conversion_score'] >= 50 else 'High'}
- Deal Size: {'Large' if opp['Amount'] > 200000 else 'Medium' if opp['Amount'] > 100000 else 'Small'}

📝 RECOMMENDED ACTIONS:
{self.followup_gen.generate_actions(opp, 'opportunity')}
"""
                    return summary
            return f"Opportunity '{opportunity_name}' not found"
        
        @tool
        def get_all_opportunities_summary() -> str:
            """Get summary of all opportunities with key metrics and insights."""
            opps = self.sf_agent.get_opportunities()
            scored = self.scorer.score_opportunities(opps)
            
            total_value = sum(o['Amount'] for o in scored if o['Amount'])
            avg_score = sum(o['conversion_score'] for o in scored) / len(scored)
            high_value = [o for o in scored if o['Amount'] > 200000]
            hot_deals = [o for o in scored if o['conversion_score'] >= 80]
            
            # Stage breakdown
            stages = {}
            for opp in scored:
                stage = opp.get('StageName', 'Unknown')
                stages[stage] = stages.get(stage, 0) + 1
            
            summary = f"""📊 COMPLETE OPPORTUNITY PIPELINE SUMMARY

💰 FINANCIAL OVERVIEW:
- Total Pipeline Value: ${total_value:,.0f}
- Number of Opportunities: {len(scored)}
- Average Deal Size: ${total_value/len(scored):,.0f}
- High-Value Deals (>$200K): {len(high_value)}

🎯 CONVERSION ANALYSIS:
- Average AI Score: {avg_score:.1f}/100
- Hot Deals (Score ≥80): {len(hot_deals)}
- Deals Needing Attention (Score <50): {len([o for o in scored if o['conversion_score'] < 50])}

📈 STAGE BREAKDOWN:
{chr(10).join([f'- {stage}: {count} deals' for stage, count in stages.items()])}

🏆 TOP 5 OPPORTUNITIES:
{chr(10).join([f'{i+1}. {o["Name"]} - ${o["Amount"]:,.0f} (Score: {o["conversion_score"]})' for i, o in enumerate(scored[:5])])}

⚠️ PRIORITY ACTIONS:
- Focus on {len(hot_deals)} hot deals with high conversion probability
- Review {len([o for o in scored if o['conversion_score'] < 50])} underperforming opportunities
- Total potential revenue at risk: ${sum(o['Amount'] for o in scored if o['conversion_score'] < 50):,.0f}
"""
            return summary
        
        tools = [
            get_top_leads,
            get_top_opportunities,
            search_lead_by_name,
            generate_followup_for_lead,
            compare_leads,
            get_pipeline_summary,
            get_opportunity_summary,
            get_all_opportunities_summary
        ]
        
        return create_react_agent(self.llm, tools)
    
    def chat(self, message: str):
        """Send a message to the conversational agent"""
        response = self.agent.invoke({"messages": [{"role": "user", "content": message}]})
        return response["messages"][-1].content
