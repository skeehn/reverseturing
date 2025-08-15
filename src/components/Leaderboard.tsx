import React, { useState, useEffect } from 'react';

interface LeaderboardEntry {
  rank: number;
  username: string;
  deception_score: number;
  detection_score: number;
  overall_score: number;
  games_played: number;
}

export default function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [period, setPeriod] = useState('all_time');
  const [roomType, setRoomType] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
  }, [period, roomType]);

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ period });
      if (roomType) params.append('room_type', roomType);
      
      const response = await fetch(`http://localhost:5000/api/leaderboard?${params}`);
      const data = await response.json();
      setLeaderboard(data.leaderboard || []);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8 text-center">Leaderboard</h1>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex flex-wrap gap-4 justify-center">
          <div>
            <label className="text-gray-400 mr-2">Period:</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="bg-gray-700 text-white px-3 py-1 rounded"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="all_time">All Time</option>
            </select>
          </div>
          
          <div>
            <label className="text-gray-400 mr-2">Room Type:</label>
            <select
              value={roomType || ''}
              onChange={(e) => setRoomType(e.target.value || null)}
              className="bg-gray-700 text-white px-3 py-1 rounded"
            >
              <option value="">All Rooms</option>
              <option value="poetry">Poetry</option>
              <option value="debate">Debate</option>
              <option value="personal">Personal</option>
              <option value="creative">Creative</option>
            </select>
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      {loading ? (
        <div className="text-center py-20">
          <div className="animate-spin w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
        </div>
      ) : leaderboard.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          No leaderboard data available yet. Start playing to see rankings!
        </div>
      ) : (
        <div className="bg-gray-800 rounded-lg overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left">Rank</th>
                <th className="px-4 py-3 text-left">Player</th>
                <th className="px-4 py-3 text-center">Deception</th>
                <th className="px-4 py-3 text-center">Detection</th>
                <th className="px-4 py-3 text-center">Overall</th>
                <th className="px-4 py-3 text-center">Games</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((entry, index) => (
                <tr
                  key={index}
                  className={`border-t border-gray-700 ${
                    index < 3 ? 'bg-gray-700/50' : ''
                  }`}
                >
                  <td className="px-4 py-3">
                    <span className={`font-bold ${
                      index === 0 ? 'text-yellow-400' :
                      index === 1 ? 'text-gray-300' :
                      index === 2 ? 'text-orange-400' : ''
                    }`}>
                      {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${entry.rank}`}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-semibold">{entry.username}</td>
                  <td className="px-4 py-3 text-center">{entry.deception_score.toFixed(2)}</td>
                  <td className="px-4 py-3 text-center">{entry.detection_score.toFixed(2)}</td>
                  <td className="px-4 py-3 text-center font-bold text-blue-400">
                    {entry.overall_score.toFixed(2)}
                  </td>
                  <td className="px-4 py-3 text-center">{entry.games_played}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Legend */}
      <div className="mt-8 bg-gray-800 rounded-lg p-4">
        <h3 className="font-bold mb-2">Score Explanation:</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-400">
          <div>
            <span className="text-white font-semibold">Deception Score:</span> How well you fool the AI judge
          </div>
          <div>
            <span className="text-white font-semibold">Detection Score:</span> How well you identify AI responses
          </div>
          <div>
            <span className="text-white font-semibold">Overall Score:</span> Combined performance metric
          </div>
        </div>
      </div>
    </div>
  );
}