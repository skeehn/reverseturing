import React from 'react';

interface Results {
  prompt: string;
  left_response: string;
  right_response: string;
  left_is: string;
  right_is: string;
  judge_verdict: {
    human: { human_prob: number; reasoning: string };
    ai: { human_prob: number; reasoning: string };
    correct: boolean;
  };
  player_votes: { left: number; right: number };
  player_accuracy: number;
  correct_votes: number;
  total_votes: number;
}

export function ResultsDisplay({ results }: { results: Results }) {
    const humanResponse = results.left_is === 'human' ? results.left_response : results.right_response;
    const aiResponse = results.left_is === 'ai' ? results.left_response : results.right_response;
    
    return (
        <div className="results-display bg-gray-800 rounded-lg p-6">
            <h3 className="text-3xl font-bold mb-6 text-center">🎭 Round Results</h3>
            
            <div className="mb-6 p-4 bg-gray-700 rounded-lg">
                <h4 className="font-semibold mb-2">📝 Prompt:</h4>
                <p className="text-gray-300">{results.prompt}</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="response-card bg-gray-700 rounded-lg p-4">
                    <h4 className="font-semibold text-green-400 mb-3">👤 Human Response</h4>
                    <p className="text-gray-300 mb-4">{humanResponse}</p>
                    <div className="judge-verdict p-3 bg-gray-600 rounded">
                        <p><strong>Judge's Verdict:</strong> {(results.judge_verdict.human.human_prob * 100).toFixed(1)}% human</p>
                        <p className="text-sm text-gray-400 mt-2">{results.judge_verdict.human.reasoning}</p>
                    </div>
                </div>
                
                <div className="response-card bg-gray-700 rounded-lg p-4">
                    <h4 className="font-semibold text-blue-400 mb-3">🤖 AI Response</h4>
                    <p className="text-gray-300 mb-4">{aiResponse}</p>
                    <div className="judge-verdict p-3 bg-gray-600 rounded">
                        <p><strong>Judge's Verdict:</strong> {(results.judge_verdict.ai.human_prob * 100).toFixed(1)}% human</p>
                        <p className="text-sm text-gray-400 mt-2">{results.judge_verdict.ai.reasoning}</p>
                    </div>
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-blue-400">
                        {results.judge_verdict.correct ? '✓' : '✗'}
                    </div>
                    <div className="text-sm text-gray-400">Judge Accuracy</div>
                </div>
                
                <div className="text-center p-4 bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-green-400">
                        {(results.player_accuracy * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-400">Player Accuracy</div>
                </div>
                
                <div className="text-center p-4 bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-purple-400">
                        {results.correct_votes}/{results.total_votes}
                    </div>
                    <div className="text-sm text-gray-400">Correct Votes</div>
                </div>
            </div>
            
            <div className="mt-6 p-4 bg-gray-700 rounded-lg">
                <h4 className="font-semibold mb-3 text-center">📊 Voting Results</h4>
                <div className="flex justify-center space-x-8">
                    <div className="text-center">
                        <div className="text-lg font-bold">Response A</div>
                        <div className="text-2xl text-green-400">{results.player_votes.left}</div>
                        <div className="text-sm text-gray-400">votes</div>
                    </div>
                    <div className="text-center">
                        <div className="text-lg font-bold">Response B</div>
                        <div className="text-2xl text-blue-400">{results.player_votes.right}</div>
                        <div className="text-sm text-gray-400">votes</div>
                    </div>
                </div>
            </div>
        </div>
    );
}