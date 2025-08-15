import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Room {
  room_key: string;
  room_type: string;
  player_count: number;
  max_players: number;
}

const ROOM_TYPES = [
  { id: 'poetry', name: 'Poetry', icon: '📝', description: 'Write poems and verses' },
  { id: 'debate', name: 'Debate', icon: '💬', description: 'Argue and persuade' },
  { id: 'personal', name: 'Personal', icon: '👤', description: 'Share personal stories' },
  { id: 'creative', name: 'Creative', icon: '🎨', description: 'Creative writing' },
];

export default function Lobby() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedType, setSelectedType] = useState('general');
  const [roomName, setRoomName] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRooms();
    const interval = setInterval(fetchRooms, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRooms = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/rooms');
      const data = await response.json();
      setRooms(data.rooms || []);
    } catch (error) {
      console.error('Failed to fetch rooms:', error);
    }
  };

  const createRoom = () => {
    if (!roomName.trim()) {
      alert('Please enter a room name');
      return;
    }
    
    localStorage.setItem('selectedRoomType', selectedType);
    navigate(`/room/${roomName}`);
  };

  const joinRoom = (roomKey: string, roomType: string) => {
    localStorage.setItem('selectedRoomType', roomType);
    navigate(`/room/${roomKey}`);
  };

  const quickPlay = () => {
    const randomRoom = `room-${Date.now()}`;
    const randomType = ROOM_TYPES[Math.floor(Math.random() * ROOM_TYPES.length)].id;
    localStorage.setItem('selectedRoomType', randomType);
    navigate(`/room/${randomRoom}`);
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8 text-center">Game Lobby</h1>

      {/* Quick Play Button */}
      <div className="text-center mb-8">
        <button
          onClick={quickPlay}
          className="bg-green-600 hover:bg-green-700 text-white text-xl font-bold py-4 px-8 rounded-lg transition-colors"
        >
          🎮 Quick Play
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Create Room Section */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Create New Room</h2>
          
          <div className="mb-4">
            <label className="block text-gray-300 mb-2">Room Name</label>
            <input
              type="text"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              placeholder="Enter room name..."
              className="w-full px-3 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-300 mb-2">Room Type</label>
            <div className="grid grid-cols-2 gap-3">
              {ROOM_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    selectedType === type.id
                      ? 'border-blue-500 bg-blue-500/20'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <div className="text-2xl mb-1">{type.icon}</div>
                  <div className="font-semibold">{type.name}</div>
                  <div className="text-xs text-gray-400">{type.description}</div>
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={createRoom}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors"
          >
            Create Room
          </button>
        </div>

        {/* Active Rooms Section */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">Active Rooms</h2>
          
          {rooms.length === 0 ? (
            <p className="text-gray-400">No active rooms. Create one to start playing!</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {rooms.map((room) => (
                <div
                  key={room.room_key}
                  className="bg-gray-700 p-4 rounded-lg hover:bg-gray-600 cursor-pointer transition-colors"
                  onClick={() => joinRoom(room.room_key, room.room_type)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-lg">{room.room_key}</h3>
                      <p className="text-sm text-gray-400">
                        Type: {room.room_type} • Players: {room.player_count}/{room.max_players}
                      </p>
                    </div>
                    <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors">
                      Join
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Game Instructions */}
      <div className="mt-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-2xl font-bold mb-4">How to Play</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-gray-300">
          <div>
            <h3 className="font-semibold text-blue-400 mb-2">1. Respond</h3>
            <p>Write a response to the given prompt, trying to sound as human as possible.</p>
          </div>
          <div>
            <h3 className="font-semibold text-green-400 mb-2">2. Vote</h3>
            <p>Guess which response was written by a human and which by AI.</p>
          </div>
          <div>
            <h3 className="font-semibold text-purple-400 mb-2">3. Learn</h3>
            <p>See the results and learn how the AI judge made its decision.</p>
          </div>
        </div>
      </div>
    </div>
  );
}