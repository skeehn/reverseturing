"""Database models and connection for Reverse Turing Game"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import JSON, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class Player(UserMixin, db.Model):
    """Player model for user accounts"""
    __tablename__ = 'players'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Stats
    human_wins = db.Column(db.Integer, default=0)
    ai_detection_score = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)
    deception_score = db.Column(db.Float, default=0.0)
    detection_accuracy = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    game_sessions = db.relationship('GameSession', secondary='session_players', back_populates='players')
    votes = db.relationship('Vote', back_populates='player', lazy='dynamic')
    
    def update_stats(self, won_as_human=False, detected_correctly=False):
        """Update player statistics"""
        self.games_played += 1
        if won_as_human:
            self.human_wins += 1
        if detected_correctly:
            self.ai_detection_score += 1
        self.detection_accuracy = self.ai_detection_score / self.games_played if self.games_played > 0 else 0
        self.deception_score = self.human_wins / self.games_played if self.games_played > 0 else 0

class Room(db.Model):
    """Game room model"""
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    room_key = db.Column(db.String(50), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  # poetry, debate, personal, creative
    active = db.Column(db.Boolean, default=True)
    max_players = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('GameSession', back_populates='room', lazy='dynamic')

class Prompt(db.Model):
    """Prompts for the game"""
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    times_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance metrics
    avg_judge_accuracy = db.Column(db.Float, default=0.5)
    human_win_rate = db.Column(db.Float, default=0.5)

class GameSession(db.Model):
    """Individual game sessions"""
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    
    # Foreign keys
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id'))
    
    # Game data
    room_type = db.Column(db.String(50))
    human_response = db.Column(db.Text)
    ai_response = db.Column(db.Text)
    judge_prediction = db.Column(JSON)  # {human_prob: 0.7, reasoning: "..."}
    actual_labels = db.Column(JSON)  # {human: 0, ai: 1}
    
    # Model metadata
    judge_model_version = db.Column(db.String(50))
    responder_model_name = db.Column(db.String(100))
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    duration_ms = db.Column(db.Integer)
    
    # Status
    status = db.Column(db.String(20), default='waiting')  # waiting, collecting, judging, revealed, completed
    
    # Relationships
    room = db.relationship('Room', back_populates='sessions')
    prompt = db.relationship('Prompt', backref='sessions')
    players = db.relationship('Player', secondary='session_players', back_populates='game_sessions')
    votes = db.relationship('Vote', back_populates='session', lazy='dynamic')
    
    def is_judge_correct(self):
        """Check if judge prediction was correct"""
        if not self.judge_prediction or not self.actual_labels:
            return None
        human_prob = self.judge_prediction.get('human_prob', 0.5)
        judge_choice = 'human' if human_prob >= 0.5 else 'ai'
        actual = 'human' if self.actual_labels.get('human') == 1 else 'ai'
        return judge_choice == actual

# Association table for many-to-many relationship
session_players = db.Table('session_players',
    db.Column('session_id', db.Integer, db.ForeignKey('game_sessions.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('players.id'), primary_key=True)
)

class Vote(db.Model):
    """Player votes on responses"""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    
    chosen_label = db.Column(db.String(10))  # 'left' or 'right'
    actual_vote = db.Column(db.String(10))  # 'human' or 'ai'
    correct = db.Column(db.Boolean)
    confidence = db.Column(db.Float, default=0.5)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    session = db.relationship('GameSession', back_populates='votes')
    player = db.relationship('Player', back_populates='votes')
    
    # Unique constraint to prevent duplicate votes
    __table_args__ = (
        db.UniqueConstraint('session_id', 'player_id', name='unique_session_player_vote'),
    )

class TrainingBatch(db.Model):
    """Batches for model training"""
    __tablename__ = 'training_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    misclassified_examples = db.Column(JSON)  # List of session IDs
    total_examples = db.Column(db.Integer)
    model_version = db.Column(db.String(50))
    new_model_version = db.Column(db.String(50))
    
    # Training metadata
    training_started_at = db.Column(db.DateTime)
    training_completed_at = db.Column(db.DateTime)
    training_loss = db.Column(db.Float)
    validation_accuracy = db.Column(db.Float)
    
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    error_message = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ModelMetadata(db.Model):
    """Model version tracking"""
    __tablename__ = 'model_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), unique=True, nullable=False)
    model_type = db.Column(db.String(20))  # 'judge' or 'responder'
    base_model = db.Column(db.String(100))
    
    # Model location
    model_path = db.Column(db.String(255))
    lora_adapter_path = db.Column(db.String(255))
    
    # Performance metrics
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    
    # Training info
    training_examples = db.Column(db.Integer)
    training_batch_id = db.Column(db.Integer, db.ForeignKey('training_batches.id'))
    
    # Status
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deployed_at = db.Column(db.DateTime)
    
    notes = db.Column(db.Text)

class Leaderboard(db.Model):
    """Leaderboard entries"""
    __tablename__ = 'leaderboards'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    room_type = db.Column(db.String(50))  # null for overall
    period = db.Column(db.String(20))  # 'daily', 'weekly', 'monthly', 'all_time'
    
    # Scores
    deception_score = db.Column(db.Float, default=0.0)
    detection_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    games_played = db.Column(db.Integer, default=0)
    
    # Rank
    rank = db.Column(db.Integer)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    player = db.relationship('Player', backref='leaderboard_entries')
    
    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_leaderboard_ranking', 'room_type', 'period', 'overall_score'),
        Index('idx_leaderboard_player', 'player_id', 'period'),
    )

def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
def get_or_create_room(room_key, room_type='general'):
    """Get existing room or create new one"""
    room = Room.query.filter_by(room_key=room_key).first()
    if not room:
        room = Room(room_key=room_key, room_type=room_type)
        db.session.add(room)
        db.session.commit()
    return room