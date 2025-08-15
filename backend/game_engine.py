"""Game session management for Reverse Turing Game"""

import logging
import random
import time
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from flask_socketio import SocketIO, emit

# Local imports
from database import (
    db, GameSession as DBGameSession, Prompt, Vote, 
    Player, Room, TrainingBatch
)
from prompts.room_prompts import ROOM_PROMPTS

logger = logging.getLogger(__name__)

class GameSession:
    """Manages a single game session in a room"""
    
    def __init__(self, room_id: str, room_type: str = "general", 
                 judge_ai=None, responder_ai=None, 
                 db_session=None, socketio=None):
        """Initialize a game session
        
        Args:
            room_id: Unique room identifier
            room_type: Type of room (poetry, debate, personal, creative)
            judge_ai: JudgeAI instance
            responder_ai: ResponderAI instance
            db_session: SQLAlchemy database session
            socketio: SocketIO instance
        """
        self.room_id = room_id
        self.room_type = room_type
        self.players = {}  # {player_id: {'username': str, 'responded': bool, 'voted': bool}}
        self.current_prompt = None
        self.current_prompt_id = None
        self.responses = {}  # {'human': str, 'ai': str}
        self.response_order = []  # ['human', 'ai'] or ['ai', 'human'] for display
        self.votes = {}  # {player_id: 'left' or 'right'}
        self.judgments = {}  # {'human': {...}, 'ai': {...}}
        self.status = 'waiting'  # waiting, prompting, collecting, judging, voting, revealing, completed
        self.round_start_time = None
        self.current_session_id = None
        
        # AI models
        self.judge_ai = judge_ai
        self.responder_ai = responder_ai
        
        # Database and socket
        self.db = db_session
        self.socketio = socketio
        
        # Timers
        self.response_timer = None
        self.voting_timer = None
        
        logger.info(f"GameSession created for room {room_id} (type: {room_type})")
    
    def add_player(self, player_id: str, username: str) -> bool:
        """Add a player to the session
        
        Args:
            player_id: Player's unique ID
            username: Player's display name
            
        Returns:
            True if player was added successfully
        """
        if player_id not in self.players:
            self.players[player_id] = {
                'username': username,
                'responded': False,
                'voted': False,
                'response': None,
                'vote': None
            }
            logger.info(f"Player {username} ({player_id}) joined room {self.room_id}")
            return True
        return False
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the session
        
        Args:
            player_id: Player's unique ID
            
        Returns:
            True if player was removed successfully
        """
        if player_id in self.players:
            username = self.players[player_id]['username']
            del self.players[player_id]
            logger.info(f"Player {username} ({player_id}) left room {self.room_id}")
            
            # Remove their vote if they had one
            if player_id in self.votes:
                del self.votes[player_id]
            
            return True
        return False
    
    def get_player_count(self) -> int:
        """Get the number of players in the session"""
        return len(self.players)
    
    async def start_round(self):
        """Start a new game round"""
        try:
            logger.info(f"Starting new round in room {self.room_id}")
            
            # Reset round state
            self.status = 'prompting'
            self.responses = {}
            self.votes = {}
            self.judgments = {}
            self.round_start_time = time.time()
            
            # Reset player states
            for player_id in self.players:
                self.players[player_id]['responded'] = False
                self.players[player_id]['voted'] = False
                self.players[player_id]['response'] = None
                self.players[player_id]['vote'] = None
            
            # Get a random prompt
            self.current_prompt = self.get_prompt()
            
            # Create database session
            if self.db:
                db_session = DBGameSession(
                    room_type=self.room_type,
                    status='collecting',
                    judge_model_version='v1.0',  # TODO: Get from model
                    responder_model_name=self.responder_ai.model_name if self.responder_ai else 'unknown'
                )
                
                # Link to prompt
                if self.current_prompt_id:
                    db_session.prompt_id = self.current_prompt_id
                
                # Link to room
                room = Room.query.filter_by(room_key=self.room_id).first()
                if room:
                    db_session.room_id = room.id
                
                self.db.add(db_session)
                self.db.commit()
                self.current_session_id = db_session.id
            
            # Generate AI response immediately
            if self.responder_ai:
                logger.info("Generating AI response...")
                ai_response = self.responder_ai.generate_response(self.current_prompt)
                self.responses['ai'] = ai_response
                logger.info(f"AI response generated: {ai_response[:100]}...")
            else:
                # Fallback response
                self.responses['ai'] = "This is a placeholder AI response."
            
            # Update status
            self.status = 'collecting'
            
            # Emit prompt to all players
            if self.socketio:
                self.socketio.emit('new_round', {
                    'prompt': self.current_prompt,
                    'room_type': self.room_type,
                    'round_number': self.get_round_number(),
                    'timeout': 90  # seconds
                }, room=self.room_id)
            
            # Start response timer
            self._start_response_timer()
            
        except Exception as e:
            logger.error(f"Error starting round: {str(e)}")
            self.status = 'error'
            if self.socketio:
                self.socketio.emit('error', {
                    'message': 'Failed to start round'
                }, room=self.room_id)
    
    def get_prompt(self) -> str:
        """Get a random prompt for the current room type
        
        Returns:
            Prompt text
        """
        # First try to get from database
        if self.db:
            prompt = Prompt.query.filter_by(room_type=self.room_type).order_by(
                db.func.random()
            ).first()
            
            if prompt:
                self.current_prompt_id = prompt.id
                prompt.times_used += 1
                self.db.commit()
                return prompt.text
        
        # Fallback to hardcoded prompts
        prompts = ROOM_PROMPTS.get(self.room_type, ROOM_PROMPTS.get('general', []))
        if not prompts:
            prompts = [
                "What's your favorite childhood memory?",
                "Describe a perfect day.",
                "What would you do with a million dollars?",
                "Tell me about a time you overcame a challenge."
            ]
        
        return random.choice(prompts)
    
    def submit_human_response(self, player_id: str, response: str) -> bool:
        """Submit a human player's response
        
        Args:
            player_id: Player's unique ID
            response: Player's response text
            
        Returns:
            True if response was accepted
        """
        if self.status != 'collecting':
            logger.warning(f"Response rejected - wrong status: {self.status}")
            return False
        
        if player_id not in self.players:
            logger.warning(f"Response rejected - unknown player: {player_id}")
            return False
        
        if self.players[player_id]['responded']:
            logger.warning(f"Response rejected - player already responded: {player_id}")
            return False
        
        # Store the response
        self.responses['human'] = response
        self.players[player_id]['responded'] = True
        self.players[player_id]['response'] = response
        
        logger.info(f"Human response received from {player_id}: {response[:50]}...")
        
        # Check if we have both responses
        if 'human' in self.responses and 'ai' in self.responses:
            # Move to judging phase
            self._start_judging()
        
        return True
    
    def _start_judging(self):
        """Start the judging phase"""
        try:
            logger.info("Starting judging phase...")
            self.status = 'judging'
            
            # Cancel response timer
            if self.response_timer:
                self.response_timer.cancel()
            
            # Notify players
            if self.socketio:
                self.socketio.emit('judging_started', {
                    'message': 'AI Judge is analyzing responses...'
                }, room=self.room_id)
            
            # Judge both responses
            if self.judge_ai:
                human_judgment = self.judge_ai.judge_response(
                    self.current_prompt, 
                    self.responses['human']
                )
                ai_judgment = self.judge_ai.judge_response(
                    self.current_prompt, 
                    self.responses['ai']
                )
                
                self.judgments = {
                    'human': human_judgment,
                    'ai': ai_judgment
                }
                
                logger.info(f"Judge verdicts - Human: {human_judgment['human_prob']:.2f}, AI: {ai_judgment['human_prob']:.2f}")
            else:
                # Fallback judgments
                self.judgments = {
                    'human': {'human_prob': 0.7, 'reasoning': 'Seems human-like'},
                    'ai': {'human_prob': 0.3, 'reasoning': 'Seems AI-generated'}
                }
            
            # Save to database
            self.save_session_data()
            
            # Move to voting phase
            self._start_voting()
            
        except Exception as e:
            logger.error(f"Error in judging phase: {str(e)}")
            self.status = 'error'
    
    def _start_voting(self):
        """Start the voting phase"""
        logger.info("Starting voting phase...")
        self.status = 'voting'
        
        # Randomize order for display
        self.response_order = ['human', 'ai'] if random.random() > 0.5 else ['ai', 'human']
        
        # Prepare responses for display (without labels)
        left_response = self.responses[self.response_order[0]]
        right_response = self.responses[self.response_order[1]]
        
        # Emit voting phase
        if self.socketio:
            self.socketio.emit('voting_phase', {
                'prompt': self.current_prompt,
                'left_response': left_response,
                'right_response': right_response,
                'timeout': 30  # seconds
            }, room=self.room_id)
        
        # Start voting timer
        self._start_voting_timer()
    
    def submit_vote(self, player_id: str, vote: str) -> bool:
        """Submit a player's vote
        
        Args:
            player_id: Player's unique ID
            vote: 'left' or 'right'
            
        Returns:
            True if vote was accepted
        """
        if self.status != 'voting':
            return False
        
        if player_id not in self.players:
            return False
        
        if self.players[player_id]['voted']:
            return False
        
        # Store the vote
        self.votes[player_id] = vote
        self.players[player_id]['voted'] = True
        self.players[player_id]['vote'] = vote
        
        logger.info(f"Vote received from {player_id}: {vote}")
        
        # Check if all players have voted
        if len(self.votes) == len(self.players):
            self._reveal_results()
        
        return True
    
    def _reveal_results(self):
        """Reveal the results of the round"""
        logger.info("Revealing results...")
        self.status = 'revealing'
        
        # Cancel voting timer
        if self.voting_timer:
            self.voting_timer.cancel()
        
        # Calculate results
        left_is = self.response_order[0]
        right_is = self.response_order[1]
        
        # Count player votes
        player_votes = {'left': 0, 'right': 0}
        for vote in self.votes.values():
            player_votes[vote] += 1
        
        # Determine winners
        judge_correct = self.judgments['human']['human_prob'] > self.judgments['ai']['human_prob']
        
        # Calculate player accuracy
        correct_votes = 0
        for player_id, vote in self.votes.items():
            if (vote == 'left' and left_is == 'human') or (vote == 'right' and right_is == 'human'):
                correct_votes += 1
        
        player_accuracy = correct_votes / len(self.votes) if self.votes else 0
        
        # Update player stats
        self._update_player_stats()
        
        # Prepare results
        results = {
            'prompt': self.current_prompt,
            'left_response': self.responses[left_is],
            'right_response': self.responses[right_is],
            'left_is': left_is,
            'right_is': right_is,
            'judge_verdict': {
                'human': self.judgments['human'],
                'ai': self.judgments['ai'],
                'correct': judge_correct
            },
            'player_votes': player_votes,
            'player_accuracy': player_accuracy,
            'correct_votes': correct_votes,
            'total_votes': len(self.votes)
        }
        
        # Emit results
        if self.socketio:
            self.socketio.emit('round_results', results, room=self.room_id)
        
        # Mark session as completed
        self.status = 'completed'
        
        # Check if judge was wrong (for training)
        if not judge_correct:
            self._mark_for_training()
    
    def save_session_data(self):
        """Save session data to database"""
        if not self.db or not self.current_session_id:
            return
        
        try:
            # Update session record
            session = DBGameSession.query.get(self.current_session_id)
            if session:
                session.human_response = self.responses.get('human', '')
                session.ai_response = self.responses.get('ai', '')
                session.judge_prediction = {
                    'human': self.judgments.get('human', {}),
                    'ai': self.judgments.get('ai', {})
                }
                session.actual_labels = {'human': 1, 'ai': 0}
                session.status = self.status
                session.completed_at = datetime.utcnow()
                
                if self.round_start_time:
                    session.duration_ms = int((time.time() - self.round_start_time) * 1000)
                
                self.db.commit()
                logger.info(f"Session data saved: {self.current_session_id}")
        
        except Exception as e:
            logger.error(f"Error saving session data: {str(e)}")
            self.db.rollback()
    
    def _update_player_stats(self):
        """Update player statistics based on round results"""
        if not self.db:
            return
        
        try:
            for player_id, vote in self.votes.items():
                # Skip guest players
                if player_id.startswith('guest_'):
                    continue
                
                # Get player from database
                player = Player.query.get(int(player_id))
                if not player:
                    continue
                
                # Check if they voted correctly
                left_is = self.response_order[0]
                right_is = self.response_order[1]
                correct = (vote == 'left' and left_is == 'human') or (vote == 'right' and right_is == 'human')
                
                # Update stats
                player.games_played += 1
                if correct:
                    player.ai_detection_score += 1
                
                # If they submitted the human response
                if player_id in self.players and self.players[player_id]['responded']:
                    # Check if judge thought their response was human
                    if self.judgments['human']['human_prob'] > 0.5:
                        player.human_wins += 1
                
                # Update derived stats
                player.update_stats()
                
            self.db.commit()
            logger.info("Player stats updated")
            
        except Exception as e:
            logger.error(f"Error updating player stats: {str(e)}")
            self.db.rollback()
    
    def _mark_for_training(self):
        """Mark session for training if judge was wrong"""
        if not self.db or not self.current_session_id:
            return
        
        try:
            # Check if we should create a training batch
            misclassified_count = DBGameSession.query.filter_by(
                judge_prediction={'correct': False}
            ).count()
            
            if misclassified_count >= 10:  # Batch size threshold
                # Create training batch
                batch = TrainingBatch(
                    misclassified_examples={'session_ids': [self.current_session_id]},
                    total_examples=1,
                    model_version='v1.0',
                    status='pending'
                )
                self.db.add(batch)
                self.db.commit()
                logger.info(f"Training batch created with session {self.current_session_id}")
                
        except Exception as e:
            logger.error(f"Error marking for training: {str(e)}")
            self.db.rollback()
    
    def _start_response_timer(self):
        """Start timer for response collection phase"""
        from threading import Timer
        
        def timeout():
            if self.status == 'collecting':
                logger.info("Response timeout reached")
                # Use AI response only if no human response
                if 'human' not in self.responses:
                    self.responses['human'] = "No response provided"
                self._start_judging()
        
        self.response_timer = Timer(90.0, timeout)  # 90 seconds
        self.response_timer.start()
    
    def _start_voting_timer(self):
        """Start timer for voting phase"""
        from threading import Timer
        
        def timeout():
            if self.status == 'voting':
                logger.info("Voting timeout reached")
                self._reveal_results()
        
        self.voting_timer = Timer(30.0, timeout)  # 30 seconds
        self.voting_timer.start()
    
    def get_round_number(self) -> int:
        """Get the current round number for this room"""
        if not self.db:
            return 1
        
        try:
            room = Room.query.filter_by(room_key=self.room_id).first()
            if room:
                return DBGameSession.query.filter_by(room_id=room.id).count() + 1
        except:
            pass
        
        return 1
    
    def cleanup(self):
        """Clean up session resources"""
        if self.response_timer:
            self.response_timer.cancel()
        if self.voting_timer:
            self.voting_timer.cancel()
        
        logger.info(f"GameSession {self.room_id} cleaned up")