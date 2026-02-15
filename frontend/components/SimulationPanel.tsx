import { useState } from 'react';
import { simulationApi } from '../services/api';
import { motion } from 'framer-motion';
import { Play, User, Bot, TrendingUp, AlertTriangle } from 'lucide-react';

interface SimulationPanelProps {
  sessionId: number;
}

export default function SimulationPanel({ sessionId }: SimulationPanelProps) {
  const [userDraft, setUserDraft] = useState('');
  const [simulation, setSimulation] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    if (!userDraft.trim()) return;

    setLoading(true);
    try {
      const result = await simulationApi.simulateResponse(sessionId, userDraft);
      setSimulation(result);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="analysis-card p-6">
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          🎭 Digital Twin Simulator
        </h2>
        <p className="text-gray-300 mb-6">
          Preview how the other person might respond to your message
        </p>

        {/* Draft Input */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
              Draft Your Response
            </label>
            <textarea
              value={userDraft}
              onChange={(e) => setUserDraft(e.target.value)}
              placeholder="Type what you're thinking of saying..."
              rows={4}
              className="w-full px-4 py-3 bg-transparent text-gray-200 placeholder-gray-400 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
          </div>

          <button
            onClick={handleSimulate}
            disabled={!userDraft.trim() || loading}
            className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-purple-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                Simulating...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Simulate Response
              </>
            )}
          </button>
        </div>
      </div>

      {/* Simulation Results */}
      {simulation && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Dialogue Preview */}
          <div className="analysis-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">💬 Predicted Exchange</h3>
            
            <div className="space-y-4">
              {/* User Message */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-700/20 flex items-center justify-center flex-shrink-0 text-blue-300">
                  <User className="w-4 h-4 text-blue-300" />
                </div>
                <div className="flex-1">
                  <div className="bg-black/20 rounded-lg p-3">
                    <p className="text-gray-100">{simulation.user_draft}</p>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">You</div>
                </div>
              </div>

              {/* Simulated Response */}
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-700/20 flex items-center justify-center flex-shrink-0 text-purple-300">
                  <Bot className="w-4 h-4 text-purple-300" />
                </div>
                <div className="flex-1">
                  <div className="bg-black/20 rounded-lg p-3">
                    <p className="text-gray-100">{simulation.simulated_opponent_response}</p>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">Predicted Response (Digital Twin)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Impact Analysis */}
          <div className="analysis-card p-6">
            <h3 className="text-lg font-bold text-white mb-4">📊 Impact Analysis</h3>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className={`p-4 rounded-lg ${
                simulation.predicted_escalation > 0.6
                  ? 'bg-red-900/20 border border-red-700'
                  : simulation.predicted_escalation > 0.3
                  ? 'bg-yellow-900/20 border border-yellow-700'
                  : 'bg-green-900/20 border border-green-700'
              }`}>
                <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
                  <TrendingUp className="w-4 h-4" />
                  Escalation Risk
                </div>
                <div className="text-2xl font-bold text-white">
                  {(simulation.predicted_escalation * 100).toFixed(0)}%
                </div>
              </div>

              <div className={`p-4 rounded-lg ${
                simulation.conflict_score_change > 0.2
                  ? 'bg-red-900/20 border border-red-700'
                  : simulation.conflict_score_change > 0
                  ? 'bg-yellow-900/20 border border-yellow-700'
                  : 'bg-green-900/20 border border-green-700'
              }`}>
                <div className="flex items-center gap-2 text-sm text-gray-400 mb-1">
                  <AlertTriangle className="w-4 h-4" />
                  Conflict Change
                </div>
                <div className="text-2xl font-bold text-white">
                  {simulation.conflict_score_change > 0 ? '+' : ''}
                  {(simulation.conflict_score_change * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {/* Recommendation */}
            <div className={`p-4 rounded-lg ${
              simulation.predicted_escalation > 0.6
                ? 'bg-red-900/20 border-l-4 border-red-500'
                : simulation.predicted_escalation > 0.3
                ? 'bg-yellow-900/20 border-l-4 border-yellow-500'
                : 'bg-green-900/20 border-l-4 border-green-500'
            }`}>
              <div className="font-medium text-white mb-1">Recommendation</div>
              <div className="text-sm text-gray-300">{simulation.recommendation}</div>
            </div>
          </div>

          {/* Opponent Profile */}
          {simulation.opponent_profile && (
            <div className="analysis-card p-6">
              <h3 className="text-lg font-bold text-white mb-4">🤖 Opponent Profile</h3>
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-400">Communication Style:</span>
                  <span className="ml-2 px-2 py-1 bg-gray-800 rounded text-sm font-medium text-gray-200">
                    {simulation.opponent_profile.communication_style}
                  </span>
                </div>
                <div>
                  <span className="text-sm text-gray-400">Sentiment Baseline:</span>
                  <span className="ml-2 font-medium text-gray-200">
                    {simulation.opponent_profile.sentiment_baseline.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
