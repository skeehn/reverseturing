import React, { useState, useEffect } from 'react';

interface Metric {
  title: string;
  value: string;
  trend: string;
  color?: string;
}

function MetricCard({ title, value, trend, color = "blue" }: Metric) {
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-gray-400 text-sm uppercase tracking-wide mb-2">{title}</h3>
      <div className={`text-3xl font-bold text-${color}-400 mb-2`}>{value}</div>
      <p className="text-sm text-gray-500">{trend}</p>
    </div>
  );
}

export function Analytics() {
  const [metrics, setMetrics] = useState({
    judgeAccuracy: 73.4,
    humanWinRate: 41.2,
    modelVersion: 'v1.7',
    totalGames: 1234,
    activePlayersToday: 56,
    avgSessionLength: '12.5'
  });

  return (
    <div className="analytics p-6 max-w-7xl mx-auto">
      <h2 className="text-4xl font-bold mb-8">Game Analytics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard 
          title="Judge Accuracy" 
          value={`${metrics.judgeAccuracy}%`}
          trend="+2.1% this week"
          color="blue"
        />
        <MetricCard 
          title="Human Win Rate" 
          value={`${metrics.humanWinRate}%`}
          trend="Humans getting better!"
          color="green"
        />
        <MetricCard 
          title="Model Version" 
          value={metrics.modelVersion}
          trend="Updated 2 hours ago"
          color="purple"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard 
          title="Total Games" 
          value={metrics.totalGames.toLocaleString()}
          trend="+156 today"
          color="yellow"
        />
        <MetricCard 
          title="Active Players" 
          value={metrics.activePlayersToday.toString()}
          trend="Online now"
          color="indigo"
        />
        <MetricCard 
          title="Avg Session" 
          value={`${metrics.avgSessionLength} min`}
          trend="Engagement up 15%"
          color="pink"
        />
      </div>
      
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-semibold mb-4">Judge Performance Trends</h3>
        <div className="h-64 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-6xl mb-4">📊</div>
            <p>Performance charts will be displayed here</p>
            <p className="text-sm mt-2">Tracking accuracy, confidence, and learning rate</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Room Performance</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span>Poetry</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-700 rounded-full h-2 mr-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{width: '78%'}}></div>
                </div>
                <span className="text-sm">78%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>Debate</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-700 rounded-full h-2 mr-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                <span className="text-sm">65%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>Personal</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-700 rounded-full h-2 mr-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{width: '82%'}}></div>
                </div>
                <span className="text-sm">82%</span>
              </div>
            </div>
            <div className="flex justify-between items-center">
              <span>Creative</span>
              <div className="flex items-center">
                <div className="w-32 bg-gray-700 rounded-full h-2 mr-2">
                  <div className="bg-yellow-500 h-2 rounded-full" style={{width: '71%'}}></div>
                </div>
                <span className="text-sm">71%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Recent Training</h3>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">2 hours ago</span>
              <span className="text-green-400">+1.2% accuracy</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">5 hours ago</span>
              <span className="text-green-400">+0.8% accuracy</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">12 hours ago</span>
              <span className="text-yellow-400">+0.3% accuracy</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">1 day ago</span>
              <span className="text-green-400">+2.1% accuracy</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}