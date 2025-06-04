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
    penalty_attempts: Optional[int] = 0
    penalty_goals: Optional[int] = 0
    penalty_conversion_rate: Optional[float] = 0.0
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
    penalty_attempts: Optional[int] = 0
    penalty_goals: Optional[int] = 0

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

class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    referee_name: str
    match_date: Optional[str] = None

class MatchPredictionResponse(BaseModel):
    success: bool
    home_team: str
    away_team: str
    referee: str
    predicted_home_goals: float
    predicted_away_goals: float
    home_xg: float
    away_xg: float
    prediction_breakdown: Dict
    confidence_factors: Dict

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
        
        # Calculate numerical confidence based on sample size
        # Higher number of matches = higher confidence (0-100 scale)
        if matches_with_ref >= 10:
            confidence = min(95, 70 + (matches_with_ref - 10) * 2.5)  # 70-95%
        elif matches_with_ref >= 5:
            confidence = 50 + (matches_with_ref - 5) * 4  # 50-70%
        elif matches_with_ref >= 2:
            confidence = 20 + (matches_with_ref - 2) * 10  # 20-50%
        else:
            confidence = matches_with_ref * 10  # 0-20%
        
        confidence = round(confidence, 1)
        
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

# Match Prediction Engine
class MatchPredictor:
    def __init__(self):
        self.rbs_scaling_factor = 0.2  # RBS of -5 gives -1.0 xG adjustment
    
    async def calculate_team_averages(self, team_name, is_home, exclude_opponent=None, season_filter=None):
        """Calculate comprehensive team averages with home/away context"""
        # Build query for team stats
        query = {
            "team_name": team_name,
            "is_home": is_home
        }
        
        # Get team stats
        team_stats = await db.team_stats.find(query).to_list(1000)
        
        # Get corresponding matches to filter by season/opponent if needed
        if exclude_opponent or season_filter:
            match_ids = [stat['match_id'] for stat in team_stats]
            match_query = {"match_id": {"$in": match_ids}}
            if season_filter:
                match_query["season"] = season_filter
            
            matches = await db.matches.find(match_query).to_list(1000)
            valid_match_ids = set()
            
            for match in matches:
                # Exclude specific opponent if requested
                if exclude_opponent:
                    opponent = match['away_team'] if match['home_team'] == team_name else match['home_team']
                    if opponent == exclude_opponent:
                        continue
                valid_match_ids.add(match['match_id'])
            
            # Filter team stats by valid matches
            team_stats = [stat for stat in team_stats if stat['match_id'] in valid_match_ids]
        
        if not team_stats:
            return None
        
        # Calculate comprehensive averages
        total_matches = len(team_stats)
        averages = {
            'shots_total': sum(stat.get('shots_total', 0) for stat in team_stats) / total_matches,
            'shots_on_target': sum(stat.get('shots_on_target', 0) for stat in team_stats) / total_matches,
            'xg': sum(stat.get('xg', 0) for stat in team_stats) / total_matches,
            'fouls': sum(stat.get('fouls', 0) for stat in team_stats) / total_matches,
            'fouls_drawn': sum(stat.get('fouls_drawn', 0) for stat in team_stats) / total_matches,
            'penalties_awarded': sum(stat.get('penalty_attempts', 0) for stat in team_stats) / total_matches,  # Average penalty attempts per match
            'penalty_attempts': sum(stat.get('penalty_attempts', 0) for stat in team_stats) / total_matches,
            'penalty_goals': sum(stat.get('penalty_goals', 0) for stat in team_stats) / total_matches,
            'yellow_cards': sum(stat.get('yellow_cards', 0) for stat in team_stats) / total_matches,
            'red_cards': sum(stat.get('red_cards', 0) for stat in team_stats) / total_matches,
            'possession_pct': sum(stat.get('possession_pct', 0) for stat in team_stats) / total_matches,
            'goals': 0,  # Will calculate from matches
            'goals_conceded': 0,  # Will calculate from matches
            'matches_count': total_matches,
        }
        
        # Calculate actual goals scored and conceded from matches
        match_ids = [stat['match_id'] for stat in team_stats]
        matches = await db.matches.find({"match_id": {"$in": match_ids}}).to_list(1000)
        
        total_goals = 0
        total_goals_conceded = 0
        total_points = 0
        
        for match in matches:
            if match['home_team'] == team_name and is_home:
                total_goals += match['home_score']
                total_goals_conceded += match['away_score']
                # Calculate points
                if match['home_score'] > match['away_score']:
                    total_points += 3
                elif match['home_score'] == match['away_score']:
                    total_points += 1
            elif match['away_team'] == team_name and not is_home:
                total_goals += match['away_score']
                total_goals_conceded += match['home_score']
                # Calculate points
                if match['away_score'] > match['home_score']:
                    total_points += 3
                elif match['away_score'] == match['home_score']:
                    total_points += 1
        
        averages['goals'] = total_goals / total_matches if total_matches > 0 else 0
        averages['goals_conceded'] = total_goals_conceded / total_matches if total_matches > 0 else 0
        averages['points_per_game'] = total_points / total_matches if total_matches > 0 else 0
        
        # Calculate derived metrics
        averages['xg_per_shot'] = averages['xg'] / averages['shots_total'] if averages['shots_total'] > 0 else 0
        averages['goals_per_xg'] = averages['goals'] / averages['xg'] if averages['xg'] > 0 else 1.0
        averages['shot_accuracy'] = averages['shots_on_target'] / averages['shots_total'] if averages['shots_total'] > 0 else 0.3
        averages['conversion_rate'] = averages['goals'] / averages['shots_on_target'] if averages['shots_on_target'] > 0 else 0.1
        averages['penalty_conversion_rate'] = averages['penalty_goals'] / averages['penalty_attempts'] if averages['penalty_attempts'] > 0 else 0.77
        
        # Defensive metrics (shots conceded, xG conceded)
        averages['shots_conceded'] = 0  # Will be calculated from opponent data
        averages['xg_conceded'] = averages['goals_conceded'] * 0.9  # Rough estimate
        
        return averages
    
    async def calculate_ppg(self, team_name, season_filter=None):
        """Calculate Points Per Game for a team"""
        # Get all matches for this team
        query = {
            "$or": [
                {"home_team": team_name},
                {"away_team": team_name}
            ]
        }
        if season_filter:
            query["season"] = season_filter
        
        matches = await db.matches.find(query).to_list(1000)
        
        if not matches:
            return 0
        
        total_points = 0
        for match in matches:
            if match['home_team'] == team_name:
                if match['home_score'] > match['away_score']:
                    total_points += 3  # Win
                elif match['home_score'] == match['away_score']:
                    total_points += 1  # Draw
                # Loss = 0 points
            else:  # Away team
                if match['away_score'] > match['home_score']:
                    total_points += 3  # Win
                elif match['away_score'] == match['home_score']:
                    total_points += 1  # Draw
                # Loss = 0 points
        
        return total_points / len(matches)
    
    async def get_referee_bias(self, team_name, referee_name):
        """Get referee bias score for team-referee combination"""
        rbs_result = await db.rbs_results.find_one({
            "team_name": team_name,
            "referee": referee_name
        })
        
        if rbs_result:
            return rbs_result['rbs_score'], rbs_result['confidence_level']
        return 0.0, 0.0
    
    async def predict_match(self, home_team, away_team, referee_name, match_date=None):
        """Enhanced prediction function using comprehensive team stats"""
        try:
            # Get comprehensive team averages (home and away context)
            home_stats = await self.calculate_team_averages(home_team, is_home=True, exclude_opponent=away_team)
            away_stats = await self.calculate_team_averages(away_team, is_home=False, exclude_opponent=home_team)
            
            # Get defensive stats (what teams concede when playing home/away)
            home_defensive = await self.calculate_team_averages(home_team, is_home=True)
            away_defensive = await self.calculate_team_averages(away_team, is_home=False)
            
            if not home_stats or not away_stats:
                raise ValueError("Insufficient historical data for one or both teams")
            
            # Enhanced xG calculation using multiple factors
            
            # Method 1: Shot-based xG calculation
            home_shot_xg = home_stats['shots_total'] * home_stats['xg_per_shot']
            away_shot_xg = away_stats['shots_total'] * away_stats['xg_per_shot']
            
            # Method 2: Historical xG average
            home_hist_xg = home_stats['xg']
            away_hist_xg = away_stats['xg']
            
            # Method 3: Opponent defensive consideration
            home_vs_defense = home_stats['shots_total'] * (away_defensive['goals_conceded'] / away_defensive['shots_conceded'] if away_defensive.get('shots_conceded', 0) > 0 else 0.1)
            away_vs_defense = away_stats['shots_total'] * (home_defensive['goals_conceded'] / home_defensive.get('shots_conceded', 10) if home_defensive.get('shots_conceded', 0) > 0 else 0.1)
            
            # Combine methods with weights
            home_base_xg = (home_shot_xg * 0.4 + home_hist_xg * 0.4 + home_vs_defense * 0.2)
            away_base_xg = (away_shot_xg * 0.4 + away_hist_xg * 0.4 + away_vs_defense * 0.2)
            
            # Factor in additional team stats
            
            # Possession adjustment (teams with higher possession typically create more chances)
            possession_factor_home = 1 + ((home_stats['possession_pct'] - 50) * 0.01)  # +/- 1% per percentage point above/below 50%
            possession_factor_away = 1 + ((away_stats['possession_pct'] - 50) * 0.01)
            
            home_base_xg *= possession_factor_home
            away_base_xg *= possession_factor_away
            
            # Fouls drawn factor (teams that draw more fouls get more set pieces and penalties)
            fouls_factor_home = 1 + (home_stats['fouls_drawn'] - 10) * 0.02  # Baseline 10 fouls drawn per match
            fouls_factor_away = 1 + (away_stats['fouls_drawn'] - 10) * 0.02
            
            home_base_xg *= max(0.8, min(1.3, fouls_factor_home))  # Cap between 0.8x and 1.3x
            away_base_xg *= max(0.8, min(1.3, fouls_factor_away))
            
            # Enhanced penalties factor using conversion rates
            # Each penalty attempt adds potential xG, weighted by team's conversion rate
            # Using penalties_awarded (average penalty attempts per match)
            home_penalty_xg = home_stats['penalties_awarded'] * 0.79 * home_stats['penalty_conversion_rate']
            away_penalty_xg = away_stats['penalties_awarded'] * 0.79 * away_stats['penalty_conversion_rate']
            
            home_base_xg += home_penalty_xg
            away_base_xg += away_penalty_xg
            
            # Get PPG for both teams (use calculated PPG from team averages)
            home_ppg = home_stats['points_per_game']
            away_ppg = away_stats['points_per_game']
            
            # Enhanced PPG adjustment considering home/away context
            ppg_diff = home_ppg - away_ppg
            ppg_adjustment = ppg_diff * 0.15  # Base adjustment factor
            
            # Apply PPG adjustment
            home_adjusted_xg = home_base_xg + ppg_adjustment
            away_adjusted_xg = away_base_xg - ppg_adjustment
            
            # Get referee bias with enhanced calculation
            home_rbs, home_rbs_confidence = await self.get_referee_bias(home_team, referee_name)
            away_rbs, away_rbs_confidence = await self.get_referee_bias(away_team, referee_name)
            
            # Apply referee bias (enhanced scaling)
            home_ref_adjustment = home_rbs * self.rbs_scaling_factor
            away_ref_adjustment = away_rbs * self.rbs_scaling_factor
            
            # Final xG predictions with bounds
            final_home_xg = max(0.1, home_adjusted_xg + home_ref_adjustment)
            final_away_xg = max(0.1, away_adjusted_xg + away_ref_adjustment)
            
            # Enhanced goal prediction using conversion rates
            # Use team-specific conversion rates rather than just goals_per_xg
            home_conversion = max(0.5, min(2.0, home_stats['goals_per_xg']))
            away_conversion = max(0.5, min(2.0, away_stats['goals_per_xg']))
            
            predicted_home_goals = final_home_xg * home_conversion
            predicted_away_goals = final_away_xg * away_conversion
            
            # Round to reasonable precision
            predicted_home_goals = round(predicted_home_goals, 2)
            predicted_away_goals = round(predicted_away_goals, 2)
            final_home_xg = round(final_home_xg, 2)
            final_away_xg = round(final_away_xg, 2)
            
            # Comprehensive prediction breakdown
            prediction_breakdown = {
                "home_base_xg": round(home_base_xg, 2),
                "away_base_xg": round(away_base_xg, 2),
                "ppg_adjustment": round(ppg_adjustment, 2),
                "home_ref_adjustment": round(home_ref_adjustment, 2),
                "away_ref_adjustment": round(away_ref_adjustment, 2),
                "home_shots_avg": round(home_stats['shots_total'], 1),
                "away_shots_avg": round(away_stats['shots_total'], 1),
                "home_xg_per_shot": round(home_stats['xg_per_shot'], 3),
                "away_xg_per_shot": round(away_stats['xg_per_shot'], 3),
                "home_possession_avg": round(home_stats['possession_pct'], 1),
                "away_possession_avg": round(away_stats['possession_pct'], 1),
                "home_fouls_drawn_avg": round(home_stats['fouls_drawn'], 1),
                "away_fouls_drawn_avg": round(away_stats['fouls_drawn'], 1),
                "home_penalties_avg": round(home_stats['penalties_awarded'], 3),  # Average penalty attempts per match
                "away_penalties_avg": round(away_stats['penalties_awarded'], 3),  # Average penalty attempts per match
                "home_penalty_conversion": round(home_stats['penalty_conversion_rate'], 3),
                "away_penalty_conversion": round(away_stats['penalty_conversion_rate'], 3),
                "home_penalty_goals_avg": round(home_stats['penalty_goals'], 3),  # Average penalty goals per match
                "away_penalty_goals_avg": round(away_stats['penalty_goals'], 3),  # Average penalty goals per match
                "home_goals_avg": round(home_stats['goals'], 2),
                "away_goals_avg": round(away_stats['goals'], 2),
                "home_conversion_rate": round(home_conversion, 2),
                "away_conversion_rate": round(away_conversion, 2)
            }
            
            # Enhanced confidence factors
            confidence_factors = {
                "home_matches_count": home_stats['matches_count'],
                "away_matches_count": away_stats['matches_count'],
                "home_rbs_confidence": home_rbs_confidence,
                "away_rbs_confidence": away_rbs_confidence,
                "home_ppg": round(home_ppg, 2),
                "away_ppg": round(away_ppg, 2),
                "home_rbs_score": round(home_rbs, 3),
                "away_rbs_score": round(away_rbs, 3),
                "overall_confidence": min(90, max(20, (home_stats['matches_count'] + away_stats['matches_count']) / 2 * 4)),
                "data_quality": {
                    "home_shots_data": "good" if home_stats['shots_total'] > 0 else "estimated",
                    "away_shots_data": "good" if away_stats['shots_total'] > 0 else "estimated",
                    "home_xg_data": "good" if home_stats['xg'] > 0 else "limited",
                    "away_xg_data": "good" if away_stats['xg'] > 0 else "limited"
                }
            }
            
            return MatchPredictionResponse(
                success=True,
                home_team=home_team,
                away_team=away_team,
                referee=referee_name,
                predicted_home_goals=predicted_home_goals,
                predicted_away_goals=predicted_away_goals,
                home_xg=final_home_xg,
                away_xg=final_away_xg,
                prediction_breakdown=prediction_breakdown,
                confidence_factors=confidence_factors
            )
            
        except Exception as e:
            return MatchPredictionResponse(
                success=False,
                home_team=home_team,
                away_team=away_team,
                referee=referee_name,
                predicted_home_goals=0.0,
                predicted_away_goals=0.0,
                home_xg=0.0,
                away_xg=0.0,
                prediction_breakdown={"error": str(e)},
                confidence_factors={"error": "Insufficient data"}
            )

# Initialize Match Predictor
match_predictor = MatchPredictor()

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
                    xg=safe_float(row.get('xg', 0)),
                    penalty_attempts=safe_int(row.get('penalty_attempts', 0)),
                    penalty_goals=safe_int(row.get('penalty_goals', 0))
                )
                player_stats_batch.append(stats.dict())
            
            if player_stats_batch:
                await db.player_stats.insert_many(player_stats_batch)
                total_processed += len(player_stats_batch)
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded {total_processed} player stat records with penalty data",
            records_processed=total_processed
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")

@api_router.post("/migrate-confidence")
async def migrate_confidence():
    """Migrate old text confidence values to numerical confidence values"""
    try:
        # Get all RBS results
        results = await db.rbs_results.find().to_list(10000)
        
        updated_count = 0
        for result in results:
            if isinstance(result.get('confidence_level'), str):
                # Convert old text values to numerical
                matches_with_ref = result.get('matches_with_ref', 1)
                
                # Calculate numerical confidence
                if matches_with_ref >= 10:
                    confidence = min(95, 70 + (matches_with_ref - 10) * 2.5)
                elif matches_with_ref >= 5:
                    confidence = 50 + (matches_with_ref - 5) * 4
                elif matches_with_ref >= 2:
                    confidence = 20 + (matches_with_ref - 2) * 10
                else:
                    confidence = matches_with_ref * 10
                
                confidence = round(confidence, 1)
                
                # Update the document
                await db.rbs_results.update_one(
                    {"_id": result["_id"]},
                    {"$set": {"confidence_level": confidence}}
                )
                updated_count += 1
        
        return {
            "success": True,
            "message": f"Migrated {updated_count} confidence values to numerical format",
            "updated_count": updated_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating confidence values: {str(e)}")

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

@api_router.post("/recalculate-all-stats")
async def recalculate_all_stats():
    """Comprehensive function to recalculate all stats in the correct order"""
    try:
        results = {}
        
        # Step 1: Calculate team stats from player data
        print("Step 1: Aggregating player stats to team level...")
        player_response = await calculate_team_stats_from_players()
        results['player_aggregation'] = player_response
        
        # Step 2: Calculate shots data
        print("Step 2: Calculating shots and shots on target...")
        shots_response = await calculate_shots_from_data()
        results['shots_calculation'] = shots_response
        
        # Step 3: Recalculate RBS scores with updated data
        print("Step 3: Recalculating RBS scores...")
        
        # Get fresh data for RBS calculation
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
        
        # Insert new results
        if rbs_results:
            await db.rbs_results.insert_many(rbs_results)
        
        results['rbs_calculation'] = {
            "success": True,
            "message": f"Calculated RBS for {len(rbs_results)} team-referee combinations",
            "results_count": len(rbs_results)
        }
        
        # Step 4: Get final stats summary
        final_stats = await get_stats()
        results['final_stats'] = final_stats
        
        return {
            "success": True,
            "message": "Successfully recalculated all stats",
            "details": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recalculating all stats: {str(e)}")

@api_router.post("/calculate-shots-from-data")
async def calculate_shots_from_data():
    """Calculate and populate shots and shots on target data using multiple methods"""
    try:
        # Get all team stats
        team_stats = await db.team_stats.find().to_list(10000)
        
        # Get all matches to cross-reference
        matches = await db.matches.find().to_list(10000)
        match_dict = {match['match_id']: match for match in matches}
        
        # Get all player stats for additional context
        player_stats = await db.player_stats.find().to_list(15000)
        
        # Group player stats by match and team for context
        player_by_team_match = {}
        for player in player_stats:
            key = f"{player['match_id']}_{player['team_name']}"
            if key not in player_by_team_match:
                player_by_team_match[key] = []
            player_by_team_match[key].append(player)
        
        updated_count = 0
        
        for team_stat in team_stats:
            match_id = team_stat['match_id']
            team_name = team_stat['team_name']
            key = f"{match_id}_{team_name}"
            
            # Get match info
            match = match_dict.get(match_id)
            if not match:
                continue
                
            # Get player stats for this team in this match
            team_players = player_by_team_match.get(key, [])
            
            # Method 1: Use existing shots data if available and > 0
            existing_shots = team_stat.get('shots_total', 0)
            existing_shots_ot = team_stat.get('shots_on_target', 0)
            
            if existing_shots > 0 and existing_shots_ot > 0:
                # Data already exists, skip
                continue
            
            # Method 2: Calculate from player data and team context
            team_xg = sum(player.get('xg', 0) for player in team_players)
            team_goals = sum(player.get('goals', 0) for player in team_players)
            
            # Get actual goals from match data for verification
            if team_stat['is_home']:
                actual_goals = match.get('home_score', 0)
            else:
                actual_goals = match.get('away_score', 0)
            
            # Use actual goals from match if different from player sum
            if actual_goals != team_goals:
                team_goals = actual_goals
            
            # Method 3: Estimate shots using multiple factors
            shots_total = 0
            shots_on_target = 0
            
            if team_xg > 0:
                # Base estimation: Average xG per shot in professional football is ~0.11
                base_shots = max(1, int(team_xg / 0.11))
                
                # Adjust based on goals scored (more goals usually means more shots)
                goal_factor = 1 + (team_goals * 0.3)  # Each goal adds 30% more shots
                estimated_shots = int(base_shots * goal_factor)
                
                # Ensure reasonable bounds (3-25 shots per match)
                shots_total = max(3, min(25, estimated_shots))
                
                # Shots on target estimation
                # Typically 30-40% of shots are on target, higher for teams that score
                if team_goals > 0:
                    on_target_ratio = min(0.6, 0.25 + (team_goals * 0.1))  # 25% base + 10% per goal
                else:
                    on_target_ratio = max(0.2, team_xg * 0.3)  # At least 20%, up based on xG
                
                shots_on_target = max(1, min(shots_total, int(shots_total * on_target_ratio)))
                
                # Ensure all goals are counted as shots on target at minimum
                shots_on_target = max(shots_on_target, team_goals)
                shots_total = max(shots_total, shots_on_target)
                
            else:
                # Fallback for teams with no xG data
                if team_goals > 0:
                    shots_total = max(3, team_goals * 4)  # Rough estimate: 4 shots per goal
                    shots_on_target = max(team_goals, int(shots_total * 0.3))
                else:
                    # Very defensive/poor performance
                    shots_total = 3
                    shots_on_target = 1
            
            # Method 4: Cross-reference with possession and attacking intent
            possession = team_stat.get('possession_pct', 50)
            
            # Teams with higher possession typically have more shots
            if possession > 60:
                shots_total = int(shots_total * 1.2)
            elif possession < 35:
                shots_total = int(shots_total * 0.8)
            
            # Final bounds check
            shots_total = max(1, min(30, shots_total))
            shots_on_target = max(1, min(shots_total, shots_on_target))
            
            # Update the team stats
            update_data = {
                'shots_total': shots_total,
                'shots_on_target': shots_on_target
            }
            
            await db.team_stats.update_one(
                {'_id': team_stat['_id']},
                {'$set': update_data}
            )
            
            updated_count += 1
        
        return {
            "success": True,
            "message": f"Updated shots data for {updated_count} team stat records",
            "updated_count": updated_count,
            "total_records": len(team_stats)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating shots data: {str(e)}")

@api_router.post("/set-team-penalty-data")
async def set_team_penalty_data(team_data: dict):
    """Manually set penalty data for specific teams where we have accurate information"""
    try:
        # Expected format: {"Arsenal": {"match_id": "some-id", "attempts": 2, "goals": 2}}
        updates_made = 0
        
        for team_name, penalty_info in team_data.items():
            match_id = penalty_info.get('match_id')
            attempts = penalty_info.get('attempts', 0)
            goals = penalty_info.get('goals', 0)
            
            if not match_id:
                continue
            
            # Update the specific match team stats
            result = await db.team_stats.update_one(
                {"team_name": team_name, "match_id": match_id},
                {"$set": {
                    "penalty_attempts": attempts,
                    "penalty_goals": goals,
                    "penalties_awarded": attempts,
                    "penalty_conversion_rate": goals / attempts if attempts > 0 else 0.77
                }}
            )
            
            if result.modified_count > 0:
                updates_made += 1
                
                # Also update a player from that team/match
                players = await db.player_stats.find({"team_name": team_name, "match_id": match_id}).to_list(100)
                if players:
                    # Find the best candidate for penalty taker
                    best_candidate = max(players, key=lambda p: p.get('goals', 0) * 3 + p.get('xg', 0))
                    
                    await db.player_stats.update_one(
                        {"_id": best_candidate["_id"]},
                        {"$set": {
                            "penalty_attempts": attempts,
                            "penalty_goals": goals
                        }}
                    )
        
        return {
            "success": True,
            "message": f"Updated penalty data for {updates_made} team-match combinations",
            "updates_made": updates_made
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting penalty data: {str(e)}")

@api_router.get("/find-high-scoring-matches/{team_name}")
async def find_high_scoring_matches(team_name: str):
    """Find matches where a team scored multiple goals - likely penalty candidates"""
    try:
        # Get all matches for this team
        matches = await db.matches.find({
            "$or": [
                {"home_team": team_name},
                {"away_team": team_name}
            ]
        }).to_list(1000)
        
        # Find high-scoring matches
        high_scoring = []
        for match in matches:
            team_goals = match['home_score'] if match['home_team'] == team_name else match['away_score']
            if team_goals >= 2:  # Matches where team scored 2+ goals
                high_scoring.append({
                    "match_id": match['match_id'],
                    "date": match.get('match_date', 'Unknown'),
                    "opponent": match['away_team'] if match['home_team'] == team_name else match['home_team'],
                    "venue": "Home" if match['home_team'] == team_name else "Away",
                    "score": f"{match['home_score']}-{match['away_score']}",
                    "team_goals": team_goals
                })
        
        # Sort by team goals descending
        high_scoring.sort(key=lambda x: x['team_goals'], reverse=True)
        
        return {
            "success": True,
            "team_name": team_name,
            "high_scoring_matches": high_scoring[:10]  # Top 10
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding high-scoring matches: {str(e)}")

@api_router.post("/reset-penalty-data")
async def reset_penalty_data():
    """Reset all penalty data to zero before repopulating"""
    try:
        # Reset all team stats penalty fields
        await db.team_stats.update_many(
            {},
            {'$set': {
                'penalty_attempts': 0,
                'penalty_goals': 0,
                'penalty_conversion_rate': 0.77,
                'penalties_awarded': 0
            }}
        )
        
        # Reset all player stats penalty fields
        await db.player_stats.update_many(
            {},
            {'$set': {
                'penalty_attempts': 0,
                'penalty_goals': 0
            }}
        )
        
        return {
            "success": True,
            "message": "Reset all penalty data to zero"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting penalty data: {str(e)}")

@api_router.post("/populate-penalty-data")
async def populate_penalty_data():
    """Populate penalty attempts and goals data using conservative, realistic estimation"""
    try:
        # Get all player stats and team stats
        player_stats = await db.player_stats.find().to_list(15000)
        team_stats = await db.team_stats.find().to_list(10000)
        matches = await db.matches.find().to_list(10000)
        
        # Create a match lookup
        match_dict = {match['match_id']: match for match in matches}
        
        # Group player stats by match and team
        player_by_team_match = {}
        for player in player_stats:
            key = f"{player['match_id']}_{player['team_name']}"
            if key not in player_by_team_match:
                player_by_team_match[key] = []
            player_by_team_match[key].append(player)
        
        # Much more conservative penalty estimation
        # In reality, penalties are rare - maybe 1 in every 8-10 matches across all teams
        player_updates = 0
        team_updates = 0
        
        # Group by teams to track season totals
        team_season_penalties = {}
        
        for team_stat in team_stats:
            match_id = team_stat['match_id']
            team_name = team_stat['team_name']
            key = f"{match_id}_{team_name}"
            
            # Initialize team tracking
            if team_name not in team_season_penalties:
                team_season_penalties[team_name] = {
                    'total_attempts': 0,
                    'total_goals': 0,
                    'matches_processed': 0
                }
            
            # Get match and team players
            match = match_dict.get(match_id)
            team_players = player_by_team_match.get(key, [])
            
            if not match or not team_players:
                continue
            
            # Get actual goals scored by the team
            if team_stat['is_home']:
                team_goals = match.get('home_score', 0)
            else:
                team_goals = match.get('away_score', 0)
            
            # Much more conservative penalty estimation
            team_fouls_drawn = sum(p.get('fouls_drawn', 0) for p in team_players)
            team_total_xg = sum(p.get('xg', 0) for p in team_players)
            
            # Very strict penalty criteria
            penalty_likelihood = 0
            
            # Only award penalties in very specific circumstances
            # Factor 1: Goals significantly exceed xG AND high fouls drawn
            if team_goals >= 2 and team_total_xg > 0:
                xg_diff = team_goals - team_total_xg
                if xg_diff > 1.2 and team_fouls_drawn > 15:  # Very high threshold
                    penalty_likelihood = 0.6
                elif xg_diff > 0.9 and team_fouls_drawn > 18:  # Exceptional circumstances
                    penalty_likelihood = 0.4
            
            # Factor 2: Extremely high fouls drawn (suggesting controversial match)
            if team_fouls_drawn > 20:  # Very high fouls drawn
                penalty_likelihood += 0.3
            
            # Factor 3: High-scoring match with goals exceeding xG significantly
            if team_goals >= 3 and team_total_xg > 0 and (team_goals - team_total_xg) > 1.0:
                penalty_likelihood += 0.2
            
            # Determine penalty attempts (much more conservative)
            # Only award penalty if likelihood is very high AND team hasn't had too many this season
            penalty_attempts = 0
            penalty_goals = 0
            
            # Very conservative limits: max 2-3 penalties per team per season
            max_penalties_per_season = 3
            
            if (penalty_likelihood > 0.7 and 
                team_season_penalties[team_name]['total_attempts'] < max_penalties_per_season):
                
                penalty_attempts = 1
                team_season_penalties[team_name]['total_attempts'] += 1
                
                # Conservative penalty conversion (league average ~77%)
                if penalty_likelihood > 0.8:
                    penalty_goals = 1
                    team_season_penalties[team_name]['total_goals'] += 1
                else:
                    # Miss the penalty
                    penalty_goals = 0
            
            # Update team-level penalty stats
            penalty_conversion_rate = 0.77  # Default league average
            if team_season_penalties[team_name]['total_attempts'] > 0:
                penalty_conversion_rate = team_season_penalties[team_name]['total_goals'] / team_season_penalties[team_name]['total_attempts']
            
            # Update team stats
            await db.team_stats.update_one(
                {'_id': team_stat['_id']},
                {'$set': {
                    'penalty_attempts': penalty_attempts,
                    'penalty_goals': penalty_goals,
                    'penalty_conversion_rate': round(penalty_conversion_rate, 3),
                    'penalties_awarded': penalty_attempts
                }}
            )
            team_updates += 1
            
            # Distribute penalty stats to players
            if penalty_attempts > 0 and team_players:
                # Find the most likely penalty taker (highest goals + xG combination)
                best_candidate = max(team_players, 
                    key=lambda p: p.get('goals', 0) * 3 + p.get('xg', 0) + p.get('fouls_drawn', 0) * 0.05)
                
                # Update the penalty taker's stats
                await db.player_stats.update_one(
                    {'_id': best_candidate['_id']},
                    {'$set': {
                        'penalty_attempts': penalty_attempts,
                        'penalty_goals': penalty_goals
                    }}
                )
                player_updates += 1
        
        # Summary of penalties awarded by team
        penalty_summary = {}
        for team, data in team_season_penalties.items():
            if data['total_attempts'] > 0:
                penalty_summary[team] = {
                    'total_attempts': data['total_attempts'],
                    'total_goals': data['total_goals'],
                    'conversion_rate': round(data['total_goals'] / data['total_attempts'], 3) if data['total_attempts'] > 0 else 0
                }
        
        return {
            "success": True,
            "message": f"Populated conservative penalty data for {team_updates} team stats and {player_updates} player stats",
            "team_updates": team_updates,
            "player_updates": player_updates,
            "penalty_summary": penalty_summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error populating penalty data: {str(e)}")

@api_router.post("/calculate-team-stats-from-players")
async def calculate_team_stats_from_players():
    """Calculate team-level stats by aggregating player stats for each match"""
    try:
        # Get all player stats
        player_stats = await db.player_stats.find().to_list(15000)
        
        # Get all team stats to update
        team_stats = await db.team_stats.find().to_list(10000)
        
        # Get all matches for goal verification
        matches = await db.matches.find().to_list(10000)
        match_dict = {match['match_id']: match for match in matches}
        
        # Group player stats by match_id and team_name
        team_aggregations = {}
        
        for player in player_stats:
            key = f"{player['match_id']}_{player['team_name']}"
            
            if key not in team_aggregations:
                team_aggregations[key] = {
                    'match_id': player['match_id'],
                    'team_name': player['team_name'],
                    'fouls_drawn': 0,
                    'xg': 0.0,
                    'goals': 0,
                    'assists': 0,
                    'player_yellow_cards': 0,
                    'player_fouls_committed': 0,
                    'penalty_attempts': 0,
                    'penalty_goals': 0
                }
            
            # Aggregate player stats to team level
            team_aggregations[key]['fouls_drawn'] += player.get('fouls_drawn', 0)
            team_aggregations[key]['xg'] += player.get('xg', 0)
            team_aggregations[key]['goals'] += player.get('goals', 0)
            team_aggregations[key]['assists'] += player.get('assists', 0)
            team_aggregations[key]['player_yellow_cards'] += player.get('yellow_cards', 0)
            team_aggregations[key]['player_fouls_committed'] += player.get('fouls_committed', 0)
            team_aggregations[key]['penalty_attempts'] += player.get('penalty_attempts', 0)
            team_aggregations[key]['penalty_goals'] += player.get('penalty_goals', 0)
        
        # Update team stats with aggregated data
        updated_count = 0
        
        for team_stat in team_stats:
            key = f"{team_stat['match_id']}_{team_stat['team_name']}"
            
            if key in team_aggregations:
                aggregated = team_aggregations[key]
                
                # Get match data for goal verification
                match = match_dict.get(team_stat['match_id'])
                actual_goals = 0
                if match:
                    if team_stat['is_home']:
                        actual_goals = match.get('home_score', 0)
                    else:
                        actual_goals = match.get('away_score', 0)
                
                # Use actual goals from match if available, otherwise use player sum
                final_goals = actual_goals if actual_goals >= 0 else aggregated['goals']
                
                # Calculate penalty conversion rate
                penalty_attempts = aggregated['penalty_attempts']
                penalty_goals = aggregated['penalty_goals']
                penalty_conversion_rate = penalty_goals / penalty_attempts if penalty_attempts > 0 else 0.77  # League average
                
                # Prepare update data
                update_data = {
                    'fouls_drawn': aggregated['fouls_drawn'],
                    'xg': round(aggregated['xg'], 2),
                    'penalties_awarded': penalty_attempts,  # Now using actual attempts instead of estimation
                    'penalty_attempts': penalty_attempts,
                    'penalty_goals': penalty_goals,
                    'penalty_conversion_rate': round(penalty_conversion_rate, 3)
                }
                
                # Update the team stats record
                await db.team_stats.update_one(
                    {'_id': team_stat['_id']},
                    {'$set': update_data}
                )
                
                updated_count += 1
        
        return {
            "success": True,
            "message": f"Updated {updated_count} team stats with player-aggregated data including penalty stats",
            "team_aggregations_found": len(team_aggregations),
            "team_stats_updated": updated_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating team stats from players: {str(e)}")

@api_router.post("/debug/add-more-sample-stats")
async def add_more_realistic_stats():
    """Add realistic sample data to more records for better RBS calculation"""
    try:
        # Get more team stats records to update
        team_stats = await db.team_stats.find().limit(100).to_list(100)
        
        import random
        updated_count = 0
        
        for stat in team_stats:
            # Add varied realistic sample values
            realistic_data = {
                "fouls_drawn": random.randint(6, 18),  # Varied fouls drawn per match
                "penalties_awarded": random.choices([0, 1], weights=[85, 15])[0],  # 15% chance of penalty
                "xg": round(random.uniform(0.3, 4.2), 2)  # Varied xG values
            }
            
            await db.team_stats.update_one(
                {"_id": stat["_id"]},
                {"$set": realistic_data}
            )
            updated_count += 1
        
        return {
            "success": True,
            "message": f"Updated {updated_count} team stats with varied realistic sample data",
            "updated_count": updated_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding sample data: {str(e)}")

@api_router.post("/debug/add-sample-stats")
async def add_sample_realistic_stats():
    """Add some realistic sample data to test the RBS table display"""
    try:
        # Get a few team stats records to update with realistic data
        team_stats = await db.team_stats.find().limit(10).to_list(10)
        
        import random
        updated_count = 0
        
        for stat in team_stats:
            # Add realistic sample values
            realistic_data = {
                "fouls_drawn": random.randint(8, 16),  # Realistic fouls drawn per match
                "penalties_awarded": random.choice([0, 0, 0, 0, 0, 1]),  # Occasional penalty
                "xg": round(random.uniform(0.5, 3.5), 2)  # Realistic xG values
            }
            
            await db.team_stats.update_one(
                {"_id": stat["_id"]},
                {"$set": realistic_data}
            )
            updated_count += 1
        
        return {
            "success": True,
            "message": f"Updated {updated_count} team stats with realistic sample data",
            "updated_count": updated_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding sample data: {str(e)}")

@api_router.get("/debug/match-penalty-data/{match_id}")
async def get_match_penalty_data(match_id: str):
    """Get penalty data for a specific match from both player and team stats"""
    try:
        # Get player stats for this match
        player_stats = await db.player_stats.find({"match_id": match_id}).to_list(100)
        
        # Get team stats for this match  
        team_stats = await db.team_stats.find({"match_id": match_id}).to_list(10)
        
        # Filter for penalty data
        penalty_players = [p for p in player_stats if p.get('penalty_attempts', 0) > 0 or p.get('penalty_goals', 0) > 0]
        
        # Convert ObjectId to string
        for player in penalty_players:
            if '_id' in player:
                player['_id'] = str(player['_id'])
                
        for team in team_stats:
            if '_id' in team:
                team['_id'] = str(team['_id'])
        
        return {
            "success": True,
            "match_id": match_id,
            "penalty_players": penalty_players,
            "team_stats": team_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching match penalty data: {str(e)}")

@api_router.get("/debug/penalty-players-sample")
async def get_penalty_players_sample():
    """Get sample of players who have penalty attempts or goals"""
    try:
        # Find players with penalty attempts
        penalty_players = await db.player_stats.find({
            "$or": [
                {"penalty_attempts": {"$gt": 0}},
                {"penalty_goals": {"$gt": 0}}
            ]
        }).limit(20).to_list(20)
        
        # Convert ObjectId to string
        for player in penalty_players:
            if '_id' in player:
                player['_id'] = str(player['_id'])
        
        return {
            "success": True,
            "penalty_players_found": len(penalty_players),
            "sample_data": penalty_players
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching penalty players: {str(e)}")

@api_router.get("/debug/team-stats/{team_name}")
async def get_team_specific_stats(team_name: str):
    """Get all team stats for a specific team"""
    try:
        team_stats = await db.team_stats.find({"team_name": team_name}).limit(5).to_list(5)
        
        # Convert ObjectId to string
        for stat in team_stats:
            if '_id' in stat:
                stat['_id'] = str(stat['_id'])
        
        return {
            "success": True,
            "team_name": team_name,
            "sample_count": len(team_stats),
            "sample_data": team_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching team stats: {str(e)}")

@api_router.get("/debug/team-penalty-analysis/{team_name}")
async def get_team_penalty_analysis(team_name: str):
    """Debug endpoint to analyze penalty data for a specific team"""
    try:
        # Get all team stats for this team
        home_stats = await db.team_stats.find({"team_name": team_name, "is_home": True}).to_list(1000)
        away_stats = await db.team_stats.find({"team_name": team_name, "is_home": False}).to_list(1000)
        
        # Calculate totals and averages
        home_total_penalty_attempts = sum(stat.get('penalty_attempts', 0) for stat in home_stats)
        home_total_penalty_goals = sum(stat.get('penalty_goals', 0) for stat in home_stats)
        home_matches = len(home_stats)
        
        away_total_penalty_attempts = sum(stat.get('penalty_attempts', 0) for stat in away_stats)
        away_total_penalty_goals = sum(stat.get('penalty_goals', 0) for stat in away_stats)
        away_matches = len(away_stats)
        
        # Calculate averages
        home_penalties_per_match = home_total_penalty_attempts / home_matches if home_matches > 0 else 0
        away_penalties_per_match = away_total_penalty_attempts / away_matches if away_matches > 0 else 0
        
        # Conversion rates
        home_conversion = home_total_penalty_goals / home_total_penalty_attempts if home_total_penalty_attempts > 0 else 0
        away_conversion = away_total_penalty_goals / away_total_penalty_attempts if away_total_penalty_attempts > 0 else 0
        
        return {
            "success": True,
            "team_name": team_name,
            "home_performance": {
                "matches": home_matches,
                "total_penalty_attempts": home_total_penalty_attempts,
                "total_penalty_goals": home_total_penalty_goals,
                "penalties_per_match": round(home_penalties_per_match, 3),
                "conversion_rate": round(home_conversion, 3)
            },
            "away_performance": {
                "matches": away_matches,
                "total_penalty_attempts": away_total_penalty_attempts,
                "total_penalty_goals": away_total_penalty_goals,
                "penalties_per_match": round(away_penalties_per_match, 3),
                "conversion_rate": round(away_conversion, 3)
            },
            "overall": {
                "total_matches": home_matches + away_matches,
                "total_penalty_attempts": home_total_penalty_attempts + away_total_penalty_attempts,
                "total_penalty_goals": home_total_penalty_goals + away_total_penalty_goals,
                "overall_penalties_per_match": round((home_total_penalty_attempts + away_total_penalty_attempts) / (home_matches + away_matches) if (home_matches + away_matches) > 0 else 0, 3),
                "overall_conversion_rate": round((home_total_penalty_goals + away_total_penalty_goals) / (home_total_penalty_attempts + away_total_penalty_attempts) if (home_total_penalty_attempts + away_total_penalty_attempts) > 0 else 0, 3)
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing penalty data: {str(e)}")

@api_router.get("/debug/player-stats-sample")
async def get_player_stats_sample():
    """Debug endpoint to check player stats data structure"""
    try:
        # Get a few sample player stats to see what fields we actually have
        sample_stats = await db.player_stats.find().limit(5).to_list(5)
        
        # Convert ObjectId to string
        for stat in sample_stats:
            if '_id' in stat:
                stat['_id'] = str(stat['_id'])
        
        return {
            "success": True,
            "sample_count": len(sample_stats),
            "sample_data": sample_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sample player stats: {str(e)}")

@api_router.get("/debug/team-stats-sample")
async def get_team_stats_sample():
    """Debug endpoint to check team stats data structure"""
    try:
        # Get a few sample team stats to see what fields we actually have
        sample_stats = await db.team_stats.find().limit(5).to_list(5)
        
        # Convert ObjectId to string
        for stat in sample_stats:
            if '_id' in stat:
                stat['_id'] = str(stat['_id'])
        
        return {
            "success": True,
            "sample_count": len(sample_stats),
            "sample_data": sample_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sample team stats: {str(e)}")

@api_router.get("/referee/{referee_name}")
async def get_referee_details(referee_name: str):
    """Get detailed stats for a specific referee"""
    try:
        # Get all matches for this referee
        matches = await db.matches.find({"referee": referee_name}).to_list(1000)
        
        # Convert ObjectId to string for matches
        for match in matches:
            if '_id' in match:
                match['_id'] = str(match['_id'])
        
        # Get all team stats for matches with this referee
        match_ids = [match['match_id'] for match in matches]
        team_stats = await db.team_stats.find({"match_id": {"$in": match_ids}}).to_list(1000)
        
        # Convert ObjectId to string for team stats
        for stat in team_stats:
            if '_id' in stat:
                stat['_id'] = str(stat['_id'])
        
        # Get RBS results for this referee
        rbs_results = await db.rbs_results.find({"referee": referee_name}).to_list(1000)
        
        # Calculate overall averages for this referee
        if team_stats:
            total_stats = len(team_stats)
            overall_averages = {
                'yellow_cards': sum(s.get('yellow_cards', 0) for s in team_stats) / total_stats,
                'red_cards': sum(s.get('red_cards', 0) for s in team_stats) / total_stats,
                'fouls': sum(s.get('fouls', 0) for s in team_stats) / total_stats,
                'fouls_drawn': sum(s.get('fouls_drawn', 0) for s in team_stats) / total_stats,
                'penalties_awarded': sum(s.get('penalties_awarded', 0) for s in team_stats) / total_stats,
                'possession_pct': sum(s.get('possession_pct', 0) for s in team_stats) / total_stats,
                'xg': sum(s.get('xg', 0) for s in team_stats) / total_stats,
                'shots_total': sum(s.get('shots_total', 0) for s in team_stats) / total_stats,
                'shots_on_target': sum(s.get('shots_on_target', 0) for s in team_stats) / total_stats,
            }
        else:
            overall_averages = {}
        
        # Convert ObjectId to string for RBS results
        for result in rbs_results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
        
        # Sort RBS results by RBS score (most biased first)
        rbs_results.sort(key=lambda x: abs(x['rbs_score']), reverse=True)
        
        return {
            "success": True,
            "referee": referee_name,
            "total_matches": len(matches),
            "total_teams": len(set(s['team_name'] for s in team_stats)),
            "overall_averages": {k: round(v, 2) for k, v in overall_averages.items()},
            "rbs_results": rbs_results,
            "matches": matches[:10]  # Return first 10 matches as sample
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching referee details: {str(e)}")

@api_router.get("/referee-summary")
async def get_referee_summary():
    """Get summary stats for all referees"""
    try:
        # Get all referees with their match counts
        pipeline = [
            {"$group": {
                "_id": "$referee",
                "total_matches": {"$sum": 1},
                "competitions": {"$addToSet": "$competition"},
                "seasons": {"$addToSet": "$season"}
            }},
            {"$sort": {"total_matches": -1}}
        ]
        
        referee_stats = await db.matches.aggregate(pipeline).to_list(1000)
        
        # Get RBS results count for each referee
        rbs_pipeline = [
            {"$group": {
                "_id": "$referee",
                "rbs_count": {"$sum": 1},
                "avg_bias": {"$avg": "$rbs_score"},
                "max_bias": {"$max": "$rbs_score"},
                "min_bias": {"$min": "$rbs_score"}
            }}
        ]
        
        rbs_stats = await db.rbs_results.aggregate(rbs_pipeline).to_list(1000)
        rbs_dict = {stat['_id']: stat for stat in rbs_stats}
        
        # Combine the data
        for referee in referee_stats:
            referee_name = referee['_id']
            if referee_name in rbs_dict:
                referee.update(rbs_dict[referee_name])
                referee['avg_bias'] = round(referee.get('avg_bias', 0), 3)
                referee['max_bias'] = round(referee.get('max_bias', 0), 3)
                referee['min_bias'] = round(referee.get('min_bias', 0), 3)
            else:
                referee.update({
                    'rbs_count': 0,
                    'avg_bias': 0,
                    'max_bias': 0,
                    'min_bias': 0
                })
        
        return {
            "success": True,
            "referees": referee_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching referee summary: {str(e)}")

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

@api_router.post("/predict-match", response_model=MatchPredictionResponse)
async def predict_match(request: MatchPredictionRequest):
    """Predict match outcome using xG-based algorithm"""
    try:
        prediction = await match_predictor.predict_match(
            home_team=request.home_team,
            away_team=request.away_team,
            referee_name=request.referee_name,
            match_date=request.match_date
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@api_router.get("/team-performance/{team_name}")
async def get_team_performance(team_name: str):
    """Get team performance stats for prediction insights"""
    try:
        # Get home and away stats
        home_stats = await match_predictor.calculate_team_averages(team_name, is_home=True)
        away_stats = await match_predictor.calculate_team_averages(team_name, is_home=False)
        
        # Get PPG
        ppg = await match_predictor.calculate_ppg(team_name)
        
        # Get recent form (last 5 matches)
        recent_matches = await db.matches.find({
            "$or": [
                {"home_team": team_name},
                {"away_team": team_name}
            ]
        }).sort([("match_date", -1)]).limit(5).to_list(5)
        
        return {
            "success": True,
            "team_name": team_name,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "ppg": round(ppg, 2),
            "recent_matches": len(recent_matches),
            "total_matches": (home_stats['matches_count'] if home_stats else 0) + 
                           (away_stats['matches_count'] if away_stats else 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching team performance: {str(e)}")

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
