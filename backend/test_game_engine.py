"""
Unit tests for the game engine module
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

# Import the modules to test
from game_engine import GameEngine, GamePhase, GameRoom, Player


class TestGameEngine(unittest.TestCase):
    """Test suite for GameEngine class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = GameEngine()
        self.room_id = "test_room_001"
        self.player_id = "player_001"
        self.player_name = "TestPlayer"
        
    def test_create_room(self):
        """Test room creation"""
        room = self.engine.create_room(
            room_id=self.room_id,
            room_type="poetry",
            max_players=4
        )
        
        self.assertIsNotNone(room)
        self.assertEqual(room.room_id, self.room_id)
        self.assertEqual(room.room_type, "poetry")
        self.assertEqual(room.max_players, 4)
        self.assertEqual(room.phase, GamePhase.WAITING)
        
    def test_join_room(self):
        """Test player joining a room"""
        # Create room first
        room = self.engine.create_room(self.room_id)
        
        # Join room
        success = self.engine.join_room(
            room_id=self.room_id,
            player_id=self.player_id,
            player_name=self.player_name
        )
        
        self.assertTrue(success)
        self.assertIn(self.player_id, room.players)
        self.assertEqual(room.players[self.player_id].name, self.player_name)
        
    def test_join_full_room(self):
        """Test joining a full room"""
        # Create room with max 2 players
        room = self.engine.create_room(self.room_id, max_players=2)
        
        # Add 2 players
        self.engine.join_room(self.room_id, "player1", "Player1")
        self.engine.join_room(self.room_id, "player2", "Player2")
        
        # Try to add third player
        success = self.engine.join_room(self.room_id, "player3", "Player3")
        
        self.assertFalse(success)
        self.assertEqual(len(room.players), 2)
        
    def test_leave_room(self):
        """Test player leaving a room"""
        # Setup
        room = self.engine.create_room(self.room_id)
        self.engine.join_room(self.room_id, self.player_id, self.player_name)
        
        # Leave room
        success = self.engine.leave_room(self.room_id, self.player_id)
        
        self.assertTrue(success)
        self.assertNotIn(self.player_id, room.players)
        
    def test_start_game(self):
        """Test starting a game"""
        # Setup room with minimum players
        room = self.engine.create_room(self.room_id)
        self.engine.join_room(self.room_id, "player1", "Player1")
        self.engine.join_room(self.room_id, "player2", "Player2")
        
        # Start game
        success = self.engine.start_game(self.room_id)
        
        self.assertTrue(success)
        self.assertEqual(room.phase, GamePhase.RESPONDING)
        self.assertIsNotNone(room.current_prompt)
        
    def test_submit_response(self):
        """Test submitting a player response"""
        # Setup and start game
        room = self.engine.create_room(self.room_id)
        self.engine.join_room(self.room_id, self.player_id, self.player_name)
        self.engine.join_room(self.room_id, "player2", "Player2")
        self.engine.start_game(self.room_id)
        
        # Submit response
        response_text = "This is my response to the prompt"
        success = self.engine.submit_response(
            room_id=self.room_id,
            player_id=self.player_id,
            response=response_text
        )
        
        self.assertTrue(success)
        self.assertEqual(room.responses[self.player_id], response_text)
        
    def test_submit_vote(self):
        """Test submitting a vote"""
        # Setup game in voting phase
        room = self.engine.create_room(self.room_id)
        self.engine.join_room(self.room_id, self.player_id, self.player_name)
        self.engine.join_room(self.room_id, "player2", "Player2")
        room.phase = GamePhase.VOTING
        
        # Submit vote
        success = self.engine.submit_vote(
            room_id=self.room_id,
            player_id=self.player_id,
            voted_response_id="response_001"
        )
        
        self.assertTrue(success)
        self.assertEqual(room.votes[self.player_id], "response_001")
        
    def test_phase_transitions(self):
        """Test game phase transitions"""
        room = self.engine.create_room(self.room_id)
        
        # Test all phase transitions
        transitions = [
            (GamePhase.WAITING, GamePhase.RESPONDING),
            (GamePhase.RESPONDING, GamePhase.VOTING),
            (GamePhase.VOTING, GamePhase.JUDGING),
            (GamePhase.JUDGING, GamePhase.RESULTS),
            (GamePhase.RESULTS, GamePhase.RESPONDING),
        ]
        
        for from_phase, to_phase in transitions:
            room.phase = from_phase
            self.engine.transition_phase(self.room_id, to_phase)
            self.assertEqual(room.phase, to_phase)


class TestGameRoom(unittest.TestCase):
    """Test suite for GameRoom class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.room = GameRoom(
            room_id="test_room",
            room_type="debate",
            max_players=6
        )
        
    def test_room_initialization(self):
        """Test room initialization"""
        self.assertEqual(self.room.room_id, "test_room")
        self.assertEqual(self.room.room_type, "debate")
        self.assertEqual(self.room.max_players, 6)
        self.assertEqual(len(self.room.players), 0)
        self.assertEqual(self.room.phase, GamePhase.WAITING)
        
    def test_add_player(self):
        """Test adding a player to room"""
        player = Player("player1", "TestPlayer")
        self.room.add_player(player)
        
        self.assertIn("player1", self.room.players)
        self.assertEqual(self.room.players["player1"].name, "TestPlayer")
        
    def test_remove_player(self):
        """Test removing a player from room"""
        player = Player("player1", "TestPlayer")
        self.room.add_player(player)
        self.room.remove_player("player1")
        
        self.assertNotIn("player1", self.room.players)
        
    def test_is_full(self):
        """Test checking if room is full"""
        self.room.max_players = 2
        
        self.assertFalse(self.room.is_full())
        
        self.room.add_player(Player("p1", "Player1"))
        self.assertFalse(self.room.is_full())
        
        self.room.add_player(Player("p2", "Player2"))
        self.assertTrue(self.room.is_full())
        
    def test_reset_round(self):
        """Test resetting a round"""
        # Add some data
        self.room.responses = {"p1": "response1"}
        self.room.votes = {"p1": "vote1"}
        self.room.ai_response = "AI response"
        
        # Reset
        self.room.reset_round()
        
        # Check cleared
        self.assertEqual(len(self.room.responses), 0)
        self.assertEqual(len(self.room.votes), 0)
        self.assertIsNone(self.room.ai_response)


class TestPlayer(unittest.TestCase):
    """Test suite for Player class"""
    
    def test_player_initialization(self):
        """Test player initialization"""
        player = Player("player123", "John Doe")
        
        self.assertEqual(player.player_id, "player123")
        self.assertEqual(player.name, "John Doe")
        self.assertEqual(player.score, 0)
        self.assertEqual(player.games_played, 0)
        
    def test_update_score(self):
        """Test updating player score"""
        player = Player("p1", "Player")
        
        player.update_score(10)
        self.assertEqual(player.score, 10)
        
        player.update_score(5)
        self.assertEqual(player.score, 15)
        
    def test_increment_games(self):
        """Test incrementing games played"""
        player = Player("p1", "Player")
        
        player.increment_games()
        self.assertEqual(player.games_played, 1)
        
        player.increment_games()
        self.assertEqual(player.games_played, 2)


@pytest.fixture
def mock_ai_judge():
    """Mock AI judge for testing"""
    with patch('game_engine.AIJudge') as mock:
        judge = mock.return_value
        judge.analyze.return_value = {
            'is_human': True,
            'confidence': 0.85,
            'reasoning': 'Test reasoning'
        }
        yield judge


@pytest.fixture
def mock_ai_responder():
    """Mock AI responder for testing"""
    with patch('game_engine.AIResponder') as mock:
        responder = mock.return_value
        responder.generate.return_value = "This is an AI generated response"
        yield responder


def test_ai_integration(mock_ai_judge, mock_ai_responder):
    """Test AI components integration"""
    engine = GameEngine()
    room = engine.create_room("ai_test_room")
    
    # Test AI responder
    ai_response = mock_ai_responder.generate("Test prompt")
    assert ai_response == "This is an AI generated response"
    
    # Test AI judge
    judgment = mock_ai_judge.analyze("Test response")
    assert judgment['is_human'] == True
    assert judgment['confidence'] == 0.85


if __name__ == '__main__':
    unittest.main()