import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { io, Socket } from 'socket.io-client';
import { ResultsDisplay } from './ResultsDisplay';
import { useSocket } from '../context/SocketContext';

export function GameRoom() {
    const { roomId } = useParams<{ roomId: string }>();
    const navigate = useNavigate();
    const socket = useSocket();
    
    const [currentPrompt, setCurrentPrompt] = useState('');
    const [userResponse, setUserResponse] = useState('');
    const [gameState, setGameState] = useState('waiting'); // waiting, responding, judging, voting, results
    const [results, setResults] = useState<any>(null);
    const [leftResponse, setLeftResponse] = useState('');
    const [rightResponse, setRightResponse] = useState('');
    const [playerCount, setPlayerCount] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [selectedVote, setSelectedVote] = useState<'left' | 'right' | null>(null);
    
    useEffect(() => {
        if (!socket || !roomId) return;
        
        // Join room
        socket.emit('join_room', { 
            room_id: roomId, 
            room_type: localStorage.getItem('selectedRoomType') || 'general' 
        });
        
        // Event listeners
        socket.on('player_joined', (data) => {
            setPlayerCount(data.player_count);
        });
        
        socket.on('new_round', (data) => {
            setCurrentPrompt(data.prompt);
            setGameState('responding');
            setUserResponse('');
            setTimeRemaining(data.timeout || 90);
        });
        
        socket.on('judging_started', () => {
            setGameState('judging');
        });
        
        socket.on('voting_phase', (data) => {
            setLeftResponse(data.left_response);
            setRightResponse(data.right_response);
            setGameState('voting');
            setTimeRemaining(data.timeout || 30);
            setSelectedVote(null);
        });
        
        socket.on('round_results', (data) => {
            setResults(data);
            setGameState('results');
        });
        
        socket.on('error', (data) => {
            console.error('Game error:', data.message);
            alert(data.message);
        });
        
        return () => {
            socket.emit('leave_room', { room_id: roomId });
        };
    }, [socket, roomId]);
    
    // Timer countdown
    useEffect(() => {
        if (timeRemaining > 0) {
            const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
            return () => clearTimeout(timer);
        }
    }, [timeRemaining]);
    
    const submitResponse = () => {
        if (!socket || !userResponse.trim()) return;
        
        socket.emit('submit_response', {
            room_id: roomId,
            response: userResponse
        });
        setGameState('waiting');
    };
    
    const submitVote = (vote: 'left' | 'right') => {
        if (!socket) return;
        
        setSelectedVote(vote);
        socket.emit('submit_vote', {
            room_id: roomId,
            vote: vote
        });
    };
    
    const requestNewRound = () => {
        if (!socket) return;
        
        socket.emit('request_new_round', {
            room_id: roomId
        });
        setGameState('waiting');
    };
    
    return (
        <div className="game-room p-6 max-w-6xl mx-auto">
            <div className="mb-6 flex justify-between items-center">
                <h2 className="text-2xl font-bold">Room: {roomId}</h2>
                <div className="flex items-center space-x-4">
                    <span className="text-gray-400">Players: {playerCount}</span>
                    {timeRemaining > 0 && (
                        <span className="text-yellow-400">
                            Time: {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
                        </span>
                    )}
                    <button
                        onClick={() => navigate('/lobby')}
                        className="text-red-400 hover:text-red-300"
                    >
                        Leave Room
                    </button>
                </div>
            </div>
            
            {gameState === 'waiting' && (
                <div className="text-center py-20">
                    <h3 className="text-3xl mb-4">Waiting for next round...</h3>
                    <p className="text-gray-400">The game will start when enough players join</p>
                </div>
            )}
            
            {gameState === 'responding' && (
                <div className="response-phase bg-gray-800 p-6 rounded-lg">
                    <h3 className="text-xl font-bold mb-4">Write Your Response!</h3>
                    <div className="prompt-box bg-gray-700 p-4 rounded mb-4">
                        <p className="text-lg">{currentPrompt}</p>
                    </div>
                    <textarea
                        value={userResponse}
                        onChange={(e) => setUserResponse(e.target.value)}
                        placeholder="Write your response here... Try to sound human!"
                        className="w-full h-32 p-3 bg-gray-700 text-white border border-gray-600 rounded focus:border-blue-500 focus:outline-none"
                        maxLength={500}
                    />
                    <div className="flex justify-between items-center mt-4">
                        <span className="text-sm text-gray-400">
                            {userResponse.length}/500 characters
                        </span>
                        <button 
                            onClick={submitResponse}
                            disabled={!userResponse.trim()}
                            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-2 rounded transition-colors"
                        >
                            Submit Response
                        </button>
                    </div>
                </div>
            )}
            
            {gameState === 'judging' && (
                <div className="text-center py-20">
                    <h3 className="text-3xl mb-4">AI Judge is analyzing...</h3>
                    <div className="animate-pulse">
                        <div className="w-16 h-16 bg-blue-500 rounded-full mx-auto"></div>
                    </div>
                    <p className="text-gray-400 mt-4">The judge is determining which response is human</p>
                </div>
            )}
            
            {gameState === 'voting' && (
                <div className="voting-phase">
                    <h3 className="text-2xl font-bold mb-6 text-center">Which response is HUMAN?</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div 
                            className={`response-card bg-gray-800 p-6 rounded-lg cursor-pointer transition-all ${
                                selectedVote === 'left' ? 'ring-4 ring-green-500' : 'hover:bg-gray-700'
                            }`}
                            onClick={() => !selectedVote && submitVote('left')}
                        >
                            <h4 className="font-semibold text-green-400 mb-3">Response A</h4>
                            <p className="text-gray-300">{leftResponse}</p>
                            {selectedVote === 'left' && (
                                <p className="mt-4 text-green-400 font-semibold">✓ Your Vote</p>
                            )}
                        </div>
                        
                        <div 
                            className={`response-card bg-gray-800 p-6 rounded-lg cursor-pointer transition-all ${
                                selectedVote === 'right' ? 'ring-4 ring-blue-500' : 'hover:bg-gray-700'
                            }`}
                            onClick={() => !selectedVote && submitVote('right')}
                        >
                            <h4 className="font-semibold text-blue-400 mb-3">Response B</h4>
                            <p className="text-gray-300">{rightResponse}</p>
                            {selectedVote === 'right' && (
                                <p className="mt-4 text-blue-400 font-semibold">✓ Your Vote</p>
                            )}
                        </div>
                    </div>
                    {!selectedVote && (
                        <p className="text-center text-gray-400 mt-6">Click on the response you think was written by a human</p>
                    )}
                </div>
            )}
            
            {gameState === 'results' && results && (
                <>
                    <ResultsDisplay results={results} />
                    <div className="text-center mt-8">
                        <button
                            onClick={requestNewRound}
                            className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
                        >
                            Play Another Round
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}