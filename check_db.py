
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import json

async def check_database():
    # Load environment variables
    load_dotenv('/app/backend/.env')
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    print(f"Connecting to database: {db_name}")
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check team_stats collection for fouls_drawn and penalties_awarded
    print("\nChecking team_stats collection:")
    team_stats_count = await db.team_stats.count_documents({})
    print(f"Total team_stats documents: {team_stats_count}")
    
    # Check for Arsenal team stats
    arsenal_stats = await db.team_stats.find({"team_name": "Arsenal"}).to_list(100)
    print(f"Arsenal team stats documents: {len(arsenal_stats)}")
    
    if arsenal_stats:
        # Check first document
        first_doc = arsenal_stats[0]
        print("\nSample Arsenal team stats document:")
        print(f"  - Match ID: {first_doc.get('match_id', 'N/A')}")
        print(f"  - Is Home: {first_doc.get('is_home', 'N/A')}")
        print(f"  - Fouls Drawn: {first_doc.get('fouls_drawn', 'N/A')}")
        print(f"  - Penalties Awarded: {first_doc.get('penalties_awarded', 'N/A')}")
        
        # Count documents with non-zero fouls_drawn
        non_zero_fouls = sum(1 for doc in arsenal_stats if doc.get('fouls_drawn', 0) > 0)
        print(f"\nArsenal documents with non-zero fouls_drawn: {non_zero_fouls}/{len(arsenal_stats)}")
        
        # Count documents with non-zero penalties_awarded
        non_zero_penalties = sum(1 for doc in arsenal_stats if doc.get('penalties_awarded', 0) > 0)
        print(f"Arsenal documents with non-zero penalties_awarded: {non_zero_penalties}/{len(arsenal_stats)}")
    
    # Check player_stats collection
    print("\nChecking player_stats collection:")
    player_stats_count = await db.player_stats.count_documents({})
    print(f"Total player_stats documents: {player_stats_count}")
    
    # Check for Arsenal player stats
    arsenal_player_stats = await db.player_stats.find({"team_name": "Arsenal"}).to_list(1000)
    print(f"Arsenal player stats documents: {len(arsenal_player_stats)}")
    
    if arsenal_player_stats:
        # Count documents with non-zero fouls_drawn
        non_zero_fouls = sum(1 for doc in arsenal_player_stats if doc.get('fouls_drawn', 0) > 0)
        print(f"Arsenal player documents with non-zero fouls_drawn: {non_zero_fouls}/{len(arsenal_player_stats)}")
        
        # Count documents with non-zero penalty_attempts
        non_zero_penalties = sum(1 for doc in arsenal_player_stats if doc.get('penalty_attempts', 0) > 0)
        print(f"Arsenal player documents with non-zero penalty_attempts: {non_zero_penalties}/{len(arsenal_player_stats)}")
        
        # Get sample player with non-zero fouls_drawn
        player_with_fouls = next((doc for doc in arsenal_player_stats if doc.get('fouls_drawn', 0) > 0), None)
        if player_with_fouls:
            print("\nSample Arsenal player with non-zero fouls_drawn:")
            print(f"  - Player: {player_with_fouls.get('player_name', 'N/A')}")
            print(f"  - Match ID: {player_with_fouls.get('match_id', 'N/A')}")
            print(f"  - Fouls Drawn: {player_with_fouls.get('fouls_drawn', 'N/A')}")
    
    # Check RBS results collection
    print("\nChecking rbs_results collection:")
    rbs_count = await db.rbs_results.count_documents({})
    print(f"Total RBS results documents: {rbs_count}")
    
    # Check for Arsenal RBS results
    arsenal_rbs = await db.rbs_results.find({"team_name": "Arsenal"}).to_list(100)
    print(f"Arsenal RBS results documents: {len(arsenal_rbs)}")
    
    if arsenal_rbs:
        # Check first document
        first_doc = arsenal_rbs[0]
        print("\nSample Arsenal RBS result:")
        print(f"  - Referee: {first_doc.get('referee', 'N/A')}")
        print(f"  - RBS Score: {first_doc.get('rbs_score', 'N/A')}")
        
        # Check stats breakdown
        stats_breakdown = first_doc.get("stats_breakdown", {})
        if stats_breakdown:
            print("\nStats Breakdown:")
            for stat, value in stats_breakdown.items():
                print(f"  - {stat}: {value}")
            
            # Check if fouls_drawn and penalties_awarded are included
            if 'fouls_drawn' in stats_breakdown:
                print("\n✅ Fouls drawn is included in RBS calculation")
            else:
                print("\n❌ Fouls drawn is missing from RBS calculation")
            
            if 'penalties_awarded' in stats_breakdown:
                print("✅ Penalties awarded is included in RBS calculation")
            else:
                print("❌ Penalties awarded is missing from RBS calculation")
            
            # Check if values are non-zero
            if stats_breakdown.get('fouls_drawn', 0) != 0:
                print("✅ Fouls drawn has non-zero value in RBS calculation")
            else:
                print("❌ Fouls drawn has zero value in RBS calculation")
            
            if stats_breakdown.get('penalties_awarded', 0) != 0:
                print("✅ Penalties awarded has non-zero value in RBS calculation")
            else:
                print("❌ Penalties awarded has zero value in RBS calculation")

# Run the async function
if __name__ == "__main__":
    asyncio.run(check_database())
