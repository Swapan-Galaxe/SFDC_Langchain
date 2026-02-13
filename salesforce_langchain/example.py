from salesforce_agent import SalesforceAgent
from prioritization import LeadPrioritizer, OpportunityScorer, FollowUpGenerator
import os

def main():
    # Initialize
    agent = SalesforceAgent(
        sf_username=os.getenv("SF_USERNAME"),
        sf_password=os.getenv("SF_PASSWORD"),
        sf_token=os.getenv("SF_TOKEN")
    )
    
    lead_prioritizer = LeadPrioritizer()
    opp_scorer = OpportunityScorer()
    followup_gen = FollowUpGenerator()
    
    # Get and prioritize leads
    print("Fetching leads...")
    leads = agent.get_leads()
    prioritized_leads = lead_prioritizer.prioritize_leads(leads)
    
    print("\nTop 5 Prioritized Leads:")
    for i, lead in enumerate(prioritized_leads[:5], 1):
        print(f"{i}. {lead.get('Name')} - Score: {lead['priority_score']}")
    
    # Score opportunities
    print("\n\nFetching opportunities...")
    opportunities = agent.get_opportunities()
    scored_opps = opp_scorer.score_opportunities(opportunities)
    
    print("\nTop 5 Scored Opportunities:")
    for i, opp in enumerate(scored_opps[:5], 1):
        print(f"{i}. {opp.get('Name')} - Score: {opp['conversion_score']}")
    
    # Generate follow-ups for top lead
    if prioritized_leads:
        top_lead = prioritized_leads[0]
        print(f"\n\nFollow-up actions for top lead ({top_lead.get('Name')}):")
        actions = followup_gen.generate_actions(top_lead, "lead")
        print(actions)
    
    # Generate follow-ups for top opportunity
    if scored_opps:
        top_opp = scored_opps[0]
        print(f"\n\nFollow-up actions for top opportunity ({top_opp.get('Name')}):")
        actions = followup_gen.generate_actions(top_opp, "opportunity")
        print(actions)

if __name__ == "__main__":
    main()
