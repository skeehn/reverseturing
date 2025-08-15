import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();

  if (!user) {
    return <div>Loading...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-4xl font-bold mb-8">Player Profile</h1>

      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">👤 {user.username}</h2>
        <p className="text-gray-400">Player ID: #{user.id}</p>
      </div>

      {user.stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-blue-400">{user.stats.games_played}</div>
            <div className="text-gray-400 mt-2">Games Played</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-green-400">{user.stats.human_wins}</div>
            <div className="text-gray-400 mt-2">Successful Deceptions</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6 text-center">
            <div className="text-3xl font-bold text-purple-400">
              {(user.stats.detection_accuracy * 100).toFixed(1)}%
            </div>
            <div className="text-gray-400 mt-2">Detection Accuracy</div>
          </div>
        </div>
      )}

      <div className="mt-8 bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold mb-4">Achievements</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {user.stats && user.stats.games_played >= 10 && (
            <div className="text-center">
              <div className="text-4xl mb-2">🎮</div>
              <div className="text-sm">Regular Player</div>
            </div>
          )}
          {user.stats && user.stats.human_wins >= 5 && (
            <div className="text-center">
              <div className="text-4xl mb-2">🎭</div>
              <div className="text-sm">Master Deceiver</div>
            </div>
          )}
          {user.stats && user.stats.detection_accuracy >= 0.7 && (
            <div className="text-center">
              <div className="text-4xl mb-2">🔍</div>
              <div className="text-sm">AI Detective</div>
            </div>
          )}
          {user.stats && user.stats.games_played >= 50 && (
            <div className="text-center">
              <div className="text-4xl mb-2">⭐</div>
              <div className="text-sm">Veteran</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}