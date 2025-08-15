"""Main Flask application for Reverse Turing Game"""

import logging
import uuid
from datetime import datetime
from flask import Flask, request, session, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import redis
import json

# Local imports
from config import get_config
from database import db, init_db, Player, GameSession as DBGameSession, get_or_create_room
from game_engine import GameSession
from models.judge import JudgeAI
from models.responder import ResponderAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize extensions
CORS(app, resources={r"/*": {"origins": app.config['CORS_ALLOWED_ORIGINS']}})
socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ALLOWED_ORIGINS'], 
                    async_mode='eventlet', logger=True, engineio_logger=True)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# Initialize database
init_db(app)

# Initialize Redis
redis_client = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'],
    password=app.config['REDIS_PASSWORD'],
    decode_responses=True
)

# Active game sessions
active_sessions = {}

# Initialize AI models (lazy loading)
judge_ai = None
responder_ai = None

def get_judge_ai():
    """Lazy load judge AI model"""
    global judge_ai
    if judge_ai is None:
        logger.info("Loading Judge AI model...")
        judge_ai = JudgeAI()
    return judge_ai

def get_responder_ai():
    """Lazy load responder AI model"""
    global responder_ai
    if responder_ai is None:
        logger.info("Loading Responder AI model...")
        responder_ai = ResponderAI()
    return responder_ai

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return Player.query.get(int(user_id))

# ===== REST API Routes =====

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'models_loaded': {
            'judge': judge_ai is not None,
            'responder': responder_ai is not None
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new player"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if Player.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if Player.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new player
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    player = Player(
        username=username,
        email=email,
        password_hash=password_hash
    )
    
    db.session.add(player)
    db.session.commit()
    
    return jsonify({
        'message': 'Registration successful',
        'player_id': player.id,
        'username': player.username
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    """Login a player"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not all([username, password]):
        return jsonify({'error': 'Missing username or password'}), 400
    
    player = Player.query.filter_by(username=username).first()
    
    if not player or not bcrypt.check_password_hash(player.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last seen
    player.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Login user
    login_user(player)
    
    # Store in session
    session['player_id'] = player.id
    session['username'] = player.username
    
    return jsonify({
        'message': 'Login successful',
        'player_id': player.id,
        'username': player.username,
        'stats': {
            'games_played': player.games_played,
            'human_wins': player.human_wins,
            'detection_accuracy': player.detection_accuracy
        }
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout current player"""
    logout_user()
    session.clear()
    return jsonify({'message': 'Logout successful'})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get list of active rooms"""
    from database import Room
    
    rooms = Room.query.filter_by(active=True).all()
    room_list = []
    
    for room in rooms:
        # Get player count from Redis
        player_count = redis_client.scard(f"room:{room.room_key}:players")
        room_list.append({
            'room_key': room.room_key,
            'room_type': room.room_type,
            'player_count': player_count,
            'max_players': room.max_players
        })
    
    return jsonify({'rooms': room_list})

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get leaderboard data"""
    room_type = request.args.get('room_type', None)
    period = request.args.get('period', 'all_time')
    
    from database import Leaderboard
    
    query = Leaderboard.query.filter_by(period=period)
    if room_type:
        query = query.filter_by(room_type=room_type)
    
    leaderboard = query.order_by(Leaderboard.overall_score.desc()).limit(100).all()
    
    result = []
    for entry in leaderboard:
        result.append({
            'rank': entry.rank,
            'username': entry.player.username,
            'deception_score': entry.deception_score,
            'detection_score': entry.detection_score,
            'overall_score': entry.overall_score,
            'games_played': entry.games_played
        })
    
    return jsonify({'leaderboard': result})

# ===== WebSocket Events =====

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    if 'player_id' not in session:
        # Assign temporary player ID
        session['player_id'] = f"guest_{uuid.uuid4().hex[:8]}"
        session['username'] = f"Guest_{session['player_id'][-4:]}"
    
    logger.info(f"Client connected: {session.get('username')}")
    emit('connected', {
        'player_id': session['player_id'],
        'username': session['username']
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {session.get('username')}")
    
    # Remove from any rooms
    for room_id, game_session in active_sessions.items():
        if session.get('player_id') in game_session.players:
            game_session.remove_player(session['player_id'])
            if len(game_session.players) == 0:
                # Clean up empty session
                del active_sessions[room_id]
                redis_client.delete(f"room:{room_id}:players")

@socketio.on('join_room')
def on_join(data):
    """Handle player joining a room"""
    room_id = data.get('room_id')
    room_type = data.get('room_type', 'general')
    player_id = session.get('player_id')
    username = session.get('username')
    
    if not room_id:
        emit('error', {'message': 'Room ID required'})
        return
    
    # Join the Socket.IO room
    join_room(room_id)
    
    # Add to Redis set
    redis_client.sadd(f"room:{room_id}:players", player_id)
    
    # Create or get game session
    if room_id not in active_sessions:
        logger.info(f"Creating new game session for room {room_id}")
        active_sessions[room_id] = GameSession(
            room_id=room_id, 
            room_type=room_type,
            judge_ai=get_judge_ai(),
            responder_ai=get_responder_ai(),
            db_session=db.session,
            socketio=socketio
        )
        
        # Create room in database if needed
        get_or_create_room(room_id, room_type)
    
    game_session = active_sessions[room_id]
    game_session.add_player(player_id, username)
    
    # Notify room
    emit('player_joined', {
        'player_id': player_id,
        'username': username,
        'player_count': len(game_session.players),
        'room_info': {
            'room_id': room_id,
            'room_type': room_type,
            'status': game_session.status
        }
    }, room=room_id)
    
    # Start round if enough players
    if len(game_session.players) >= app.config['MIN_PLAYERS_PER_ROOM'] and game_session.status == 'waiting':
        socketio.start_background_task(game_session.start_round)

@socketio.on('leave_room')
def on_leave(data):
    """Handle player leaving a room"""
    room_id = data.get('room_id')
    player_id = session.get('player_id')
    username = session.get('username')
    
    if not room_id:
        return
    
    # Leave Socket.IO room
    leave_room(room_id)
    
    # Remove from Redis
    redis_client.srem(f"room:{room_id}:players", player_id)
    
    # Update game session
    if room_id in active_sessions:
        game_session = active_sessions[room_id]
        game_session.remove_player(player_id)
        
        emit('player_left', {
            'player_id': player_id,
            'username': username,
            'player_count': len(game_session.players)
        }, room=room_id)
        
        # Clean up if empty
        if len(game_session.players) == 0:
            del active_sessions[room_id]

@socketio.on('submit_response')
def on_response(data):
    """Handle human response submission"""
    room_id = data.get('room_id')
    response = data.get('response')
    player_id = session.get('player_id')
    
    if not all([room_id, response]):
        emit('error', {'message': 'Missing required data'})
        return
    
    if room_id not in active_sessions:
        emit('error', {'message': 'Invalid room'})
        return
    
    game_session = active_sessions[room_id]
    
    # Validate response length
    if len(response) > app.config['MAX_RESPONSE_LENGTH']:
        emit('error', {'message': f'Response too long (max {app.config["MAX_RESPONSE_LENGTH"]} characters)'})
        return
    
    # Submit response
    success = game_session.submit_human_response(player_id, response)
    
    if success:
        emit('response_submitted', {
            'player_id': player_id,
            'status': 'success'
        }, room=room_id)
    else:
        emit('error', {'message': 'Failed to submit response'})

@socketio.on('submit_vote')
def on_vote(data):
    """Handle player vote on which response is human"""
    room_id = data.get('room_id')
    vote = data.get('vote')  # 'left' or 'right'
    player_id = session.get('player_id')
    
    if not all([room_id, vote]):
        emit('error', {'message': 'Missing required data'})
        return
    
    if room_id not in active_sessions:
        emit('error', {'message': 'Invalid room'})
        return
    
    game_session = active_sessions[room_id]
    success = game_session.submit_vote(player_id, vote)
    
    if success:
        emit('vote_submitted', {
            'player_id': player_id,
            'status': 'success'
        })
    else:
        emit('error', {'message': 'Failed to submit vote'})

@socketio.on('request_new_round')
def on_new_round(data):
    """Request a new round in the room"""
    room_id = data.get('room_id')
    
    if room_id not in active_sessions:
        emit('error', {'message': 'Invalid room'})
        return
    
    game_session = active_sessions[room_id]
    
    if game_session.status != 'completed':
        emit('error', {'message': 'Current round not completed'})
        return
    
    # Start new round
    socketio.start_background_task(game_session.start_round)

# ===== Main Entry Point =====

if __name__ == '__main__':
    logger.info("Starting Reverse Turing Game server...")
    
    # Pre-load models if configured
    if app.config.get('PRELOAD_MODELS', False):
        logger.info("Pre-loading AI models...")
        get_judge_ai()
        get_responder_ai()
    
    # Run the application
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=5000, 
                 debug=app.config['DEBUG'])