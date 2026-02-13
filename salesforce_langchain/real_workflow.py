import os
from salesforce_agent import SalesforceAgent
from prioritization import LeadPrioritizer, OpportunityScorer, FollowUpGenerator, SalesVisualizer

def full_workflow():
    print("🚀 FULL REAL DATA WORKFLOW")
    print("=" * 50)
    
    # Setup
    agent = SalesforceAgent(
        sf_username=os.getenv("SF_USERNAME"),
        sf_password=os.getenv("SF_PASSWORD"),
        sf_token=os.getenv("SF_TOKEN"),
        limit=20  # Process 20 real records
    )
    
    # Step 1: Fetch real data
    print("\n1️⃣ FETCHING REAL SALESFORCE DATA...")
    leads = agent.get_leads()
    opportunities = agent.get_opportunities()
    print(f"📊 Retrieved {len(leads)} leads and {len(opportunities)} opportunities")
    
    # Step 2: AI-powered scoring
    print("\n2️⃣ AI SCORING & PRIORITIZATION...")
    prioritizer = LeadPrioritizer()
    scorer = OpportunityScorer()
    
    scored_leads = prioritizer.prioritize_leads(leads)
    scored_opps = scorer.score_opportunities(opportunities)
    
    # Display top results
    print(f"\n🏆 TOP 5 LEADS:")
    for i, lead in enumerate(scored_leads[:5]):
        print(f"{i+1}. {lead['Name']} ({lead['Company']}) - Score: {lead['priority_score']}")
    
    print(f"\n💎 TOP 5 OPPORTUNITIES:")
    for i, opp in enumerate(scored_opps[:5]):
        print(f"{i+1}. {opp['Name']} - ${opp['Amount']} - Score: {opp['conversion_score']}")
    
    # Step 3: Generate follow-ups
    print("\n3️⃣ GENERATING FOLLOW-UP ACTIONS...")
    generator = FollowUpGenerator()
    
    if scored_leads:
        top_lead_followup = generator.generate_actions(scored_leads[0], "lead")
        print(f"\n📝 Follow-up for top lead ({scored_leads[0]['Name']}):")
        print(top_lead_followup)
    
    if scored_opps:
        top_opp_followup = generator.generate_actions(scored_opps[0], "opportunity")
        print(f"\n💼 Follow-up for top opportunity ({scored_opps[0]['Name']}):")
        print(top_opp_followup)
    
    # Step 4: Visual analytics
    print("\n4️⃣ GENERATING VISUAL ANALYTICS...")
    visualizer = SalesVisualizer()
    
    if scored_leads and scored_opps:
        visualizer.dashboard(scored_leads, scored_opps)
        print("✅ Interactive dashboard generated")
    
    # Step 5: Natural language queries
    print("\n5️⃣ TESTING NATURAL LANGUAGE INTERFACE...")
    executor = agent.create_agent()
    
    queries = [
        "What are my top 3 highest priority leads?",
        "Show me opportunities over $10,000 and their scores",
        "Generate follow-ups for my best lead"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        try:
            result = executor.invoke({"input": query})
            print("✅ Processed successfully")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 WORKFLOW COMPLETE!")
    print(f"📈 Analyzed {len(leads)} leads and {len(opportunities)} opportunities")
    print("💡 Ready for production use!")

if __name__ == "__main__":
    full_workflow()