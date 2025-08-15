import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import { GameRoom } from './components/GameRoom';
import { Analytics } from './components/Analytics';
import Login from './components/Login';
import Register from './components/Register';
import Lobby from './components/Lobby';
import Leaderboard from './components/Leaderboard';
import Profile from './components/Profile';
import Navigation from './components/Navigation';

// Context
import { AuthProvider, useAuth } from './context/AuthContext';
import { SocketProvider } from './context/SocketContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App min-h-screen bg-gray-900 text-white">
          <Navigation />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/lobby" element={<ProtectedRoute><Lobby /></ProtectedRoute>} />
              <Route path="/room/:roomId" element={
                <ProtectedRoute>
                  <SocketProvider>
                    <GameRoom />
                  </SocketProvider>
                </ProtectedRoute>
              } />
              <Route path="/leaderboard" element={<Leaderboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

// Home Component
function Home() {
  const { isAuthenticated } = useAuth();
  
  return (
    <div className="text-center py-20">
      <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
        Reverse Turing Game
      </h1>
      <p className="text-xl mb-8 text-gray-300">
        Can you fool the AI judge? Can you spot the AI?
      </p>
      <div className="space-x-4">
        {isAuthenticated ? (
          <a
            href="/lobby"
            className="inline-block bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Play Now
          </a>
        ) : (
          <>
            <a
              href="/login"
              className="inline-block bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Login
            </a>
            <a
              href="/register"
              className="inline-block bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Register
            </a>
          </>
        )}
      </div>
      
      <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-2">🤖 AI Judge</h3>
          <p className="text-gray-400">
            An AI judge analyzes responses to determine if they're human or AI-generated
          </p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-2">🎭 Deceive & Detect</h3>
          <p className="text-gray-400">
            Write responses to fool the judge, then vote on which responses are human
          </p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-xl font-bold mb-2">📈 Continuous Learning</h3>
          <p className="text-gray-400">
            The AI judge learns from its mistakes, getting better with every game
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;