import { useState, useEffect } from 'react';
import { Send, User, Users } from 'lucide-react';
import { realtimeApi } from '../services/api';
import { motion } from 'framer-motion';

interface DialogueInputProps {
  sessionId: number | null;
  creatingSession?: boolean;
  onAddTurn: (speaker: string, text: string) => void;
}

export default function DialogueInput({ sessionId, creatingSession = false, onAddTurn }: DialogueInputProps) {
  const [speaker, setSpeaker] = useState<'user' | 'opponent'>('user');
  const [text, setText] = useState('');
  const [realtimeScore, setRealtimeScore] = useState<any>(null);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (text.trim().length > 5) {
      const timer = setTimeout(async () => {
        try {
          const score = await realtimeApi.getScore(text, sessionId || undefined);
          setRealtimeScore(score);
        } catch (error) {
          console.error('Failed to get realtime score:', error);
        }
      }, 500);

      return () => clearTimeout(timer);
    } else {
      setRealtimeScore(null);
    }
  }, [text, sessionId]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || !sessionId) return;

    onAddTurn(speaker, text);
    setText('');
    setRealtimeScore(null);
  };

  return (
    <div className="analysis-card">
      <h2 className="text-xl font-bold text-white mb-4">💬 Enter Dialogue</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Speaker Selection */}
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setSpeaker('user')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              speaker === 'user'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-800 text-gray-200 hover:bg-gray-700'
            }`}
          >
            <User className="w-4 h-4" />
            You
          </button>
          <button
            type="button"
            onClick={() => setSpeaker('opponent')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all flex items-center justify-center gap-2 ${
              speaker === 'opponent'
                ? 'bg-purple-600 text-white shadow-md'
                : 'bg-gray-800 text-gray-200 hover:bg-gray-700'
            }`}
          >
            <Users className="w-4 h-4" />
            Other Person
          </button>
        </div>

        {/* Text Input */}
        <div className="relative">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`Enter ${speaker === 'user' ? 'your' : "other person's"} message...`}
            rows={4}
            className="w-full px-4 py-3 bg-transparent text-gray-200 placeholder-gray-400 border border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
          
          {/* Real-time Score Indicator */}
          {realtimeScore && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`absolute bottom-2 right-2 px-3 py-1 rounded-full text-xs font-medium ${
                realtimeScore.color === 'green'
                  ? 'bg-green-900/30 text-green-300'
                  : realtimeScore.color === 'yellow'
                  ? 'bg-yellow-900/30 text-yellow-300'
                  : 'bg-red-900/30 text-red-300'
              }`}
            >
              {realtimeScore.quick_tip}
            </motion.div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!text.trim() || creatingSession}
          className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
        >
          <Send className="w-4 h-4" />
          {creatingSession ? 'Creating session…' : 'Add to Conversation'}
        </button>
      </form>

      {/* Real-time Metrics */}
      {realtimeScore && (
        <div className="mt-4 grid grid-cols-3 gap-2">
          <div className="bg-black/20 rounded p-2 text-center">
            <div className="text-xs text-gray-400">Conflict</div>
            <div className="text-sm font-bold text-gray-100">{(realtimeScore.conflict_score * 100).toFixed(0)}%</div>
          </div>
          <div className="bg-black/20 rounded p-2 text-center">
            <div className="text-xs text-gray-400">Aggression</div>
            <div className="text-sm font-bold text-gray-100">{(realtimeScore.aggression_score * 100).toFixed(0)}%</div>
          </div>
          <div className="bg-black/20 rounded p-2 text-center">
            <div className="text-xs text-gray-400">Passive</div>
            <div className="text-sm font-bold text-gray-100">{(realtimeScore.passive_aggression_score * 100).toFixed(0)}%</div>
          </div>
        </div>
      )}
    </div>
  );
}
