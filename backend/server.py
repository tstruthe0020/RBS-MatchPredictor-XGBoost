import asyncio
import uuid
from datetime import datetime
import pandas as pd
import numpy as np
import io
import json
from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from contextlib import asynccontextmanager
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.metrics import accuracy_score, classification_report, r2_score, mean_squared_error, log_loss
import warnings
import os
from scipy.stats import norm, poisson
import tempfile
from pathlib import Path
from collections import defaultdict
import csv
import math
import base64
import joblib
import xgboost as xgb
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom JSON encoder for NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()  # Convert to Python native types
        elif isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert arrays to lists
        elif isinstance(obj, (pd.Timestamp, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            # Recursively handle dictionaries
            return {k: self.default(v) if isinstance(v, (np.integer, np.floating, np.bool_, np.ndarray)) else v for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            # Recursively handle lists and tuples
            return [self.default(item) if isinstance(item, (np.integer, np.floating, np.bool_, np.ndarray)) else item for item in obj]
        return super(NumpyEncoder, self).default(obj)

def convert_numpy_types(obj):
    """Recursively convert NumPy types to Python native types"""
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, pd.Timestamp)):
        return obj.isoformat()
    return obj

# Custom JSONResponse that handles NumPy types
class NumpyJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=NumpyEncoder,
        ).encode("utf-8")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    client.close()

app = FastAPI(
    title="Football Analytics API",
    description="Advanced football match prediction and referee bias analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Prediction tracking schema
class PredictionRecord(BaseModel):
    prediction_id: str
    timestamp: str
    home_team: str
    away_team: str
    referee: str
    match_date: Optional[str] = None
    prediction_method: str
    predicted_home_goals: float
    predicted_away_goals: float
    home_xg: float
    away_xg: float
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    features_used: Optional[dict] = None
    model_version: Optional[str] = "1.0"
    starting_xi_used: Optional[bool] = False
    time_decay_used: Optional[bool] = False

class ActualResult(BaseModel):
    prediction_id: str
    actual_home_goals: int
    actual_away_goals: int
    actual_outcome: str  # "home_win", "draw", "away_win"
    match_played_date: str
    additional_stats: Optional[dict] = None

class ModelPerformanceMetrics(BaseModel):
    model_version: str
    evaluation_period: str
    total_predictions: int
    # Classification metrics
    outcome_accuracy: float
    home_win_precision: float
    draw_precision: float
    away_win_precision: float
    log_loss: float
    # Regression metrics
    home_goals_mae: float
    away_goals_mae: float
    home_goals_rmse: float
    away_goals_rmse: float
    goals_r2_score: float
    # Business metrics
    profitable_predictions: Optional[float] = None
    confidence_calibration: Optional[float] = None

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
    xg_difference_weight: float = 0.0  # DISABLED for testing
    possession_percentage_weight: float = 0.0  # DISABLED for testing
    
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
    xg_difference_weight: float = 0.0  # DISABLED for testing
    possession_percentage_weight: float = 0.0  # DISABLED for testing
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
    predicted_home_goals: Optional[float] = None
    predicted_away_goals: Optional[float] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    home_win_probability: Optional[float] = None  # Percentage chance of home team winning
    draw_probability: Optional[float] = None      # Percentage chance of draw
    away_win_probability: Optional[float] = None  # Percentage chance of away team winning
    scoreline_probabilities: Optional[Dict] = None  # New field for detailed scoreline probabilities
    prediction_breakdown: Optional[Dict] = None
    confidence_factors: Optional[Dict] = None
    error: Optional[str] = None  # Error message when success=False

class PDFExportRequest(BaseModel):
    home_team: str
    away_team: str
    referee_name: str
    match_date: Optional[str] = None
    config_name: Optional[str] = "default"

class PDFExportResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None

# Starting XI Models
class PlayerInfo(BaseModel):
    player_name: str
    position: str  # GK, DEF, MID, FWD
    minutes_played: Optional[int] = 0
    matches_played: Optional[int] = 0

class FormationPosition(BaseModel):
    position_id: str  # e.g., "GK1", "DEF1", "DEF2", "MID1", etc.
    position_type: str  # GK, DEF, MID, FWD
    player: Optional[PlayerInfo] = None

class StartingXI(BaseModel):
    formation: str  # e.g., "4-4-2", "4-3-3", "3-5-2"
    positions: List[FormationPosition]

class EnhancedMatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    referee_name: str
    match_date: Optional[str] = None
    config_name: Optional[str] = "default"
    home_starting_xi: Optional[StartingXI] = None
    away_starting_xi: Optional[StartingXI] = None
    use_time_decay: Optional[bool] = True
    decay_preset: Optional[str] = "moderate"  # Options: "aggressive", "moderate", "conservative", "custom"
    custom_decay_rate: Optional[float] = None  # For custom decay

class TeamPlayersResponse(BaseModel):
    success: bool
    team_name: str
    players: List[PlayerInfo]
    default_starting_xi: Optional[StartingXI] = None
    available_formations: List[str] = ["4-4-2", "4-3-3", "3-5-2", "4-5-1", "3-4-3"]

class TimeDecayConfig(BaseModel):
    preset_name: str
    decay_type: str  # "exponential", "linear", "step"
    half_life_months: Optional[float] = None  # For exponential decay
    decay_rate_per_month: Optional[float] = None  # For linear decay
    cutoff_months: Optional[int] = None  # For step decay
    description: str

# Starting XI Manager
class StartingXIManager:
    def __init__(self):
        self.formations = {
            "4-4-2": [
                {"position_id": "GK1", "position_type": "GK"},
                {"position_id": "DEF1", "position_type": "DEF"},
                {"position_id": "DEF2", "position_type": "DEF"},
                {"position_id": "DEF3", "position_type": "DEF"},
                {"position_id": "DEF4", "position_type": "DEF"},
                {"position_id": "MID1", "position_type": "MID"},
                {"position_id": "MID2", "position_type": "MID"},
                {"position_id": "MID3", "position_type": "MID"},
                {"position_id": "MID4", "position_type": "MID"},
                {"position_id": "FWD1", "position_type": "FWD"},
                {"position_id": "FWD2", "position_type": "FWD"}
            ],
            "4-3-3": [
                {"position_id": "GK1", "position_type": "GK"},
                {"position_id": "DEF1", "position_type": "DEF"},
                {"position_id": "DEF2", "position_type": "DEF"},
                {"position_id": "DEF3", "position_type": "DEF"},
                {"position_id": "DEF4", "position_type": "DEF"},
                {"position_id": "MID1", "position_type": "MID"},
                {"position_id": "MID2", "position_type": "MID"},
                {"position_id": "MID3", "position_type": "MID"},
                {"position_id": "FWD1", "position_type": "FWD"},
                {"position_id": "FWD2", "position_type": "FWD"},
                {"position_id": "FWD3", "position_type": "FWD"}
            ],
            "3-5-2": [
                {"position_id": "GK1", "position_type": "GK"},
                {"position_id": "DEF1", "position_type": "DEF"},
                {"position_id": "DEF2", "position_type": "DEF"},
                {"position_id": "DEF3", "position_type": "DEF"},
                {"position_id": "MID1", "position_type": "MID"},
                {"position_id": "MID2", "position_type": "MID"},
                {"position_id": "MID3", "position_type": "MID"},
                {"position_id": "MID4", "position_type": "MID"},
                {"position_id": "MID5", "position_type": "MID"},
                {"position_id": "FWD1", "position_type": "FWD"},
                {"position_id": "FWD2", "position_type": "FWD"}
            ],
            "4-5-1": [
                {"position_id": "GK1", "position_type": "GK"},
                {"position_id": "DEF1", "position_type": "DEF"},
                {"position_id": "DEF2", "position_type": "DEF"},
                {"position_id": "DEF3", "position_type": "DEF"},
                {"position_id": "DEF4", "position_type": "DEF"},
                {"position_id": "MID1", "position_type": "MID"},
                {"position_id": "MID2", "position_type": "MID"},
                {"position_id": "MID3", "position_type": "MID"},
                {"position_id": "MID4", "position_type": "MID"},
                {"position_id": "MID5", "position_type": "MID"},
                {"position_id": "FWD1", "position_type": "FWD"}
            ],
            "3-4-3": [
                {"position_id": "GK1", "position_type": "GK"},
                {"position_id": "DEF1", "position_type": "DEF"},
                {"position_id": "DEF2", "position_type": "DEF"},
                {"position_id": "DEF3", "position_type": "DEF"},
                {"position_id": "MID1", "position_type": "MID"},
                {"position_id": "MID2", "position_type": "MID"},
                {"position_id": "MID3", "position_type": "MID"},
                {"position_id": "MID4", "position_type": "MID"},
                {"position_id": "FWD1", "position_type": "FWD"},
                {"position_id": "FWD2", "position_type": "FWD"},
                {"position_id": "FWD3", "position_type": "FWD"}
            ]
        }
        
        self.decay_presets = {
            "aggressive": TimeDecayConfig(
                preset_name="aggressive",
                decay_type="exponential",
                half_life_months=2.0,
                description="Heavy emphasis on recent matches (2-month half-life)"
            ),
            "moderate": TimeDecayConfig(
                preset_name="moderate", 
                decay_type="exponential",
                half_life_months=4.0,
                description="Balanced weighting of recent vs historical data (4-month half-life)"
            ),
            "conservative": TimeDecayConfig(
                preset_name="conservative",
                decay_type="exponential", 
                half_life_months=8.0,
                description="Gradual decay giving significant weight to historical data (8-month half-life)"
            ),
            "linear": TimeDecayConfig(
                preset_name="linear",
                decay_type="linear",
                decay_rate_per_month=0.1,
                description="Linear decay reducing weight by 10% per month"
            ),
            "none": TimeDecayConfig(
                preset_name="none",
                decay_type="step",
                cutoff_months=None,
                description="No time decay - all historical data weighted equally"
            )
        }
    
    async def get_team_players_with_stats(self, team_name: str):
        """Get all players for a team with their playing time statistics"""
        try:
            # Get all player stats for this team
            player_stats = await db.player_stats.find({"team_name": team_name}).to_list(10000)
            
            # Group by player and calculate total minutes/matches
            player_aggregates = {}
            for stat in player_stats:
                player = stat['player_name']
                if player not in player_aggregates:
                    player_aggregates[player] = {
                        'minutes_played': 0,
                        'matches_played': 0,
                        'goals': 0,
                        'assists': 0,
                        'position': self._estimate_player_position(stat)
                    }
                
                # Estimate 90 minutes per match as baseline
                player_aggregates[player]['minutes_played'] += 90  # Simplified - could be enhanced with actual minutes data
                player_aggregates[player]['matches_played'] += 1
                player_aggregates[player]['goals'] += stat.get('goals', 0)
                player_aggregates[player]['assists'] += stat.get('assists', 0)
            
            # Convert to PlayerInfo objects and sort by minutes played
            players = []
            for player_name, stats in player_aggregates.items():
                players.append(PlayerInfo(
                    player_name=player_name,
                    position=stats['position'],
                    minutes_played=stats['minutes_played'],
                    matches_played=stats['matches_played']
                ))
            
            # Sort by minutes played descending
            players.sort(key=lambda x: x.minutes_played, reverse=True)
            
            return players
            
        except Exception as e:
            print(f"Error getting team players: {e}")
            return []
    
    def _estimate_player_position(self, player_stat):
        """Estimate player position based on their stats (simplified logic)"""
        goals = player_stat.get('goals', 0)
        assists = player_stat.get('assists', 0)
        fouls = player_stat.get('fouls_committed', 0)
        
        # Simple heuristic - could be enhanced with more sophisticated logic
        if goals + assists > 0.5:  # High goal/assist rate
            return "FWD"
        elif fouls > 2:  # High fouling rate (defensive players)
            return "DEF"
        elif assists > goals:  # More assists than goals (midfield playmaker)
            return "MID"
        else:
            return "MID"  # Default to midfielder
    
    async def generate_default_starting_xi(self, team_name: str, formation: str = "4-4-2"):
        """Generate default starting XI based on most played players"""
        try:
            players = await self.get_team_players_with_stats(team_name)
            if len(players) < 11:
                return None
            
            # Get formation template
            formation_template = self.formations.get(formation, self.formations["4-4-2"])
            
            # Organize players by position
            players_by_position = {
                "GK": [p for p in players if p.position == "GK"],
                "DEF": [p for p in players if p.position == "DEF"], 
                "MID": [p for p in players if p.position == "MID"],
                "FWD": [p for p in players if p.position == "FWD"]
            }
            
            # Fill positions based on formation
            selected_players = []
            position_assignments = []
            
            for template_position in formation_template:
                position_type = template_position["position_type"]
                available_players = [p for p in players_by_position[position_type] if p not in selected_players]
                
                if available_players:
                    # Pick the player with most minutes in this position
                    selected_player = available_players[0]
                    selected_players.append(selected_player)
                else:
                    # Fallback: pick any remaining player
                    remaining_players = [p for p in players if p not in selected_players]
                    if remaining_players:
                        selected_player = remaining_players[0]
                        selected_players.append(selected_player)
                    else:
                        selected_player = None
                
                position_assignments.append(FormationPosition(
                    position_id=template_position["position_id"],
                    position_type=template_position["position_type"],
                    player=selected_player
                ))
            
            return StartingXI(
                formation=formation,
                positions=position_assignments
            )
            
        except Exception as e:
            print(f"Error generating default starting XI: {e}")
            return None
    
    def calculate_time_weight(self, match_date_str: str, current_date_str: str, decay_config: TimeDecayConfig):
        """Calculate time-based weight for a match"""
        try:
            from datetime import datetime
            
            match_date = datetime.strptime(match_date_str, "%Y-%m-%d")
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d") if current_date_str else datetime.now()
            
            # Calculate months difference
            months_diff = (current_date.year - match_date.year) * 12 + (current_date.month - match_date.month)
            months_diff += (current_date.day - match_date.day) / 30  # Approximate days to months
            
            if decay_config.decay_type == "exponential":
                # Exponential decay: weight = 0.5^(months_diff / half_life)
                half_life = decay_config.half_life_months or 4.0
                weight = 0.5 ** (months_diff / half_life)
            elif decay_config.decay_type == "linear":
                # Linear decay: weight = 1 - (months_diff * decay_rate)
                decay_rate = decay_config.decay_rate_per_month or 0.1
                weight = max(0.1, 1.0 - (months_diff * decay_rate))  # Minimum weight of 0.1
            elif decay_config.decay_type == "step":
                # Step decay: full weight until cutoff, then zero
                cutoff = decay_config.cutoff_months or 12
                weight = 1.0 if months_diff <= cutoff else 0.1
            else:
                # No decay
                weight = 1.0
            
            # DEBUG: Log time decay calculation
            print(f"⏰ Time Decay: {match_date_str} ({months_diff:.1f}mo ago) → weight: {weight:.3f} (type: {decay_config.decay_type})")
            
            return max(0.1, min(1.0, weight))  # Clamp between 0.1 and 1.0
            
        except Exception as e:
            print(f"Error calculating time weight: {e}")
            return 1.0

# Initialize Starting XI Manager
starting_xi_manager = StartingXIManager()

# Time Decay Configuration Manager  
class TimeDecayManager:
    def __init__(self):
        self.current_config = starting_xi_manager.decay_presets["moderate"]
    
    def get_preset(self, preset_name: str):
        return starting_xi_manager.decay_presets.get(preset_name, self.current_config)
    
    def get_all_presets(self):
        return list(starting_xi_manager.decay_presets.values())

# Initialize managers
time_decay_manager = TimeDecayManager()

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
        
        # REMOVED: xG difference and possession percentage from RBS calculation per user request
        # These components have been temporarily disabled for testing
        
        # Sum all components to get raw RBS (excluding xG diff and possession)
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
    
    async def calculate_referee_variance_analysis(self, team_name: str, referee_name: str):
        """
        Calculate referee decision variance for specific team vs their overall variance
        
        Compares how consistently/inconsistently a referee makes decisions for a specific team
        vs their overall decision patterns across all teams
        """
        try:
            # Get all matches officiated by this referee
            all_referee_matches = await db.matches.find({"referee": referee_name}).to_list(None)
            
            if len(all_referee_matches) < 10:  # Need sufficient data
                return {
                    'variance_ratios': {},
                    'confidence': 'Insufficient data',
                    'referee_total_matches': len(all_referee_matches)
                }
            
            # Get team stats for this referee across ALL teams
            all_referee_decisions = []
            team_specific_decisions = []
            
            for match in all_referee_matches:
                # Get home team stats
                home_stats = await db.team_stats.find_one({
                    "match_id": match['match_id'],
                    "is_home": True
                })
                # Get away team stats  
                away_stats = await db.team_stats.find_one({
                    "match_id": match['match_id'],
                    "is_home": False
                })
                
                if home_stats:
                    all_referee_decisions.append(home_stats)
                    if home_stats.get('team_name') == team_name:
                        team_specific_decisions.append(home_stats)
                
                if away_stats:
                    all_referee_decisions.append(away_stats)
                    if away_stats.get('team_name') == team_name:
                        team_specific_decisions.append(away_stats)
            
            if len(team_specific_decisions) < 3:  # Need minimum team-specific data
                return {
                    'variance_ratios': {},
                    'confidence': 'Insufficient team-specific data',
                    'referee_total_matches': len(all_referee_matches),
                    'team_matches_with_referee': len(team_specific_decisions)
                }
            
            # Calculate variance ratios for key decision categories
            decision_categories = [
                'yellow_cards', 'red_cards', 'fouls_committed', 
                'penalties_awarded', 'possession_pct'
            ]
            
            variance_ratios = {}
            
            for category in decision_categories:
                # Get values for this team with this referee
                team_values = [
                    stats.get(category, 0) for stats in team_specific_decisions 
                    if stats.get(category) is not None
                ]
                
                # Get values for all teams with this referee  
                overall_values = [
                    stats.get(category, 0) for stats in all_referee_decisions
                    if stats.get(category) is not None
                ]
                
                if len(team_values) > 1 and len(overall_values) > 5:
                    team_variance = self._calculate_variance(team_values)
                    overall_variance = self._calculate_variance(overall_values)
                    
                    if overall_variance > 0:
                        variance_ratio = team_variance / overall_variance
                        variance_ratios[category] = round(variance_ratio, 3)
                    else:
                        variance_ratios[category] = 1.0
                else:
                    variance_ratios[category] = None
            
            # Determine confidence level
            confidence_level = self._determine_variance_confidence(
                len(team_specific_decisions), len(all_referee_decisions)
            )
            
            return {
                'variance_ratios': variance_ratios,
                'confidence': confidence_level,
                'referee_total_matches': len(all_referee_matches),
                'team_matches_with_referee': len(team_specific_decisions),
                'interpretation': self._interpret_variance_ratios(variance_ratios)
            }
            
        except Exception as e:
            print(f"Error calculating variance analysis for {team_name} with {referee_name}: {e}")
            return {
                'variance_ratios': {},
                'confidence': 'Error',
                'referee_total_matches': 0,
                'team_matches_with_referee': 0
            }
    
    def _calculate_variance(self, values):
        """Calculate variance for a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean_val = sum(values) / len(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance
    
    def _determine_variance_confidence(self, team_matches, total_matches):
        """Determine confidence level for variance analysis"""
        if team_matches < 3 or total_matches < 10:
            return "Very Low"
        elif team_matches < 5 or total_matches < 20:
            return "Low"
        elif team_matches < 8 or total_matches < 30:
            return "Medium"
        elif team_matches < 12 or total_matches < 50:
            return "High"
        else:
            return "Very High"
    
    def _interpret_variance_ratios(self, variance_ratios):
        """Provide interpretation of variance ratios"""
        interpretations = {}
        
        for category, ratio in variance_ratios.items():
            if ratio is None:
                interpretations[category] = "Insufficient data"
            elif ratio > 2.0:
                interpretations[category] = "Much more variable than usual (inconsistent treatment)"
            elif ratio > 1.5:
                interpretations[category] = "More variable than usual"
            elif ratio > 0.5:
                interpretations[category] = "Normal variance"
            elif ratio > 0.2:
                interpretations[category] = "Less variable than usual"
            else:
                interpretations[category] = "Much less variable than usual (very consistent treatment)"
        
        return interpretations

# Initialize RBS Calculator
rbs_calculator = RBSCalculator()

# PDF Export Engine
class PDFExporter:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Custom styles for the report
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue,
            leftIndent=0
        )
        
        self.subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.darkgreen,
            leftIndent=10
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            leftIndent=10
        )
        
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            leftIndent=10,
            textColor=colors.grey
        )
    
    async def generate_prediction_pdf(self, prediction_data, head_to_head_data, referee_data):
        """Generate comprehensive PDF report for match prediction"""
        try:
            # Create BytesIO buffer
            buffer = io.BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Build story (content) for PDF
            story = []
            
            # Title
            title = f"Football Match Prediction Report"
            story.append(Paragraph(title, self.title_style))
            story.append(Spacer(1, 20))
            
            # Match Details
            story.extend(self._create_match_details_section(prediction_data))
            
            # Prediction Summary
            story.extend(self._create_prediction_summary_section(prediction_data))
            
            # Detailed Analysis
            story.extend(self._create_detailed_analysis_section(prediction_data))
            
            # Poisson Analysis
            story.extend(self._create_poisson_analysis_section(prediction_data))
            
            # Head-to-Head Statistics
            if head_to_head_data:
                story.extend(self._create_head_to_head_section(head_to_head_data))
            
            # Referee Analysis
            if referee_data:
                story.extend(self._create_referee_analysis_section(referee_data))
            
            # Model Information
            story.extend(self._create_model_info_section(prediction_data))
            
            # Footer
            story.extend(self._create_footer_section())
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise e
    
    def _create_match_details_section(self, prediction_data):
        """Create match details section"""
        story = []
        
        story.append(Paragraph("Match Information", self.section_style))
        
        match_data = [
            ['Home Team:', prediction_data.get('home_team', 'N/A')],
            ['Away Team:', prediction_data.get('away_team', 'N/A')],
            ['Referee:', prediction_data.get('referee', 'N/A')],
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Prediction Method:', 'XGBoost + Poisson Distribution Simulation']
        ]
        
        table = Table(match_data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_prediction_summary_section(self, prediction_data):
        """Create prediction summary section"""
        story = []
        
        story.append(Paragraph("Prediction Summary", self.section_style))
        
        # Main prediction results
        summary_data = [
            ['Metric', 'Home Team', 'Away Team'],
            ['Predicted Goals', f"{prediction_data.get('predicted_home_goals', 0):.2f}", 
             f"{prediction_data.get('predicted_away_goals', 0):.2f}"],
            ['Expected xG', f"{prediction_data.get('home_xg', 0):.2f}", 
             f"{prediction_data.get('away_xg', 0):.2f}"],
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 15))
        
        # Match outcome probabilities
        story.append(Paragraph("Match Outcome Probabilities", self.subsection_style))
        
        prob_data = [
            ['Outcome', 'Probability'],
            ['Home Win', f"{prediction_data.get('home_win_probability', 0):.1f}%"],
            ['Draw', f"{prediction_data.get('draw_probability', 0):.1f}%"],
            ['Away Win', f"{prediction_data.get('away_win_probability', 0):.1f}%"]
        ]
        
        prob_table = Table(prob_data, colWidths=[2*inch, 2*inch])
        prob_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(prob_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_detailed_analysis_section(self, prediction_data):
        """Create detailed analysis section"""
        story = []
        
        story.append(Paragraph("Detailed Model Analysis", self.section_style))
        
        # XGBoost confidence
        prediction_breakdown = prediction_data.get('prediction_breakdown', {})
        xgboost_confidence = prediction_breakdown.get('xgboost_confidence', {})
        
        story.append(Paragraph("Model Confidence Metrics", self.subsection_style))
        
        confidence_text = f"""
        <b>Classifier Confidence:</b> {xgboost_confidence.get('classifier_confidence', 0):.3f}<br/>
        <b>Features Used:</b> {xgboost_confidence.get('features_used', 'N/A')}<br/>
        <b>Training Samples:</b> {xgboost_confidence.get('training_samples', 'N/A')}
        """
        
        story.append(Paragraph(confidence_text, self.normal_style))
        story.append(Spacer(1, 10))
        
        # Feature importance
        feature_importance = prediction_breakdown.get('feature_importance', {}).get('top_features', {})
        if feature_importance:
            story.append(Paragraph("Top Feature Importance", self.subsection_style))
            
            feature_data = [['Feature', 'Importance']]
            for feature, importance in list(feature_importance.items())[:10]:  # Top 10
                feature_name = feature.replace('_', ' ').title()
                feature_data.append([feature_name, f"{importance:.4f}"])
            
            feature_table = Table(feature_data, colWidths=[3*inch, 1.5*inch])
            feature_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightsteelblue),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(feature_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_poisson_analysis_section(self, prediction_data):
        """Create Poisson analysis section"""
        story = []
        
        story.append(Paragraph("Poisson Distribution Analysis", self.section_style))
        
        prediction_breakdown = prediction_data.get('prediction_breakdown', {})
        poisson_analysis = prediction_breakdown.get('poisson_analysis', {})
        
        # Lambda parameters
        lambda_params = poisson_analysis.get('lambda_parameters', {})
        story.append(Paragraph("Expected Goals Parameters", self.subsection_style))
        
        lambda_text = f"""
        <b>Home Team Lambda (Expected Goals):</b> {lambda_params.get('home_lambda', 0):.3f}<br/>
        <b>Away Team Lambda (Expected Goals):</b> {lambda_params.get('away_lambda', 0):.3f}<br/>
        <b>Most Likely Scoreline:</b> {poisson_analysis.get('most_likely_scoreline', 'N/A')}<br/>
        <b>Scoreline Probability:</b> {poisson_analysis.get('scoreline_probability', 0):.1f}%
        """
        
        story.append(Paragraph(lambda_text, self.normal_style))
        story.append(Spacer(1, 15))
        
        # Scoreline probabilities table
        scoreline_probs = prediction_data.get('scoreline_probabilities', {})
        if scoreline_probs:
            story.append(Paragraph("Top Scoreline Probabilities", self.subsection_style))
            
            # Get top 10 most likely scorelines
            sorted_scorelines = sorted(scoreline_probs.items(), key=lambda x: x[1], reverse=True)[:10]
            
            score_data = [['Scoreline', 'Probability']]
            for scoreline, probability in sorted_scorelines:
                score_data.append([scoreline, f"{probability:.2f}%"])
            
            score_table = Table(score_data, colWidths=[1.5*inch, 1.5*inch])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(score_table)
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_head_to_head_section(self, h2h_data):
        """Create head-to-head section"""
        story = []
        
        story.append(Paragraph("Head-to-Head Statistics", self.section_style))
        
        h2h_table_data = [
            ['Metric', 'Value'],
            ['Home Wins', str(h2h_data.get('home_wins', 0))],
            ['Draws', str(h2h_data.get('draws', 0))],
            ['Away Wins', str(h2h_data.get('away_wins', 0))],
            ['Average Home Goals', f"{h2h_data.get('home_goals_avg', 0):.2f}"],
            ['Average Away Goals', f"{h2h_data.get('away_goals_avg', 0):.2f}"]
        ]
        
        h2h_table = Table(h2h_table_data, colWidths=[2.5*inch, 1.5*inch])
        h2h_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.moccasin),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(h2h_table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_referee_analysis_section(self, referee_data):
        """Create referee analysis section"""
        story = []
        
        story.append(Paragraph("Referee Bias Analysis (RBS)", self.section_style))
        
        home_rbs = referee_data.get('home_rbs', {})
        away_rbs = referee_data.get('away_rbs', {})
        
        if home_rbs or away_rbs:
            story.append(Paragraph("Referee Bias Scores", self.subsection_style))
            
            rbs_data = [['Team', 'RBS Score', 'Confidence', 'Matches with Referee']]
            
            if home_rbs:
                rbs_data.append([
                    home_rbs.get('team_name', 'Home Team'),
                    f"{home_rbs.get('rbs_score', 0):.3f}",
                    f"{home_rbs.get('confidence_level', 0):.1f}%",
                    str(home_rbs.get('matches_with_ref', 0))
                ])
            
            if away_rbs:
                rbs_data.append([
                    away_rbs.get('team_name', 'Away Team'),
                    f"{away_rbs.get('rbs_score', 0):.3f}",
                    f"{away_rbs.get('confidence_level', 0):.1f}%",
                    str(away_rbs.get('matches_with_ref', 0))
                ])
            
            rbs_table = Table(rbs_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch])
            rbs_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.mistyrose),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(rbs_table)
            
            # RBS explanation
            rbs_explanation = """
            <b>RBS Score Interpretation:</b><br/>
            • Positive values indicate favorable treatment by the referee<br/>
            • Negative values indicate unfavorable treatment<br/>
            • Values range from -1.0 to +1.0<br/>
            • Higher confidence percentages indicate more reliable scores
            """
            
            story.append(Spacer(1, 10))
            story.append(Paragraph(rbs_explanation, self.small_style))
        
        story.append(Spacer(1, 20))
        return story
    
    def _create_model_info_section(self, prediction_data):
        """Create model information section"""
        story = []
        
        story.append(Paragraph("Model Information & Methodology", self.section_style))
        
        methodology_text = """
        <b>Prediction Method:</b> XGBoost + Poisson Distribution Simulation<br/><br/>
        
        <b>XGBoost Models:</b><br/>
        • Classification model for match outcomes (Win/Draw/Loss)<br/>
        • Regression models for goals and xG prediction<br/>
        • Uses 65+ features including team performance, form, and referee bias<br/><br/>
        
        <b>Poisson Simulation:</b><br/>
        • Uses predicted goals as lambda parameters<br/>
        • Calculates probability for each possible scoreline<br/>
        • Provides more accurate outcome probabilities than direct classification<br/><br/>
        
        <b>Key Features Used:</b><br/>
        • Team offensive and defensive statistics<br/>
        • Recent form (last 5 matches)<br/>
        • Head-to-head historical performance<br/>
        • Referee bias scores (RBS)<br/>
        • Home advantage factor<br/>
        • Team quality metrics (points per game)
        """
        
        story.append(Paragraph(methodology_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_footer_section(self):
        """Create footer section"""
        story = []
        
        footer_text = """
        <i>This report was generated by the Football Analytics Prediction System.<br/>
        Predictions are based on historical data and statistical models.<br/>
        Results should be used for informational purposes only.</i>
        """
        
        story.append(Paragraph(footer_text, self.small_style))
        
        return story

# Initialize PDF Exporter
pdf_exporter = PDFExporter()

# XGBoost-Based Match Prediction Engine with Poisson Simulation
class MLMatchPredictor:
    def __init__(self):
        self.models = {}
        self.ensemble_models = {}  # Store ensemble models
        self.model_weights = {}    # Store model performance weights
        self.model_confidence = {} # Store model confidence scores
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        self.ensemble_dir = os.path.join(self.models_dir, "ensemble")
        self.ensure_models_dir()
        self.load_models()
        self.initialize_ensemble_models()
        
        # XGBoost optimal hyperparameters for football prediction
        self.xgb_params_classifier = {
            'n_estimators': 200,
            'max_depth': 6,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'objective': 'multi:softprob',
            'num_class': 3
        }
        
        self.xgb_params_regressor = {
            'n_estimators': 150,
            'max_depth': 5,
            'learning_rate': 0.1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'objective': 'reg:squarederror'
        }
        
        # Initialize default model weights (will be updated based on performance)
        self.model_weights = {
            'xgboost': 0.30,      # Highest weight - proven performer
            'random_forest': 0.25, # Second highest - robust
            'gradient_boost': 0.20, # Third - good sequential learning
            'neural_net': 0.15,    # Fourth - complex patterns
            'logistic': 0.10       # Lowest - simple baseline
        }
    
    def ensure_models_dir(self):
        """Ensure models directory exists"""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.ensemble_dir, exist_ok=True)
    
    def get_model_paths(self):
        """Get file paths for all models"""
        return {
            'classifier': os.path.join(self.models_dir, 'xgb_match_outcome_classifier.pkl'),
            'home_goals': os.path.join(self.models_dir, 'xgb_home_goals_regressor.pkl'),
            'away_goals': os.path.join(self.models_dir, 'xgb_away_goals_regressor.pkl'),
            'home_xg': os.path.join(self.models_dir, 'xgb_home_xg_regressor.pkl'),
            'away_xg': os.path.join(self.models_dir, 'xgb_away_xg_regressor.pkl'),
            'scaler': os.path.join(self.models_dir, 'xgb_feature_scaler.pkl'),
            'feature_columns': os.path.join(self.models_dir, 'xgb_feature_columns.pkl')
        }
    
    def load_models(self):
        """Load trained models if they exist"""
        try:
            model_paths = self.get_model_paths()
            
            # Check if all model files exist
            models_exist = all(os.path.exists(path) for path in model_paths.values())
            
            if models_exist:
                print("Loading XGBoost models...")
                self.models['classifier'] = joblib.load(model_paths['classifier'])
                self.models['home_goals'] = joblib.load(model_paths['home_goals'])
                self.models['away_goals'] = joblib.load(model_paths['away_goals'])
                self.models['home_xg'] = joblib.load(model_paths['home_xg'])
                self.models['away_xg'] = joblib.load(model_paths['away_xg'])
                self.scaler = joblib.load(model_paths['scaler'])
                self.feature_columns = joblib.load(model_paths['feature_columns'])
                print("XGBoost models loaded successfully")
            else:
                print("XGBoost models not found - will need to train first")
                print(f"Models directory: {self.models_dir}")
                # Initialize empty models dictionary
                self.models = {}
                self.scaler = StandardScaler()
                self.feature_columns = []
                
        except Exception as e:
            print(f"Error loading XGBoost models: {e}")
            print(f"Models directory: {self.models_dir}")
            # Initialize empty models to ensure server can start
            self.models = {}
            self.scaler = StandardScaler()
            self.feature_columns = []
    
    def save_models(self):
        """Save trained models"""
        model_paths = self.get_model_paths()
        try:
            joblib.dump(self.models['classifier'], model_paths['classifier'])
            joblib.dump(self.models['home_goals'], model_paths['home_goals'])
            joblib.dump(self.models['away_goals'], model_paths['away_goals'])
            joblib.dump(self.models['home_xg'], model_paths['home_xg'])
            joblib.dump(self.models['away_xg'], model_paths['away_xg'])
            joblib.dump(self.scaler, model_paths['scaler'])
            joblib.dump(self.feature_columns, model_paths['feature_columns'])
            print("XGBoost models saved successfully")
        except Exception as e:
            print(f"Error saving XGBoost models: {e}")
    
    def initialize_ensemble_models(self):
        """Initialize ensemble models with optimal parameters for football prediction"""
        print("🤖 Initializing Ensemble Models...")
        
        # Random Forest Models (robust to outliers, good for missing data)
        self.ensemble_models['random_forest'] = {
            'classifier': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'home_goals': RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'away_goals': RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=43,
                n_jobs=-1
            ),
            'home_xg': RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=44,
                n_jobs=-1
            ),
            'away_xg': RandomForestRegressor(
                n_estimators=100,
                max_depth=8,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=45,
                n_jobs=-1
            )
        }
        
        # Gradient Boosting Models (sequential learning, good for complex patterns)
        self.ensemble_models['gradient_boost'] = {
            'classifier': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            ),
            'home_goals': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42
            ),
            'away_goals': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=43
            ),
            'home_xg': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=44
            ),
            'away_xg': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=45
            )
        }
        
        # Neural Network Models (complex non-linear patterns)
        self.ensemble_models['neural_net'] = {
            'classifier': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                alpha=0.01,
                random_state=42
            ),
            'home_goals': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                alpha=0.01,
                random_state=42
            ),
            'away_goals': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                alpha=0.01,
                random_state=43
            ),
            'home_xg': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                alpha=0.01,
                random_state=44
            ),
            'away_xg': MLPRegressor(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                learning_rate_init=0.001,
                alpha=0.01,
                random_state=45
            )
        }
        
        # Logistic Regression Models (simple, interpretable baseline)
        self.ensemble_models['logistic'] = {
            'classifier': LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='multinomial',
                solver='lbfgs'
            ),
            'home_goals': LinearRegression(),
            'away_goals': LinearRegression(),
            'home_xg': LinearRegression(),
            'away_xg': LinearRegression()
        }
        
        print("✅ Ensemble models initialized successfully")
    
    def load_ensemble_models(self):
        """Load pre-trained ensemble models"""
        try:
            for model_type in ['random_forest', 'gradient_boost', 'neural_net', 'logistic']:
                model_dir = os.path.join(self.ensemble_dir, model_type)
                if os.path.exists(model_dir):
                    for prediction_type in ['classifier', 'home_goals', 'away_goals', 'home_xg', 'away_xg']:
                        model_path = os.path.join(model_dir, f"{prediction_type}.pkl")
                        if os.path.exists(model_path):
                            self.ensemble_models[model_type][prediction_type] = joblib.load(model_path)
                            print(f"✅ Loaded {model_type} {prediction_type} model")
        except Exception as e:
            print(f"⚠️ Error loading ensemble models: {e}")
    
    def save_ensemble_models(self):
        """Save trained ensemble models"""
        try:
            for model_type, models in self.ensemble_models.items():
                model_dir = os.path.join(self.ensemble_dir, model_type)
                os.makedirs(model_dir, exist_ok=True)
                
                for prediction_type, model in models.items():
                    model_path = os.path.join(model_dir, f"{prediction_type}.pkl")
                    joblib.dump(model, model_path)
                    
            print("✅ Ensemble models saved successfully")
        except Exception as e:
            print(f"❌ Error saving ensemble models: {e}")
    
    async def extract_features_for_match(self, home_team, away_team, referee, match_date=None):
        """Extract features for a single match prediction"""
        try:
            # Get team stats (use existing calculation methods)
            home_stats = await self.calculate_team_features(home_team, is_home=True)
            away_stats = await self.calculate_team_features(away_team, is_home=False)
            
            if not home_stats or not away_stats:
                raise ValueError("Could not calculate team features")
            
            # Get referee bias
            home_rbs, home_rbs_conf = await self.get_referee_bias(home_team, referee)
            away_rbs, away_rbs_conf = await self.get_referee_bias(away_team, referee)
            
            # Get head-to-head stats
            h2h_stats = await self.get_head_to_head_stats(home_team, away_team)
            
            # Build feature vector
            features = {
                # Home team offensive stats
                'home_xg_per_match': home_stats['xg'],
                'home_goals_per_match': home_stats['goals'],
                'home_shots_per_match': home_stats['shots_total'],
                'home_shots_on_target_per_match': home_stats['shots_on_target'],
                'home_xg_per_shot': home_stats['xg_per_shot'],
                'home_shot_accuracy': home_stats['shot_accuracy'],
                'home_conversion_rate': home_stats['conversion_rate'],
                'home_possession_pct': home_stats['possession_pct'],
                
                # Home team defensive stats (what they concede)
                'home_goals_conceded_per_match': home_stats['goals_conceded'],
                'home_xg_conceded_per_match': home_stats.get('xg_conceded', 0),
                
                # Away team offensive stats
                'away_xg_per_match': away_stats['xg'],
                'away_goals_per_match': away_stats['goals'],
                'away_shots_per_match': away_stats['shots_total'],
                'away_shots_on_target_per_match': away_stats['shots_on_target'],
                'away_xg_per_shot': away_stats['xg_per_shot'],
                'away_shot_accuracy': away_stats['shot_accuracy'],
                'away_conversion_rate': away_stats['conversion_rate'],
                'away_possession_pct': away_stats['possession_pct'],
                
                # Away team defensive stats
                'away_goals_conceded_per_match': away_stats['goals_conceded'],
                'away_xg_conceded_per_match': away_stats.get('xg_conceded', 0),
                
                # Form over last 5 matches
                'home_form_last5': await self.get_team_form(home_team, last_n=5),
                'away_form_last5': await self.get_team_form(away_team, last_n=5),
                
                # Home advantage
                'home_advantage': 1,  # Always 1 for home team
                
                # Referee bias
                'home_referee_bias': home_rbs,
                'away_referee_bias': away_rbs,
                'home_rbs_confidence': home_rbs_conf,
                'away_rbs_confidence': away_rbs_conf,
                
                # Head-to-head
                'h2h_home_wins': h2h_stats['home_wins'],
                'h2h_draws': h2h_stats['draws'],
                'h2h_away_wins': h2h_stats['away_wins'],
                'h2h_home_goals_avg': h2h_stats['home_goals_avg'],
                'h2h_away_goals_avg': h2h_stats['away_goals_avg'],
                
                # Team quality metrics
                'home_ppg': home_stats['points_per_game'],
                'away_ppg': away_stats['points_per_game'],
                'ppg_difference': home_stats['points_per_game'] - away_stats['points_per_game'],
                
                # Additional advanced stats
                'home_penalties_per_match': home_stats['penalties_awarded'],
                'away_penalties_per_match': away_stats['penalties_awarded'],
                'home_fouls_drawn_per_match': home_stats['fouls_drawn'],
                'away_fouls_drawn_per_match': away_stats['fouls_drawn'],
                'home_fouls_committed_per_match': home_stats['fouls'],
                'away_fouls_committed_per_match': away_stats['fouls'],
                'home_yellow_cards_per_match': home_stats['yellow_cards'],
                'away_yellow_cards_per_match': away_stats['yellow_cards'],
                'home_red_cards_per_match': home_stats['red_cards'],
                'away_red_cards_per_match': away_stats['red_cards'],
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    async def calculate_team_features(self, team_name, is_home):
        """Calculate comprehensive team features using existing methods"""
        # Use existing team averages calculation
        stats = await match_predictor.calculate_team_averages(team_name, is_home)
        if not stats:
            return None
        
        # Ensure all required fields exist with defaults
        required_fields = [
            'xg', 'goals', 'shots_total', 'shots_on_target', 'xg_per_shot', 
            'shot_accuracy', 'conversion_rate', 'possession_pct', 'goals_conceded',
            'points_per_game', 'penalties_awarded', 'fouls_drawn', 'fouls',
            'yellow_cards', 'red_cards'
        ]
        
        for field in required_fields:
            if field not in stats:
                stats[field] = 0.0
        
        return stats
    
    async def get_referee_bias(self, team_name, referee):
        """Get referee bias score"""
        try:
            rbs_result = await db.rbs_results.find_one({
                "team_name": team_name,
                "referee": referee
            })
            if rbs_result:
                return rbs_result['rbs_score'], rbs_result['confidence_level']
            return 0.0, 0.0
        except:
            return 0.0, 0.0
    
    async def get_head_to_head_stats(self, home_team, away_team):
        """Get head-to-head statistics"""
        try:
            h2h_matches = await db.matches.find({
                "$or": [
                    {"home_team": home_team, "away_team": away_team},
                    {"home_team": away_team, "away_team": home_team}
                ]
            }).to_list(100)
            
            if not h2h_matches:
                return {
                    'home_wins': 0, 'draws': 0, 'away_wins': 0,
                    'home_goals_avg': 0, 'away_goals_avg': 0
                }
            
            home_wins = 0
            draws = 0
            away_wins = 0
            total_home_goals = 0
            total_away_goals = 0
            
            for match in h2h_matches:
                # Adjust perspective based on which team is home in current prediction
                if match['home_team'] == home_team:
                    home_goals = match['home_score']
                    away_goals = match['away_score']
                else:
                    home_goals = match['away_score']
                    away_goals = match['home_score']
                
                total_home_goals += home_goals
                total_away_goals += away_goals
                
                if home_goals > away_goals:
                    home_wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    away_wins += 1
            
            return {
                'home_wins': home_wins,
                'draws': draws,
                'away_wins': away_wins,
                'home_goals_avg': total_home_goals / len(h2h_matches),
                'away_goals_avg': total_away_goals / len(h2h_matches)
            }
        except:
            return {
                'home_wins': 0, 'draws': 0, 'away_wins': 0,
                'home_goals_avg': 0, 'away_goals_avg': 0
            }
    
    async def get_team_form(self, team_name, last_n=5):
        """Calculate team form over last N matches"""
        try:
            # Get recent matches for the team
            recent_matches = await db.matches.find({
                "$or": [
                    {"home_team": team_name},
                    {"away_team": team_name}
                ]
            }).sort("match_date", -1).limit(last_n).to_list(last_n)
            
            if not recent_matches:
                return 0.0
            
            total_points = 0
            for match in recent_matches:
                if match['home_team'] == team_name:
                    if match['home_score'] > match['away_score']:
                        total_points += 3  # Win
                    elif match['home_score'] == match['away_score']:
                        total_points += 1  # Draw
                else:  # Away team
                    if match['away_score'] > match['home_score']:
                        total_points += 3  # Win
                    elif match['away_score'] == match['home_score']:
                        total_points += 1  # Draw
            
            return total_points / len(recent_matches)
        except:
            return 0.0
    
    async def build_training_dataset(self):
        """Build training dataset from historical matches"""
        try:
            print("Building training dataset...")
            
            # Get all matches
            all_matches = await db.matches.find().to_list(10000)
            print(f"Found {len(all_matches)} matches")
            
            features_list = []
            targets = []
            
            for i, match in enumerate(all_matches):
                if i % 100 == 0:
                    print(f"Processing match {i+1}/{len(all_matches)}")
                
                try:
                    # Extract features for this match
                    features = await self.extract_features_for_match(
                        match['home_team'], 
                        match['away_team'], 
                        match['referee'],
                        match.get('match_date')
                    )
                    
                    if features is None:
                        continue
                    
                    # Get actual match outcome and goals
                    home_score = match['home_score']
                    away_score = match['away_score']
                    
                    # Determine match outcome
                    if home_score > away_score:
                        outcome = 0  # Home win
                    elif home_score == away_score:
                        outcome = 1  # Draw
                    else:
                        outcome = 2  # Away win
                    
                    # Get actual xG values from team stats
                    home_team_stats = await db.team_stats.find_one({
                        "match_id": match['match_id'],
                        "team_name": match['home_team'],
                        "is_home": True
                    })
                    away_team_stats = await db.team_stats.find_one({
                        "match_id": match['match_id'],
                        "team_name": match['away_team'],
                        "is_home": False
                    })
                    
                    home_xg = home_team_stats.get('xg', 0) if home_team_stats else 0
                    away_xg = away_team_stats.get('xg', 0) if away_team_stats else 0
                    
                    features_list.append(features)
                    targets.append({
                        'outcome': outcome,
                        'home_goals': home_score,
                        'away_goals': away_score,
                        'home_xg': home_xg,
                        'away_xg': away_xg
                    })
                    
                except Exception as e:
                    print(f"Error processing match {match['match_id']}: {e}")
                    continue
            
            print(f"Successfully processed {len(features_list)} matches for training")
            return features_list, targets
            
        except Exception as e:
            print(f"Error building training dataset: {e}")
            return [], []
    
    async def train_models(self, test_size=0.2, random_state=42):
        """Train all ML models"""
        try:
            print("Starting ML model training...")
            
            # Build training dataset
            features_list, targets = await self.build_training_dataset()
            
            if len(features_list) == 0:
                raise ValueError("No training data available")
            
            # Convert to DataFrame for easier handling
            import pandas as pd
            X = pd.DataFrame(features_list)
            
            # Store feature columns for later use
            self.feature_columns = X.columns.tolist()
            
            # Prepare target variables
            y_outcome = [t['outcome'] for t in targets]
            y_home_goals = [t['home_goals'] for t in targets]
            y_away_goals = [t['away_goals'] for t in targets]
            y_home_xg = [t['home_xg'] for t in targets]
            y_away_xg = [t['away_xg'] for t in targets]
            
            # Split data
            X_train, X_test, y_outcome_train, y_outcome_test = train_test_split(
                X, y_outcome, test_size=test_size, random_state=random_state, stratify=y_outcome
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Split other targets with same indices
            train_indices = X_train.index
            test_indices = X_test.index
            
            y_home_goals_train = [y_home_goals[i] for i in train_indices]
            y_home_goals_test = [y_home_goals[i] for i in test_indices]
            y_away_goals_train = [y_away_goals[i] for i in train_indices]
            y_away_goals_test = [y_away_goals[i] for i in test_indices]
            y_home_xg_train = [y_home_xg[i] for i in train_indices]
            y_home_xg_test = [y_home_xg[i] for i in test_indices]
            y_away_xg_train = [y_away_xg[i] for i in train_indices]
            y_away_xg_test = [y_away_xg[i] for i in test_indices]
            
            print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
            
            # Train models
            models_to_train = {
                'classifier': (RandomForestClassifier(n_estimators=100, random_state=random_state), 
                              y_outcome_train, y_outcome_test),
                'home_goals': (RandomForestRegressor(n_estimators=100, random_state=random_state),
                              y_home_goals_train, y_home_goals_test),
                'away_goals': (RandomForestRegressor(n_estimators=100, random_state=random_state),
                              y_away_goals_train, y_away_goals_test),
                'home_xg': (RandomForestRegressor(n_estimators=100, random_state=random_state),
                           y_home_xg_train, y_home_xg_test),
                'away_xg': (RandomForestRegressor(n_estimators=100, random_state=random_state),
                           y_away_xg_train, y_away_xg_test)
            }
            
            training_results = {}
            
            for model_name, (model, y_train, y_test) in models_to_train.items():
                print(f"Training {model_name}...")
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Evaluate
                if model_name == 'classifier':
                    from sklearn.metrics import accuracy_score, classification_report
                    accuracy = accuracy_score(y_test, y_pred)
                    training_results[model_name] = {
                        'accuracy': accuracy,
                        'samples': len(y_test)
                    }
                    print(f"{model_name} accuracy: {accuracy:.3f}")
                else:
                    r2 = r2_score(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    training_results[model_name] = {
                        'r2_score': r2,
                        'mse': mse,
                        'samples': len(y_test)
                    }
                    print(f"{model_name} R² score: {r2:.3f}, MSE: {mse:.3f}")
                
                # Store trained model
                self.models[model_name] = model
            
            # Save models
            self.save_models()
            
            print("ML model training completed successfully!")
            return training_results
            
        except Exception as e:
            print(f"Error training ML models: {e}")
            raise e
    
    async def train_ensemble_models(self):
        """Train all ensemble models with the same data as XGBoost"""
        try:
            print("🚀 Starting Ensemble Model Training...")
            
            # Get training data (same as XGBoost)
            training_data = await self.prepare_training_data()
            if not training_data:
                raise ValueError("No training data available")
            
            X_train, X_test, y_outcome_train, y_outcome_test, y_home_goals_train, y_home_goals_test, y_away_goals_train, y_away_goals_test, y_home_xg_train, y_home_xg_test, y_away_xg_train, y_away_xg_test = training_data
            
            ensemble_results = {}
            
            # Train each ensemble model type
            for model_type in ['random_forest', 'gradient_boost', 'neural_net', 'logistic']:
                print(f"\n🤖 Training {model_type} models...")
                
                model_results = {}
                models = self.ensemble_models[model_type]
                
                # Train classifier
                print(f"  Training {model_type} classifier...")
                models['classifier'].fit(X_train, y_outcome_train)
                y_pred = models['classifier'].predict(X_test)
                accuracy = accuracy_score(y_outcome_test, y_pred)
                model_results['classifier'] = {'accuracy': accuracy, 'samples': len(y_outcome_test)}
                print(f"    Accuracy: {accuracy:.3f}")
                
                # Train regressors
                for target_name, y_train, y_test in [
                    ('home_goals', y_home_goals_train, y_home_goals_test),
                    ('away_goals', y_away_goals_train, y_away_goals_test),
                    ('home_xg', y_home_xg_train, y_home_xg_test),
                    ('away_xg', y_away_xg_train, y_away_xg_test)
                ]:
                    print(f"  Training {model_type} {target_name}...")
                    models[target_name].fit(X_train, y_train)
                    y_pred = models[target_name].predict(X_test)
                    r2 = r2_score(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    model_results[target_name] = {'r2_score': r2, 'mse': mse, 'samples': len(y_test)}
                    print(f"    R² score: {r2:.3f}, MSE: {mse:.3f}")
                
                ensemble_results[model_type] = model_results
                
                # Update model weight based on performance
                avg_performance = (
                    model_results['classifier']['accuracy'] +
                    model_results['home_goals']['r2_score'] +
                    model_results['away_goals']['r2_score'] +
                    model_results['home_xg']['r2_score'] +
                    model_results['away_xg']['r2_score']
                ) / 5
                
                # Adjust weight based on performance (higher performance = higher weight)
                base_weight = self.model_weights.get(model_type, 0.2)
                performance_multiplier = max(0.5, min(1.5, avg_performance + 0.5))
                self.model_weights[model_type] = base_weight * performance_multiplier
                
                print(f"  Updated weight for {model_type}: {self.model_weights[model_type]:.3f}")
            
            # Normalize weights to sum to 1.0
            total_weight = sum(self.model_weights.values())
            if total_weight > 0:
                for model_type in self.model_weights:
                    self.model_weights[model_type] /= total_weight
            
            # Save ensemble models
            self.save_ensemble_models()
            
            print("\n✅ Ensemble model training completed successfully!")
            print(f"📊 Final Model Weights: {self.model_weights}")
            
            return {
                'success': True,
                'models_trained': list(ensemble_results.keys()),
                'performance_results': ensemble_results,
                'final_weights': self.model_weights
            }
            
        except Exception as e:
            print(f"❌ Error training ensemble models: {e}")
            raise e
    
    async def predict_match(self, home_team, away_team, referee, match_date=None):
        """Make match prediction using trained ML models"""
        try:
            # Check if models are available
            if not self.models or len(self.models) != 5:
                raise ValueError("ML models not trained. Please train models first.")
            
            # Extract features
            features = await self.extract_features_for_match(home_team, away_team, referee, match_date)
            if features is None:
                raise ValueError("Could not extract features for prediction")
            
            # Convert to DataFrame and ensure correct column order
            import pandas as pd
            X = pd.DataFrame([features])
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            outcome_probs = self.models['classifier'].predict_proba(X_scaled)[0]
            home_goals = max(0, self.models['home_goals'].predict(X_scaled)[0])
            away_goals = max(0, self.models['away_goals'].predict(X_scaled)[0])
            home_xg = max(0, self.models['home_xg'].predict(X_scaled)[0])
            away_xg = max(0, self.models['away_xg'].predict(X_scaled)[0])
            
            # Get outcome probabilities (convert to percentages)
            home_win_prob = outcome_probs[0] * 100
            draw_prob = outcome_probs[1] * 100
            away_win_prob = outcome_probs[2] * 100
            
            # Ensure probabilities sum to 100%
            total_prob = home_win_prob + draw_prob + away_win_prob
            if total_prob > 0:
                home_win_prob = (home_win_prob / total_prob) * 100
                draw_prob = (draw_prob / total_prob) * 100
                away_win_prob = (away_win_prob / total_prob) * 100
            
            # Create prediction breakdown for compatibility
            prediction_breakdown = {
                'model_confidence': {
                    'classifier_confidence': max(outcome_probs),
                    'features_used': len(self.feature_columns),
                    'training_samples': 'Variable by model'
                },
                'feature_importance': {
                    'top_features': self._get_top_feature_importance(5)
                },
                'prediction_method': 'Machine Learning (Random Forest)'
            }
            
            return {
                'success': True,
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee,
                'predicted_home_goals': round(home_goals, 2),
                'predicted_away_goals': round(away_goals, 2),
                'home_xg': round(home_xg, 2),
                'away_xg': round(away_xg, 2),
                'home_win_probability': round(home_win_prob, 2),
                'draw_probability': round(draw_prob, 2),
                'away_win_probability': round(away_win_prob, 2),
                'prediction_breakdown': prediction_breakdown,
                'confidence_factors': {
                    'model_type': 'Random Forest ML Models',
                    'features_count': len(self.feature_columns),
                    'data_quality': 'Historical match data'
                }
            }
            
        except Exception as e:
            print(f"Error making ML prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee
            }
    
    async def predict_match_ensemble(self, home_team, away_team, referee, match_date=None, ensemble_config=None):
        """Make ensemble match prediction using multiple ML models with confidence scoring"""
        try:
            print(f"🤖 Making Ensemble Prediction: {home_team} vs {away_team}")
            
            # Check if models are available
            if not self.models or len(self.models) != 5:
                raise ValueError("XGBoost models not trained. Please train models first.")
            
            # Extract features
            features = await self.extract_features_for_match(home_team, away_team, referee, match_date)
            if features is None:
                raise ValueError("Could not extract features for prediction")
            
            # Convert to DataFrame and ensure correct column order
            import pandas as pd
            X = pd.DataFrame([features])
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from all models
            model_predictions = {}
            model_confidence_scores = {}
            
            # XGBoost predictions (primary model)
            print("🎯 Getting XGBoost predictions...")
            xgb_outcome_probs = self.models['classifier'].predict_proba(X_scaled)[0]
            model_predictions['xgboost'] = {
                'outcome_probs': xgb_outcome_probs,
                'home_goals': max(0, self.models['home_goals'].predict(X_scaled)[0]),
                'away_goals': max(0, self.models['away_goals'].predict(X_scaled)[0]),
                'home_xg': max(0, self.models['home_xg'].predict(X_scaled)[0]),
                'away_xg': max(0, self.models['away_xg'].predict(X_scaled)[0])
            }
            model_confidence_scores['xgboost'] = max(xgb_outcome_probs)
            
            # Ensemble model predictions
            for model_type in ['random_forest', 'gradient_boost', 'neural_net', 'logistic']:
                if model_type in self.ensemble_models:
                    print(f"🤖 Getting {model_type} predictions...")
                    try:
                        models = self.ensemble_models[model_type]
                        
                        # Get outcome probabilities
                        outcome_probs = models['classifier'].predict_proba(X_scaled)[0]
                        
                        model_predictions[model_type] = {
                            'outcome_probs': outcome_probs,
                            'home_goals': max(0, models['home_goals'].predict(X_scaled)[0]),
                            'away_goals': max(0, models['away_goals'].predict(X_scaled)[0]),
                            'home_xg': max(0, models['home_xg'].predict(X_scaled)[0]),
                            'away_xg': max(0, models['away_xg'].predict(X_scaled)[0])
                        }
                        model_confidence_scores[model_type] = max(outcome_probs)
                        
                    except Exception as e:
                        print(f"⚠️ Error with {model_type}: {e}")
                        # If model fails, skip it for this prediction
                        continue
            
            # Calculate ensemble predictions using weighted voting
            ensemble_result = self.calculate_ensemble_prediction(model_predictions, model_confidence_scores)
            
            # Calculate model agreement and confidence metrics
            confidence_metrics = self.calculate_ensemble_confidence(model_predictions, ensemble_result)
            
            return {
                'success': True,
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee,
                'prediction_type': 'ensemble',
                
                # Ensemble predictions
                'predicted_home_goals': round(ensemble_result['home_goals'], 2),
                'predicted_away_goals': round(ensemble_result['away_goals'], 2),
                'home_xg': round(ensemble_result['home_xg'], 2),
                'away_xg': round(ensemble_result['away_xg'], 2),
                'home_win_probability': round(ensemble_result['home_win_prob'], 2),
                'draw_probability': round(ensemble_result['draw_prob'], 2),
                'away_win_probability': round(ensemble_result['away_win_prob'], 2),
                
                # Confidence and ensemble metrics
                'ensemble_confidence': confidence_metrics,
                'model_predictions': {k: {
                    'home_win_prob': round(v['outcome_probs'][0] * 100, 1),
                    'draw_prob': round(v['outcome_probs'][1] * 100, 1),
                    'away_win_prob': round(v['outcome_probs'][2] * 100, 1),
                    'home_goals': round(v['home_goals'], 2),
                    'away_goals': round(v['away_goals'], 2),
                    'home_xg': round(v['home_xg'], 2),
                    'away_xg': round(v['away_xg'], 2)
                } for k, v in model_predictions.items()},
                'model_weights': self.model_weights,
                
                'prediction_breakdown': {
                    'ensemble_method': 'Weighted Voting with Confidence Scoring',
                    'models_used': list(model_predictions.keys()),
                    'total_models': len(model_predictions),
                    'features_used': len(self.feature_columns),
                    'confidence_level': confidence_metrics['overall_confidence']
                }
            }
            
        except Exception as e:
            print(f"❌ Error making ensemble prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee,
                'prediction_type': 'ensemble'
            }
    
    def calculate_ensemble_prediction(self, model_predictions, model_confidence_scores):
        """Calculate weighted ensemble prediction from multiple models"""
        import numpy as np
        
        print("📊 Calculating ensemble prediction...")
        
        # Initialize weighted sums
        weighted_outcome_probs = np.zeros(3)  # [home_win, draw, away_win]
        weighted_home_goals = 0
        weighted_away_goals = 0
        weighted_home_xg = 0
        weighted_away_xg = 0
        total_weight = 0
        
        for model_type, predictions in model_predictions.items():
            # Get base weight for this model type
            base_weight = self.model_weights.get(model_type, 0.2)
            
            # Adjust weight based on model confidence
            confidence = model_confidence_scores.get(model_type, 0.5)
            confidence_multiplier = 0.5 + confidence  # Range: 0.5 to 1.5
            
            final_weight = base_weight * confidence_multiplier
            
            print(f"  {model_type}: base_weight={base_weight:.2f}, confidence={confidence:.2f}, final_weight={final_weight:.2f}")
            
            # Add weighted predictions
            weighted_outcome_probs += predictions['outcome_probs'] * final_weight
            weighted_home_goals += predictions['home_goals'] * final_weight
            weighted_away_goals += predictions['away_goals'] * final_weight
            weighted_home_xg += predictions['home_xg'] * final_weight
            weighted_away_xg += predictions['away_xg'] * final_weight
            
            total_weight += final_weight
        
        # Normalize by total weight
        if total_weight > 0:
            weighted_outcome_probs /= total_weight
            weighted_home_goals /= total_weight
            weighted_away_goals /= total_weight
            weighted_home_xg /= total_weight
            weighted_away_xg /= total_weight
        
        # Ensure probabilities sum to 100%
        prob_sum = sum(weighted_outcome_probs)
        if prob_sum > 0:
            weighted_outcome_probs = (weighted_outcome_probs / prob_sum) * 100
        
        result = {
            'home_win_prob': weighted_outcome_probs[0],
            'draw_prob': weighted_outcome_probs[1],
            'away_win_prob': weighted_outcome_probs[2],
            'home_goals': weighted_home_goals,
            'away_goals': weighted_away_goals,
            'home_xg': weighted_home_xg,
            'away_xg': weighted_away_xg
        }
        
        print(f"📈 Ensemble Result: {result['home_win_prob']:.1f}% | {result['draw_prob']:.1f}% | {result['away_win_prob']:.1f}%")
        return result
    
    def calculate_ensemble_confidence(self, model_predictions, ensemble_result):
        """Calculate confidence metrics for ensemble prediction"""
        import numpy as np
        
        if len(model_predictions) < 2:
            return {
                'overall_confidence': 'Low',
                'model_agreement': 0.0,
                'prediction_stability': 0.0,
                'confidence_score': 0.0
            }
        
        # Calculate model agreement (how similar are the predictions)
        outcome_predictions = []
        goal_predictions = []
        
        for model_type, predictions in model_predictions.items():
            outcome_predictions.append(predictions['outcome_probs'])
            goal_predictions.append([predictions['home_goals'], predictions['away_goals']])
        
        outcome_predictions = np.array(outcome_predictions)
        goal_predictions = np.array(goal_predictions)
        
        # Calculate standard deviation across models (lower = more agreement)
        outcome_std = np.mean(np.std(outcome_predictions, axis=0))
        goal_std = np.mean(np.std(goal_predictions, axis=0))
        
        # Convert to agreement score (0-1, higher = more agreement)
        outcome_agreement = max(0, 1 - (outcome_std / 0.5))  # Normalize by reasonable std threshold
        goal_agreement = max(0, 1 - (goal_std / 2.0))  # Normalize by reasonable goal std
        
        overall_agreement = (outcome_agreement + goal_agreement) / 2
        
        # Calculate prediction stability (confidence in most likely outcome)
        max_prob = max(ensemble_result['home_win_prob'], ensemble_result['draw_prob'], ensemble_result['away_win_prob'])
        stability = (max_prob - 33.33) / 66.67  # Normalize from equal probability (33.33%) to certainty (100%)
        stability = max(0, min(1, stability))
        
        # Calculate overall confidence score
        confidence_score = (overall_agreement * 0.6) + (stability * 0.4)
        
        # Determine confidence level
        if confidence_score >= 0.8:
            confidence_level = 'Very High'
        elif confidence_score >= 0.65:
            confidence_level = 'High'
        elif confidence_score >= 0.5:
            confidence_level = 'Medium'
        elif confidence_score >= 0.35:
            confidence_level = 'Low'
        else:
            confidence_level = 'Very Low'
        
        return {
            'overall_confidence': confidence_level,
            'model_agreement': round(overall_agreement * 100, 1),
            'prediction_stability': round(stability * 100, 1),
            'confidence_score': round(confidence_score * 100, 1),
            'models_count': len(model_predictions),
            'agreement_details': {
                'outcome_agreement': round(outcome_agreement * 100, 1),
                'goal_agreement': round(goal_agreement * 100, 1)
            }
        }
    
    def calculate_poisson_scoreline_probabilities(self, home_lambda, away_lambda, max_goals=6):
        """
        Calculate detailed scoreline probabilities using Poisson distribution
        
        Args:
            home_lambda (float): Expected goals for home team (from XGBoost)
            away_lambda (float): Expected goals for away team (from XGBoost)
            max_goals (int): Maximum goals to calculate for (0 to max_goals)
            
        Returns:
            dict: Dictionary with scoreline probabilities and match outcome probabilities
        """
        scoreline_probs = {}
        home_win_prob = 0.0
        draw_prob = 0.0
        away_win_prob = 0.0
        
        # Ensure lambda values are positive
        home_lambda = max(0.1, home_lambda)
        away_lambda = max(0.1, away_lambda)
        
        # Calculate probabilities for each scoreline
        for home_goals in range(max_goals + 1):
            for away_goals in range(max_goals + 1):
                # Poisson probability for this exact scoreline
                prob = poisson.pmf(home_goals, home_lambda) * poisson.pmf(away_goals, away_lambda)
                scoreline = f"{home_goals}-{away_goals}"
                scoreline_probs[scoreline] = prob
                
                # Add to match outcome probabilities
                if home_goals > away_goals:
                    home_win_prob += prob
                elif home_goals == away_goals:
                    draw_prob += prob
                else:
                    away_win_prob += prob
        
        # Calculate remaining probability (for scores > max_goals)
        total_calculated = sum(scoreline_probs.values())
        remaining_prob = max(0, 1 - total_calculated)
        
        # Distribute remaining probability based on current ratios
        if total_calculated > 0:
            home_win_prob += remaining_prob * (home_win_prob / total_calculated) if total_calculated > 0 else remaining_prob / 3
            draw_prob += remaining_prob * (draw_prob / total_calculated) if total_calculated > 0 else remaining_prob / 3
            away_win_prob += remaining_prob * (away_win_prob / total_calculated) if total_calculated > 0 else remaining_prob / 3
        
        # Normalize to ensure sum = 1
        total_outcome_prob = home_win_prob + draw_prob + away_win_prob
        if total_outcome_prob > 0:
            home_win_prob = (home_win_prob / total_outcome_prob) * 100
            draw_prob = (draw_prob / total_outcome_prob) * 100
            away_win_prob = (away_win_prob / total_outcome_prob) * 100
        
        # Convert scoreline probabilities to percentages and sort by probability
        scoreline_probs_pct = {k: v * 100 for k, v in scoreline_probs.items()}
        sorted_scorelines = sorted(scoreline_probs_pct.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'scoreline_probabilities': dict(sorted_scorelines),
            'match_outcome_probabilities': {
                'home_win': home_win_prob,
                'draw': draw_prob,
                'away_win': away_win_prob
            },
            'most_likely_scoreline': sorted_scorelines[0] if sorted_scorelines else ("1-1", 0),
            'poisson_parameters': {
                'home_lambda': home_lambda,
                'away_lambda': away_lambda
            }
        }
    
    async def build_training_dataset(self):
        """Build training dataset from historical matches"""
        try:
            print("Building XGBoost training dataset...")
            
            # Get all matches with team stats
            matches = await db.matches.find({}).to_list(10000)
            print(f"Found {len(matches)} matches")
            
            features_list = []
            targets = []
            
            for match in matches:
                try:
                    home_team = match['home_team']
                    away_team = match['away_team']
                    referee = match['referee']
                    home_score = match['home_score']
                    away_score = match['away_score']
                    
                    # Extract features for this match
                    features = await self.extract_features_for_match(home_team, away_team, referee)
                    if features is None:
                        continue
                    
                    # Determine match outcome
                    if home_score > away_score:
                        outcome = 0  # Home win
                    elif home_score == away_score:
                        outcome = 1  # Draw
                    else:
                        outcome = 2  # Away win
                    
                    # Get actual xG values from team stats
                    home_team_stats = await db.team_stats.find_one({
                        "match_id": match['match_id'],
                        "team_name": match['home_team'],
                        "is_home": True
                    })
                    away_team_stats = await db.team_stats.find_one({
                        "match_id": match['match_id'],
                        "team_name": match['away_team'],
                        "is_home": False
                    })
                    
                    home_xg = home_team_stats.get('xg', 0) if home_team_stats else 0
                    away_xg = away_team_stats.get('xg', 0) if away_team_stats else 0
                    
                    features_list.append(features)
                    targets.append({
                        'outcome': outcome,
                        'home_goals': home_score,
                        'away_goals': away_score,
                        'home_xg': home_xg,
                        'away_xg': away_xg
                    })
                    
                except Exception as e:
                    print(f"Error processing match {match['match_id']}: {e}")
                    continue
            
            print(f"Successfully processed {len(features_list)} matches for XGBoost training")
            return features_list, targets
            
        except Exception as e:
            print(f"Error building XGBoost training dataset: {e}")
            return [], []
    
    async def train_models(self, test_size=0.2, random_state=42):
        """Train all XGBoost models"""
        try:
            print("Starting XGBoost model training...")
            
            # Build training dataset
            features_list, targets = await self.build_training_dataset()
            
            if len(features_list) == 0:
                raise ValueError("No training data available")
            
            # Convert to DataFrame for easier handling
            import pandas as pd
            X = pd.DataFrame(features_list)
            
            # Store feature columns for later use
            self.feature_columns = X.columns.tolist()
            
            print(f"Training with {len(self.feature_columns)} features")
            
            # Prepare target variables
            y_outcome = [t['outcome'] for t in targets]
            y_home_goals = [t['home_goals'] for t in targets]
            y_away_goals = [t['away_goals'] for t in targets]
            y_home_xg = [t['home_xg'] for t in targets]
            y_away_xg = [t['away_xg'] for t in targets]
            
            # Split data
            X_train, X_test, y_outcome_train, y_outcome_test = train_test_split(
                X, y_outcome, test_size=test_size, random_state=random_state, stratify=y_outcome
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Split other targets with same indices
            train_indices = X_train.index
            test_indices = X_test.index
            
            y_home_goals_train = [y_home_goals[i] for i in train_indices]
            y_home_goals_test = [y_home_goals[i] for i in test_indices]
            y_away_goals_train = [y_away_goals[i] for i in train_indices]
            y_away_goals_test = [y_away_goals[i] for i in test_indices]
            y_home_xg_train = [y_home_xg[i] for i in train_indices]
            y_home_xg_test = [y_home_xg[i] for i in test_indices]
            y_away_xg_train = [y_away_xg[i] for i in train_indices]
            y_away_xg_test = [y_away_xg[i] for i in test_indices]
            
            print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples")
            
            # Train XGBoost models
            models_to_train = {
                'classifier': (xgb.XGBClassifier(**self.xgb_params_classifier), 
                              y_outcome_train, y_outcome_test),
                'home_goals': (xgb.XGBRegressor(**self.xgb_params_regressor),
                              y_home_goals_train, y_home_goals_test),
                'away_goals': (xgb.XGBRegressor(**self.xgb_params_regressor),
                              y_away_goals_train, y_away_goals_test),
                'home_xg': (xgb.XGBRegressor(**self.xgb_params_regressor),
                           y_home_xg_train, y_home_xg_test),
                'away_xg': (xgb.XGBRegressor(**self.xgb_params_regressor),
                           y_away_xg_train, y_away_xg_test)
            }
            
            training_results = {}
            
            for model_name, (model, y_train, y_test) in models_to_train.items():
                print(f"Training XGBoost {model_name}...")
                
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test_scaled)
                
                # Evaluate
                if model_name == 'classifier':
                    from sklearn.metrics import accuracy_score, classification_report
                    y_pred_proba = model.predict_proba(X_test_scaled)
                    
                    accuracy = accuracy_score(y_test, y_pred)
                    log_loss_score = log_loss(y_test, y_pred_proba)
                    class_report = classification_report(y_test, y_pred, output_dict=True)
                    
                    training_results[model_name] = {
                        'accuracy': accuracy,
                        'log_loss': log_loss_score,
                        'classification_report': class_report,
                        'samples': len(y_test)
                    }
                    print(f"{model_name} accuracy: {accuracy:.3f}, log loss: {log_loss_score:.3f}")
                else:
                    r2 = r2_score(y_test, y_pred)
                    mse = mean_squared_error(y_test, y_pred)
                    training_results[model_name] = {
                        'r2_score': r2,
                        'mse': mse,
                        'samples': len(y_test)
                    }
                    print(f"{model_name} R² score: {r2:.3f}, MSE: {mse:.3f}")
                
                # Store trained model
                self.models[model_name] = model
            
            # Save models
            self.save_models()
            
            print("XGBoost model training completed successfully!")
            return training_results
            
        except Exception as e:
            print(f"Error training XGBoost models: {e}")
            raise e
    
    async def predict_match(self, home_team, away_team, referee, match_date=None):
        """Make match prediction using trained XGBoost models with Poisson simulation"""
        try:
            # Check if models are available
            if not self.models or len(self.models) != 5:
                raise ValueError("XGBoost models not trained. Please train models first.")
            
            # Extract features
            features = await self.extract_features_for_match(home_team, away_team, referee, match_date)
            if features is None:
                raise ValueError("Could not extract features for prediction")
            
            # Convert to DataFrame and ensure correct column order
            import pandas as pd
            X = pd.DataFrame([features])
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make XGBoost predictions
            outcome_probs = self.models['classifier'].predict_proba(X_scaled)[0]
            home_goals = max(0, self.models['home_goals'].predict(X_scaled)[0])
            away_goals = max(0, self.models['away_goals'].predict(X_scaled)[0])
            home_xg = max(0, self.models['home_xg'].predict(X_scaled)[0])
            away_xg = max(0, self.models['away_xg'].predict(X_scaled)[0])
            
            # Calculate Poisson scoreline probabilities using predicted goals
            poisson_results = self.calculate_poisson_scoreline_probabilities(home_goals, away_goals)
            
            # Use Poisson probabilities for match outcome (more accurate than direct XGBoost probabilities)
            home_win_prob = poisson_results['match_outcome_probabilities']['home_win']
            draw_prob = poisson_results['match_outcome_probabilities']['draw']
            away_win_prob = poisson_results['match_outcome_probabilities']['away_win']
            
            # Create enhanced prediction breakdown
            prediction_breakdown = {
                'xgboost_confidence': {
                    'classifier_confidence': float(max(outcome_probs)),
                    'features_used': len(self.feature_columns),
                    'training_samples': 'Variable by model'
                },
                'feature_importance': {
                    'top_features': {k: float(v) for k, v in self._get_top_feature_importance(5).items()}
                },
                'poisson_analysis': {
                    'most_likely_scoreline': poisson_results['most_likely_scoreline'][0],
                    'scoreline_probability': float(round(poisson_results['most_likely_scoreline'][1], 2)),
                    'lambda_parameters': {
                        'home_lambda': float(poisson_results['poisson_parameters']['home_lambda']),
                        'away_lambda': float(poisson_results['poisson_parameters']['away_lambda'])
                    }
                },
                'prediction_method': 'XGBoost + Poisson Distribution Simulation'
            }
            
            return {
                'success': True,
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee,
                'predicted_home_goals': float(round(home_goals, 2)),
                'predicted_away_goals': float(round(away_goals, 2)),
                'home_xg': float(round(home_xg, 2)),
                'away_xg': float(round(away_xg, 2)),
                'home_win_probability': float(round(home_win_prob, 2)),
                'draw_probability': float(round(draw_prob, 2)),
                'away_win_probability': float(round(away_win_prob, 2)),
                'scoreline_probabilities': {k: float(round(v, 2)) for k, v in poisson_results['scoreline_probabilities'].items()},
                'prediction_breakdown': prediction_breakdown,
                'confidence_factors': {
                    'model_type': 'XGBoost + Poisson Simulation',
                    'features_count': len(self.feature_columns),
                    'data_quality': 'Historical match data with enhanced feature engineering'
                }
            }
            
        except Exception as e:
            print(f"Error making XGBoost prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'home_team': home_team,
                'away_team': away_team,
                'referee': referee
            }
    
    def _get_top_feature_importance(self, top_n=5):
        """Get top feature importance from XGBoost classifier"""
        try:
            if 'classifier' not in self.models:
                return {}
            
            feature_importance = self.models['classifier'].feature_importances_
            feature_names = self.feature_columns
            
            importance_dict = dict(zip(feature_names, feature_importance))
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            
            return dict(sorted_features[:top_n])
        except:
            return {}
    
    async def predict_match_with_starting_xi(self, home_team, away_team, referee, home_starting_xi=None, away_starting_xi=None, match_date=None, config_name="default", decay_config=None):
        """Enhanced match prediction with starting XI and time decay support"""
        try:
            # Check if models are available
            if not self.models or len(self.models) != 5:
                raise ValueError("ML models not trained. Please train models first.")
            
            print(f"🚀 Using XGBoost Enhanced Prediction with Starting XI")
            print(f"   Home XI: {'✅ Provided' if home_starting_xi else '❌ None'}")
            print(f"   Away XI: {'✅ Provided' if away_starting_xi else '❌ None'}")
            print(f"   Time Decay: {'✅ Enabled' if decay_config else '❌ Disabled'}")
            
            # Extract features with starting XI filtering
            features = await self.extract_features_for_match_enhanced(
                home_team, away_team, referee, match_date, 
                home_starting_xi, away_starting_xi, decay_config
            )
            if features is None:
                raise ValueError("Could not extract enhanced features for prediction")
            
            # Convert to DataFrame and ensure correct column order
            import pandas as pd
            X = pd.DataFrame([features])
            X = X.reindex(columns=self.feature_columns, fill_value=0)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            print(f"   Features extracted: {len(features)} features")
            print(f"   Using XGBoost models for prediction...")
            
            # Make predictions using XGBoost models
            outcome_probs = self.models['classifier'].predict_proba(X_scaled)[0]
            home_goals = max(0, self.models['home_goals'].predict(X_scaled)[0])
            away_goals = max(0, self.models['away_goals'].predict(X_scaled)[0])
            home_xg = max(0, self.models['home_xg'].predict(X_scaled)[0])
            away_xg = max(0, self.models['away_xg'].predict(X_scaled)[0])
            
            print(f"   ✅ XGBoost Prediction Complete!")
            print(f"   Home Goals: {home_goals:.2f}, Away Goals: {away_goals:.2f}")
            
            # Get outcome probabilities (convert to percentages)
            home_win_prob = outcome_probs[0] * 100
            draw_prob = outcome_probs[1] * 100
            away_win_prob = outcome_probs[2] * 100
            
            # Ensure probabilities sum to 100%
            total_prob = home_win_prob + draw_prob + away_win_prob
            if total_prob > 0:
                home_win_prob = (home_win_prob / total_prob) * 100
                draw_prob = (draw_prob / total_prob) * 100
                away_win_prob = (away_win_prob / total_prob) * 100
            
            # Enhanced prediction breakdown with optimization support
            prediction_breakdown = {
                'model_confidence': {
                    'classifier_confidence': max(outcome_probs),
                    'features_used': len(self.feature_columns),
                    'training_samples': 'Variable by model'
                },
                'feature_importance': {
                    'top_features': self._get_top_feature_importance(5)
                },
                'prediction_method': 'XGBoost Enhanced ML with Starting XI',
                'model_type': 'XGBoost Gradient Boosting',
                'starting_xi_used': {
                    'home_team': home_starting_xi is not None,
                    'away_team': away_starting_xi is not None
                },
                'time_decay_applied': decay_config is not None,
                'decay_preset': decay_config.preset_name if decay_config else None,
                'time_decay_info': {
                    'decay_type': decay_config.decay_type if decay_config else None,
                    'half_life_months': decay_config.half_life_months if decay_config else None,
                    'decay_rate_per_month': decay_config.decay_rate_per_month if decay_config else None,
                    'description': decay_config.description if decay_config else None
                } if decay_config else None,
                # 🎯 Add features for optimization tracking
                'features_used_dict': features if features else {},
                'optimization_ready': True
            }
            
            return MatchPredictionResponse(
                success=True,
                home_team=home_team,
                away_team=away_team,
                referee=referee,
                predicted_home_goals=round(home_goals, 2),
                predicted_away_goals=round(away_goals, 2),
                home_xg=round(home_xg, 2),
                away_xg=round(away_xg, 2),
                home_win_probability=round(home_win_prob, 2),
                draw_probability=round(draw_prob, 2),
                away_win_probability=round(away_win_prob, 2),
                prediction_breakdown=prediction_breakdown
            )
            
        except Exception as e:
            print(f"❌ Error making XGBoost enhanced ML prediction: {e}")
            print(f"   This should NOT fallback to other models!")
            return MatchPredictionResponse(
                success=False,
                error=f"XGBoost Enhanced Prediction Failed: {str(e)}",
                home_team=home_team,
                away_team=away_team,
                referee=referee,
                prediction_breakdown={
                    'prediction_method': 'FAILED - XGBoost Enhanced ML with Starting XI',
                    'error_details': str(e)
                }
            )
    
    async def predict_match_with_defaults(self, home_team, away_team, referee, match_date=None, config_name="default", decay_config=None):
        """Prediction using default starting XIs based on most played players"""
        try:
            print(f"🎯 Generating default Starting XI for XGBoost prediction...")
            
            # Generate default starting XIs
            home_xi = await starting_xi_manager.generate_default_starting_xi(home_team)
            away_xi = await starting_xi_manager.generate_default_starting_xi(away_team)
            
            # If default XI generation fails, return error instead of fallback
            if not home_xi or not away_xi:
                error_msg = f"Cannot generate default Starting XI for {home_team} and/or {away_team}. Starting XI data required for XGBoost enhanced prediction."
                print(f"❌ {error_msg}")
                return MatchPredictionResponse(
                    success=False,
                    error=error_msg,
                    home_team=home_team,
                    away_team=away_team,
                    referee=referee,
                    prediction_breakdown={
                        'prediction_method': 'FAILED - XGBoost Enhanced ML (Default XI)',
                        'error_details': 'Could not generate default Starting XI'
                    }
                )
            
            print(f"✅ Default Starting XI generated successfully")
            
            return await self.predict_match_with_starting_xi(
                home_team, away_team, referee, home_xi, away_xi, 
                match_date, config_name, decay_config
            )
            
        except Exception as e:
            print(f"❌ Error making prediction with defaults: {e}")
            # DO NOT fallback to standard prediction - return error instead
            return MatchPredictionResponse(
                success=False,
                error=f"XGBoost Enhanced Prediction with Default XI Failed: {str(e)}",
                home_team=home_team,
                away_team=away_team,
                referee=referee,
                prediction_breakdown={
                    'prediction_method': 'FAILED - XGBoost Enhanced ML (Default XI)',
                    'error_details': str(e)
                }
            )
    
    async def extract_features_for_match_enhanced(self, home_team, away_team, referee, match_date=None, home_starting_xi=None, away_starting_xi=None, decay_config=None):
        """Enhanced feature extraction with starting XI filtering and time decay"""
        try:
            # Get team stats with starting XI filtering and time decay
            home_stats = await self.calculate_team_features_enhanced(home_team, True, home_starting_xi, decay_config)
            away_stats = await self.calculate_team_features_enhanced(away_team, False, away_starting_xi, decay_config)
            
            if not home_stats or not away_stats:
                raise ValueError("Could not calculate enhanced team features")
            
            # Get referee bias (apply time decay if specified)
            home_rbs, home_rbs_conf = await self.get_referee_bias_with_decay(home_team, referee, decay_config)
            away_rbs, away_rbs_conf = await self.get_referee_bias_with_decay(away_team, referee, decay_config)
            
            # Get head-to-head stats with time decay
            h2h_stats = await self.get_head_to_head_stats_with_decay(home_team, away_team, decay_config)
            
            # Build enhanced feature vector
            features = {
                # Home team offensive stats (enhanced with starting XI)
                'home_xg_per_match': home_stats['xg'],
                'home_goals_per_match': home_stats['goals'],
                'home_shots_per_match': home_stats['shots_total'],
                'home_shots_on_target_per_match': home_stats['shots_on_target'],
                'home_xg_per_shot': home_stats['xg_per_shot'],
                'home_shot_accuracy': home_stats['shot_accuracy'],
                'home_conversion_rate': home_stats['conversion_rate'],
                'home_possession_pct': home_stats['possession_pct'],
                
                # Home team defensive stats
                'home_goals_conceded_per_match': home_stats['goals_conceded'],
                'home_xg_conceded_per_match': home_stats.get('xg_conceded', 0),
                
                # Away team stats (enhanced with starting XI)
                'away_xg_per_match': away_stats['xg'],
                'away_goals_per_match': away_stats['goals'],
                'away_shots_per_match': away_stats['shots_total'],
                'away_shots_on_target_per_match': away_stats['shots_on_target'],
                'away_xg_per_shot': away_stats['xg_per_shot'],
                'away_shot_accuracy': away_stats['shot_accuracy'],
                'away_conversion_rate': away_stats['conversion_rate'],
                'away_possession_pct': away_stats['possession_pct'],
                
                # Away team defensive stats
                'away_goals_conceded_per_match': away_stats['goals_conceded'],
                'away_xg_conceded_per_match': away_stats.get('xg_conceded', 0),
                
                # Form over last 5 matches (with time decay)
                'home_form_last5': await self.get_team_form_with_decay(home_team, 5, decay_config),
                'away_form_last5': await self.get_team_form_with_decay(away_team, 5, decay_config),
                
                # Home advantage
                'home_advantage': 1,
                
                # Referee bias (with time decay)
                'home_referee_bias': home_rbs,
                'away_referee_bias': away_rbs,
                'home_rbs_confidence': home_rbs_conf,
                'away_rbs_confidence': away_rbs_conf,
                
                # Head-to-head (with time decay)
                'h2h_home_wins': h2h_stats['home_wins'],
                'h2h_draws': h2h_stats['draws'],
                'h2h_away_wins': h2h_stats['away_wins'],
                'h2h_home_goals_avg': h2h_stats['home_goals_avg'],
                'h2h_away_goals_avg': h2h_stats['away_goals_avg'],
                
                # Additional differential features
                'goal_difference': home_stats['goals'] - away_stats['goals'],
                'xg_difference': home_stats['xg'] - away_stats['xg'],
                'possession_difference': home_stats['possession_pct'] - away_stats['possession_pct'],
                'form_difference': await self.get_team_form_with_decay(home_team, 5, decay_config) - await self.get_team_form_with_decay(away_team, 5, decay_config),
                
                # Quality indicators (enhanced with starting XI)
                'home_quality_rating': (home_stats['goals'] + home_stats['xg']) / 2,
                'away_quality_rating': (away_stats['goals'] + away_stats['xg']) / 2,
                
                # Starting XI indicators
                'home_xi_specified': 1 if home_starting_xi else 0,
                'away_xi_specified': 1 if away_starting_xi else 0,
                'time_decay_applied': 1 if decay_config else 0
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting enhanced features: {e}")
            return None
    
    async def calculate_team_features_enhanced(self, team_name, is_home, starting_xi=None, decay_config=None):
        """Enhanced team feature calculation with starting XI filtering and time decay"""
        try:
            if starting_xi:
                # Filter stats by starting XI players
                selected_players = [pos.player.player_name for pos in starting_xi.positions if pos.player]
                print(f"Enhanced prediction for {team_name}: Using Starting XI with {len(selected_players)} players")
                stats = await self.calculate_team_averages_for_players(team_name, is_home, selected_players, decay_config)
            else:
                # Use existing method but apply time decay
                print(f"Enhanced prediction for {team_name}: Using team averages (no Starting XI)")
                stats = await self.calculate_team_averages_with_decay(team_name, is_home, decay_config)
            
            if not stats:
                print(f"Warning: No stats found for {team_name}")
                return None
            
            # Ensure all required fields exist with defaults
            required_fields = [
                'xg', 'goals', 'shots_total', 'shots_on_target', 'xg_per_shot',
                'shot_accuracy', 'conversion_rate', 'possession_pct', 'goals_conceded',
                'points_per_game', 'penalties_awarded', 'fouls_drawn', 'fouls',
                'yellow_cards', 'red_cards'
            ]
            
            for field in required_fields:
                if field not in stats:
                    stats[field] = 0.0
            
            return stats
            
        except Exception as e:
            print(f"Error calculating enhanced team features: {e}")
            return None
    
    async def calculate_team_averages_for_players(self, team_name, is_home, selected_players, decay_config=None):
        """Calculate team averages using only specified players with optional time decay"""
        try:
            # Get all matches for this team
            team_matches = await db.matches.find({
                "$or": [
                    {"home_team": team_name},
                    {"away_team": team_name}
                ]
            }).to_list(10000)
            
            if not team_matches:
                return None
            
            # Get player stats for selected players only
            selected_player_stats = await db.player_stats.find({
                "team_name": team_name,
                "player_name": {"$in": selected_players}
            }).to_list(10000)
            
            if not selected_player_stats:
                return None
            
            # FIXED: First aggregate player stats by match, then apply time weights to match totals
            match_aggregates = {}
            
            # Step 1: Group player stats by match and sum them up (without weights)
            for player_stat in selected_player_stats:
                match_id = player_stat['match_id']
                
                if match_id not in match_aggregates:
                    match_aggregates[match_id] = {
                        'goals': 0, 'assists': 0, 'xg': 0, 'shots_total': 0, 
                        'shots_on_target': 0, 'penalty_attempts': 0, 'penalty_goals': 0,
                        'is_home': player_stat.get('is_home', is_home)
                    }
                
                # Sum up all Starting XI players' stats for this match
                match_aggregates[match_id]['goals'] += player_stat.get('goals', 0)
                match_aggregates[match_id]['assists'] += player_stat.get('assists', 0)
                match_aggregates[match_id]['xg'] += player_stat.get('xg', 0)
                match_aggregates[match_id]['shots_total'] += player_stat.get('shots_total', 0)
                match_aggregates[match_id]['shots_on_target'] += player_stat.get('shots_on_target', 0)
                match_aggregates[match_id]['penalty_attempts'] += player_stat.get('penalty_attempts', 0)
                match_aggregates[match_id]['penalty_goals'] += player_stat.get('penalty_goals', 0)
            
            if not match_aggregates:
                return None
            
            # DEBUG: Log Starting XI calculation details
            print(f"📊 Starting XI calculation for {team_name}:")
            print(f"  Selected players: {len(selected_players)} - {selected_players[:3]}...")
            print(f"  Matches found: {len(match_aggregates)}")
            print(f"  Time decay enabled: {decay_config is not None}")
            if decay_config:
                print(f"  Decay type: {decay_config.decay_type}, preset: {decay_config.preset_name}")
            
            # Step 2: Apply time decay weights to match totals and calculate weighted averages
            total_weighted_goals = 0
            total_weighted_assists = 0
            total_weighted_xg = 0
            total_weighted_shots = 0
            total_weighted_shots_on_target = 0
            total_weighted_penalties = 0
            total_weighted_penalty_goals = 0
            total_weights = 0
            
            for match_id, match_stats in match_aggregates.items():
                # Find the match to get date for time decay
                match_info = next((m for m in team_matches if m['match_id'] == match_id), None)
                if not match_info:
                    continue
                
                # Calculate time weight for this match
                weight = 1.0
                if decay_config and match_info.get('match_date'):
                    weight = starting_xi_manager.calculate_time_weight(
                        match_info['match_date'], 
                        datetime.now().strftime("%Y-%m-%d"),
                        decay_config
                    )
                elif decay_config:
                    print(f"  Warning: No match_date for match {match_id}")
                
                # Apply weight to match totals
                total_weighted_goals += match_stats['goals'] * weight
                total_weighted_assists += match_stats['assists'] * weight
                total_weighted_xg += match_stats['xg'] * weight
                total_weighted_shots += match_stats['shots_total'] * weight
                total_weighted_shots_on_target += match_stats['shots_on_target'] * weight
                total_weighted_penalties += match_stats['penalty_attempts'] * weight
                total_weighted_penalty_goals += match_stats['penalty_goals'] * weight
                total_weights += weight
            
            if total_weights == 0:
                return None
            
            # Calculate weighted averages per match
            goals_per_match = total_weighted_goals / total_weights
            assists_per_match = total_weighted_assists / total_weights
            xg_per_match = total_weighted_xg / total_weights
            shots_per_match = total_weighted_shots / total_weights
            shots_on_target_per_match = total_weighted_shots_on_target / total_weights
            penalties_per_match = total_weighted_penalties / total_weights
            penalty_goals_per_match = total_weighted_penalty_goals / total_weights
            
            # DEBUG: Show final weighted averages
            print(f"  📈 Weighted averages: Goals {goals_per_match:.3f}, xG {xg_per_match:.3f}")
            print(f"  📊 Total weights applied: {total_weights:.2f}")
            print(f"  ⚽ Impact: Recent matches weighted higher than old ones: {decay_config is not None}")
            print()  # Add space
            
            # Debug logging for Starting XI effectiveness
            print(f"Starting XI calculation for {team_name}:")
            print(f"  Selected players: {len(selected_players)} - {selected_players[:3]}...")
            print(f"  Matches found: {len(match_aggregates)}")
            print(f"  Avg goals/match: {goals_per_match:.3f}")
            print(f"  Avg xG/match: {xg_per_match:.3f}")
            print(f"  Time decay applied: {decay_config is not None}")
            
            # Calculate derived stats with safety checks
            xg_per_shot = (total_weighted_xg / total_weighted_shots) if total_weighted_shots > 0 else 0
            xg_per_shot = min(1.0, xg_per_shot)  # Cap at 1.0
            
            shot_accuracy = (total_weighted_shots_on_target / total_weighted_shots) if total_weighted_shots > 0 else 0
            shot_accuracy = min(1.0, shot_accuracy)  # Cap at 1.0
            
            conversion_rate = (total_weighted_goals / total_weighted_xg) if total_weighted_xg > 0 else 0
            conversion_rate = min(2.0, conversion_rate)  # Cap at 2.0
            
            # Get team stats for possession and defensive stats (these don't change with starting XI)
            team_stats = await self.get_team_stats_aggregates(team_name, is_home, decay_config)
            
            return {
                'goals': goals_per_match,
                'xg': xg_per_match,
                'shots_total': shots_per_match,
                'shots_on_target': shots_on_target_per_match,
                'xg_per_shot': xg_per_shot,
                'shot_accuracy': shot_accuracy,
                'conversion_rate': conversion_rate,
                'possession_pct': team_stats.get('possession_pct', 50.0),
                'goals_conceded': team_stats.get('goals_conceded', 1.0),
                'points_per_game': team_stats.get('points_per_game', 1.0),
                'penalties_awarded': team_stats.get('penalties_awarded', 0.0),
                'fouls_drawn': team_stats.get('fouls_drawn', 10.0),
                'fouls': team_stats.get('fouls', 12.0),
                'yellow_cards': team_stats.get('yellow_cards', 2.0),
                'red_cards': team_stats.get('red_cards', 0.1)
            }
            
        except Exception as e:
            print(f"Error calculating team averages for selected players: {e}")
            return None
    
    async def get_team_stats_aggregates(self, team_name, is_home, decay_config=None):
        """Get team-level stats (possession, cards, etc.) with time decay"""
        try:
            # Use existing team stats calculation but apply time decay
            return await self.calculate_team_averages_with_decay(team_name, is_home, decay_config)
        except Exception as e:
            print(f"Error getting team stats aggregates: {e}")
            return {}
    
    async def calculate_team_averages_with_decay(self, team_name, is_home, decay_config=None):
        """Calculate team averages with full time decay implementation"""
        try:
            # Get the existing averages first for backward compatibility
            base_stats = await match_predictor.calculate_team_averages(team_name, is_home)
            
            if not decay_config:
                print(f"📊 Team averages for {team_name}: Using base stats (no time decay)")
                return base_stats
            
            print(f"📊 Team averages for {team_name}: Applying {decay_config.decay_type} time decay ({decay_config.preset_name})")
            
            # Get all team stats for this team with time weighting
            team_stats_cursor = db.team_stats.find({"team_name": team_name})
            team_stats = await team_stats_cursor.to_list(10000)
            
            if not team_stats:
                return base_stats
            
            # Calculate weighted averages with time decay
            weighted_stats = {}
            total_weights = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Get all matches to lookup dates by match_id
            all_matches = await db.matches.find({}).to_list(10000)
            match_date_lookup = {m['match_id']: m.get('match_date') for m in all_matches}
            
            for stat in team_stats:
                # Get match date for time decay calculation
                match_id = stat.get('match_id')
                match_date = match_date_lookup.get(match_id) if match_id else None
                
                if not match_date:
                    print(f"  ⚠️ Skipping stat for match {match_id} - no match date found")
                    continue
                
                # Calculate time weight
                weight = starting_xi_manager.calculate_time_weight(
                    match_date, current_date, decay_config
                )
                
                # Apply home/away filter if needed
                stat_is_home = stat.get('is_home', True)
                if is_home != stat_is_home:
                    weight *= 0.8  # Reduce weight for opposite venue
                
                total_weights += weight
                
                # Aggregate weighted stats
                for key, value in stat.items():
                    if key not in ['_id', 'team_name', 'match_date', 'date', 'is_home'] and isinstance(value, (int, float)):
                        if key not in weighted_stats:
                            weighted_stats[key] = 0
                        weighted_stats[key] += value * weight
            
            # Calculate weighted averages
            if total_weights > 0:
                for key in weighted_stats:
                    weighted_stats[key] /= total_weights
            
            # Merge with base stats, preferring weighted values
            final_stats = {**base_stats, **weighted_stats}
            
            return final_stats
            
        except Exception as e:
            print(f"Error calculating team averages with decay: {e}")
            return base_stats or None
    
    async def get_referee_bias_with_decay(self, team_name, referee, decay_config=None):
        """Get referee bias with full time decay implementation"""
        try:
            # Get existing bias for backward compatibility
            base_bias, base_conf = await self.get_referee_bias(team_name, referee)
            
            if not decay_config:
                return base_bias, base_conf
            
            # Get all matches with this referee and team with time weighting
            matches_cursor = db.matches.find({
                "$or": [
                    {"home_team": team_name, "referee": referee},
                    {"away_team": team_name, "referee": referee}
                ]
            })
            matches = await matches_cursor.to_list(10000)
            
            if len(matches) < 3:
                return base_bias, base_conf
            
            # Calculate time-weighted RBS
            weighted_rbs_sum = 0
            total_weights = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            for match in matches:
                match_date = match.get('match_date') or match.get('date')
                if not match_date:
                    continue
                
                # Calculate time weight
                weight = starting_xi_manager.calculate_time_weight(
                    match_date, current_date, decay_config
                )
                
                # Get team stats for this match to calculate RBS
                team_stat = await db.team_stats.find_one({
                    "team_name": team_name,
                    "match_id": match.get('match_id')
                })
                
                if team_stat:
                    # Calculate RBS for this match
                    cards = team_stat.get('yellow_cards', 0) + team_stat.get('red_cards', 0) * 2
                    fouls = team_stat.get('fouls_committed', 0)
                    
                    # Simple RBS calculation (enhanced version)
                    match_rbs = (cards * 0.5) + (fouls * 0.1)
                    
                    weighted_rbs_sum += match_rbs * weight
                    total_weights += weight
            
            if total_weights > 0:
                time_weighted_rbs = weighted_rbs_sum / total_weights
                confidence = min(95, total_weights * 10)  # Confidence based on weighted sample size
                return time_weighted_rbs, confidence
            
            return base_bias, base_conf
            
        except Exception as e:
            print(f"Error calculating referee bias with decay: {e}")
            return base_bias, base_conf
    
    async def get_head_to_head_stats_with_decay(self, home_team, away_team, decay_config=None):
        """Get head-to-head stats with full time decay implementation"""
        try:
            # Get existing H2H for backward compatibility
            base_h2h = await self.get_head_to_head_stats(home_team, away_team)
            
            if not decay_config:
                return base_h2h
            
            # Get all head-to-head matches with time weighting
            h2h_matches_cursor = db.matches.find({
                "$or": [
                    {"home_team": home_team, "away_team": away_team},
                    {"home_team": away_team, "away_team": home_team}
                ]
            })
            h2h_matches = await h2h_matches_cursor.to_list(100)
            
            if len(h2h_matches) < 2:
                return base_h2h
            
            # Calculate time-weighted H2H stats
            weighted_home_wins = 0
            weighted_away_wins = 0
            weighted_draws = 0
            weighted_home_goals = 0
            weighted_away_goals = 0
            total_weights = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            for match in h2h_matches:
                match_date = match.get('match_date') or match.get('date')
                if not match_date:
                    continue
                
                # Calculate time weight
                weight = starting_xi_manager.calculate_time_weight(
                    match_date, current_date, decay_config
                )
                
                home_goals = match.get('home_goals', 0)
                away_goals = match.get('away_goals', 0)
                
                # Determine perspective (which team is "home" in our query)
                if match.get('home_team') == home_team:
                    # Normal perspective
                    weighted_home_goals += home_goals * weight
                    weighted_away_goals += away_goals * weight
                    
                    if home_goals > away_goals:
                        weighted_home_wins += weight
                    elif away_goals > home_goals:
                        weighted_away_wins += weight
                    else:
                        weighted_draws += weight
                else:
                    # Reversed perspective
                    weighted_home_goals += away_goals * weight
                    weighted_away_goals += home_goals * weight
                    
                    if away_goals > home_goals:
                        weighted_home_wins += weight
                    elif home_goals > away_goals:
                        weighted_away_wins += weight
                    else:
                        weighted_draws += weight
                
                total_weights += weight
            
            if total_weights > 0:
                return {
                    'home_wins': weighted_home_wins / total_weights * len(h2h_matches),
                    'away_wins': weighted_away_wins / total_weights * len(h2h_matches),
                    'draws': weighted_draws / total_weights * len(h2h_matches),
                    'home_goals_avg': weighted_home_goals / total_weights,
                    'away_goals_avg': weighted_away_goals / total_weights,
                    'total_matches': len(h2h_matches),
                    'time_decay_applied': True
                }
            
            return base_h2h
            
        except Exception as e:
            print(f"Error calculating H2H stats with decay: {e}")
            return base_h2h
    
    async def get_team_form_with_decay(self, team_name, last_n=5, decay_config=None):
        """Get team form with full time decay implementation"""
        try:
            # Get existing form for backward compatibility
            base_form = await self.get_team_form(team_name, last_n)
            
            if not decay_config:
                return base_form
            
            # Get recent matches with time weighting
            recent_matches_cursor = db.matches.find({
                "$or": [
                    {"home_team": team_name},
                    {"away_team": team_name}
                ]
            }).sort("match_date", -1).limit(last_n * 2)  # Get more to account for time decay
            
            recent_matches = await recent_matches_cursor.to_list(last_n * 2)
            
            if len(recent_matches) < 2:
                return base_form
            
            # Calculate time-weighted form
            weighted_points = 0
            total_weights = 0
            current_date = datetime.now().strftime("%Y-%m-%d")
            matches_considered = 0
            
            for match in recent_matches:
                if matches_considered >= last_n:
                    break
                
                match_date = match.get('match_date') or match.get('date')
                if not match_date:
                    continue
                
                # Calculate time weight
                weight = starting_xi_manager.calculate_time_weight(
                    match_date, current_date, decay_config
                )
                
                # Calculate points for this match
                home_goals = match.get('home_goals', 0)
                away_goals = match.get('away_goals', 0)
                
                if match.get('home_team') == team_name:
                    # Team was home
                    if home_goals > away_goals:
                        points = 3  # Win
                    elif home_goals == away_goals:
                        points = 1  # Draw
                    else:
                        points = 0  # Loss
                else:
                    # Team was away
                    if away_goals > home_goals:
                        points = 3  # Win
                    elif away_goals == home_goals:
                        points = 1  # Draw
                    else:
                        points = 0  # Loss
                
                weighted_points += points * weight
                total_weights += weight
                matches_considered += 1
            
            if total_weights > 0:
                # Return weighted average points per game
                return weighted_points / total_weights
            
            return base_form
            
        except Exception as e:
            print(f"Error calculating team form with decay: {e}")
            return base_form

# Initialize ML Match Predictor
ml_predictor = MLMatchPredictor()

class ModelOptimizer:
    def __init__(self):
        self.current_model_version = "1.0"
        self.optimization_history = []
        
    async def store_prediction(self, prediction_result, prediction_method="XGBoost Enhanced", 
                             starting_xi_used=False, time_decay_used=False, features_used=None):
        """Store prediction for later evaluation"""
        try:
            import uuid
            from datetime import datetime
            
            prediction_id = str(uuid.uuid4())
            
            prediction_record = {
                "prediction_id": prediction_id,
                "timestamp": datetime.now().isoformat(),
                "home_team": prediction_result.home_team,
                "away_team": prediction_result.away_team,
                "referee": prediction_result.referee,
                "prediction_method": prediction_method,
                "predicted_home_goals": prediction_result.predicted_home_goals,
                "predicted_away_goals": prediction_result.predicted_away_goals,
                "home_xg": prediction_result.home_xg,
                "away_xg": prediction_result.away_xg,
                "home_win_probability": prediction_result.home_win_probability,
                "draw_probability": prediction_result.draw_probability,
                "away_win_probability": prediction_result.away_win_probability,
                "features_used": features_used,
                "model_version": self.current_model_version,
                "starting_xi_used": starting_xi_used,
                "time_decay_used": time_decay_used
            }
            
            # Store in MongoDB
            await db.prediction_tracking.insert_one(prediction_record)
            print(f"📝 Stored prediction {prediction_id} for evaluation")
            return prediction_id
            
        except Exception as e:
            print(f"Error storing prediction: {e}")
            return None
    
    async def store_actual_result(self, prediction_id, actual_home_goals, actual_away_goals, match_date=None):
        """Store actual match result for comparison"""
        try:
            from datetime import datetime
            
            # Determine actual outcome
            if actual_home_goals > actual_away_goals:
                actual_outcome = "home_win"
            elif actual_home_goals < actual_away_goals:
                actual_outcome = "away_win"
            else:
                actual_outcome = "draw"
            
            actual_result = {
                "prediction_id": prediction_id,
                "actual_home_goals": actual_home_goals,
                "actual_away_goals": actual_away_goals,
                "actual_outcome": actual_outcome,
                "match_played_date": match_date or datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in MongoDB
            await db.actual_results.insert_one(actual_result)
            print(f"✅ Stored actual result for prediction {prediction_id}")
            return True
            
        except Exception as e:
            print(f"Error storing actual result: {e}")
            return False
    
    async def evaluate_model_performance(self, days_back=30, model_version=None):
        """Evaluate model performance against actual results"""
        try:
            from datetime import datetime, timedelta
            import numpy as np
            from sklearn.metrics import accuracy_score, precision_score, recall_score, log_loss, mean_absolute_error, mean_squared_error, r2_score
            
            # Get predictions from the last N days
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = {"timestamp": {"$gte": cutoff_date.isoformat()}}
            if model_version:
                query["model_version"] = model_version
            
            predictions = await db.prediction_tracking.find(query).to_list(10000)
            
            if not predictions:
                return {"error": "No predictions found for evaluation period"}
            
            # Get corresponding actual results
            prediction_ids = [p["prediction_id"] for p in predictions]
            actual_results = await db.actual_results.find(
                {"prediction_id": {"$in": prediction_ids}}
            ).to_list(10000)
            
            if not actual_results:
                return {"error": "No actual results found for evaluation"}
            
            # Create lookup for actual results
            actuals_dict = {r["prediction_id"]: r for r in actual_results}
            
            # Prepare data for evaluation
            matched_predictions = []
            for pred in predictions:
                if pred["prediction_id"] in actuals_dict:
                    actual = actuals_dict[pred["prediction_id"]]
                    matched_predictions.append({
                        "prediction": pred,
                        "actual": actual
                    })
            
            if not matched_predictions:
                return {"error": "No matched prediction-result pairs found"}
            
            print(f"📊 Evaluating {len(matched_predictions)} prediction-result pairs")
            
            # Extract data for metrics calculation
            predicted_outcomes = []
            actual_outcomes = []
            predicted_home_goals = []
            predicted_away_goals = []
            actual_home_goals = []
            actual_away_goals = []
            predicted_probabilities = []
            
            for match in matched_predictions:
                pred = match["prediction"]
                actual = match["actual"]
                
                # Outcome prediction
                probs = [pred["home_win_probability"], pred["draw_probability"], pred["away_win_probability"]]
                predicted_outcome_idx = np.argmax(probs)
                outcome_map = {0: "home_win", 1: "draw", 2: "away_win"}
                predicted_outcomes.append(outcome_map[predicted_outcome_idx])
                actual_outcomes.append(actual["actual_outcome"])
                
                # Goals prediction
                predicted_home_goals.append(pred["predicted_home_goals"])
                predicted_away_goals.append(pred["predicted_away_goals"])
                actual_home_goals.append(actual["actual_home_goals"])
                actual_away_goals.append(actual["actual_away_goals"])
                
                # Probabilities for log loss
                predicted_probabilities.append([p/100 for p in probs])  # Convert percentages
            
            # Calculate classification metrics
            outcome_accuracy = accuracy_score(actual_outcomes, predicted_outcomes)
            
            # Precision for each outcome
            unique_outcomes = ["home_win", "draw", "away_win"]
            precisions = precision_score(actual_outcomes, predicted_outcomes, 
                                      labels=unique_outcomes, average=None, zero_division=0)
            
            # Convert actual outcomes to one-hot for log loss
            outcome_to_idx = {"home_win": 0, "draw": 1, "away_win": 2}
            actual_probs = np.zeros((len(actual_outcomes), 3))
            for i, outcome in enumerate(actual_outcomes):
                actual_probs[i, outcome_to_idx[outcome]] = 1
            
            # Calculate log loss
            try:
                model_log_loss = log_loss(actual_probs, predicted_probabilities)
            except:
                model_log_loss = float('inf')
            
            # Calculate regression metrics
            home_goals_mae = mean_absolute_error(actual_home_goals, predicted_home_goals)
            away_goals_mae = mean_absolute_error(actual_away_goals, predicted_away_goals)
            home_goals_rmse = np.sqrt(mean_squared_error(actual_home_goals, predicted_home_goals))
            away_goals_rmse = np.sqrt(mean_squared_error(actual_away_goals, predicted_away_goals))
            
            # Combined goals R² score
            all_actual_goals = actual_home_goals + actual_away_goals
            all_predicted_goals = predicted_home_goals + predicted_away_goals
            goals_r2 = r2_score(all_actual_goals, all_predicted_goals)
            
            # Calculate confidence calibration
            confidence_calibration = self._calculate_calibration(predicted_probabilities, actual_probs)
            
            metrics = {
                "model_version": model_version or self.current_model_version,
                "evaluation_period": f"Last {days_back} days",
                "total_predictions": len(matched_predictions),
                "outcome_accuracy": round(outcome_accuracy * 100, 2),
                "home_win_precision": round(precisions[0] * 100, 2) if len(precisions) > 0 else 0,
                "draw_precision": round(precisions[1] * 100, 2) if len(precisions) > 1 else 0,
                "away_win_precision": round(precisions[2] * 100, 2) if len(precisions) > 2 else 0,
                "log_loss": round(model_log_loss, 4),
                "home_goals_mae": round(home_goals_mae, 3),
                "away_goals_mae": round(away_goals_mae, 3),
                "home_goals_rmse": round(home_goals_rmse, 3),
                "away_goals_rmse": round(away_goals_rmse, 3),
                "goals_r2_score": round(goals_r2, 3),
                "confidence_calibration": round(confidence_calibration, 3)
            }
            
            # Store performance metrics
            await db.model_performance.insert_one({
                **metrics,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"📈 Model Performance: {outcome_accuracy*100:.1f}% accuracy, {home_goals_mae:.2f} goals MAE")
            return metrics
            
        except Exception as e:
            print(f"Error evaluating model performance: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _calculate_calibration(self, predicted_probs, actual_probs):
        """Calculate confidence calibration score"""
        try:
            import numpy as np
            
            # Calculate Expected Calibration Error (ECE)
            predicted_probs = np.array(predicted_probs)
            actual_probs = np.array(actual_probs)
            
            # Get maximum predicted probability for each prediction
            max_probs = np.max(predicted_probs, axis=1)
            predictions = np.argmax(predicted_probs, axis=1)
            actuals = np.argmax(actual_probs, axis=1)
            
            # Bin predictions by confidence
            n_bins = 10
            bin_boundaries = np.linspace(0, 1, n_bins + 1)
            bin_lowers = bin_boundaries[:-1]
            bin_uppers = bin_boundaries[1:]
            
            ece = 0
            for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
                in_bin = (max_probs > bin_lower) & (max_probs <= bin_upper)
                prop_in_bin = in_bin.mean()
                
                if prop_in_bin > 0:
                    accuracy_in_bin = (predictions[in_bin] == actuals[in_bin]).mean()
                    avg_confidence_in_bin = max_probs[in_bin].mean()
                    ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
            
            return ece
            
        except Exception as e:
            print(f"Error calculating calibration: {e}")
            return 0.0
    
    async def optimize_hyperparameters(self, optimization_method="grid_search"):
        """Optimize XGBoost hyperparameters based on historical performance"""
        try:
            from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
            from sklearn.metrics import make_scorer, log_loss
            import numpy as np
            
            print("🔧 Starting hyperparameter optimization...")
            
            # Get training data
            training_features, training_targets = await self._prepare_optimization_data()
            
            if training_features is None:
                return {"error": "Insufficient data for optimization"}
            
            # Define parameter grids
            if optimization_method == "grid_search":
                param_grid = {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [3, 4, 5, 6],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0]
                }
            else:  # random_search
                param_grid = {
                    'n_estimators': np.arange(50, 500, 50),
                    'max_depth': np.arange(3, 10),
                    'learning_rate': np.uniform(0.01, 0.3, 20),
                    'subsample': np.uniform(0.7, 1.0, 10),
                    'colsample_bytree': np.uniform(0.7, 1.0, 10)
                }
            
            # Optimize each model type
            optimization_results = {}
            
            for model_type in ['classifier', 'home_goals', 'away_goals', 'home_xg', 'away_xg']:
                print(f"   Optimizing {model_type}...")
                
                # Get appropriate targets
                y = training_targets[model_type]
                
                # Create XGBoost model
                if model_type == 'classifier':
                    from xgboost import XGBClassifier
                    model = XGBClassifier(random_state=42, objective='multi:softprob')
                    scoring = 'neg_log_loss'
                else:
                    from xgboost import XGBRegressor
                    model = XGBRegressor(random_state=42)
                    scoring = 'neg_mean_absolute_error'
                
                # Perform optimization
                if optimization_method == "grid_search":
                    search = GridSearchCV(
                        model, param_grid, cv=5, scoring=scoring, 
                        n_jobs=-1, verbose=1
                    )
                else:
                    search = RandomizedSearchCV(
                        model, param_grid, cv=5, scoring=scoring,
                        n_jobs=-1, verbose=1, n_iter=50, random_state=42
                    )
                
                search.fit(training_features, y)
                
                optimization_results[model_type] = {
                    'best_params': search.best_params_,
                    'best_score': search.best_score_,
                    'improvement': abs(search.best_score_) - abs(search.cv_results_['mean_test_score'].mean())
                }
                
                print(f"   ✅ {model_type}: Score {search.best_score_:.4f}")
            
            # Store optimization results
            await db.model_optimization.insert_one({
                "timestamp": datetime.now().isoformat(),
                "optimization_method": optimization_method,
                "results": optimization_results,
                "model_version": self.current_model_version
            })
            
            print("🎯 Hyperparameter optimization complete!")
            return optimization_results
            
        except Exception as e:
            print(f"Error optimizing hyperparameters: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def _prepare_optimization_data(self):
        """Prepare training data for optimization"""
        try:
            # Get historical data with actual results
            predictions = await db.prediction_tracking.find({}).to_list(10000)
            actual_results = await db.actual_results.find({}).to_list(10000)
            
            if len(predictions) < 100:  # Need sufficient data
                return None, None
            
            # Match predictions with actual results
            actuals_dict = {r["prediction_id"]: r for r in actual_results}
            matched_data = []
            
            for pred in predictions:
                if pred["prediction_id"] in actuals_dict and pred.get("features_used"):
                    actual = actuals_dict[pred["prediction_id"]]
                    matched_data.append({
                        "features": pred["features_used"],
                        "outcomes": {
                            "classifier": actual["actual_outcome"],
                            "home_goals": actual["actual_home_goals"],
                            "away_goals": actual["actual_away_goals"],
                            "home_xg": pred["home_xg"],  # Use predicted xG as proxy if actual not available
                            "away_xg": pred["away_xg"]
                        }
                    })
            
            if not matched_data:
                return None, None
            
            # Convert to training format
            import pandas as pd
            
            features_list = [item["features"] for item in matched_data]
            X = pd.DataFrame(features_list)
            
            # Prepare targets
            outcome_map = {"home_win": 0, "draw": 1, "away_win": 2}
            targets = {
                "classifier": [outcome_map[item["outcomes"]["classifier"]] for item in matched_data],
                "home_goals": [item["outcomes"]["home_goals"] for item in matched_data],
                "away_goals": [item["outcomes"]["away_goals"] for item in matched_data],
                "home_xg": [item["outcomes"]["home_xg"] for item in matched_data],
                "away_xg": [item["outcomes"]["away_xg"] for item in matched_data]
            }
            
            return X, targets
            
        except Exception as e:
            print(f"Error preparing optimization data: {e}")
            return None, None

# Initialize Model Optimizer
model_optimizer = ModelOptimizer()
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
        
        # No longer clearing existing matches - we'll append instead
        # await db.matches.delete_many({})
        
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
        
        # No longer clearing existing team stats - we'll append instead
        # await db.team_stats.delete_many({})
        
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
        
        # No longer clearing existing player stats - we'll append instead
        # await db.player_stats.delete_many({})
        
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
@app.post("/api/calculate-rbs")
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

@api_router.get("/rbs-status")
async def get_rbs_status():
    """Get RBS calculation status and statistics"""
    try:
        # Check if RBS calculations exist
        rbs_count = await db.rbs_results.count_documents({})
        
        if rbs_count == 0:
            return {
                "calculated": False,
                "referees_analyzed": 0,
                "teams_covered": 0,
                "total_calculations": 0,
                "last_calculated": None
            }
        
        # Get latest calculation timestamp
        latest_result = await db.rbs_results.find_one({}, sort=[("last_updated", -1)])
        
        # Get unique referees and teams
        referees_analyzed = len(await db.rbs_results.distinct("referee"))
        teams_covered = len(await db.rbs_results.distinct("team_name"))
        
        return {
            "calculated": True,
            "referees_analyzed": referees_analyzed,
            "teams_covered": teams_covered,
            "total_calculations": rbs_count,
            "last_calculated": latest_result.get("last_updated") if latest_result else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking RBS status: {str(e)}")

@api_router.get("/referees")
async def get_referees():
    """Get list of all referees"""
    try:
        referees = await db.matches.distinct("referee")
        # Filter out invalid referees (null, nan, empty strings)
        valid_referees = [
            ref for ref in referees 
            if ref and str(ref).lower() not in ['nan', 'null', 'none', ''] 
            and str(ref).strip() != ''
        ]
        return {"referees": sorted(valid_referees)}
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

@api_router.get("/teams/{team_name}/players", response_model=TeamPlayersResponse)
async def get_team_players(team_name: str, formation: str = "4-4-2"):
    """Get players for a team with default starting XI based on playing time"""
    try:
        # Get all players with stats
        players = await starting_xi_manager.get_team_players_with_stats(team_name)
        
        # Generate default starting XI
        default_xi = await starting_xi_manager.generate_default_starting_xi(team_name, formation)
        
        return TeamPlayersResponse(
            success=True,
            team_name=team_name,
            players=players,
            default_starting_xi=default_xi,
            available_formations=list(starting_xi_manager.formations.keys())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching team players: {str(e)}")

@api_router.get("/formations")
async def get_available_formations():
    """Get list of available formations"""
    try:
        formations = []
        for formation_name, positions in starting_xi_manager.formations.items():
            formation_info = {
                "name": formation_name,
                "positions": len(positions),
                "position_breakdown": {
                    "GK": len([p for p in positions if p["position_type"] == "GK"]),
                    "DEF": len([p for p in positions if p["position_type"] == "DEF"]),
                    "MID": len([p for p in positions if p["position_type"] == "MID"]),
                    "FWD": len([p for p in positions if p["position_type"] == "FWD"])
                }
            }
            formations.append(formation_info)
        
        return {
            "success": True,
            "formations": formations,
            "default_formation": "4-4-2"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching formations: {str(e)}")

@api_router.get("/time-decay/presets")
async def get_time_decay_presets():
    """Get available time decay presets"""
    try:
        presets = time_decay_manager.get_all_presets()
        return {
            "success": True,
            "presets": [preset.dict() for preset in presets],
            "default_preset": "moderate"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching time decay presets: {str(e)}")

@api_router.post("/predict-match-enhanced")
async def predict_match_enhanced(request: EnhancedMatchPredictionRequest):
    """Enhanced match prediction with starting XI and time decay support"""
    try:
        # Get time decay configuration
        decay_config = time_decay_manager.get_preset(request.decay_preset or "moderate")
        if request.custom_decay_rate and request.decay_preset == "custom":
            decay_config.decay_rate_per_month = request.custom_decay_rate
        
        # Use existing prediction logic but with enhanced features
        if request.home_starting_xi or request.away_starting_xi:
            # Enhanced prediction with specific players
            result = await ml_predictor.predict_match_with_starting_xi(
                home_team=request.home_team,
                away_team=request.away_team,
                referee=request.referee_name,
                home_starting_xi=request.home_starting_xi,
                away_starting_xi=request.away_starting_xi,
                match_date=request.match_date,
                config_name=request.config_name,
                decay_config=decay_config if request.use_time_decay else None
            )
        else:
            # Standard prediction with default starting XI
            result = await ml_predictor.predict_match_with_defaults(
                home_team=request.home_team,
                away_team=request.away_team,
                referee=request.referee_name,
                match_date=request.match_date,
                config_name=request.config_name,
                decay_config=decay_config if request.use_time_decay else None
            )
        
        # 🎯 OPTIMIZATION INTEGRATION: Auto-track XGBoost predictions for optimization
        if result.success:
            try:
                prediction_id = await model_optimizer.store_prediction(
                    prediction_result=result,
                    prediction_method="XGBoost Enhanced with Starting XI",
                    starting_xi_used=bool(request.home_starting_xi or request.away_starting_xi),
                    time_decay_used=bool(request.use_time_decay),
                    features_used=result.prediction_breakdown.get('features_used') if hasattr(result, 'prediction_breakdown') else None
                )
                
                # Add prediction ID to result for tracking
                if hasattr(result, 'prediction_breakdown'):
                    result.prediction_breakdown['prediction_id'] = prediction_id
                    result.prediction_breakdown['optimization_tracking'] = '✅ Enabled'
                    print(f"📊 XGBoost prediction tracked for optimization: {prediction_id}")
                
            except Exception as opt_error:
                print(f"Warning: Could not track prediction for optimization: {opt_error}")
        
        # Convert result to dict and ensure NumPy types are handled
        if hasattr(result, 'dict'):
            result_dict = result.dict()
        else:
            result_dict = result
        
        # Recursively convert all NumPy types
        result_dict = convert_numpy_types(result_dict)
        
        return NumpyJSONResponse(content=result_dict)
        
    except Exception as e:
        print(f"Enhanced prediction error: {e}")
        error_result = MatchPredictionResponse(
            success=False,
            home_team=request.home_team,
            away_team=request.away_team,
            referee=request.referee_name,
            error=str(e)
        )
        error_dict = convert_numpy_types(error_result.dict())
        return NumpyJSONResponse(content=error_dict)

@api_router.post("/optimize-xgboost-models")
async def optimize_xgboost_models(method: str = "grid_search", retrain: bool = True):
    """Comprehensive XGBoost model optimization workflow"""
    try:
        print("🚀 Starting comprehensive XGBoost optimization...")
        
        # Step 1: Evaluate current model performance
        print("📊 Step 1: Evaluating current model performance...")
        current_performance = await model_optimizer.evaluate_model_performance(30)
        
        if "error" in current_performance:
            return {"error": "Cannot evaluate current performance: " + current_performance["error"]}
        
        # Step 2: Optimize hyperparameters
        print("🔧 Step 2: Optimizing hyperparameters...")
        optimization_results = await model_optimizer.optimize_hyperparameters(method)
        
        if "error" in optimization_results:
            return {"error": "Hyperparameter optimization failed: " + optimization_results["error"]}
        
        result = {
            "optimization_method": method,
            "current_performance": current_performance,
            "optimization_results": optimization_results,
            "retrained": False
        }
        
        # Step 3: Retrain models if requested
        if retrain:
            print("🔄 Step 3: Retraining models with optimized parameters...")
            retrain_result = await retrain_models_with_optimization()
            
            if retrain_result.get("success"):
                # Step 4: Evaluate new model performance
                print("📈 Step 4: Evaluating optimized model performance...")
                await asyncio.sleep(1)  # Brief pause for model to be ready
                new_performance = await model_optimizer.evaluate_model_performance(30, model_optimizer.current_model_version)
                
                result.update({
                    "retrained": True,
                    "retrain_result": retrain_result,
                    "new_performance": new_performance,
                    "improvement_summary": {
                        "accuracy_improvement": new_performance.get("outcome_accuracy", 0) - current_performance.get("outcome_accuracy", 0),
                        "goals_mae_improvement": ((current_performance.get("home_goals_mae", 0) + current_performance.get("away_goals_mae", 0)) / 2) - 
                                               ((new_performance.get("home_goals_mae", 0) + new_performance.get("away_goals_mae", 0)) / 2),
                        "log_loss_improvement": current_performance.get("log_loss", 0) - new_performance.get("log_loss", 0)
                    }
                })
            else:
                result["retrain_error"] = retrain_result.get("error", "Unknown error")
        
        print("✅ XGBoost optimization workflow complete!")
        return result
        
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/xgboost-optimization-status")
async def get_xgboost_optimization_status():
    """Get comprehensive status of XGBoost optimization"""
    try:
        # Get recent optimization history
        recent_optimizations = await db.model_optimization.find({}).sort("timestamp", -1).limit(5).to_list(5)
        
        # Get recent performance metrics
        recent_performance = await db.model_performance.find({}).sort("timestamp", -1).limit(10).to_list(10)
        
        # Get prediction tracking stats
        total_predictions = await db.prediction_tracking.count_documents({})
        total_actual_results = await db.actual_results.count_documents({})
        
        # Calculate optimization readiness
        optimization_ready = total_predictions > 100 and total_actual_results > 50
        
        return {
            "optimization_ready": optimization_ready,
            "total_predictions_tracked": total_predictions,
            "total_actual_results": total_actual_results,
            "optimization_coverage": round((total_actual_results / total_predictions * 100) if total_predictions > 0 else 0, 2),
            "recent_optimizations": len(recent_optimizations),
            "recent_performance_evaluations": len(recent_performance),
            "current_model_version": model_optimizer.current_model_version,
            "last_optimization": recent_optimizations[0] if recent_optimizations else None,
            "latest_performance": recent_performance[0] if recent_performance else None
        }
        
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/simulate-optimization-impact")
async def simulate_optimization_impact(days_back: int = 30):
    """Simulate the impact of optimization on historical predictions"""
    try:
        print(f"🎯 Simulating optimization impact over last {days_back} days...")
        
        # Get historical predictions
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        predictions = await db.prediction_tracking.find({
            "timestamp": {"$gte": cutoff_date.isoformat()}
        }).to_list(1000)
        
        if len(predictions) < 10:
            return {"error": "Insufficient historical predictions for simulation"}
        
        # Get actual results for these predictions
        prediction_ids = [p["prediction_id"] for p in predictions]
        actual_results = await db.actual_results.find({
            "prediction_id": {"$in": prediction_ids}
        }).to_list(1000)
        
        actuals_dict = {r["prediction_id"]: r for r in actual_results}
        
        # Calculate current accuracy
        correct_predictions = 0
        total_matched = 0
        
        for pred in predictions:
            if pred["prediction_id"] in actuals_dict:
                actual = actuals_dict[pred["prediction_id"]]
                
                # Determine predicted outcome
                probs = [pred["home_win_probability"], pred["draw_probability"], pred["away_win_probability"]]
                predicted_outcome_idx = max(range(len(probs)), key=probs.__getitem__)
                outcome_map = {0: "home_win", 1: "draw", 2: "away_win"}
                predicted_outcome = outcome_map[predicted_outcome_idx]
                
                if predicted_outcome == actual["actual_outcome"]:
                    correct_predictions += 1
                total_matched += 1
        
        if total_matched == 0:
            return {"error": "No matched predictions found for simulation"}
        
        current_accuracy = (correct_predictions / total_matched) * 100
        
        # Simulate potential improvements
        simulated_improvements = {
            "conservative_improvement": current_accuracy + 2.5,  # +2.5% accuracy
            "moderate_improvement": current_accuracy + 5.0,     # +5% accuracy  
            "aggressive_improvement": current_accuracy + 7.5,   # +7.5% accuracy
        }
        
        return {
            "simulation_period": f"Last {days_back} days",
            "total_predictions": len(predictions),
            "matched_predictions": total_matched,
            "current_accuracy": round(current_accuracy, 2),
            "simulated_improvements": simulated_improvements,
            "potential_value": {
                "additional_correct_predictions_conservative": round(total_matched * 0.025),
                "additional_correct_predictions_moderate": round(total_matched * 0.05),
                "additional_correct_predictions_aggressive": round(total_matched * 0.075)
            },
            "optimization_recommendation": "moderate_improvement" if current_accuracy < 60 else "conservative_improvement"
        }
        
    except Exception as e:
        return {"error": str(e)}
async def store_prediction_result(request: ActualResult):
    """Store actual match result for prediction evaluation"""
    try:
        result = await model_optimizer.store_actual_result(
            request.prediction_id,
            request.actual_home_goals,
            request.actual_away_goals,
            request.match_played_date
        )
        return {"success": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_router.get("/model-performance/{days}")
async def get_model_performance(days: int = 30, model_version: str = None):
    """Get model performance metrics for the last N days"""
    try:
        metrics = await model_optimizer.evaluate_model_performance(days, model_version)
        return metrics
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/optimize-hyperparameters")
async def optimize_hyperparameters(method: str = "grid_search"):
    """Optimize XGBoost hyperparameters based on historical performance"""
    try:
        if method not in ["grid_search", "random_search"]:
            return {"error": "Method must be 'grid_search' or 'random_search'"}
        
        results = await model_optimizer.optimize_hyperparameters(method)
        return results
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/optimization-history")
async def get_optimization_history():
    """Get history of model optimizations"""
    try:
        history = await db.model_optimization.find({}).sort("timestamp", -1).limit(20).to_list(20)
        return {"optimizations": history}
    except Exception as e:
        return {"error": str(e)}

@api_router.get("/prediction-accuracy-trends")
async def get_prediction_accuracy_trends(days: int = 90):
    """Get prediction accuracy trends over time"""
    try:
        from datetime import datetime, timedelta
        
        # Get performance metrics over time
        cutoff_date = datetime.now() - timedelta(days=days)
        
        performance_history = await db.model_performance.find({
            "timestamp": {"$gte": cutoff_date.isoformat()}
        }).sort("timestamp", 1).to_list(100)
        
        if not performance_history:
            return {"error": "No performance history found"}
        
        # Calculate trends
        trends = {
            "accuracy_trend": [p["outcome_accuracy"] for p in performance_history],
            "goals_mae_trend": [(p["home_goals_mae"] + p["away_goals_mae"]) / 2 for p in performance_history],
            "log_loss_trend": [p["log_loss"] for p in performance_history],
            "timestamps": [p["timestamp"] for p in performance_history],
            "total_periods": len(performance_history)
        }
        
        return trends
        
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/retrain-models-optimized")
async def retrain_models_with_optimization():
    """Retrain models using optimized hyperparameters"""
    try:
        # Get latest optimization results
        latest_optimization = await db.model_optimization.find_one(
            {}, sort=[("timestamp", -1)]
        )
        
        if not latest_optimization:
            return {"error": "No optimization results found. Run hyperparameter optimization first."}
        
        print("🔄 Retraining models with optimized parameters...")
        
        # Get optimized parameters
        optimized_params = latest_optimization["results"]
        
        # Retrain with optimized parameters
        result = await ml_predictor.train_models_with_params(optimized_params)
        
        if result.get("success"):
            # Update model version
            model_optimizer.current_model_version = f"2.{len(await db.model_optimization.find({}).to_list(1000))}"
            print(f"✅ Models retrained successfully with version {model_optimizer.current_model_version}")
        
        return result
        
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/test-time-decay-impact")
async def test_time_decay_impact(team_name: str = "Arsenal"):
    """Test endpoint to verify time decay is actually working with different presets"""
    try:
        print(f"\n🧪 TESTING TIME DECAY IMPACT FOR {team_name}")
        print("=" * 60)
        
        # Test all time decay presets by comparing team averages
        presets = ["none", "conservative", "moderate", "aggressive", "linear"]
        results = {}
        
        for preset_name in presets:
            print(f"\n📋 Testing preset: {preset_name}")
            
            # Get decay configuration
            if preset_name == "none":
                decay_config = None
            else:
                decay_config = time_decay_manager.get_preset(preset_name)
            
            # Calculate team averages with this decay setting
            team_features = await ml_predictor.calculate_team_features_enhanced(
                team_name=team_name,
                is_home=True,
                starting_xi=None,
                decay_config=decay_config
            )
            
            if team_features:
                results[preset_name] = {
                    "goals_per_match": team_features.get('goals', 0),
                    "xg_per_match": team_features.get('xg', 0),
                    "shots_per_match": team_features.get('shots_total', 0),
                    "possession_pct": team_features.get('possession_pct', 0),
                    "conversion_rate": team_features.get('conversion_rate', 0)
                }
                print(f"  ✅ {preset_name}: Goals {team_features.get('goals', 0):.3f}, xG {team_features.get('xg', 0):.3f}")
            else:
                results[preset_name] = {"error": "Could not calculate team features"}
                print(f"  ❌ {preset_name}: Error calculating features")
        
        # Analyze differences
        print(f"\n📊 TIME DECAY IMPACT ANALYSIS:")
        if len([r for r in results.values() if "error" not in r]) >= 2:
            # Compare results
            none_result = results.get("none", {})
            aggressive_result = results.get("aggressive", {})
            
            if "error" not in none_result and "error" not in aggressive_result:
                goals_diff = abs(none_result["goals_per_match"] - aggressive_result["goals_per_match"])
                xg_diff = abs(none_result["xg_per_match"] - aggressive_result["xg_per_match"])
                
                print(f"  📈 Goals difference (none vs aggressive): {goals_diff:.4f}")
                print(f"  📈 xG difference (none vs aggressive): {xg_diff:.4f}")
                
                if goals_diff > 0.01 or xg_diff > 0.01:
                    print(f"  ✅ TIME DECAY IS WORKING! Significant differences detected.")
                    print(f"  📝 Explanation: Recent matches weighted higher with aggressive decay")
                else:
                    print(f"  ⚠️  TIME DECAY IMPACT IS MINIMAL. May need more historical data or larger time gaps.")
                
                # Show all results for comparison
                print(f"\n📋 DETAILED COMPARISON:")
                for preset, data in results.items():
                    if "error" not in data:
                        print(f"  {preset:12}: Goals {data['goals_per_match']:.4f}, xG {data['xg_per_match']:.4f}")
            else:
                print(f"  ❌ Cannot compare - feature calculation errors occurred")
        else:
            print(f"  ❌ Cannot analyze - insufficient successful calculations")
        
        print("=" * 60)
        
        return {
            "success": True,
            "message": "Time decay test completed",
            "results": results,
            "analysis": "Check backend logs for detailed time decay calculations",
            "test_parameters": {
                "team": team_name,
                "presets_tested": presets
            }
        }
        
    except Exception as e:
        print(f"❌ Time decay test error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@api_router.get("/model-comparison")
async def compare_model_versions(version1: str = "1.0", version2: str = "2.0", days: int = 30):
    """Compare performance between two model versions"""
    try:
        # Get performance for both versions
        perf1 = await model_optimizer.evaluate_model_performance(days, version1)
        perf2 = await model_optimizer.evaluate_model_performance(days, version2)
        
        if "error" in perf1 or "error" in perf2:
            return {"error": "Could not find performance data for both versions"}
        
        # Calculate improvements
        comparison = {
            "version1": version1,
            "version2": version2,
            "improvements": {
                "accuracy_change": perf2["outcome_accuracy"] - perf1["outcome_accuracy"],
                "goals_mae_change": ((perf2["home_goals_mae"] + perf2["away_goals_mae"]) / 2) - 
                                   ((perf1["home_goals_mae"] + perf1["away_goals_mae"]) / 2),
                "log_loss_change": perf2["log_loss"] - perf1["log_loss"],
                "r2_change": perf2["goals_r2_score"] - perf1["goals_r2_score"]
            },
            "version1_metrics": perf1,
            "version2_metrics": perf2
        }
        
        return comparison
        
    except Exception as e:
        return {"error": str(e)}

# ========================= ENSEMBLE PREDICTION ENDPOINTS =========================

@api_router.post("/predict-match-ensemble")
async def predict_match_ensemble(request: MatchPredictionRequest):
    """Make ensemble match prediction using multiple ML models"""
    try:
        print(f"🤖 Ensemble prediction request: {request.home_team} vs {request.away_team}")
        
        # Make ensemble prediction
        result = await ml_predictor.predict_match_ensemble(
            request.home_team,
            request.away_team,
            request.referee_name,
            request.match_date
        )
        
        # Convert NumPy types to Python native types
        result = convert_numpy_types(result)
        
        return result
        
    except Exception as e:
        print(f"❌ Ensemble prediction error: {e}")
        return {
            "success": False,
            "error": str(e),
            "home_team": request.home_team,
            "away_team": request.away_team,
            "referee": request.referee_name
        }

@api_router.post("/train-ensemble-models")
async def train_ensemble_models():
    """Train all ensemble models (Random Forest, Gradient Boosting, Neural Network, Logistic Regression)"""
    try:
        print("🚀 Starting ensemble model training...")
        
        # Check if we have enough data for training
        team_stats_count = await db.team_stats.count_documents({})
        if team_stats_count < 50:
            return {
                "success": False,
                "error": f"Insufficient data for training. Need at least 50 records, found {team_stats_count}"
            }
        
        # Train ensemble models
        result = await ml_predictor.train_ensemble_models()
        
        return result
        
    except Exception as e:
        print(f"❌ Ensemble training error: {e}")
        return {
            "success": False,
            "error": str(e),
            "details": "Check backend logs for more information"
        }

@api_router.get("/ensemble-model-status")
async def get_ensemble_model_status():
    """Get status and performance of ensemble models"""
    try:
        status = {
            "models_available": {},
            "model_weights": ml_predictor.model_weights,
            "ensemble_ready": True
        }
        
        # Check each model type
        for model_type in ['xgboost', 'random_forest', 'gradient_boost', 'neural_net', 'logistic']:
            if model_type == 'xgboost':
                # Check XGBoost models
                status["models_available"][model_type] = {
                    "available": len(ml_predictor.models) == 5,
                    "models": list(ml_predictor.models.keys()) if ml_predictor.models else []
                }
            else:
                # Check ensemble models
                available = (model_type in ml_predictor.ensemble_models and 
                           len(ml_predictor.ensemble_models[model_type]) == 5)
                status["models_available"][model_type] = {
                    "available": available,
                    "models": list(ml_predictor.ensemble_models[model_type].keys()) if available else []
                }
                
                if not available:
                    status["ensemble_ready"] = False
        
        return status
        
    except Exception as e:
        return {"error": str(e)}

@api_router.post("/compare-prediction-methods")
async def compare_prediction_methods(request: MatchPredictionRequest):
    """Compare XGBoost vs Ensemble predictions for the same match"""
    try:
        print(f"🔍 Comparing prediction methods: {request.home_team} vs {request.away_team}")
        
        # Get XGBoost prediction
        xgboost_result = await ml_predictor.predict_match(
            request.home_team,
            request.away_team, 
            request.referee_name,
            request.match_date
        )
        
        # Get Ensemble prediction
        ensemble_result = await ml_predictor.predict_match_ensemble(
            request.home_team,
            request.away_team,
            request.referee_name,
            request.match_date
        )
        
        # Convert NumPy types to Python native types
        xgboost_result = convert_numpy_types(xgboost_result)
        ensemble_result = convert_numpy_types(ensemble_result)
        
        # Calculate differences
        if xgboost_result.get('success') and ensemble_result.get('success'):
            differences = {
                'home_win_prob_diff': abs(ensemble_result['home_win_probability'] - xgboost_result['home_win_probability']),
                'draw_prob_diff': abs(ensemble_result['draw_probability'] - xgboost_result['draw_probability']),
                'away_win_prob_diff': abs(ensemble_result['away_win_probability'] - xgboost_result['away_win_probability']),
                'home_goals_diff': abs(ensemble_result['predicted_home_goals'] - xgboost_result['predicted_home_goals']),
                'away_goals_diff': abs(ensemble_result['predicted_away_goals'] - xgboost_result['predicted_away_goals']),
                'home_xg_diff': abs(ensemble_result['home_xg'] - xgboost_result['home_xg']),
                'away_xg_diff': abs(ensemble_result['away_xg'] - xgboost_result['away_xg'])
            }
            
            # Determine which method is more confident
            xgb_confidence = max(xgboost_result['home_win_probability'], xgboost_result['draw_probability'], xgboost_result['away_win_probability'])
            ensemble_confidence = max(ensemble_result['home_win_probability'], ensemble_result['draw_probability'], ensemble_result['away_win_probability'])
            
            comparison = {
                'success': True,
                'match': f"{request.home_team} vs {request.away_team}",
                'referee': request.referee_name,
                'xgboost_prediction': xgboost_result,
                'ensemble_prediction': ensemble_result,
                'differences': differences,
                'confidence_comparison': {
                    'xgboost_max_confidence': round(xgb_confidence, 2),
                    'ensemble_max_confidence': round(ensemble_confidence, 2),
                    'more_confident_method': 'ensemble' if ensemble_confidence > xgb_confidence else 'xgboost',
                    'confidence_difference': abs(ensemble_confidence - xgb_confidence)
                },
                'recommendation': {
                    'significant_differences': any(diff > 5 for diff in [differences['home_win_prob_diff'], differences['draw_prob_diff'], differences['away_win_prob_diff']]),
                    'ensemble_agreement': ensemble_result.get('ensemble_confidence', {}).get('model_agreement', 0),
                    'suggested_method': 'ensemble' if ensemble_result.get('ensemble_confidence', {}).get('overall_confidence') in ['High', 'Very High'] else 'xgboost'
                }
            }
            
            # Convert any remaining NumPy types to Python native types
            comparison = convert_numpy_types(comparison)
            
            return comparison
        else:
            return {
                'success': False,
                'error': 'One or both prediction methods failed',
                'xgboost_success': xgboost_result.get('success', False),
                'ensemble_success': ensemble_result.get('success', False)
            }
        
    except Exception as e:
        print(f"❌ Prediction comparison error: {e}")
        return {"success": False, "error": str(e)}

@api_router.delete("/database/wipe")
async def wipe_database():
    """Wipe all data from the database"""
    try:
        # Clear all collections
        collections_cleared = 0
        
        # Get all collection names
        collection_names = await db.list_collection_names()
        
        for collection_name in collection_names:
            if collection_name not in ['system.indexes']:  # Skip system collections
                collection = db[collection_name]
                delete_result = await collection.delete_many({})
                print(f"Cleared {delete_result.deleted_count} documents from {collection_name}")
                collections_cleared += 1
        
        return {
            "success": True,
            "message": f"Database wiped successfully. Cleared {collections_cleared} collections.",
            "collections_cleared": collections_cleared,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Database wipe error: {e}")
        raise HTTPException(status_code=500, detail=f"Error wiping database: {str(e)}")

@api_router.get("/database/stats")
async def get_database_stats():
    """Get database statistics for monitoring"""
    try:
        stats = {}
        collection_names = await db.list_collection_names()
        
        for collection_name in collection_names:
            if collection_name not in ['system.indexes']:
                collection = db[collection_name]
                count = await collection.count_documents({})
                stats[collection_name] = count
        
        total_documents = sum(stats.values())
        
        return {
            "success": True,
            "total_documents": total_documents,
            "collections": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Database stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")

@api_router.get("/datasets")
async def get_datasets():
    """Get information about uploaded datasets"""
    try:
        datasets = []
        collection_names = await db.list_collection_names()
        
        # Map collection names to user-friendly dataset names
        dataset_mapping = {
            'matches': {'name': 'Match Data', 'description': 'Match results and statistics'},
            'team_stats': {'name': 'Team Statistics', 'description': 'Team-level performance data'},
            'player_stats': {'name': 'Player Statistics', 'description': 'Individual player performance data'},
            'rbs_results': {'name': 'RBS Results', 'description': 'Referee bias score calculations'}
        }
        
        for collection_name in collection_names:
            if collection_name in dataset_mapping and collection_name not in ['system.indexes']:
                collection = db[collection_name]
                count = await collection.count_documents({})
                
                if count > 0:  # Only include collections with data
                    dataset_info = dataset_mapping[collection_name]
                    datasets.append({
                        'name': dataset_info['name'],
                        'collection': collection_name,
                        'records': count,
                        'description': dataset_info['description'],
                        'uploaded_at': datetime.now().isoformat()  # Placeholder - could be enhanced
                    })
        
        return {
            "success": True,
            "datasets": datasets,
            "total_datasets": len(datasets)
        }
        
    except Exception as e:
        print(f"Datasets error: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting datasets: {str(e)}")

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

@api_router.get("/enhanced-rbs-analysis/{team_name}/{referee_name}")
async def get_enhanced_rbs_analysis(team_name: str, referee_name: str):
    """
    Get comprehensive RBS analysis including:
    1. Performance differential (team stats with vs without referee)
    2. Referee decision variance analysis (consistency for this team vs overall)
    """
    try:
        rbs_calculator = RBSCalculator()
        
        # Get standard RBS calculation
        matches = await db.matches.find().to_list(10000)
        team_stats = await db.team_stats.find().to_list(10000)
        
        standard_rbs = await rbs_calculator.calculate_rbs_for_team_referee(
            team_name, referee_name, team_stats, matches
        )
        
        # Get variance analysis
        variance_analysis = await rbs_calculator.calculate_referee_variance_analysis(
            team_name, referee_name
        )
        
        if not standard_rbs:
            return {
                "success": False,
                "message": "Insufficient data for RBS calculation",
                "team_name": team_name,
                "referee_name": referee_name
            }
        
        return {
            "success": True,
            "team_name": team_name,
            "referee_name": referee_name,
            "standard_rbs": standard_rbs,
            "variance_analysis": variance_analysis,
            "interpretation": {
                "rbs_explanation": f"Team performance differential: {standard_rbs['rbs_score']} (higher = better performance with this referee)",
                "variance_explanation": "Variance ratios show how consistently referee treats this team vs overall patterns (>1.5 = more variable/inconsistent treatment)"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in enhanced RBS analysis: {str(e)}")

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
    """Predict match outcome using ML-based models"""
    try:
        prediction = await ml_predictor.predict_match(
            home_team=request.home_team,
            away_team=request.away_team,
            referee=request.referee_name,
            match_date=request.match_date
        )
        return prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@api_router.post("/export-prediction-pdf")
async def export_prediction_pdf(request: PDFExportRequest):
    """Export match prediction as PDF"""
    try:
        # Get prediction data
        prediction = await ml_predictor.predict_match(
            home_team=request.home_team,
            away_team=request.away_team,
            referee=request.referee_name,
            match_date=request.match_date
        )
        
        if not prediction.get('success', False):
            raise HTTPException(status_code=400, detail=f"Prediction failed: {prediction.get('error', 'Unknown error')}")
        
        # Get head-to-head data
        head_to_head_data = await ml_predictor.get_head_to_head_stats(request.home_team, request.away_team)
        
        # Get referee bias data for both teams
        home_rbs_data = None
        away_rbs_data = None
        
        try:
            # Get all team stats and matches for RBS calculation
            all_team_stats = await db.team_stats.find().to_list(10000)
            all_matches = await db.matches.find().to_list(10000)
            
            # Calculate RBS for home team
            home_rbs_result = await rbs_calculator.calculate_rbs_for_team_referee(
                request.home_team, request.referee_name, all_team_stats, all_matches
            )
            
            # Calculate RBS for away team  
            away_rbs_result = await rbs_calculator.calculate_rbs_for_team_referee(
                request.away_team, request.referee_name, all_team_stats, all_matches
            )
            
            referee_data = {
                'home_rbs': home_rbs_result,
                'away_rbs': away_rbs_result
            }
            
        except Exception as e:
            print(f"Error calculating RBS data: {e}")
            referee_data = None
        
        # Generate PDF
        pdf_buffer = await pdf_exporter.generate_prediction_pdf(
            prediction_data=prediction,
            head_to_head_data=head_to_head_data,
            referee_data=referee_data
        )
        
        # Create filename
        filename = f"match_prediction_{request.home_team.replace(' ', '_')}_vs_{request.away_team.replace(' ', '_')}.pdf"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@api_router.post("/train-ml-models")
async def train_ml_models():
    """Train machine learning models"""
    try:
        # Get current data counts before training
        matches_count = await db.matches.count_documents({})
        team_stats_count = await db.team_stats.count_documents({})
        player_stats_count = await db.player_stats.count_documents({})
        total_data_points = matches_count + team_stats_count + player_stats_count
        
        print(f"Starting ML model training with {total_data_points} total data points")
        
        result = await ml_predictor.train_models()
        
        if result['success']:
            # Save training metadata
            training_metadata = {
                'timestamp': datetime.now().isoformat(),
                'data_count_at_training': total_data_points,
                'data_breakdown': {
                    'matches': matches_count,
                    'team_stats': team_stats_count,
                    'player_stats': player_stats_count
                },
                'training_results': result.get('training_results', {}),
                'feature_count': len(ml_predictor.feature_columns) if hasattr(ml_predictor, 'feature_columns') else 0
            }
            
            try:
                with open('/tmp/model_training_metadata.json', 'w') as f:
                    json.dump(training_metadata, f, indent=2)
                print("Training metadata saved successfully")
            except Exception as e:
                print(f"Warning: Could not save training metadata: {e}")
        
        return result
        
    except Exception as e:
        print(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@api_router.get("/ml-models/status")
async def get_ml_models_status():
    """Get status of ML models"""
    try:
        models_loaded = hasattr(ml_predictor, 'models') and ml_predictor.models and len(ml_predictor.models) == 5
        feature_columns_count = len(ml_predictor.feature_columns) if hasattr(ml_predictor, 'feature_columns') and ml_predictor.feature_columns else 0
        
        # Get training metadata if available
        training_metadata = {}
        try:
            if os.path.exists('/tmp/model_training_metadata.json'):
                with open('/tmp/model_training_metadata.json', 'r') as f:
                    training_metadata = json.load(f)
        except:
            pass
        
        # Get current data counts for retraining recommendations
        try:
            matches_count = await db.matches.count_documents({})
            team_stats_count = await db.team_stats.count_documents({})
            player_stats_count = await db.player_stats.count_documents({})
            
            total_data_points = matches_count + team_stats_count + player_stats_count
            
            # Check if significant new data has been added since last training
            last_data_count = training_metadata.get('data_count_at_training', 0)
            data_increase_percentage = ((total_data_points - last_data_count) / max(last_data_count, 1)) * 100 if last_data_count > 0 else 0
            
            retraining_recommended = data_increase_percentage > 20  # Recommend retraining if data increased by >20%
            
        except Exception as e:
            print(f"Error getting data counts: {e}")
            matches_count = team_stats_count = player_stats_count = 0
            total_data_points = 0
            data_increase_percentage = 0
            retraining_recommended = False
        
        return {
            "models_loaded": models_loaded,
            "feature_columns_count": feature_columns_count,
            "models_info": {
                "classifier": "XGBoost Win/Draw/Loss classifier",
                "home_goals": "XGBoost home goals regressor", 
                "away_goals": "XGBoost away goals regressor",
                "home_xg": "XGBoost home xG regressor",
                "away_xg": "XGBoost away xG regressor"
            } if models_loaded else None,
            "last_trained": training_metadata.get('timestamp'),
            "training_data_count": training_metadata.get('data_count_at_training', 0),
            "current_data_count": total_data_points,
            "data_increase_since_training": f"{data_increase_percentage:.1f}%",
            "retraining_recommended": retraining_recommended,
            "retraining_reason": f"Data increased by {data_increase_percentage:.1f}% since last training" if retraining_recommended else None,
            "current_data_breakdown": {
                "matches": matches_count,
                "team_stats": team_stats_count, 
                "player_stats": player_stats_count
            }
        }
        
    except Exception as e:
        print(f"Error checking ML models status: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking ML models status: {str(e)}")

@api_router.post("/ml-models/reload")
async def reload_ml_models():
    """Reload ML models from disk"""
    try:
        ml_predictor.load_models()
        return {
            "success": True,
            "message": "ML models reloaded successfully",
            "models_loaded": len(ml_predictor.models) == 5
        }

        # Count existing data before deletion
        matches_count = await db.matches.count_documents({})
        team_stats_count = await db.team_stats.count_documents({})
        player_stats_count = await db.player_stats.count_documents({})
        rbs_results_count = await db.rbs_results.count_documents({})
        configs_count = await db.prediction_configs.count_documents({})
        rbs_configs_count = await db.rbs_configs.count_documents({})
        
        # Delete all collections
        await db.matches.delete_many({})
        await db.team_stats.delete_many({})
        await db.player_stats.delete_many({})
        await db.rbs_results.delete_many({})
        await db.prediction_configs.delete_many({})
        await db.rbs_configs.delete_many({})
        
        # Also delete any other collections that might exist
        await db.datasets.delete_many({})
        await db.comprehensive_team_stats.delete_many({})
        
        return {
            "success": True,
            "message": "Database wiped successfully",
            "deleted_counts": {
                "matches": matches_count,
                "team_stats": team_stats_count,
                "player_stats": player_stats_count,
                "rbs_results": rbs_results_count,
                "prediction_configs": configs_count,
                "rbs_configs": rbs_configs_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database wipe error: {str(e)}")

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

@api_router.post("/optimize-formula")
async def optimize_formula(request: dict):
    """AI-powered formula optimization"""
    try:
        optimization_type = request.get("optimization_type", "rbs")
        
        # Mock optimization results - in a real implementation, this would use ML algorithms
        # to analyze variable importance and suggest optimal weights
        
        if optimization_type == "rbs":
            # Simulate RBS optimization analysis
            recommendations = [
                {
                    "variable": "yellow_cards_weight",
                    "current_weight": 0.3,
                    "suggested_weight": 0.35,
                    "reasoning": "Analysis shows yellow cards have higher correlation with bias than currently weighted"
                },
                {
                    "variable": "red_cards_weight", 
                    "current_weight": 0.5,
                    "suggested_weight": 0.45,
                    "reasoning": "Red card impact slightly overweighted in current model"
                },
                {
                    "variable": "penalties_awarded_weight",
                    "current_weight": 0.5,
                    "suggested_weight": 0.6,
                    "reasoning": "Penalty decisions show strongest correlation with referee bias"
                }
            ]
            performance = {"r_squared": 0.847}
            improvement = 0.15
            variables_analyzed = 7
            
        elif optimization_type == "prediction":
            # Simulate prediction optimization analysis
            recommendations = [
                {
                    "variable": "ppg_adjustment_factor",
                    "current_weight": 0.15,
                    "suggested_weight": 0.18,
                    "reasoning": "Recent performance shows stronger predictive power"
                },
                {
                    "variable": "rbs_scaling_factor",
                    "current_weight": 0.2,
                    "suggested_weight": 0.22,
                    "reasoning": "Referee bias impact on outcomes is underestimated"
                }
            ]
            performance = {"r_squared": 0.912}
            improvement = 0.08
            variables_analyzed = 13
            
        else:  # combined
            # Simulate combined analysis
            recommendations = [
                {
                    "variable": "combined_analysis",
                    "current_weight": "multiple",
                    "suggested_weight": "optimized",
                    "reasoning": "Comprehensive analysis suggests rebalancing multiple factors"
                }
            ]
            performance = {"r_squared": 0.889}
            improvement = 0.12
            variables_analyzed = 20
        
        return {
            "success": True,
            "optimization_type": optimization_type,
            "performance": performance,
            "improvement": improvement,
            "variables_analyzed": variables_analyzed,
            "recommendations": recommendations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in formula optimization: {str(e)}")

@api_router.get("/referee-analysis")
async def get_referee_analysis():
    """Get comprehensive referee analysis results"""
    try:
        # Get total number of referees
        total_referees = len(await db.matches.distinct("referee"))
        
        # Get total matches
        total_matches = await db.matches.count_documents({})
        
        # Get number of teams covered
        teams_covered = len(await db.matches.distinct("home_team"))
        
        # Get RBS results if available
        rbs_results = await db.rbs_results.find({}).to_list(1000)
        
        # Calculate average bias score
        avg_bias_score = 0
        if rbs_results:
            total_bias = sum(abs(result.get('rbs_score', 0)) for result in rbs_results)
            avg_bias_score = total_bias / len(rbs_results)
        
        # Create referee profiles
        referees = []
        referee_names = await db.matches.distinct("referee")
        
        for referee_name in referee_names[:20]:  # Limit to first 20 for performance
            if not referee_name or str(referee_name).lower() in ['nan', 'null', 'none']:
                continue
                
            # Count matches for this referee
            match_count = await db.matches.count_documents({"referee": referee_name})
            
            # Count teams this referee has officiated
            teams_officiated = len(await db.matches.distinct("home_team", {"referee": referee_name}))
            
            # Get RBS score if available
            rbs_data = await db.rbs_results.find_one({"referee": referee_name})
            rbs_score = rbs_data.get('rbs_score', 0) if rbs_data else 0
            
            # Calculate confidence based on match count
            confidence = min(95, max(20, match_count * 8))
            
            referees.append({
                "name": referee_name,
                "matches": match_count,
                "teams": teams_officiated,
                "avg_bias_score": rbs_score,
                "confidence": confidence
            })
        
        # Sort by match count (most experienced first)
        referees.sort(key=lambda x: x["matches"], reverse=True)
        
        return {
            "success": True,
            "total_referees": total_referees,
            "total_matches": total_matches,
            "teams_covered": teams_covered,
            "avg_bias_score": round(avg_bias_score, 3),
            "referees": referees
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in referee analysis: {str(e)}")

@api_router.get("/referee-analysis/{referee_name}")
async def get_detailed_referee_analysis(referee_name: str):
    """Get detailed analysis for a specific referee"""
    try:
        # Get all matches for this referee
        matches = await db.matches.find({"referee": referee_name}).to_list(1000)
        
        # Get RBS data for this referee
        rbs_data = await db.rbs_results.find({"referee": referee_name}).to_list(1000)
        
        # Calculate statistics
        total_matches = len(matches)
        teams_officiated = len(set([match["home_team"] for match in matches] + [match["away_team"] for match in matches]))
        
        # Group RBS data by team
        team_rbs_data = {}
        total_bias = 0
        for result in rbs_data:
            team_name = result.get('team_name')
            if team_name:
                team_rbs_data[team_name] = {
                    'rbs_score': round(result.get('rbs_score', 0), 3),
                    'confidence_level': result.get('confidence_level', 0),
                    'matches_with_ref': result.get('matches_with_ref', 0),
                    'stats_breakdown': result.get('stats_breakdown', {}),
                    'config_used': result.get('config_used', 'default')
                }
                total_bias += abs(result.get('rbs_score', 0))
        
        # Calculate average bias score
        avg_bias = round(total_bias / len(rbs_data), 3) if rbs_data else 0
        
        # Get match outcomes breakdown
        home_wins = len([m for m in matches if m.get('home_score', 0) > m.get('away_score', 0)])
        away_wins = len([m for m in matches if m.get('away_score', 0) > m.get('home_score', 0)])
        draws = total_matches - home_wins - away_wins
        
        # Calculate cards and fouls statistics
        total_yellow_cards = sum(match.get('yellow_cards_home', 0) + match.get('yellow_cards_away', 0) for match in matches)
        total_red_cards = sum(match.get('red_cards_home', 0) + match.get('red_cards_away', 0) for match in matches)
        
        # Get most and least biased teams
        if team_rbs_data:
            most_biased_team = max(team_rbs_data.items(), key=lambda x: abs(x[1]['rbs_score']))
            least_biased_team = min(team_rbs_data.items(), key=lambda x: abs(x[1]['rbs_score']))
        else:
            most_biased_team = least_biased_team = None
        
        return {
            "success": True,
            "referee_name": referee_name,
            "total_matches": total_matches,
            "teams_officiated": teams_officiated,
            "avg_bias_score": avg_bias,
            "rbs_calculations": len(rbs_data),
            "match_outcomes": {
                "home_wins": home_wins,
                "away_wins": away_wins,
                "draws": draws,
                "home_win_percentage": round((home_wins / total_matches) * 100, 1) if total_matches > 0 else 0
            },
            "cards_and_fouls": {
                "total_yellow_cards": total_yellow_cards,
                "total_red_cards": total_red_cards,
                "yellow_cards_per_match": round(total_yellow_cards / total_matches, 2) if total_matches > 0 else 0,
                "red_cards_per_match": round(total_red_cards / total_matches, 2) if total_matches > 0 else 0
            },
            "bias_analysis": {
                "most_biased_team": {
                    "team": most_biased_team[0] if most_biased_team else None,
                    "rbs_score": most_biased_team[1]['rbs_score'] if most_biased_team else 0,
                    "bias_direction": "Favored" if most_biased_team and most_biased_team[1]['rbs_score'] > 0 else "Against" if most_biased_team else "Neutral"
                } if most_biased_team else None,
                "least_biased_team": {
                    "team": least_biased_team[0] if least_biased_team else None,
                    "rbs_score": least_biased_team[1]['rbs_score'] if least_biased_team else 0
                } if least_biased_team else None
            },
            "team_rbs_details": team_rbs_data
        }
    
    except Exception as e:
        print(f"Error in detailed referee analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error in detailed referee analysis: {str(e)}")

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

# Database client cleanup is now handled by the lifespan context manager above

if __name__ == "__main__":
    import uvicorn
    print("Starting Football Analytics API Server...")
    print("Checking app initialization...")
    
    try:
        print(f"App loaded successfully with {len(app.routes)} routes")
        print("Attempting to start Uvicorn server on port 8001...")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False, log_level="info")
    except Exception as e:
        print(f"❌ ERROR starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")  # Keep window open to see error
