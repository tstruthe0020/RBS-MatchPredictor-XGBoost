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
import math
import base64
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split
from scipy.stats import poisson

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
    dataset_name: str = "default"  # New field for dataset management

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
    dataset_name: str = "default"  # New field for dataset management

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
    shots_total: Optional[int] = 0  # Added for proper shot aggregation
    shots_on_target: Optional[int] = 0  # Added for proper shot aggregation
    penalty_attempts: Optional[int] = 0
    penalty_goals: Optional[int] = 0
    dataset_name: str = "default"  # New field for dataset management

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

class MultiDatasetUploadRequest(BaseModel):
    dataset_name: str
    matches_file: str  # base64 encoded CSV content
    team_stats_file: str  # base64 encoded CSV content
    player_stats_file: str  # base64 encoded CSV content

class DatasetInfo(BaseModel):
    dataset_name: str
    matches_count: int
    team_stats_count: int
    player_stats_count: int
    created_at: str

class DatasetListResponse(BaseModel):
    success: bool
    datasets: List[DatasetInfo]

class DatasetDeleteResponse(BaseModel):
    success: bool
    message: str
    records_deleted: int

class PredictionConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config_name: str = "default"
    
    # xG Calculation Method Weights (should sum to 1.0)
    xg_shot_based_weight: float = 0.4
    xg_historical_weight: float = 0.4
    xg_opponent_defense_weight: float = 0.2
    
    # Team Performance Adjustments
    ppg_adjustment_factor: float = 0.15
    possession_adjustment_per_percent: float = 0.01
    fouls_drawn_factor: float = 0.02
    fouls_drawn_baseline: float = 10.0
    fouls_drawn_min_multiplier: float = 0.8
    fouls_drawn_max_multiplier: float = 1.3
    
    # Penalty Calculations
    penalty_xg_value: float = 0.79
    
    # Referee Bias
    rbs_scaling_factor: float = 0.2
    
    # Goal Conversion Bounds
    min_conversion_rate: float = 0.5
    max_conversion_rate: float = 2.0
    
    # xG Bounds
    min_xg_per_match: float = 0.1
    
    # Confidence Calculation
    confidence_matches_multiplier: float = 4
    max_confidence: float = 90
    min_confidence: float = 20
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class PredictionConfigRequest(BaseModel):
    config_name: str
    xg_shot_based_weight: float = 0.4
    xg_historical_weight: float = 0.4
    xg_opponent_defense_weight: float = 0.2
    ppg_adjustment_factor: float = 0.15
    possession_adjustment_per_percent: float = 0.01
    fouls_drawn_factor: float = 0.02
    fouls_drawn_baseline: float = 10.0
    fouls_drawn_min_multiplier: float = 0.8
    fouls_drawn_max_multiplier: float = 1.3
    penalty_xg_value: float = 0.79
    rbs_scaling_factor: float = 0.2
    min_conversion_rate: float = 0.5
    max_conversion_rate: float = 2.0
    min_xg_per_match: float = 0.1
    confidence_matches_multiplier: float = 4
    max_confidence: float = 90
    min_confidence: float = 20

class RBSConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config_name: str = "default"
    
    # Weights for different statistics (based on new RBS formula)
    yellow_cards_weight: float = 0.3
    red_cards_weight: float = 0.5
    fouls_committed_weight: float = 0.1
    fouls_drawn_weight: float = 0.1
    penalties_awarded_weight: float = 0.5
    xg_difference_weight: float = 0.4
    possession_percentage_weight: float = 0.2
    
    # Confidence calculation settings
    confidence_matches_multiplier: float = 4
    max_confidence: float = 95
    min_confidence: float = 10
    confidence_threshold_low: int = 2   # Minimum matches for any confidence
    confidence_threshold_medium: int = 5  # Threshold for medium confidence
    confidence_threshold_high: int = 10   # Threshold for high confidence
    
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class RBSConfigRequest(BaseModel):
    config_name: str
    yellow_cards_weight: float = 0.3
    red_cards_weight: float = 0.5
    fouls_committed_weight: float = 0.1
    fouls_drawn_weight: float = 0.1
    penalties_awarded_weight: float = 0.5
    xg_difference_weight: float = 0.4
    possession_percentage_weight: float = 0.2
    confidence_matches_multiplier: float = 4
    max_confidence: float = 95
    min_confidence: float = 10
    confidence_threshold_low: int = 2
    confidence_threshold_medium: int = 5
    confidence_threshold_high: int = 10

class RegressionAnalysisRequest(BaseModel):
    selected_stats: List[str]
    target: str  # 'points_per_game' or 'match_result'
    test_size: Optional[float] = 0.2
    random_state: Optional[int] = 42

class RegressionAnalysisResponse(BaseModel):
    success: bool
    target: str
    selected_stats: List[str]
    sample_size: int
    model_type: str
    results: Dict
    message: str

class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    referee_name: str
    match_date: Optional[str] = None
    config_name: Optional[str] = "default"  # Allow custom config selection

class MatchPredictionResponse(BaseModel):
    success: bool
    home_team: str
    away_team: str
    referee: str
    predicted_home_goals: float
    predicted_away_goals: float
    home_xg: float
    away_xg: float
    home_win_probability: float  # Percentage chance of home team winning
    draw_probability: float      # Percentage chance of draw
    away_win_probability: float  # Percentage chance of away team winning
    prediction_breakdown: Dict
    confidence_factors: Dict

# RBS Calculation Engine
class RBSCalculator:
    def __init__(self):
        # Default configuration
        self.default_config = RBSConfig()
    
    async def get_config(self, config_name: str = "default"):
        """Get RBS configuration by name"""
        config = await db.rbs_configs.find_one({"config_name": config_name})
        if config:
            # Convert MongoDB document to RBSConfig
            config.pop('_id', None)  # Remove MongoDB _id
            return RBSConfig(**config)
        else:
            # Return default config if not found
            return self.default_config
    
    async def calculate_team_avg_stats(self, team_name, all_team_stats, all_matches, with_referee=None, exclude_referee=None):
        """Calculate average stats for a team, optionally filtered by referee"""
        # Get all matches for this team
        team_matches = [m for m in all_matches if m['home_team'] == team_name or m['away_team'] == team_name]
        
        # Filter matches by referee if specified
        if with_referee:
            team_matches = [m for m in team_matches if m['referee'] == with_referee]
        elif exclude_referee:
            team_matches = [m for m in team_matches if m['referee'] != exclude_referee]
        
        if not team_matches:
            return None, 0
        
        # Get team stats for these matches and calculate averages
        team_stats_for_matches = []
        match_ids_for_team = [match['match_id'] for match in team_matches]
        
        # Get player stats for fouls_drawn and penalties_awarded aggregation
        player_stats = await db.player_stats.find({
            "match_id": {"$in": match_ids_for_team},
            "team_name": team_name
        }).to_list(10000)
        
        # Group player stats by match_id for aggregation
        player_stats_by_match = {}
        for pstat in player_stats:
            match_id = pstat['match_id']
            if match_id not in player_stats_by_match:
                player_stats_by_match[match_id] = []
            player_stats_by_match[match_id].append(pstat)
        
        for match in team_matches:
            match_stats = [s for s in all_team_stats if s['match_id'] == match['match_id'] and s['team_name'] == team_name]
            for stat in match_stats:
                # Get player stats for this match to aggregate xG, fouls_drawn, and penalties_awarded
                match_player_stats = player_stats_by_match.get(match['match_id'], [])
                match_xg = sum(ps.get('xg', 0) for ps in match_player_stats)
                match_fouls_drawn = sum(ps.get('fouls_drawn', 0) for ps in match_player_stats)
                match_penalties_awarded = sum(ps.get('penalty_attempts', 0) for ps in match_player_stats)
                
                # Override xG with aggregated value from player stats
                stat['xg'] = match_xg
                
                # Calculate xG difference (team xG - opponent xG) for this match
                opponent_name = match['away_team'] if match['home_team'] == team_name else match['home_team']
                opponent_stats = [s for s in all_team_stats if s['match_id'] == match['match_id'] and s['team_name'] == opponent_name]
                
                # Get opponent player stats for xG calculation
                opponent_player_stats = []
                for pstat in player_stats:
                    if pstat['match_id'] == match['match_id'] and pstat['team_name'] == opponent_name:
                        opponent_player_stats.append(pstat)
                
                opponent_xg = sum(ps.get('xg', 0) for ps in opponent_player_stats)
                stat['xg_difference'] = match_xg - opponent_xg
                
                # Rename fields to match new specification
                stat['fouls_committed'] = stat.get('fouls', 0)
                stat['possession_percentage'] = stat.get('possession_pct', 0)
                
                # Override with aggregated values if they exist, otherwise use team stat values
                stat['fouls_drawn'] = match_fouls_drawn if match_fouls_drawn > 0 else stat.get('fouls_drawn', 0)
                stat['penalties_awarded'] = match_penalties_awarded if match_penalties_awarded > 0 else stat.get('penalties_awarded', 0)
                
                team_stats_for_matches.append(stat)
        
        if not team_stats_for_matches:
            return None, 0
        
        # Calculate averages for required fields
        avg_stats = {}
        stat_fields = ['yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn', 'penalties_awarded', 'xg_difference', 'possession_percentage']
        
        for field in stat_fields:
            values = [s.get(field, 0) for s in team_stats_for_matches if s.get(field) is not None]
            avg_stats[field] = sum(values) / len(values) if values else 0
        
        return avg_stats, len(team_matches)
    
    async def calculate_rbs_for_team_referee(self, team_name, referee, all_team_stats, all_matches, config_name="default"):
        """Calculate RBS score for a specific team-referee combination using configurable weights"""
        # Get configuration
        config = await self.get_config(config_name)
        
        # Calculate average stats with this referee
        with_ref_stats, matches_with_ref = await self.calculate_team_avg_stats(
            team_name, all_team_stats, all_matches, with_referee=referee
        )
        
        # Calculate average stats with other referees (exclude this referee)
        without_ref_stats, matches_without_ref = await self.calculate_team_avg_stats(
            team_name, all_team_stats, all_matches, exclude_referee=referee
        )
        
        # Check minimum match requirement
        if not with_ref_stats or not without_ref_stats or matches_with_ref < config.confidence_threshold_low:
            return None
        
        # Calculate RBS using the new formula with configurable weights
        rbs_components = {}
        
        # Yellow cards (higher = worse for team, so multiply by -1)
        yellow_diff = with_ref_stats['yellow_cards'] - without_ref_stats['yellow_cards']
        rbs_components['yellow_cards'] = -yellow_diff * config.yellow_cards_weight
        
        # Red cards (higher = worse for team, so multiply by -1)
        red_diff = with_ref_stats['red_cards'] - without_ref_stats['red_cards']
        rbs_components['red_cards'] = -red_diff * config.red_cards_weight
        
        # Fouls committed (higher = worse for team, so multiply by -1)
        fouls_committed_diff = with_ref_stats['fouls_committed'] - without_ref_stats['fouls_committed']
        rbs_components['fouls_committed'] = -fouls_committed_diff * config.fouls_committed_weight
        
        # Fouls drawn (higher = better for team)
        fouls_drawn_diff = with_ref_stats['fouls_drawn'] - without_ref_stats['fouls_drawn']
        rbs_components['fouls_drawn'] = fouls_drawn_diff * config.fouls_drawn_weight
        
        # Penalties awarded (higher = better for team)
        penalties_diff = with_ref_stats['penalties_awarded'] - without_ref_stats['penalties_awarded']
        rbs_components['penalties_awarded'] = penalties_diff * config.penalties_awarded_weight
        
        # xG difference (higher = better for team)
        xg_diff = with_ref_stats['xg_difference'] - without_ref_stats['xg_difference']
        rbs_components['xg_difference'] = xg_diff * config.xg_difference_weight
        
        # Possession percentage (higher = better for team)
        possession_diff = with_ref_stats['possession_percentage'] - without_ref_stats['possession_percentage']
        rbs_components['possession_percentage'] = possession_diff * config.possession_percentage_weight
        
        # Sum all components to get raw RBS
        rbs_raw = sum(rbs_components.values())
        
        # Apply tanh normalization to get RBS between -1 and +1
        rbs_normalized = math.tanh(rbs_raw)
        
        # Calculate confidence based on configurable thresholds
        if matches_with_ref >= config.confidence_threshold_high:
            confidence = min(config.max_confidence, 70 + (matches_with_ref - config.confidence_threshold_high) * 2.5)
        elif matches_with_ref >= config.confidence_threshold_medium:
            confidence = 50 + (matches_with_ref - config.confidence_threshold_medium) * 4
        elif matches_with_ref >= config.confidence_threshold_low:
            confidence = 20 + (matches_with_ref - config.confidence_threshold_low) * 10
        else:
            confidence = matches_with_ref * 10
        
        confidence = max(config.min_confidence, min(config.max_confidence, confidence))
        confidence = round(confidence, 1)
        
        return {
            'team_name': team_name,
            'referee': referee,
            'rbs_score': round(rbs_normalized, 3),  # Return normalized score
            'rbs_raw': round(rbs_raw, 3),  # Also include raw score for debugging
            'matches_with_ref': matches_with_ref,
            'matches_without_ref': matches_without_ref,
            'confidence_level': confidence,
            'stats_breakdown': {k: round(v, 4) for k, v in rbs_components.items()},
            'config_used': config_name
        }

# Initialize RBS Calculator
rbs_calculator = RBSCalculator()

# Match Prediction Engine
class MatchPredictor:
    def __init__(self):
        self.default_config = PredictionConfig()
    
    async def get_config(self, config_name: str = "default"):
        """Get prediction configuration by name"""
        config = await db.prediction_configs.find_one({"config_name": config_name})
        if config:
            # Convert MongoDB document to PredictionConfig
            config.pop('_id', None)  # Remove MongoDB _id
            return PredictionConfig(**config)
        else:
            # Return default config if not found
            return self.default_config
    
    def calculate_match_probabilities(self, home_goals, away_goals):
        """
        Calculate match outcome probabilities using Poisson distribution
        
        Args:
            home_goals (float): Expected goals for home team
            away_goals (float): Expected goals for away team
            
        Returns:
            tuple: (home_win_prob, draw_prob, away_win_prob) as percentages
        """
        # Use actual predicted goals without modification
        home_lambda = home_goals
        away_lambda = away_goals
        
        # Handle edge case of zero goals in Poisson calculation
        if home_lambda <= 0 or away_lambda <= 0:
            # If either team has 0 predicted goals, calculate probabilities differently
            if home_lambda <= 0 and away_lambda <= 0:
                # Both teams predicted 0 goals - equal probability of all outcomes
                return 33.33, 33.33, 33.34
            elif home_lambda <= 0:
                # Home team predicted 0 goals - away team very likely to win
                return 5.0, 15.0, 80.0
            else:
                # Away team predicted 0 goals - home team very likely to win
                return 80.0, 15.0, 5.0
        
        # Calculate probabilities for different score combinations
        # We'll calculate up to a reasonable maximum (e.g., 10 goals each)
        max_goals = 10
        
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        for home_score in range(max_goals + 1):
            for away_score in range(max_goals + 1):
                # Probability of this exact score
                prob = poisson.pmf(home_score, home_lambda) * poisson.pmf(away_score, away_lambda)
                
                if home_score > away_score:
                    home_win_prob += prob
                elif home_score == away_score:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # Convert to percentages and ensure they sum to 100%
        total_prob = home_win_prob + draw_prob + away_win_prob
        
        if total_prob > 0:
            home_win_percent = (home_win_prob / total_prob) * 100
            draw_percent = (draw_prob / total_prob) * 100
            away_win_percent = (away_win_prob / total_prob) * 100
        else:
            # Fallback in case of calculation issues
            home_win_percent = 33.33
            draw_percent = 33.33
            away_win_percent = 33.34
        
        # Round to 2 decimal places
        home_win_percent = round(home_win_percent, 2)
        draw_percent = round(draw_percent, 2)
        away_win_percent = round(away_win_percent, 2)
        
        # Ensure they sum to exactly 100% by adjusting the largest probability
        total = home_win_percent + draw_percent + away_win_percent
        if total != 100.0:
            diff = 100.0 - total
            # Add the difference to the largest probability
            if home_win_percent >= draw_percent and home_win_percent >= away_win_percent:
                home_win_percent += diff
            elif draw_percent >= away_win_percent:
                draw_percent += diff
            else:
                away_win_percent += diff
            
            # Round again to ensure clean numbers
            home_win_percent = round(home_win_percent, 2)
            draw_percent = round(draw_percent, 2)
            away_win_percent = round(away_win_percent, 2)
        
        return home_win_percent, draw_percent, away_win_percent
    
    async def calculate_team_averages(self, team_name, is_home, exclude_opponent=None, season_filter=None):
        """Calculate comprehensive team averages with home/away context"""
        # Build query for team stats
        query = {
            "team_name": team_name,
            "is_home": is_home
        }
        
        # Get team stats
        team_stats = await db.team_stats.find(query).to_list(1000)
        
        if not team_stats:
            return None
        
        # Always create match_ids list
        match_ids = [stat['match_id'] for stat in team_stats]
        
        # Get corresponding matches to filter by season/opponent if needed
        if exclude_opponent or season_filter:
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
            # Update match_ids after filtering
            match_ids = [stat['match_id'] for stat in team_stats]
        
        if not team_stats:
            return None
        
        # Calculate comprehensive averages from properly calculated team stats
        total_matches = len(team_stats)
        averages = {
            'shots_total': sum(stat.get('shots_total', 0) for stat in team_stats) / total_matches,
            'shots_on_target': sum(stat.get('shots_on_target', 0) for stat in team_stats) / total_matches,
            'xg': sum(stat.get('xg', 0) for stat in team_stats) / total_matches,
            'fouls': sum(stat.get('fouls', 0) for stat in team_stats) / total_matches,
            'fouls_drawn': sum(stat.get('fouls_drawn', 0) for stat in team_stats) / total_matches,
            'penalties_awarded': sum(stat.get('penalties_awarded', 0) for stat in team_stats) / total_matches,
            'penalty_attempts': sum(stat.get('penalty_attempts', 0) for stat in team_stats) / total_matches,
            'penalty_goals': sum(stat.get('penalty_goals', 0) for stat in team_stats) / total_matches,
            'yellow_cards': sum(stat.get('yellow_cards', 0) for stat in team_stats) / total_matches,
            'red_cards': sum(stat.get('red_cards', 0) for stat in team_stats) / total_matches,
            'possession_pct': sum(stat.get('possession_pct', 0) for stat in team_stats) / total_matches,
            'possession_percentage': sum(stat.get('possession_pct', 0) for stat in team_stats) / total_matches,
            'fouls_committed': sum(stat.get('fouls', 0) for stat in team_stats) / total_matches,
            'goals': sum(stat.get('goals_scored', 0) for stat in team_stats) / total_matches,
            'goals_conceded': sum(stat.get('goals_conceded', 0) for stat in team_stats) / total_matches,
            'points': sum(stat.get('points_earned', 0) for stat in team_stats) / total_matches,
            'matches_count': total_matches,
            
            # Calculate penalty totals for correct conversion rate
            'penalty_goals_total': sum(stat.get('penalty_goals', 0) for stat in team_stats),
            'penalty_attempts_total': sum(stat.get('penalty_attempts', 0) for stat in team_stats),
            
            # Add comprehensive derived statistics using ONLY actual database values
            'xg_per_shot': sum(stat.get('xg_per_shot', 0) for stat in team_stats) / total_matches,
            'goals_per_xg': sum(stat.get('goals_per_xg', 0) for stat in team_stats) / total_matches,
            'shot_accuracy': sum(stat.get('shot_accuracy', 0) for stat in team_stats) / total_matches,
            'conversion_rate': sum(stat.get('conversion_rate', 0) for stat in team_stats) / total_matches,
            'penalty_conversion_rate': (
                sum(stat.get('penalty_goals', 0) for stat in team_stats) / 
                sum(stat.get('penalty_attempts', 0) for stat in team_stats) 
                if sum(stat.get('penalty_attempts', 0) for stat in team_stats) > 0 else 0
            ),
            'goal_difference': sum(stat.get('goal_difference', 0) for stat in team_stats) / total_matches,
            'clean_sheets': sum(stat.get('clean_sheet', 0) for stat in team_stats) / total_matches * 100,  # Convert to percentage
            'scoring_rate': sum(stat.get('scored_goals', 0) for stat in team_stats) / total_matches * 100,  # Convert to percentage
        }
        
        # Calculate additional derived metrics
        if averages['shots_total'] > 0:
            averages['shots_per_game'] = averages['shots_total']
            averages['shots_on_target_per_game'] = averages['shots_on_target']
        else:
            averages['shots_per_game'] = 0
            averages['shots_on_target_per_game'] = 0
        
        # Calculate PPG (Points Per Game) 
        averages['ppg'] = averages['points']
        averages['points_per_game'] = averages['points']  # Add for match prediction compatibility
        
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
    
    async def predict_match(self, home_team, away_team, referee_name, match_date=None, config_name="default"):
        """Enhanced prediction function using comprehensive team stats with configurable weights"""
        try:
            # Get configuration
            config = await self.get_config(config_name)
            
            # Get comprehensive team averages (home and away context)
            home_stats = await self.calculate_team_averages(home_team, is_home=True, exclude_opponent=away_team)
            away_stats = await self.calculate_team_averages(away_team, is_home=False, exclude_opponent=home_team)
            
            # Get defensive stats (what teams concede when playing home/away)
            home_defensive = await self.calculate_team_averages(home_team, is_home=True)
            away_defensive = await self.calculate_team_averages(away_team, is_home=False)
            
            if not home_stats or not away_stats:
                raise ValueError("Insufficient historical data for one or both teams")
            
            # Enhanced xG calculation using configurable weights
            
            # Method 1: Shot-based xG calculation
            home_shot_xg = home_stats['shots_total'] * home_stats['xg_per_shot']
            away_shot_xg = away_stats['shots_total'] * away_stats['xg_per_shot']
            
            # Method 2: Historical xG average
            home_hist_xg = home_stats['xg']
            away_hist_xg = away_stats['xg']
            
            # Method 3: Opponent defensive consideration
            home_vs_defense = home_stats['shots_total'] * (away_defensive['goals_conceded'] / away_defensive['shots_conceded'] if away_defensive.get('shots_conceded', 0) > 0 else 0.1)
            away_vs_defense = away_stats['shots_total'] * (home_defensive['goals_conceded'] / home_defensive.get('shots_conceded', 10) if home_defensive.get('shots_conceded', 0) > 0 else 0.1)
            
            # Combine methods with configurable weights
            home_base_xg = (
                home_shot_xg * config.xg_shot_based_weight + 
                home_hist_xg * config.xg_historical_weight + 
                home_vs_defense * config.xg_opponent_defense_weight
            )
            away_base_xg = (
                away_shot_xg * config.xg_shot_based_weight + 
                away_hist_xg * config.xg_historical_weight + 
                away_vs_defense * config.xg_opponent_defense_weight
            )
            
            # Factor in additional team stats with configurable weights
            
            # Possession adjustment (configurable rate)
            possession_factor_home = 1 + ((home_stats['possession_pct'] - 50) * config.possession_adjustment_per_percent)
            possession_factor_away = 1 + ((away_stats['possession_pct'] - 50) * config.possession_adjustment_per_percent)
            
            home_base_xg *= possession_factor_home
            away_base_xg *= possession_factor_away
            
            # Fouls drawn factor (using actual database values without bounds)
            fouls_factor_home = 1 + (home_stats['fouls_drawn'] - config.fouls_drawn_baseline) * config.fouls_drawn_factor
            fouls_factor_away = 1 + (away_stats['fouls_drawn'] - config.fouls_drawn_baseline) * config.fouls_drawn_factor
            
            home_base_xg *= fouls_factor_home
            away_base_xg *= fouls_factor_away
            
            # Penalties factor (configurable penalty xG value)
            home_penalty_xg = home_stats['penalties_awarded'] * config.penalty_xg_value * home_stats['penalty_conversion_rate']
            away_penalty_xg = away_stats['penalties_awarded'] * config.penalty_xg_value * away_stats['penalty_conversion_rate']
            
            home_base_xg += home_penalty_xg
            away_base_xg += away_penalty_xg
            
            # Get PPG for both teams (use calculated PPG from team averages)
            home_ppg = home_stats['points_per_game']
            away_ppg = away_stats['points_per_game']
            
            # Enhanced PPG adjustment (configurable factor)
            ppg_diff = home_ppg - away_ppg
            ppg_adjustment = ppg_diff * config.ppg_adjustment_factor
            
            # Apply PPG adjustment
            home_adjusted_xg = home_base_xg + ppg_adjustment
            away_adjusted_xg = away_base_xg - ppg_adjustment
            
            # Get referee bias with configurable scaling
            home_rbs, home_rbs_confidence = await self.get_referee_bias(home_team, referee_name)
            away_rbs, away_rbs_confidence = await self.get_referee_bias(away_team, referee_name)
            
            # Apply referee bias (configurable scaling)
            home_ref_adjustment = home_rbs * config.rbs_scaling_factor
            away_ref_adjustment = away_rbs * config.rbs_scaling_factor
            
            # Final xG predictions using actual calculated values
            final_home_xg = home_adjusted_xg + home_ref_adjustment
            final_away_xg = away_adjusted_xg + away_ref_adjustment
            
            # Goal prediction using actual conversion rates from database
            home_conversion = home_stats['goals_per_xg']
            away_conversion = away_stats['goals_per_xg']
            
            predicted_home_goals = final_home_xg * home_conversion
            predicted_away_goals = final_away_xg * away_conversion
            
            # Round to reasonable precision
            predicted_home_goals = round(predicted_home_goals, 2)
            predicted_away_goals = round(predicted_away_goals, 2)
            final_home_xg = round(final_home_xg, 2)
            final_away_xg = round(final_away_xg, 2)
            
            # Comprehensive prediction breakdown with config values
            prediction_breakdown = {
                "home_base_xg": round(home_base_xg, 2),
                "away_base_xg": round(away_base_xg, 2),
                "ppg_adjustment": round(ppg_adjustment, 2),
                "home_ref_adjustment": round(home_ref_adjustment, 2),
                "away_ref_adjustment": round(away_ref_adjustment, 2),
                
                # Core team statistics used in calculation
                "home_shots_avg": round(home_stats['shots_total'], 1),
                "away_shots_avg": round(away_stats['shots_total'], 1),
                "home_xg_per_shot": round(home_stats['xg_per_shot'], 3),
                "away_xg_per_shot": round(away_stats['xg_per_shot'], 3),
                "home_possession_avg": round(home_stats['possession_pct'], 1),
                "away_possession_avg": round(away_stats['possession_pct'], 1),
                "home_fouls_drawn_avg": round(home_stats['fouls_drawn'], 1),
                "away_fouls_drawn_avg": round(away_stats['fouls_drawn'], 1),
                "home_penalties_avg": round(home_stats['penalties_awarded'], 3),
                "away_penalties_avg": round(away_stats['penalties_awarded'], 3),
                "home_penalty_conversion": round(home_stats['penalty_conversion_rate'], 3),
                "away_penalty_conversion": round(away_stats['penalty_conversion_rate'], 3),
                "home_penalty_goals_avg": round(home_stats['penalty_goals'], 3),
                "away_penalty_goals_avg": round(away_stats['penalty_goals'], 3),
                "home_goals_avg": round(home_stats['goals'], 2),
                "away_goals_avg": round(away_stats['goals'], 2),
                "home_conversion_rate": round(home_conversion, 2),
                "away_conversion_rate": round(away_conversion, 2),
                
                # Adjustment factors used in calculation
                "home_possession_factor": round(possession_factor_home, 3),
                "away_possession_factor": round(possession_factor_away, 3),
                "home_fouls_factor": round(fouls_factor_home, 3),
                "away_fouls_factor": round(fouls_factor_away, 3),
                "home_penalty_xg": round(home_penalty_xg, 3),
                "away_penalty_xg": round(away_penalty_xg, 3),
                "home_ppg": round(home_ppg, 2),
                "away_ppg": round(away_ppg, 2),
                
                "config_used": config_name
            }
            
            # Confidence calculation using actual match data
            overall_confidence = (home_stats['matches_count'] + away_stats['matches_count']) / 2 * config.confidence_matches_multiplier
            
            confidence_factors = {
                "home_matches_count": home_stats['matches_count'],
                "away_matches_count": away_stats['matches_count'],
                "home_rbs_confidence": home_rbs_confidence,
                "away_rbs_confidence": away_rbs_confidence,
                "home_ppg": round(home_ppg, 2),
                "away_ppg": round(away_ppg, 2),
                "home_rbs_score": round(home_rbs, 3),
                "away_rbs_score": round(away_rbs, 3),
                "overall_confidence": round(overall_confidence, 1),
                "config_used": config_name,
                "data_quality": {
                    "home_shots_data": "good" if home_stats['shots_total'] > 0 else "estimated",
                    "away_shots_data": "good" if away_stats['shots_total'] > 0 else "estimated",
                    "home_xg_data": "good" if home_stats['xg'] > 0 else "limited",
                    "away_xg_data": "good" if away_stats['xg'] > 0 else "limited"
                }
            }
            
            # Calculate match outcome probabilities using Poisson distribution
            home_win_prob, draw_prob, away_win_prob = self.calculate_match_probabilities(
                predicted_home_goals, predicted_away_goals
            )
            
            return MatchPredictionResponse(
                success=True,
                home_team=home_team,
                away_team=away_team,
                referee=referee_name,
                predicted_home_goals=predicted_home_goals,
                predicted_away_goals=predicted_away_goals,
                home_xg=final_home_xg,
                away_xg=final_away_xg,
                home_win_probability=home_win_prob,
                draw_probability=draw_prob,
                away_win_probability=away_win_prob,
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
                home_win_probability=0.0,
                draw_probability=0.0,
                away_win_probability=0.0,
                prediction_breakdown={"error": str(e), "config_used": config_name},
                confidence_factors={"error": "Insufficient data", "config_used": config_name}
            )

# Initialize Match Predictor
match_predictor = MatchPredictor()

# Regression Analysis Engine
class RegressionAnalyzer:
    def __init__(self):
        # All statistics available for analysis - includes all RBS and Match Predictor variables
        self.available_stats = [
            # Basic team stats (used in RBS calculation)
            'yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn',
            'penalties_awarded', 'xg_difference', 'possession_percentage',
            'xg', 'shots_total', 'shots_on_target',
            
            # Advanced derived stats used in match prediction
            'goals', 'goals_conceded', 'points_per_game',
            'xg_per_shot', 'goals_per_xg', 'shot_accuracy', 
            'conversion_rate', 'penalty_conversion_rate',
            'penalty_attempts', 'penalty_goals',
            
            # Additional RBS and predictor variables
            'rbs_score', 'home_advantage', 'team_quality_rating',
            'defensive_rating', 'attacking_rating', 'form_rating',
            'head_to_head_record', 'recent_performance',
            
            # Context variables
            'is_home', 'season_progress', 'days_rest',
            'goal_difference', 'clean_sheets_rate', 'scoring_rate'
        ]
        
        # RBS-specific statistics for formula optimization  
        self.rbs_variables = [
            'yellow_cards', 'red_cards', 'fouls_committed', 'fouls_drawn',
            'penalties_awarded', 'xg_difference', 'possession_percentage'
        ]
        
        # Match Predictor-specific statistics
        self.predictor_variables = [
            'xg', 'shots_total', 'shots_on_target', 'xg_per_shot',
            'goals_per_xg', 'shot_accuracy', 'conversion_rate',
            'possession_percentage', 'fouls_drawn', 'penalties_awarded',
            'penalty_conversion_rate', 'points_per_game', 'rbs_score'
        ]
    
    def _safe_float_conversion(self, value):
        """Safely convert value to float, handling NaN and infinity"""
        try:
            if pd.isna(value) or np.isinf(value):
                return 0.0
            return float(value)
        except (ValueError, TypeError, OverflowError):
            return 0.0
    
    def _safe_dict_conversion(self, input_dict):
        """Safely convert dictionary values to floats"""
        return {key: self._safe_float_conversion(value) for key, value in input_dict.items()}
    
    async def prepare_match_data(self, include_rbs=True):
        """Prepare match data for regression analysis with comprehensive variables"""
        try:
            # Get all matches and team stats
            matches = await db.matches.find().to_list(10000)
            team_stats = await db.team_stats.find().to_list(10000)
            
            # Get RBS results if requested
            rbs_results = {}
            if include_rbs:
                rbs_data = await db.rbs_results.find().to_list(10000)
                for rbs in rbs_data:
                    key = f"{rbs['team_name']}_{rbs['referee']}"
                    rbs_results[key] = rbs['rbs_score']
            
            # Get player stats for additional calculations
            player_stats = await db.player_stats.find().to_list(50000)
            
            # Create a comprehensive dataset
            match_data = []
            
            for match in matches:
                # Get stats for both teams
                home_stats = [s for s in team_stats if s['match_id'] == match['match_id'] and s['team_name'] == match['home_team'] and s['is_home']]
                away_stats = [s for s in team_stats if s['match_id'] == match['match_id'] and s['team_name'] == match['away_team'] and not s['is_home']]
                
                if home_stats and away_stats:
                    home_stat = home_stats[0]
                    away_stat = away_stats[0]
                    
                    # Get player stats for this match
                    home_players = [p for p in player_stats if p['match_id'] == match['match_id'] and p['team_name'] == match['home_team']]
                    away_players = [p for p in player_stats if p['match_id'] == match['match_id'] and p['team_name'] == match['away_team']]
                    
                    # Calculate aggregated player stats
                    home_player_xg = sum(p.get('xg', 0) for p in home_players)
                    away_player_xg = sum(p.get('xg', 0) for p in away_players)
                    home_fouls_drawn_players = sum(p.get('fouls_drawn', 0) for p in home_players)
                    away_fouls_drawn_players = sum(p.get('fouls_drawn', 0) for p in away_players)
                    home_penalties_players = sum(p.get('penalty_attempts', 0) for p in home_players)
                    away_penalties_players = sum(p.get('penalty_attempts', 0) for p in away_players)
                    
                    # Use player stats for xG if available, otherwise team stats
                    home_xg = home_player_xg if home_player_xg > 0 else home_stat.get('xg', 0)
                    away_xg = away_player_xg if away_player_xg > 0 else away_stat.get('xg', 0)
                    
                    # Calculate xG difference
                    home_xg_diff = home_xg - away_xg
                    away_xg_diff = away_xg - home_xg
                    
                    # Calculate match results and points
                    home_score = match['home_score']
                    away_score = match['away_score']
                    
                    if home_score > away_score:
                        home_result = 'W'
                        away_result = 'L'
                        home_points = 3
                        away_points = 0
                    elif home_score < away_score:
                        home_result = 'L'
                        away_result = 'W'
                        home_points = 0
                        away_points = 3
                    else:
                        home_result = 'D'
                        away_result = 'D'
                        home_points = 1
                        away_points = 1
                    
                    # Get RBS scores
                    home_rbs_key = f"{match['home_team']}_{match['referee']}"
                    away_rbs_key = f"{match['away_team']}_{match['referee']}"
                    home_rbs = rbs_results.get(home_rbs_key, 0.0)
                    away_rbs = rbs_results.get(away_rbs_key, 0.0)
                    
                    # Calculate additional advanced metrics
                    home_fouls_drawn = home_fouls_drawn_players if home_fouls_drawn_players > 0 else home_stat.get('fouls_drawn', 0)
                    away_fouls_drawn = away_fouls_drawn_players if away_fouls_drawn_players > 0 else away_stat.get('fouls_drawn', 0)
                    home_penalties = home_penalties_players if home_penalties_players > 0 else home_stat.get('penalties_awarded', 0)
                    away_penalties = away_penalties_players if away_penalties_players > 0 else away_stat.get('penalties_awarded', 0)
                    
                    # Add home team data
                    home_data = {
                        'team': match['home_team'],
                        'opponent': match['away_team'],
                        'referee': match['referee'],
                        'match_result': home_result,
                        'points_per_game': home_points,
                        'season': match.get('season', 'Unknown'),
                        'competition': match.get('competition', 'Unknown'),
                        
                        # Basic RBS variables
                        'yellow_cards': home_stat.get('yellow_cards', 0),
                        'red_cards': home_stat.get('red_cards', 0),
                        'fouls_committed': home_stat.get('fouls', 0),
                        'fouls_drawn': home_fouls_drawn,
                        'penalties_awarded': home_penalties,
                        'xg_difference': home_xg_diff,
                        'possession_percentage': home_stat.get('possession_pct', 0),
                        
                        # Match Predictor variables
                        'xg': home_xg,
                        'shots_total': home_stat.get('shots_total', 0),
                        'shots_on_target': home_stat.get('shots_on_target', 0),
                        'is_home': True,
                        
                        # Advanced derived stats using ONLY actual database values
                        'goals': home_score,
                        'goals_conceded': away_score,
                        'xg_per_shot': home_xg / home_stat.get('shots_total') if home_stat.get('shots_total', 0) > 0 else 0,
                        'goals_per_xg': home_score / home_xg if home_xg > 0 else 0,
                        'shot_accuracy': home_stat.get('shots_on_target', 0) / home_stat.get('shots_total') if home_stat.get('shots_total', 0) > 0 else 0,
                        'conversion_rate': home_score / home_stat.get('shots_total') if home_stat.get('shots_total', 0) > 0 else 0,  # Fixed: goals per total shots
                        'penalty_attempts': home_stat.get('penalty_attempts', 0),
                        'penalty_goals': home_stat.get('penalty_goals', 0),
                        'penalty_conversion_rate': home_stat.get('penalty_goals', 0) / home_stat.get('penalty_attempts') if home_stat.get('penalty_attempts', 0) > 0 else 0,
                        
                        # Additional variables for comprehensive analysis
                        'rbs_score': home_rbs,
                        'home_advantage': 1,  # Home team gets advantage
                        'goal_difference': home_score - away_score,
                        'clean_sheets_rate': 1 if away_score == 0 else 0,
                        'scoring_rate': 1 if home_score > 0 else 0,
                        
                        # Team quality ratings (derived from averages)
                        'team_quality_rating': home_points,  # Simple proxy for team quality
                        'attacking_rating': home_xg,
                        'defensive_rating': max(0, 3 - away_xg),  # Inverse of opponent xG
                        'form_rating': home_points,  # Will be enhanced with recent form
                    }
                    
                    # Add away team data
                    away_data = {
                        'team': match['away_team'],
                        'opponent': match['home_team'],
                        'referee': match['referee'],
                        'match_result': away_result,
                        'points_per_game': away_points,
                        'season': match.get('season', 'Unknown'),
                        'competition': match.get('competition', 'Unknown'),
                        
                        # Basic RBS variables
                        'yellow_cards': away_stat.get('yellow_cards', 0),
                        'red_cards': away_stat.get('red_cards', 0),
                        'fouls_committed': away_stat.get('fouls', 0),
                        'fouls_drawn': away_fouls_drawn,
                        'penalties_awarded': away_penalties,
                        'xg_difference': away_xg_diff,
                        'possession_percentage': away_stat.get('possession_pct', 0),
                        
                        # Match Predictor variables
                        'xg': away_xg,
                        'shots_total': away_stat.get('shots_total', 0),
                        'shots_on_target': away_stat.get('shots_on_target', 0),
                        'is_home': False,
                        
                        # Advanced derived stats using ONLY actual database values
                        'goals': away_score,
                        'goals_conceded': home_score,
                        'xg_per_shot': away_xg / away_stat.get('shots_total') if away_stat.get('shots_total', 0) > 0 else 0,
                        'goals_per_xg': away_score / away_xg if away_xg > 0 else 0,
                        'shot_accuracy': away_stat.get('shots_on_target', 0) / away_stat.get('shots_total') if away_stat.get('shots_total', 0) > 0 else 0,
                        'conversion_rate': away_score / away_stat.get('shots_total') if away_stat.get('shots_total', 0) > 0 else 0,  # Fixed: goals per total shots
                        'penalty_attempts': away_stat.get('penalty_attempts', 0),
                        'penalty_goals': away_stat.get('penalty_goals', 0),
                        'penalty_conversion_rate': away_stat.get('penalty_goals', 0) / away_stat.get('penalty_attempts') if away_stat.get('penalty_attempts', 0) > 0 else 0,
                        
                        # Additional variables for comprehensive analysis
                        'rbs_score': away_rbs,
                        'home_advantage': 0,  # Away team gets no home advantage
                        'goal_difference': away_score - home_score,
                        'clean_sheets_rate': 1 if home_score == 0 else 0,
                        'scoring_rate': 1 if away_score > 0 else 0,
                        
                        # Team quality ratings (derived from averages)
                        'team_quality_rating': away_points,  # Simple proxy for team quality
                        'attacking_rating': away_xg,
                        'defensive_rating': max(0, 3 - home_xg),  # Inverse of opponent xG
                        'form_rating': away_points,  # Will be enhanced with recent form
                    }
                    
                    match_data.append(home_data)
                    match_data.append(away_data)
            
            return pd.DataFrame(match_data)
        
        except Exception as e:
            raise Exception(f"Error preparing match data: {str(e)}")
    
    def run_regression(self, df, selected_stats, target='points_per_game', test_size=0.2, random_state=42):
        """Run regression analysis on match data"""
        try:
            # Validate inputs
            if df.empty:
                raise ValueError("DataFrame is empty")
            
            # Check if selected stats exist in DataFrame
            missing_stats = [stat for stat in selected_stats if stat not in df.columns]
            if missing_stats:
                raise ValueError(f"Missing statistics in data: {missing_stats}")
            
            if target not in df.columns:
                raise ValueError(f"Target '{target}' not found in data")
            
            # Prepare features and target
            X = df[selected_stats].copy()
            y = df[target].copy()
            
            # Remove rows with missing values
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
            
            # Replace any infinity values with NaN and then drop
            X = X.replace([np.inf, -np.inf], np.nan)
            y = y.replace([np.inf, -np.inf], np.nan)
            
            # Remove any remaining NaN values
            mask = ~(X.isnull().any(axis=1) | y.isnull())
            X = X[mask]
            y = y[mask]
            
            if len(X) == 0:
                raise ValueError("No valid data remaining after removing missing values")
            
            sample_size = len(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state
            )
            
            results = {}
            
            if target == 'points_per_game':
                # Linear regression for points per game
                model = LinearRegression()
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                r2 = r2_score(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                # Prepare results
                results = {
                    'model_type': 'Linear Regression',
                    'coefficients': self._safe_dict_conversion({stat: coef for stat, coef in zip(selected_stats, model.coef_)}),
                    'intercept': self._safe_float_conversion(model.intercept_),
                    'r2_score': self._safe_float_conversion(r2),
                    'mse': self._safe_float_conversion(mse),
                    'rmse': self._safe_float_conversion(rmse),
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'feature_importance': self._safe_dict_conversion({
                        stat: abs(coef) for stat, coef in zip(selected_stats, model.coef_)
                    })
                }
                
            elif target == 'match_result':
                # Random Forest for match result classification
                model = RandomForestClassifier(n_estimators=100, random_state=random_state)
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Get classification report
                class_report = classification_report(y_test, y_pred, output_dict=True)
                
                # Feature importance
                feature_importance = self._safe_dict_conversion({
                    stat: importance 
                    for stat, importance in zip(selected_stats, model.feature_importances_)
                })
                
                results = {
                    'model_type': 'Random Forest Classifier',
                    'classification_report': class_report,
                    'feature_importance': feature_importance,
                    'accuracy': self._safe_float_conversion(class_report.get('accuracy', 0)),
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'classes': list(model.classes_)
                }
            
            else:
                raise ValueError(f"Unsupported target: {target}")
            
            return {
                'success': True,
                'target': target,
                'selected_stats': selected_stats,
                'sample_size': sample_size,
                'model_type': results['model_type'],
                'results': results,
                'message': f"Regression analysis completed successfully for {target}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'target': target,
                'selected_stats': selected_stats,
                'sample_size': 0,
                'model_type': 'N/A',
                'results': {},
                'message': f"Error in regression analysis: {str(e)}"
            }
    
    async def analyze_rbs_formula_optimization(self):
        """Analyze RBS formula variables for optimization"""
        try:
            df = await self.prepare_match_data(include_rbs=True)
            
            if df.empty:
                raise ValueError("No match data available")
            
            # Analyze RBS variables against match outcomes
            results = {}
            
            # Test current RBS variables against points_per_game
            rbs_analysis = self.run_regression(
                df=df,
                selected_stats=self.rbs_variables,
                target='points_per_game'
            )
            
            results['rbs_vs_points'] = rbs_analysis
            
            # Test individual RBS variable importance
            individual_importance = {}
            for var in self.rbs_variables:
                single_var_analysis = self.run_regression(
                    df=df,
                    selected_stats=[var],
                    target='points_per_game'
                )
                if single_var_analysis['success']:
                    individual_importance[var] = {
                        'r2_score': single_var_analysis['results'].get('r2_score', 0),
                        'coefficient': single_var_analysis['results'].get('coefficients', {}).get(var, 0)
                    }
            
            results['individual_variable_importance'] = individual_importance
            
            # Calculate correlation matrix for RBS variables
            rbs_df = df[self.rbs_variables + ['points_per_game']].copy()
            correlation_matrix = rbs_df.corr()['points_per_game'].to_dict()
            results['correlations_with_points'] = correlation_matrix
            
            # Suggest optimal weights based on analysis
            if rbs_analysis['success'] and 'coefficients' in rbs_analysis['results']:
                coefficients = rbs_analysis['results']['coefficients']
                
                # Normalize coefficients to suggest weights (keeping sign information)
                total_abs_coef = sum(abs(coef) for coef in coefficients.values())
                
                suggested_weights = {}
                if total_abs_coef > 0:
                    for var, coef in coefficients.items():
                        # Preserve sign and scale to reasonable weight range (0.1 to 1.0)
                        normalized_weight = abs(coef) / total_abs_coef
                        suggested_weight = max(0.1, min(1.0, normalized_weight * 5))  # Scale to 0.1-1.0 range
                        suggested_weights[var] = round(suggested_weight, 2)
                
                results['suggested_rbs_weights'] = suggested_weights
            
            return {
                'success': True,
                'analysis_type': 'RBS Formula Optimization',
                'rbs_variables_analyzed': self.rbs_variables,
                'sample_size': len(df),
                'results': results,
                'recommendations': self._generate_rbs_recommendations(results),
                'message': 'RBS formula optimization analysis completed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis_type': 'RBS Formula Optimization',
                'results': {},
                'message': f"Error in RBS optimization analysis: {str(e)}"
            }
    
    async def analyze_match_predictor_optimization(self):
        """Analyze Match Predictor variables for optimization"""
        try:
            df = await self.prepare_match_data(include_rbs=True)
            
            if df.empty:
                raise ValueError("No match data available")
            
            results = {}
            
            # Test current predictor variables against points_per_game
            predictor_analysis = self.run_regression(
                df=df,
                selected_stats=self.predictor_variables,
                target='points_per_game'
            )
            
            results['predictor_vs_points'] = predictor_analysis
            
            # Test against match results (classification)
            predictor_classification = self.run_regression(
                df=df,
                selected_stats=self.predictor_variables,
                target='match_result'
            )
            
            results['predictor_vs_results'] = predictor_classification
            
            # Analyze xG-related variables specifically
            xg_variables = ['xg', 'xg_per_shot', 'goals_per_xg', 'shots_total', 'shots_on_target']
            xg_analysis = self.run_regression(
                df=df,
                selected_stats=xg_variables,
                target='points_per_game'
            )
            
            results['xg_analysis'] = xg_analysis
            
            # Test importance of RBS in predictions
            if 'rbs_score' in df.columns:
                rbs_predictor_analysis = self.run_regression(
                    df=df,
                    selected_stats=['rbs_score', 'xg', 'possession_percentage', 'shots_total'],
                    target='points_per_game'
                )
                results['rbs_in_prediction'] = rbs_predictor_analysis
            
            # Calculate feature importance rankings
            if predictor_analysis['success'] and 'coefficients' in predictor_analysis['results']:
                coefficients = predictor_analysis['results']['coefficients']
                
                # Rank variables by absolute coefficient value
                ranked_importance = sorted(
                    coefficients.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
                
                results['variable_importance_ranking'] = ranked_importance
            
            return {
                'success': True,
                'analysis_type': 'Match Predictor Optimization',
                'predictor_variables_analyzed': self.predictor_variables,
                'sample_size': len(df),
                'results': results,
                'recommendations': self._generate_predictor_recommendations(results),
                'message': 'Match predictor optimization analysis completed successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis_type': 'Match Predictor Optimization',
                'results': {},
                'message': f"Error in predictor optimization analysis: {str(e)}"
            }
    
    def _generate_rbs_recommendations(self, analysis_results):
        """Generate recommendations for RBS formula optimization"""
        recommendations = []
        
        if 'suggested_rbs_weights' in analysis_results:
            weights = analysis_results['suggested_rbs_weights']
            recommendations.append({
                'type': 'weight_optimization',
                'recommendation': 'Update RBS formula weights based on statistical significance',
                'details': weights,
                'priority': 'high'
            })
        
        if 'individual_variable_importance' in analysis_results:
            importance = analysis_results['individual_variable_importance']
            
            # Find variables with negative correlation (bad for team performance)
            negative_vars = [var for var, data in importance.items() 
                           if data.get('coefficient', 0) < 0]
            
            if negative_vars:
                recommendations.append({
                    'type': 'negative_correlation_confirmed',
                    'recommendation': 'These variables correctly show negative impact on team performance',
                    'details': negative_vars,
                    'priority': 'medium'
                })
        
        # Recommendation to maintain tanh normalization
        recommendations.append({
            'type': 'normalization',
            'recommendation': 'Continue using tanh normalization to keep RBS between -1 and +1',
            'details': 'Tanh normalization provides interpretable scores and prevents extreme values',
            'priority': 'high'
        })
        
        return recommendations
    
    def _generate_predictor_recommendations(self, analysis_results):
        """Generate recommendations for Match Predictor optimization"""
        recommendations = []
        
        if 'variable_importance_ranking' in analysis_results:
            ranking = analysis_results['variable_importance_ranking']
            top_variables = ranking[:5]  # Top 5 most important
            
            recommendations.append({
                'type': 'feature_importance',
                'recommendation': 'Focus on these most predictive variables',
                'details': {var: coef for var, coef in top_variables},
                'priority': 'high'
            })
        
        if 'xg_analysis' in analysis_results and analysis_results['xg_analysis']['success']:
            xg_r2 = analysis_results['xg_analysis']['results'].get('r2_score', 0)
            recommendations.append({
                'type': 'xg_effectiveness',
                'recommendation': f'xG-related variables explain {xg_r2:.1%} of performance variance',
                'details': f'R² score: {xg_r2:.3f}',
                'priority': 'medium'
            })
        
        if 'rbs_in_prediction' in analysis_results and analysis_results['rbs_in_prediction']['success']:
            rbs_coef = analysis_results['rbs_in_prediction']['results'].get('coefficients', {}).get('rbs_score', 0)
            recommendations.append({
                'type': 'rbs_integration',
                'recommendation': f'RBS shows {"positive" if rbs_coef > 0 else "negative"} correlation with team performance',
                'details': f'RBS coefficient: {rbs_coef:.3f}',
                'priority': 'high'
            })
        
        return recommendations

# Initialize Regression Analyzer
regression_analyzer = RegressionAnalyzer()

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
                match_date=str(row['match_date']),
                dataset_name="default"  # Default dataset for single uploads
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
                xg=safe_float(row.get('xg', 0)),
                dataset_name="default"  # Default dataset for single uploads
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
                    penalty_goals=safe_int(row.get('penalty_goals', 0)),
                    dataset_name="default"  # Default dataset for single uploads
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

# Multi-Dataset Upload Endpoints

@api_router.post("/datasets", response_model=DatasetListResponse)
async def list_datasets():
    """Get list of all datasets with their record counts"""
    try:
        # Get unique dataset names from matches collection
        datasets_pipeline = [
            {"$group": {
                "_id": "$dataset_name",
                "matches_count": {"$sum": 1}
            }}
        ]
        matches_data = await db.matches.aggregate(datasets_pipeline).to_list(1000)
        
        # Get team stats counts
        team_stats_pipeline = [
            {"$group": {
                "_id": "$dataset_name", 
                "team_stats_count": {"$sum": 1}
            }}
        ]
        team_stats_data = await db.team_stats.aggregate(team_stats_pipeline).to_list(1000)
        
        # Get player stats counts
        player_stats_pipeline = [
            {"$group": {
                "_id": "$dataset_name",
                "player_stats_count": {"$sum": 1}
            }}
        ]
        player_stats_data = await db.player_stats.aggregate(player_stats_pipeline).to_list(1000)
        
        # Combine data by dataset name
        datasets_dict = {}
        
        # Add matches data
        for item in matches_data:
            dataset_name = item["_id"]
            datasets_dict[dataset_name] = {
                "dataset_name": dataset_name,
                "matches_count": item["matches_count"],
                "team_stats_count": 0,
                "player_stats_count": 0,
                "created_at": datetime.now().isoformat()
            }
        
        # Add team stats data
        for item in team_stats_data:
            dataset_name = item["_id"]
            if dataset_name in datasets_dict:
                datasets_dict[dataset_name]["team_stats_count"] = item["team_stats_count"]
        
        # Add player stats data
        for item in player_stats_data:
            dataset_name = item["_id"]
            if dataset_name in datasets_dict:
                datasets_dict[dataset_name]["player_stats_count"] = item["player_stats_count"]
        
        datasets = [DatasetInfo(**data) for data in datasets_dict.values()]
        
        return DatasetListResponse(
            success=True,
            datasets=datasets
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")

@api_router.delete("/datasets/{dataset_name}", response_model=DatasetDeleteResponse)
async def delete_dataset(dataset_name: str):
    """Delete a specific dataset and all its records"""
    try:
        # Check if dataset exists
        matches_count = await db.matches.count_documents({"dataset_name": dataset_name})
        if matches_count == 0:
            raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
        
        # Delete all records for this dataset
        matches_deleted = await db.matches.delete_many({"dataset_name": dataset_name})
        team_stats_deleted = await db.team_stats.delete_many({"dataset_name": dataset_name})
        player_stats_deleted = await db.player_stats.delete_many({"dataset_name": dataset_name})
        rbs_deleted = await db.rbs_results.delete_many({"dataset_name": dataset_name}) if hasattr(db, 'rbs_results') else None
        
        total_deleted = (
            matches_deleted.deleted_count + 
            team_stats_deleted.deleted_count + 
            player_stats_deleted.deleted_count +
            (rbs_deleted.deleted_count if rbs_deleted else 0)
        )
        
        return DatasetDeleteResponse(
            success=True,
            message=f"Successfully deleted dataset '{dataset_name}' with all associated records",
            records_deleted=total_deleted
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting dataset: {str(e)}")

@api_router.post("/upload/multi-dataset")
async def upload_multi_dataset(files: List[UploadFile] = File(...), dataset_names: List[str] = []):
    """Upload multiple datasets (sets of 3 files each) with custom names"""
    try:
        if len(files) % 3 != 0:
            raise HTTPException(
                status_code=400, 
                detail="Files must be provided in sets of 3 (matches.csv, team_stats.csv, player_stats.csv)"
            )
        
        num_datasets = len(files) // 3
        if len(dataset_names) != num_datasets:
            raise HTTPException(
                status_code=400,
                detail=f"Must provide exactly {num_datasets} dataset names for {num_datasets} datasets"
            )
        
        # Check for duplicate dataset names in request
        if len(set(dataset_names)) != len(dataset_names):
            raise HTTPException(status_code=400, detail="Dataset names must be unique")
        
        # Check if any dataset names already exist
        for dataset_name in dataset_names:
            existing_count = await db.matches.count_documents({"dataset_name": dataset_name})
            if existing_count > 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Dataset '{dataset_name}' already exists. Please choose a different name."
                )
        
        # Process each dataset (group of 3 files)
        results = []
        total_records = 0
        
        for i in range(num_datasets):
            dataset_name = dataset_names[i]
            start_idx = i * 3
            dataset_files = files[start_idx:start_idx + 3]
            
            # Determine file types based on content/filename patterns
            matches_file = None
            team_stats_file = None
            player_stats_file = None
            
            for file in dataset_files:
                filename = file.filename.lower()
                content = await file.read()
                await file.seek(0)  # Reset file pointer
                
                # Determine file type based on filename or content
                if 'match' in filename:
                    matches_file = file
                elif 'team' in filename:
                    team_stats_file = file
                elif 'player' in filename:
                    player_stats_file = file
                else:
                    # Try to determine by CSV headers
                    df_sample = pd.read_csv(io.StringIO(content.decode('utf-8')), nrows=1)
                    columns = set(df_sample.columns.str.lower())
                    
                    if 'referee' in columns and 'home_team' in columns:
                        matches_file = file
                    elif 'team_name' in columns and 'yellow_cards' in columns:
                        team_stats_file = file
                    elif 'player_name' in columns and 'goals' in columns:
                        player_stats_file = file
            
            if not all([matches_file, team_stats_file, player_stats_file]):
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not identify all three file types for dataset '{dataset_name}'. Expected: matches, team_stats, player_stats files."
                )
            
            # Process matches file
            matches_content = await matches_file.read()
            matches_df = pd.read_csv(io.StringIO(matches_content.decode('utf-8')))
            matches_df = matches_df.fillna({
                'home_score': 0, 'away_score': 0, 'result': 'Unknown',
                'season': 'Unknown', 'competition': 'Unknown', 'match_date': 'Unknown'
            })
            
            matches = []
            for _, row in matches_df.iterrows():
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
                    match_date=str(row['match_date']),
                    dataset_name=dataset_name
                )
                matches.append(match.dict())
            
            # Process team stats file
            team_stats_content = await team_stats_file.read()
            team_stats_df = pd.read_csv(io.StringIO(team_stats_content.decode('utf-8')))
            team_stats_df = team_stats_df.fillna(0)
            
            team_stats = []
            for _, row in team_stats_df.iterrows():
                def safe_int(value, default=0):
                    try:
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        return int(float(value))
                    except (ValueError, TypeError):
                        return default
                
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
                    xg=safe_float(row.get('xg', 0)),
                    dataset_name=dataset_name
                )
                team_stats.append(stats.dict())
            
            # Process player stats file
            player_stats_content = await player_stats_file.read()
            player_stats_df = pd.read_csv(io.StringIO(player_stats_content.decode('utf-8')))
            player_stats_df = player_stats_df.fillna(0)
            
            player_stats = []
            for _, row in player_stats_df.iterrows():
                def safe_int(value, default=0):
                    try:
                        if pd.isna(value) or value == '' or value is None:
                            return default
                        return int(float(value))
                    except (ValueError, TypeError):
                        return default
                
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
                    penalty_goals=safe_int(row.get('penalty_goals', 0)),
                    dataset_name=dataset_name
                )
                player_stats.append(stats.dict())
            
            # Insert all data for this dataset
            if matches:
                await db.matches.insert_many(matches)
            if team_stats:
                await db.team_stats.insert_many(team_stats)
            if player_stats:
                await db.player_stats.insert_many(player_stats)
            
            dataset_total = len(matches) + len(team_stats) + len(player_stats)
            total_records += dataset_total
            
            results.append({
                "dataset_name": dataset_name,
                "matches": len(matches),
                "team_stats": len(team_stats),
                "player_stats": len(player_stats),
                "total": dataset_total
            })
        
        return {
            "success": True,
            "message": f"Successfully uploaded {num_datasets} datasets with {total_records} total records",
            "records_processed": total_records,
            "datasets": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing multi-dataset upload: {str(e)}")

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
async def calculate_rbs(config_name: str = "default"):
    """Calculate RBS scores for all team-referee combinations and ensure all team statistics are properly calculated"""
    try:
        # Step 1: Calculate and update comprehensive team statistics first
        print("Step 1: Calculating comprehensive team statistics...")
        await calculate_comprehensive_team_stats()
        
        # Step 2: Get all data (now with updated statistics)
        matches = await db.matches.find().to_list(10000)
        team_stats = await db.team_stats.find().to_list(10000)
        
        # Step 3: Clear existing RBS results
        await db.rbs_results.delete_many({})
        
        # Step 4: Get unique team-referee combinations
        team_referee_pairs = set()
        for match in matches:
            team_referee_pairs.add((match['home_team'], match['referee']))
            team_referee_pairs.add((match['away_team'], match['referee']))
        
        # Step 5: Calculate RBS for each combination
        rbs_results = []
        for team_name, referee in team_referee_pairs:
            result = await rbs_calculator.calculate_rbs_for_team_referee(
                team_name, referee, team_stats, matches, config_name
            )
            if result:
                rbs_results.append(result)
        
        # Step 6: Insert results
        if rbs_results:
            await db.rbs_results.insert_many(rbs_results)
        
        return {
            "success": True,
            "message": f"Calculated comprehensive team statistics and RBS for {len(rbs_results)} team-referee combinations using '{config_name}' configuration",
            "results_count": len(rbs_results),
            "config_used": config_name,
            "team_stats_updated": True
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating RBS: {str(e)}")

async def calculate_comprehensive_team_stats():
    """Calculate all team statistics needed for RBS and match prediction"""
    try:
        # Get all data
        matches = await db.matches.find().to_list(10000)
        team_stats_raw = await db.team_stats.find().to_list(10000)
        player_stats = await db.player_stats.find().to_list(50000)
        
        # Group player stats by match and team for aggregation
        player_stats_by_match_team = {}
        for pstat in player_stats:
            key = f"{pstat['match_id']}_{pstat['team_name']}"
            if key not in player_stats_by_match_team:
                player_stats_by_match_team[key] = []
            player_stats_by_match_team[key].append(pstat)
        
        # Process each team stat record and calculate comprehensive metrics
        updated_team_stats = []
        
        for team_stat in team_stats_raw:
            match_id = team_stat['match_id']
            team_name = team_stat['team_name']
            
            # Get corresponding match data
            match = next((m for m in matches if m['match_id'] == match_id), None)
            if not match:
                continue
            
            # Get player stats for this team in this match
            player_key = f"{match_id}_{team_name}"
            match_player_stats = player_stats_by_match_team.get(player_key, [])
            
            # Calculate aggregated values from player stats
            aggregated_xg = sum(ps.get('xg', 0) for ps in match_player_stats)
            aggregated_fouls_drawn = sum(ps.get('fouls_drawn', 0) for ps in match_player_stats)
            aggregated_penalties = sum(ps.get('penalty_attempts', 0) for ps in match_player_stats)
            aggregated_penalty_goals = sum(ps.get('penalty_goals', 0) for ps in match_player_stats)
            aggregated_shots_total = sum(ps.get('shots_total', 0) for ps in match_player_stats)
            aggregated_shots_on_target = sum(ps.get('shots_on_target', 0) for ps in match_player_stats)
            
            # DATA SOURCE PRIORITY: Use aggregated player stats if available, otherwise use team stats
            # This ensures we use the most granular data available (individual player contributions)
            # while falling back to team-level data when player-level data is unavailable
            final_xg = aggregated_xg if aggregated_xg > 0 else team_stat.get('xg', 0)
            final_fouls_drawn = aggregated_fouls_drawn if aggregated_fouls_drawn > 0 else team_stat.get('fouls_drawn', 0)
            final_penalties = aggregated_penalties if aggregated_penalties > 0 else team_stat.get('penalties_awarded', 0)
            final_penalty_goals = aggregated_penalty_goals if aggregated_penalty_goals > 0 else team_stat.get('penalty_goals', 0)
            
            # For shots, use aggregated values if available, otherwise use team stats directly (no estimation)
            if aggregated_shots_total > 0:
                final_shots_total = aggregated_shots_total
                final_shots_on_target = aggregated_shots_on_target
            else:
                # Use team stats shot data directly - no estimation
                final_shots_total = team_stat.get('shots_total', 0)
                final_shots_on_target = team_stat.get('shots_on_target', 0)
            
            # Get actual goals from match result
            is_home = team_stat.get('is_home', False)
            actual_goals = match['home_score'] if is_home else match['away_score']
            goals_conceded = match['away_score'] if is_home else match['home_score']
            
            # Use ONLY actual database values - NO modifications or fallbacks
            shots_total = final_shots_total
            shots_on_target = final_shots_on_target
            possession_pct = team_stat.get('possession_pct')  # Use actual value or None
            
            # Calculate derived metrics using ONLY actual database values
            xg_per_shot = final_xg / shots_total if shots_total > 0 else 0
            goals_per_xg = actual_goals / final_xg if final_xg > 0 else 0
            shot_accuracy = shots_on_target / shots_total if shots_total > 0 else 0
            conversion_rate = actual_goals / shots_total if shots_total > 0 else 0  # Fixed: goals per total shots
            penalty_conversion_rate = final_penalty_goals / final_penalties if final_penalties > 0 else 0
            
            # Calculate points for this match
            if actual_goals > goals_conceded:
                points = 3  # Win
            elif actual_goals == goals_conceded:
                points = 1  # Draw
            else:
                points = 0  # Loss
            
            # Update the team stat record with all calculated values
            team_stat.update({
                # Core statistics (updated with aggregated values)
                'xg': final_xg,
                'shots_total': final_shots_total,  # Use aggregated shots total
                'shots_on_target': final_shots_on_target,  # Use aggregated shots on target
                'fouls_drawn': final_fouls_drawn,
                'penalties_awarded': final_penalties,
                'penalty_goals': final_penalty_goals,
                'penalty_attempts': final_penalties,  # Same as penalties_awarded for consistency
                
                # Derived statistics for match prediction
                'xg_per_shot': xg_per_shot,
                'goals_per_xg': goals_per_xg,
                'shot_accuracy': shot_accuracy,
                'conversion_rate': conversion_rate,
                'penalty_conversion_rate': penalty_conversion_rate,
                
                # Match outcome data
                'goals_scored': actual_goals,
                'goals_conceded': goals_conceded,
                'points_earned': points,
                
                # Additional metrics
                'goal_difference': actual_goals - goals_conceded,
                'clean_sheet': 1 if goals_conceded == 0 else 0,
                'scored_goals': 1 if actual_goals > 0 else 0,
                
                # Ensure all required fields exist with proper defaults
                'shots_total': shots_total,
                'shots_on_target': shots_on_target,
                'possession_pct': possession_pct,
                'yellow_cards': team_stat.get('yellow_cards', 0),
                'red_cards': team_stat.get('red_cards', 0),
                'fouls': team_stat.get('fouls', 0),
                
                # Add timestamp for tracking
                'stats_calculated_at': datetime.now().isoformat()
            })
            
            updated_team_stats.append(team_stat)
        
        # Update the database with comprehensive team statistics
        if updated_team_stats:
            # Clear and replace all team stats with updated versions
            await db.team_stats.delete_many({})
            await db.team_stats.insert_many(updated_team_stats)
        
        return {
            "success": True,
            "message": f"Calculated comprehensive statistics for {len(updated_team_stats)} team records",
            "records_updated": len(updated_team_stats)
        }
        
    except Exception as e:
        raise Exception(f"Error calculating comprehensive team stats: {str(e)}")

@api_router.post("/calculate-comprehensive-team-stats")
async def calculate_comprehensive_team_stats_endpoint():
    """Endpoint to manually calculate comprehensive team statistics"""
    try:
        result = await calculate_comprehensive_team_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating comprehensive team stats: {str(e)}")

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
            result = await rbs_calculator.calculate_rbs_for_team_referee(
                team_name, referee, team_stats, matches, "default"
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
    """Calculate team-level stats by aggregating player stats for each match - ONLY USES SCRAPED DATA"""
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
            
            # Aggregate player stats to team level - ONLY USING SCRAPED DATA
            team_aggregations[key]['fouls_drawn'] += player.get('fouls_drawn', 0)
            team_aggregations[key]['xg'] += player.get('xg', 0)
            team_aggregations[key]['goals'] += player.get('goals', 0)
            team_aggregations[key]['assists'] += player.get('assists', 0)
            team_aggregations[key]['player_yellow_cards'] += player.get('yellow_cards', 0)
            team_aggregations[key]['player_fouls_committed'] += player.get('fouls_committed', 0)
            
            # Use SCRAPED penalty data from CSV - no estimation
            team_aggregations[key]['penalty_attempts'] += player.get('penalty_attempts', 0)
            team_aggregations[key]['penalty_goals'] += player.get('penalty_goals', 0)
        
        # Update team stats with aggregated data
        updated_count = 0
        
        for team_stat in team_stats:
            key = f"{team_stat['match_id']}_{team_stat['team_name']}"
            
            if key in team_aggregations:
                aggregated = team_aggregations[key]
                
                # Calculate penalty conversion rate from SCRAPED data
                penalty_attempts = aggregated['penalty_attempts']
                penalty_goals = aggregated['penalty_goals']
                penalty_conversion_rate = penalty_goals / penalty_attempts if penalty_attempts > 0 else 0.77  # League average if no data
                
                # Prepare update data - ONLY using scraped data, no estimation
                update_data = {
                    'fouls_drawn': aggregated['fouls_drawn'],
                    'xg': round(aggregated['xg'], 2),
                    'penalties_awarded': penalty_attempts,  # Use actual scraped attempts
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
            "message": f"Updated {updated_count} team stats with scraped player penalty data (no estimation)",
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

@api_router.post("/initialize-default-config")
async def initialize_default_config():
    """Initialize default prediction configuration"""
    try:
        # Check if default config already exists
        existing = await db.prediction_configs.find_one({"config_name": "default"})
        
        if not existing:
            default_config = PredictionConfig(config_name="default")
            await db.prediction_configs.insert_one(default_config.dict())
            return {
                "success": True,
                "message": "Default configuration created",
                "config": default_config.dict()
            }
        else:
            return {
                "success": True,
                "message": "Default configuration already exists",
                "config": {k: v for k, v in existing.items() if k != '_id'}
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing default config: {str(e)}")

@api_router.post("/prediction-config", response_model=dict)
async def create_prediction_config(config_request: PredictionConfigRequest):
    """Create or update a prediction configuration"""
    try:
        # Validate that xG weights sum to 1.0
        total_xg_weight = (config_request.xg_shot_based_weight + 
                          config_request.xg_historical_weight + 
                          config_request.xg_opponent_defense_weight)
        
        if abs(total_xg_weight - 1.0) > 0.01:  # Allow small rounding errors
            raise HTTPException(
                status_code=400, 
                detail=f"xG weights must sum to 1.0. Current sum: {total_xg_weight}"
            )
        
        # Create config object
        config = PredictionConfig(
            config_name=config_request.config_name,
            xg_shot_based_weight=config_request.xg_shot_based_weight,
            xg_historical_weight=config_request.xg_historical_weight,
            xg_opponent_defense_weight=config_request.xg_opponent_defense_weight,
            ppg_adjustment_factor=config_request.ppg_adjustment_factor,
            possession_adjustment_per_percent=config_request.possession_adjustment_per_percent,
            fouls_drawn_factor=config_request.fouls_drawn_factor,
            fouls_drawn_baseline=config_request.fouls_drawn_baseline,
            fouls_drawn_min_multiplier=config_request.fouls_drawn_min_multiplier,
            fouls_drawn_max_multiplier=config_request.fouls_drawn_max_multiplier,
            penalty_xg_value=config_request.penalty_xg_value,
            rbs_scaling_factor=config_request.rbs_scaling_factor,
            min_conversion_rate=config_request.min_conversion_rate,
            max_conversion_rate=config_request.max_conversion_rate,
            min_xg_per_match=config_request.min_xg_per_match,
            confidence_matches_multiplier=config_request.confidence_matches_multiplier,
            max_confidence=config_request.max_confidence,
            min_confidence=config_request.min_confidence,
            updated_at=datetime.now().isoformat()
        )
        
        # Upsert configuration (update if exists, create if doesn't)
        await db.prediction_configs.update_one(
            {"config_name": config_request.config_name},
            {"$set": config.dict()},
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"Configuration '{config_request.config_name}' saved successfully",
            "config": config.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving configuration: {str(e)}")

@api_router.get("/prediction-configs")
async def list_prediction_configs():
    """List all prediction configurations"""
    try:
        configs = await db.prediction_configs.find().to_list(100)
        
        # Convert ObjectId to string and clean up
        for config in configs:
            if '_id' in config:
                config.pop('_id')
        
        return {
            "success": True,
            "configs": configs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching configurations: {str(e)}")

@api_router.get("/prediction-config/{config_name}")
async def get_prediction_config(config_name: str):
    """Get a specific prediction configuration"""
    try:
        config = await db.prediction_configs.find_one({"config_name": config_name})
        
        if not config:
            # Return default configuration if not found
            default_config = PredictionConfig(config_name="default")
            return {
                "success": True,
                "config": default_config.dict(),
                "is_default": True
            }
        
        # Remove MongoDB _id
        config.pop('_id', None)
        
        return {
            "success": True,
            "config": config,
            "is_default": False
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching configuration: {str(e)}")

@api_router.delete("/prediction-config/{config_name}")
async def delete_prediction_config(config_name: str):
    """Delete a prediction configuration"""
    try:
        if config_name == "default":
            raise HTTPException(status_code=400, detail="Cannot delete default configuration")
        
        result = await db.prediction_configs.delete_one({"config_name": config_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Configuration '{config_name}' not found")
        
        return {
            "success": True,
            "message": f"Configuration '{config_name}' deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting configuration: {str(e)}")

@api_router.post("/prediction-configs")
async def create_prediction_config(config: PredictionConfigRequest):
    """Create a new prediction configuration"""
    try:
        # Check if config name already exists
        existing = await db.prediction_configs.find_one({"config_name": config.config_name})
        
        if existing:
            raise HTTPException(status_code=400, detail=f"Configuration '{config.config_name}' already exists")
        
        # Create new configuration
        new_config = PredictionConfig(
            config_name=config.config_name,
            xg_shot_based_weight=config.xg_shot_based_weight,
            xg_historical_weight=config.xg_historical_weight,
            xg_opponent_defense_weight=config.xg_opponent_defense_weight,
            ppg_adjustment_factor=config.ppg_adjustment_factor,
            possession_adjustment_per_percent=config.possession_adjustment_per_percent,
            fouls_drawn_factor=config.fouls_drawn_factor,
            fouls_drawn_baseline=config.fouls_drawn_baseline,
            fouls_drawn_min_multiplier=config.fouls_drawn_min_multiplier,
            fouls_drawn_max_multiplier=config.fouls_drawn_max_multiplier,
            penalty_xg_value=config.penalty_xg_value,
            rbs_scaling_factor=config.rbs_scaling_factor,
            min_conversion_rate=config.min_conversion_rate,
            max_conversion_rate=config.max_conversion_rate,
            min_xg_per_match=config.min_xg_per_match,
            confidence_matches_multiplier=config.confidence_matches_multiplier,
            max_confidence=config.max_confidence,
            min_confidence=config.min_confidence
        )
        
        await db.prediction_configs.insert_one(new_config.dict())
        
        return {
            "success": True,
            "message": f"Prediction configuration '{config.config_name}' created successfully",
            "config": new_config.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating configuration: {str(e)}")

# RBS Configuration Endpoints
@api_router.post("/initialize-default-rbs-config")
async def initialize_default_rbs_config():
    """Initialize default RBS configuration"""
    try:
        # Check if default config already exists
        existing = await db.rbs_configs.find_one({"config_name": "default"})
        
        if not existing:
            default_config = RBSConfig(config_name="default")
            await db.rbs_configs.insert_one(default_config.dict())
            return {
                "success": True,
                "message": "Default RBS configuration created",
                "config": default_config.dict()
            }
        else:
            return {
                "success": True,
                "message": "Default RBS configuration already exists",
                "config": {k: v for k, v in existing.items() if k != '_id'}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing default RBS config: {str(e)}")

@api_router.post("/rbs-config", response_model=dict)
async def create_rbs_config(config_request: RBSConfigRequest):
    """Create or update an RBS configuration"""
    try:
        # Validate that weights are reasonable (no need to sum to 1.0 for RBS)
        total_weight = (config_request.yellow_cards_weight + 
                       config_request.red_cards_weight + 
                       config_request.fouls_committed_weight + 
                       config_request.fouls_drawn_weight + 
                       config_request.penalties_awarded_weight + 
                       config_request.xg_difference_weight + 
                       config_request.possession_percentage_weight)
        
        if total_weight <= 0:
            raise HTTPException(status_code=400, detail="At least one weight must be positive")
        
        # Create config object
        config = RBSConfig(
            config_name=config_request.config_name,
            yellow_cards_weight=config_request.yellow_cards_weight,
            red_cards_weight=config_request.red_cards_weight,
            fouls_committed_weight=config_request.fouls_committed_weight,
            fouls_drawn_weight=config_request.fouls_drawn_weight,
            penalties_awarded_weight=config_request.penalties_awarded_weight,
            xg_difference_weight=config_request.xg_difference_weight,
            possession_percentage_weight=config_request.possession_percentage_weight,
            confidence_matches_multiplier=config_request.confidence_matches_multiplier,
            max_confidence=config_request.max_confidence,
            min_confidence=config_request.min_confidence,
            confidence_threshold_low=config_request.confidence_threshold_low,
            confidence_threshold_medium=config_request.confidence_threshold_medium,
            confidence_threshold_high=config_request.confidence_threshold_high,
            updated_at=datetime.now().isoformat()
        )
        
        # Upsert configuration (update if exists, create if doesn't)
        await db.rbs_configs.update_one(
            {"config_name": config_request.config_name},
            {"$set": config.dict()},
            upsert=True
        )
        
        return {
            "success": True,
            "message": f"RBS Configuration '{config_request.config_name}' saved successfully",
            "config": config.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving RBS configuration: {str(e)}")

@api_router.get("/rbs-configs")
async def list_rbs_configs():
    """List all RBS configurations"""
    try:
        configs = await db.rbs_configs.find().to_list(100)
        
        # Remove MongoDB _id field from each config
        for config in configs:
            if '_id' in config:
                config.pop('_id')
        
        return {
            "success": True,
            "configs": configs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RBS configurations: {str(e)}")

@api_router.get("/rbs-config/{config_name}")
async def get_rbs_config(config_name: str):
    """Get a specific RBS configuration"""
    try:
        config = await db.rbs_configs.find_one({"config_name": config_name})
        
        if not config:
            # Return default configuration if not found
            default_config = RBSConfig(config_name="default")
            return {
                "success": True,
                "config": default_config.dict(),
                "message": f"Configuration '{config_name}' not found, returning default"
            }
        
        config.pop('_id', None)
        
        return {
            "success": True,
            "config": config,
            "message": f"Configuration '{config_name}' found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RBS configuration: {str(e)}")

@api_router.delete("/rbs-config/{config_name}")
async def delete_rbs_config(config_name: str):
    """Delete an RBS configuration"""
    try:
        if config_name == "default":
            raise HTTPException(status_code=400, detail="Cannot delete default RBS configuration")
        
        result = await db.rbs_configs.delete_one({"config_name": config_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"RBS Configuration '{config_name}' not found")
        
        return {
            "success": True,
            "message": f"RBS Configuration '{config_name}' deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting RBS configuration: {str(e)}")

@api_router.post("/rbs-configs")
async def create_rbs_config(config: RBSConfigRequest):
    """Create a new RBS configuration"""
    try:
        # Check if config name already exists
        existing = await db.rbs_configs.find_one({"config_name": config.config_name})
        
        if existing:
            raise HTTPException(status_code=400, detail=f"RBS Configuration '{config.config_name}' already exists")
        
        # Create new RBS configuration
        new_config = RBSConfig(
            config_name=config.config_name,
            yellow_cards_weight=config.yellow_cards_weight,
            red_cards_weight=config.red_cards_weight,
            fouls_committed_weight=config.fouls_committed_weight,
            fouls_drawn_weight=config.fouls_drawn_weight,
            penalties_awarded_weight=config.penalties_awarded_weight,
            xg_difference_weight=config.xg_difference_weight,
            possession_percentage_weight=config.possession_percentage_weight,
            confidence_matches_multiplier=config.confidence_matches_multiplier,
            max_confidence=config.max_confidence,
            min_confidence=config.min_confidence,
            confidence_threshold_low=config.confidence_threshold_low,
            confidence_threshold_medium=config.confidence_threshold_medium,
            confidence_threshold_high=config.confidence_threshold_high
        )
        
        await db.rbs_configs.insert_one(new_config.dict())
        
        return {
            "success": True,
            "message": f"RBS Configuration '{config.config_name}' created successfully",
            "config": new_config.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating RBS configuration: {str(e)}")

@api_router.post("/regression-analysis", response_model=RegressionAnalysisResponse)
async def perform_regression_analysis(request: RegressionAnalysisRequest):
    """Perform regression analysis on match data to determine how team stats correlate with outcomes"""
    try:
        # Prepare match data
        df = await regression_analyzer.prepare_match_data()
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No match data available for analysis")
        
        # Run regression analysis
        result = regression_analyzer.run_regression(
            df=df,
            selected_stats=request.selected_stats,
            target=request.target,
            test_size=request.test_size,
            random_state=request.random_state
        )
        
        return RegressionAnalysisResponse(**result)
    
    except Exception as e:
        return RegressionAnalysisResponse(
            success=False,
            target=request.target,
            selected_stats=request.selected_stats,
            sample_size=0,
            model_type='N/A',
            results={},
            message=f"Error performing regression analysis: {str(e)}"
        )

@api_router.get("/regression-stats")
async def get_available_regression_stats():
    """Get list of available statistics for regression analysis"""
    try:
        return {
            "success": True,
            "available_stats": regression_analyzer.available_stats,
            "targets": ["points_per_game", "match_result"],
            "descriptions": {
                # Basic team stats (RBS variables)
                "yellow_cards": "Number of yellow cards received by team",
                "red_cards": "Number of red cards received by team", 
                "fouls_committed": "Number of fouls committed by team",
                "fouls_drawn": "Number of fouls drawn by team",
                "penalties_awarded": "Number of penalties awarded to team",
                "xg_difference": "Team xG minus opponent xG",
                "possession_percentage": "Percentage of possession held by team",
                "xg": "Expected goals for team",
                "shots_total": "Total shots by team",
                "shots_on_target": "Shots on target by team",
                
                # Advanced derived stats used in match prediction
                "goals": "Actual goals scored by team",
                "goals_conceded": "Goals conceded by team",
                "points_per_game": "Points earned (3=win, 1=draw, 0=loss)",
                "xg_per_shot": "Expected goals per shot ratio",
                "goals_per_xg": "Goals scored per expected goal (finishing efficiency)",
                "shot_accuracy": "Percentage of shots that were on target",
                "conversion_rate": "Goals per total shots ratio",
                "penalty_attempts": "Number of penalty attempts",
                "penalty_goals": "Number of penalty goals scored",
                "penalty_conversion_rate": "Penalty goals / penalty attempts ratio",
                
                # Additional comprehensive variables
                "rbs_score": "Referee Bias Score for team-referee combination",
                "home_advantage": "Home field advantage indicator (1=home, 0=away)",
                "team_quality_rating": "Overall team quality based on performance",
                "defensive_rating": "Defensive performance rating",
                "attacking_rating": "Attacking performance rating",
                "form_rating": "Recent form and momentum rating",
                "goal_difference": "Goal difference for the match",
                "clean_sheets_rate": "Clean sheet indicator (1=clean sheet, 0=not)",
                "scoring_rate": "Scoring indicator (1=scored, 0=did not score)",
                "is_home": "Home/away status (1=home, 0=away)"
            },
            "categories": {
                "rbs_variables": ["yellow_cards", "red_cards", "fouls_committed", "fouls_drawn", "penalties_awarded", "xg_difference", "possession_percentage"],
                "match_predictor_variables": ["xg", "shots_total", "shots_on_target", "xg_per_shot", "goals_per_xg", "shot_accuracy", "conversion_rate", "possession_percentage", "fouls_drawn", "penalties_awarded", "penalty_conversion_rate", "points_per_game", "rbs_score"],
                "basic_stats": ["yellow_cards", "red_cards", "fouls_committed", "fouls_drawn", "penalties_awarded", "xg_difference", "possession_percentage", "xg", "shots_total", "shots_on_target"],
                "advanced_stats": ["goals", "goals_conceded", "xg_per_shot", "goals_per_xg", "shot_accuracy", "conversion_rate", "penalty_attempts", "penalty_goals", "penalty_conversion_rate", "rbs_score", "home_advantage"],
                "outcome_stats": ["points_per_game", "goal_difference", "clean_sheets_rate", "scoring_rate"],
                "context_variables": ["is_home", "team_quality_rating", "defensive_rating", "attacking_rating", "form_rating"]
            },
            "optimization_endpoints": {
                "rbs_optimization": "/api/analyze-rbs-optimization",
                "predictor_optimization": "/api/analyze-predictor-optimization"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching regression stats: {str(e)}")

@api_router.post("/suggest-prediction-config")
async def suggest_prediction_config_from_regression():
    """Suggest optimal prediction configuration weights based on regression analysis"""
    try:
        # Prepare match data
        df = await regression_analyzer.prepare_match_data()
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No match data available for analysis")
        
        # Run regression analysis on points_per_game to find most important stats
        important_stats = [
            'xg_difference', 'possession_percentage', 'shot_accuracy', 
            'conversion_rate', 'xg_per_shot', 'goals_per_xg'
        ]
        
        result = regression_analyzer.run_regression(
            df=df,
            selected_stats=important_stats,
            target='points_per_game'
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=f"Regression analysis failed: {result['message']}")
        
        coefficients = result['results'].get('coefficients', {})
        r2_score = result['results'].get('r2_score', 0)
        
        # Calculate suggested weights based on coefficient magnitudes and signs
        # Normalize by the sum of absolute coefficients
        total_abs_coef = sum(abs(coef) for coef in coefficients.values())
        
        if total_abs_coef == 0:
            raise HTTPException(status_code=400, detail="No significant coefficients found")
        
        # Create suggestions based on analysis
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        suggestions = {
            "suggested_config_name": f"regression_optimized_{timestamp}",
            "analysis_basis": {
                "r2_score": r2_score,
                "sample_size": result['sample_size'],
                "stats_analyzed": important_stats
            },
            "suggestions": {
                "xg_calculation": {
                    "explanation": "Based on regression analysis of xG-related stats",
                    "current_default": {
                        "xg_shot_based_weight": 0.4,
                        "xg_historical_weight": 0.4,
                        "xg_opponent_defense_weight": 0.2
                    }
                },
                "adjustments": {},
                "confidence_level": "medium" if r2_score > 0.3 else "low"
            }
        }
        
        # Analyze specific coefficients and make suggestions
        if 'xg_per_shot' in coefficients and coefficients['xg_per_shot'] > 0.5:
            suggestions["suggestions"]["adjustments"]["shot_quality_focus"] = {
                "recommendation": "Increase shot-based xG weight",
                "suggested_xg_shot_based_weight": 0.5,
                "suggested_xg_historical_weight": 0.35,
                "reason": f"xG per shot shows strong correlation ({coefficients['xg_per_shot']:.3f})"
            }
        
        if 'possession_percentage' in coefficients:
            pos_coef = coefficients['possession_percentage']
            if abs(pos_coef) > 0.01:
                current_factor = 0.01
                suggested_factor = min(0.02, max(0.005, current_factor * (1 + pos_coef)))
                suggestions["suggestions"]["adjustments"]["possession_adjustment"] = {
                    "current_factor": current_factor,
                    "suggested_factor": round(suggested_factor, 4),
                    "reason": f"Possession shows {'positive' if pos_coef > 0 else 'negative'} correlation ({pos_coef:.3f})"
                }
        
        if 'conversion_rate' in coefficients:
            conv_coef = coefficients['conversion_rate']
            if abs(conv_coef) > 0.1:
                suggestions["suggestions"]["adjustments"]["conversion_bounds"] = {
                    "current_min": 0.5,
                    "current_max": 2.0,
                    "suggested_adjustment": "Consider tighter bounds" if abs(conv_coef) > 0.3 else "Current bounds seem appropriate",
                    "reason": f"Conversion rate correlation: {conv_coef:.3f}"
                }
        
        return {
            "success": True,
            "suggestions": suggestions,
            "message": f"Configuration suggestions generated based on R² score of {r2_score:.3f}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "suggestions": {},
            "message": f"Error generating suggestions: {str(e)}"
        }

@api_router.post("/analyze-rbs-optimization")
async def analyze_rbs_optimization():
    """Analyze RBS formula for optimization based on statistical correlations"""
    try:
        analysis = await regression_analyzer.analyze_rbs_formula_optimization()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in RBS optimization analysis: {str(e)}")

@api_router.post("/analyze-predictor-optimization")
async def analyze_predictor_optimization():
    """Analyze Match Predictor variables for optimization based on statistical significance"""
    try:
        analysis = await regression_analyzer.analyze_match_predictor_optimization()
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in predictor optimization analysis: {str(e)}")

@api_router.post("/analyze-comprehensive-regression")
async def analyze_comprehensive_regression(request: RegressionAnalysisRequest):
    """Run comprehensive regression analysis with all available variables"""
    try:
        # Prepare data with all variables
        df = await regression_analyzer.prepare_match_data(include_rbs=True)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="No match data available for analysis")
        
        # Run the requested regression analysis
        result = regression_analyzer.run_regression(
            df=df,
            selected_stats=request.selected_stats,
            target=request.target,
            test_size=request.test_size or 0.2,
            random_state=request.random_state or 42
        )
        
        # Add additional insights if analyzing RBS or Predictor variables
        insights = {}
        
        # Check if analyzing RBS variables
        rbs_vars_analyzed = [var for var in request.selected_stats if var in regression_analyzer.rbs_variables]
        if rbs_vars_analyzed:
            insights['rbs_variables_in_analysis'] = {
                'variables': rbs_vars_analyzed,
                'recommendation': 'These variables are used in RBS calculation - consider weight adjustments based on coefficients'
            }
        
        # Check if analyzing Match Predictor variables
        predictor_vars_analyzed = [var for var in request.selected_stats if var in regression_analyzer.predictor_variables]
        if predictor_vars_analyzed:
            insights['predictor_variables_in_analysis'] = {
                'variables': predictor_vars_analyzed,
                'recommendation': 'These variables are used in match prediction - consider algorithm weight adjustments'
            }
        
        # Add correlation analysis
        if result['success'] and len(request.selected_stats) > 1:
            correlation_df = df[request.selected_stats + [request.target]].corr()
            target_correlations = correlation_df[request.target].drop(request.target).to_dict()
            insights['variable_correlations'] = {
                'correlations_with_target': target_correlations,
                'strongest_positive': max(target_correlations.items(), key=lambda x: x[1]) if target_correlations else None,
                'strongest_negative': min(target_correlations.items(), key=lambda x: x[1]) if target_correlations else None
            }
        
        result['insights'] = insights
        result['data_summary'] = {
            'total_matches': len(df),
            'teams_analyzed': df['team'].nunique() if 'team' in df.columns else 0,
            'referees_analyzed': df['referee'].nunique() if 'referee' in df.columns else 0,
            'seasons_analyzed': df['season'].nunique() if 'season' in df.columns else 0
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive regression analysis: {str(e)}")

@api_router.post("/predict-match", response_model=MatchPredictionResponse)
async def predict_match(request: MatchPredictionRequest):
    """Predict match outcome using xG-based algorithm with configurable weights"""
    try:
        prediction = await match_predictor.predict_match(
            home_team=request.home_team,
            away_team=request.away_team,
            referee_name=request.referee_name,
            match_date=request.match_date,
            config_name=request.config_name or "default"
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

@api_router.get("/debug/team-stats-sample")
async def get_team_stats_sample():
    """Get sample team stats for debugging"""
    try:
        # Get a few sample team stats
        sample_stats = await db.team_stats.find({"team_name": "Arsenal"}).limit(3).to_list(3)
        
        # Remove MongoDB _id field
        for stat in sample_stats:
            if '_id' in stat:
                stat.pop('_id')
        
        return {
            "success": True,
            "sample_stats": sample_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sample stats: {str(e)}")

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
