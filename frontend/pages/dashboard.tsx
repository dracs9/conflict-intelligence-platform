import { useEffect, useState } from 'react';
import { profileApi } from '../services/api';
import { motion } from 'framer-motion';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { TrendingUp, Award, Target, AlertCircle } from 'lucide-react';

export default function Dashboard() {
  const [userId] = useState('demo-user-001');
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await profileApi.getDashboard(userId);
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-300">Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-300">No profile data available</p>
      </div>
    );
  }

  const profile = dashboard.profile;
  const styleData = Object.entries(profile.style_distribution).map(([key, value]) => ({
    style: key,
    value: (value as number) * 100,
  }));

  return (
    <div className="min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white">📊 Your Conflict Profile</h1>
          <p className="text-gray-300 mt-2">Track your communication patterns and improvement over time</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            icon={<Target className="w-6 h-6" />}
            label="Total Conflicts"
            value={profile.total_conflicts}
            color="blue"
          />
          <MetricCard
            icon={<TrendingUp className="w-6 h-6" />}
            label="Improvement"
            value={`${dashboard.improvement_percentage.toFixed(0)}%`}
            color="green"
          />
          <MetricCard
            icon={<AlertCircle className="w-6 h-6" />}
            label="Escalation Rate"
            value={`${(profile.escalation_contribution * 100).toFixed(0)}%`}
            color={profile.escalation_contribution > 0.5 ? 'red' : 'green'}
          />
          <MetricCard
            icon={<Award className="w-6 h-6" />}
            label="Dominant Style"
            value={profile.dominant_style.replace('_', ' ')}
            color="purple"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Communication Style Radar */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="analysis-card p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Communication Style Profile</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={styleData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="style" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Style" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Conflict History Trend */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="analysis-card p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Conflict Score History</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={profile.conflict_history.slice(-10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="session_id" />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Line type="monotone" dataKey="conflict_score" stroke="#ef4444" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Insights */}
        {dashboard.insights && dashboard.insights.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-6 analysis-card p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">💡 Personalized Insights</h2>
            <div className="space-y-3">
              {dashboard.insights.map((insight: any, idx: number) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    insight.type === 'positive'
                      ? 'bg-green-900/20 border-green-500/40 text-green-300'
                      : insight.type === 'warning'
                      ? 'bg-red-900/20 border-red-500/40 text-red-300'
                      : 'bg-blue-900/20 border-blue-500/40 text-blue-300'
                  }`}
                >
                  <p className="text-gray-300">{insight.message}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Recent Sessions */}
        {dashboard.recent_sessions && dashboard.recent_sessions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-6 analysis-card p-6"
          >
            <h2 className="text-xl font-bold text-white mb-4">Recent Sessions</h2>
            <div className="space-y-2">
              {dashboard.recent_sessions.map((session: any) => (
                <div key={session.session_id} className="flex items-center justify-between p-3 chat-item rounded-lg">
                  <div>
                    <div className="font-medium text-white">{session.session_name}</div>
                    <div className="text-sm text-gray-400">{session.turn_count} turns</div>
                  </div>
                  <div className="text-sm text-gray-400">
                    {new Date(session.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string | number; color: string }) {
  return (
    <div className="stat-card">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <div className="text-sm font-medium opacity-80 text-white/80">{label}</div>
      </div>
      <div className="text-3xl font-bold mt-2 text-white">{value}</div>
    </div>
  );
}
