import os
from salesforce_agent import SalesforceAgent
from prioritization import LeadPrioritizer, OpportunityScorer, FollowUpGenerator, SalesVisualizer

def test_real_data():
    print("🔥 Testing with REAL Salesforce Data...")
    
    # Check credentials
    if not all([os.getenv("SF_USERNAME"), os.getenv("SF_PASSWORD"), os.getenv("SF_TOKEN"), os.getenv("OPENAI_API_KEY")]):
        print("❌ Missing credentials. Set SF_USERNAME, SF_PASSWORD, SF_TOKEN, OPENAI_API_KEY in .env")
        return
    
    try:
        # Initialize agent with real Salesforce connection
        agent = SalesforceAgent(
            sf_username=os.getenv("SF_USERNAME"),
            sf_password=os.getenv("SF_PASSWORD"),
            sf_token=os.getenv("SF_TOKEN"),
            limit=10  # Test with 10 real records
        )
        
        print("✅ Connected to Salesforce")
        
        # Fetch real leads
        print("\n📊 Fetching real leads...")
        real_leads = agent.get_leads()
        print(f"Found {len(real_leads)} leads")
        
        if real_leads and len(real_leads) > 0:
            # Score real leads
            prioritizer = LeadPrioritizer()
            scored_leads = prioritizer.prioritize_leads(real_leads)
            
            print(f"\n🎯 Top 3 Scored Leads:")
            for i, lead in enumerate(scored_leads[:3]):
                print(f"{i+1}. {lead.get('Name', 'N/A')} - Score: {lead.get('priority_score', 0)}")
            
            # Generate follow-up for top lead
            if scored_leads:
                generator = FollowUpGenerator()
                followup = generator.generate_actions(scored_leads[0], "lead")
                print(f"\n📝 Follow-up for top lead:\n{followup}")
        
        # Fetch real opportunities
        print("\n💰 Fetching real opportunities...")
        real_opps = agent.get_opportunities()
        print(f"Found {len(real_opps)} opportunities")
        
        if real_opps and len(real_opps) > 0:
            # Score real opportunities
            scorer = OpportunityScorer()
            scored_opps = scorer.score_opportunities(real_opps)
            
            print(f"\n🎯 Top 3 Scored Opportunities:")
            for i, opp in enumerate(scored_opps[:3]):
                print(f"{i+1}. {opp.get('Name', 'N/A')} - Amount: ${opp.get('Amount', 0)} - Score: {opp.get('conversion_score', 0)}")
        
        # Test natural language agent
        print("\n🤖 Testing AI Agent with real data...")
        executor = agent.create_agent()
        result = executor.invoke({"input": "Get top 3 leads and score them"})
        print("✅ Agent executed successfully")
        
        # Generate visualizations with real data
        if real_leads and real_opps:
            print("\n📈 Generating visualizations with real data...")
            visualizer = SalesVisualizer()
            
            if scored_leads:
                visualizer.plot_lead_scores(scored_leads[:5])
                print("✅ Lead chart generated")
            
            if scored_opps:
                visualizer.plot_opportunity_scores(scored_opps[:5])
                print("✅ Opportunity chart generated")
            
            if scored_leads and scored_opps:
                visualizer.dashboard(scored_leads[:5], scored_opps[:5])
                print("✅ Dashboard generated")
        
        print("\n🎉 Real data testing complete!")
        print(f"📊 Processed {len(real_leads)} leads and {len(real_opps)} opportunities")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your Salesforce credentials and OpenAI API key")

if __name__ == "__main__":
    test_real_data()