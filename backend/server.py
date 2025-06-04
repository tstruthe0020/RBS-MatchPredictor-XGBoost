from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
import io
from collections import defaultdict
import csv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Soccer Referee Bias Analysis Platform")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Match(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    referee: str
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    result: str
    season: str
    competition: str
    match_date: str

class TeamStats(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    team_name: str
    is_home: bool
    yellow_cards: int
    red_cards: int
    fouls: int
    possession_pct: float
    shots_total: int
    shots_on_target: int
    fouls_drawn: Optional[int] = 0
    penalties_awarded: Optional[int] = 0
    xg: Optional[float] = 0.0

class PlayerStats(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str
    player_name: str
    team_name: str
    is_home: bool
    goals: int
    assists: int
    yellow_cards: int
    fouls_committed: int
    fouls_drawn: int
    xg: float

class RBSResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_name: str
    referee: str
    rbs_score: float
    matches_with_ref: int
    matches_without_ref: int
    confidence_level: str
    stats_breakdown: Dict

class UploadResponse(BaseModel):
    success: bool
    message: str
    records_processed: int

# RBS Calculation Engine
class RBSCalculator:
    def __init__(self):
        # Weights for different statistics
        self.weights = {
            'yellow_cards': 0.3,
            'red_cards': 0.5,
            'fouls': 0.1,
            'fouls_drawn': 0.1,
            'penalties_awarded': 0.5,
            'xg_difference': 0.4,
            'possession_pct': 0.2
        }
    
    def calculate_team_avg_stats(self, team_stats_list, with_referee=None, exclude_referee=None):
        """Calculate average stats for a team, optionally filtered by referee"""
        if with_referee:
            filtered_stats = [s for s in team_stats_list if s.get('referee') == with_referee]
        elif exclude_referee:
            filtered_stats = [s for s in team_stats_list if s.get('referee') != exclude_referee]
        else:
            filtered_stats = team_stats_list
        
        if not filtered_stats:
            return None, 0
        
        avg_stats = {}
        stat_fields = ['yellow_cards', 'red_cards', 'fouls', 'fouls_drawn', 'penalties_awarded', 'xg', 'possession_pct']
        
        for field in stat_fields:
            values = [s.get(field, 0) for s in filtered_stats if s.get(field) is not None]
            avg_stats[field] = sum(values) / len(values) if values else 0
        
        return avg_stats, len(filtered_stats)
    
    def calculate_rbs_for_team_referee(self, team_name, referee, all_team_stats, all_matches):
        """Calculate RBS score for a specific team-referee combination"""
        # Get all matches for this team
        team_matches = [m for m in all_matches if m['home_team'] == team_name or m['away_team'] == team_name]
        
        # Get team stats with referee information
        team_stats_with_ref = []
        for match in team_matches:
            match_stats = [s for s in all_team_stats if s['match_id'] == match['match_id'] and s['team_name'] == team_name]
            for stat in match_stats:
                stat['referee'] = match['referee']
                team_stats_with_ref.append(stat)
        
        # Calculate average stats with this referee
        with_ref_stats, matches_with_ref = self.calculate_team_avg_stats(team_stats_with_ref, with_referee=referee)
        
        # Calculate average stats with other referees (exclude this referee)
        without_ref_stats, matches_without_ref = self.calculate_team_avg_stats(team_stats_with_ref, exclude_referee=referee)
        
        # Reduce minimum match requirement for testing
        if not with_ref_stats or not without_ref_stats or matches_with_ref < 1:
            return None
        
        # Calculate RBS using the formula
        rbs_components = {}
        total_rbs = 0
        
        # Yellow cards (higher = worse for team)
        yellow_diff = with_ref_stats['yellow_cards'] - without_ref_stats['yellow_cards']
        rbs_components['yellow_cards'] = -yellow_diff * self.weights['yellow_cards']
        
        # Red cards (higher = worse for team)
        red_diff = with_ref_stats['red_cards'] - without_ref_stats['red_cards']
        rbs_components['red_cards'] = -red_diff * self.weights['red_cards']
        
        # Fouls committed (higher = worse for team)
        fouls_diff = with_ref_stats['fouls'] - without_ref_stats['fouls']
        rbs_components['fouls'] = -fouls_diff * self.weights['fouls']
        
        # Fouls drawn (higher = better for team)
        fouls_drawn_diff = with_ref_stats['fouls_drawn'] - without_ref_stats['fouls_drawn']
        rbs_components['fouls_drawn'] = fouls_drawn_diff * self.weights['fouls_drawn']
        
        # Penalties awarded (higher = better for team)
        penalties_diff = with_ref_stats['penalties_awarded'] - without_ref_stats['penalties_awarded']
        rbs_components['penalties_awarded'] = penalties_diff * self.weights['penalties_awarded']
        
        # xG difference (higher = better for team)
        xg_diff = with_ref_stats['xg'] - without_ref_stats['xg']
        rbs_components['xg_difference'] = xg_diff * self.weights['xg_difference']
        
        # Possession percentage (higher = better for team)
        possession_diff = with_ref_stats['possession_pct'] - without_ref_stats['possession_pct']
        rbs_components['possession_pct'] = possession_diff * self.weights['possession_pct']
        
        # Sum all components
        total_rbs = sum(rbs_components.values())
        
        # Determine confidence level
        if matches_with_ref >= 5:
            confidence = "high"
        elif matches_with_ref >= 2:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            'team_name': team_name,
            'referee': referee,
            'rbs_score': round(total_rbs, 3),
            'matches_with_ref': matches_with_ref,
            'matches_without_ref': matches_without_ref,
            'confidence_level': confidence,
            'stats_breakdown': rbs_components
        }

# Initialize RBS Calculator
rbs_calculator = RBSCalculator()

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Soccer Referee Bias Analysis Platform API"}

@api_router.post("/upload/matches", response_model=UploadResponse)
async def upload_matches(file: UploadFile = File(...)):
    """Upload matches CSV file"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Clear existing matches
        await db.matches.delete_many({})
        
        # Replace NaN values with appropriate defaults
        df = df.fillna({
            'home_score': 0,
            'away_score': 0,
            'result': 'Unknown',
            'season': 'Unknown',
            'competition': 'Unknown',
            'match_date': 'Unknown'
        })
        
        # Process and insert matches
        matches = []
        for _, row in df.iterrows():
            # Helper function to safely convert to int
            def safe_int(value, default=0):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return default
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
            
            match = Match(
                match_id=str(row['match_id']),
                referee=str(row['referee']),
                home_team=str(row['home_team']),
                away_team=str(row['away_team']),
                home_score=safe_int(row['home_score']),
                away_score=safe_int(row['away_score']),
                result=str(row['result']),
                season=str(row['season']),
                competition=str(row['competition']),
                match_date=str(row['match_date'])
            )
            matches.append(match.dict())
        
        await db.matches.insert_many(matches)
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {len(matches)} matches",
            records_processed=len(matches)
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.post("/upload/team-stats", response_model=UploadResponse)
async def upload_team_stats(file: UploadFile = File(...)):
    """Upload team stats CSV file"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Clear existing team stats
        await db.team_stats.delete_many({})
        
        # Replace NaN values with 0
        df = df.fillna(0)
        
        # Process and insert team stats
        team_stats = []
        for _, row in df.iterrows():
            # Helper function to safely convert to int
            def safe_int(value, default=0):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return default
                    return int(float(value))
                except (ValueError, TypeError):
                    return default
            
            # Helper function to safely convert to float
            def safe_float(value, default=0.0):
                try:
                    if pd.isna(value) or value == '' or value is None:
                        return default
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            stats = TeamStats(
                match_id=str(row['match_id']),
                team_name=str(row['team_name']),
                is_home=bool(row.get('is_home', False)),
                yellow_cards=safe_int(row.get('yellow_cards', 0)),
                red_cards=safe_int(row.get('red_cards', 0)),
                fouls=safe_int(row.get('fouls', 0)),
                possession_pct=safe_float(row.get('possession_pct', 0)),
                shots_total=safe_int(row.get('shots_total', 0)),
                shots_on_target=safe_int(row.get('shots_on_target', 0)),
                fouls_drawn=safe_int(row.get('fouls_drawn', 0)),
                penalties_awarded=safe_int(row.get('penalties_awarded', 0)),
                xg=safe_float(row.get('xg', 0))
            )
            team_stats.append(stats.dict())
        
        await db.team_stats.insert_many(team_stats)
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {len(team_stats)} team stat records",
            records_processed=len(team_stats)
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.post("/upload/player-stats", response_model=UploadResponse)
async def upload_player_stats(file: UploadFile = File(...)):
    """Upload player stats CSV file"""
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Clear existing player stats
        await db.player_stats.delete_many({})
        
        # Replace NaN values with 0
        df = df.fillna(0)
        
        # Process and insert player stats in batches (for large files)
        batch_size = 1000
        total_processed = 0
        
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            player_stats_batch = []
            
            for _, row in batch_df.iterrows():
                # Helper function to safely convert to int
                def safe_int(value, default=0):
                    try:
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        return int(float(value))
                    except (ValueError, TypeError):
                        return default
                
                # Helper function to safely convert to float
                def safe_float(value, default=0.0):
                    try:
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                stats = PlayerStats(
                    match_id=str(row['match_id']),
                    player_name=str(row['player_name']),
                    team_name=str(row['team_name']),
                    is_home=bool(row.get('is_home', False)),
                    goals=safe_int(row.get('goals', 0)),
                    assists=safe_int(row.get('assists', 0)),
                    yellow_cards=safe_int(row.get('yellow_cards', 0)),
                    fouls_committed=safe_int(row.get('fouls_committed', 0)),
                    fouls_drawn=safe_int(row.get('fouls_drawn', 0)),
                    xg=safe_float(row.get('xg', 0))
                )
                player_stats_batch.append(stats.dict())
            
            if player_stats_batch:
                await db.player_stats.insert_many(player_stats_batch)
                total_processed += len(player_stats_batch)
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {total_processed} player stat records",
            records_processed=total_processed
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.post("/calculate-rbs")
async def calculate_rbs():
    """Calculate RBS scores for all team-referee combinations"""
    try:
        # Get all data
        matches = await db.matches.find().to_list(10000)
        team_stats = await db.team_stats.find().to_list(10000)
        
        # Clear existing RBS results
        await db.rbs_results.delete_many({})
        
        # Get unique team-referee combinations
        team_referee_pairs = set()
        for match in matches:
            team_referee_pairs.add((match['home_team'], match['referee']))
            team_referee_pairs.add((match['away_team'], match['referee']))
        
        rbs_results = []
        for team_name, referee in team_referee_pairs:
            result = rbs_calculator.calculate_rbs_for_team_referee(
                team_name, referee, team_stats, matches
            )
            if result:
                rbs_results.append(result)
        
        # Insert results
        if rbs_results:
            await db.rbs_results.insert_many(rbs_results)
        
        return {
            "success": True,
            "message": f"Calculated RBS for {len(rbs_results)} team-referee combinations",
            "results_count": len(rbs_results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating RBS: {str(e)}")

@api_router.get("/rbs-results")
async def get_rbs_results(team: Optional[str] = None, referee: Optional[str] = None):
    """Get RBS results with optional filtering"""
    try:
        filter_dict = {}
        if team:
            filter_dict['team_name'] = team
        if referee:
            filter_dict['referee'] = referee
        
        results = await db.rbs_results.find(filter_dict).to_list(1000)
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
        
        # Sort by RBS score (most biased first)
        results.sort(key=lambda x: abs(x['rbs_score']), reverse=True)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RBS results: {str(e)}")

@api_router.get("/referees")
async def get_referees():
    """Get list of all referees"""
    try:
        referees = await db.matches.distinct("referee")
        return {"referees": sorted(referees)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching referees: {str(e)}")

@api_router.get("/teams")
async def get_teams():
    """Get list of all teams"""
    try:
        home_teams = await db.matches.distinct("home_team")
        away_teams = await db.matches.distinct("away_team")
        teams = sorted(list(set(home_teams + away_teams)))
        return {"teams": teams}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching teams: {str(e)}")

@api_router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    try:
        matches_count = await db.matches.count_documents({})
        team_stats_count = await db.team_stats.count_documents({})
        player_stats_count = await db.player_stats.count_documents({})
        rbs_results_count = await db.rbs_results.count_documents({})
        
        return {
            "matches": matches_count,
            "team_stats": team_stats_count,
            "player_stats": player_stats_count,
            "rbs_results": rbs_results_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
