import { useEffect, useState } from 'react';
import Head from 'next/head';
import ConflictThermometer from '../components/ConflictThermometer';
import DialogueInput from '../components/DialogueInput';
import AnalysisPipeline from '../components/AnalysisPipeline';
import SimulationPanel from '../components/SimulationPanel';
import ScreenshotUpload from '../components/ScreenshotUpload';
import { dialogueApi, analysisApi } from '../services/api';

export default function Home() {
  const [userId] = useState('demo-user-001');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [turns, setTurns] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'input' | 'analysis' | 'simulation'>('input');

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      const session = await dialogueApi.createSession(userId, 'New Conflict Session');
      setSessionId(session.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleAddTurn = async (speaker: string, text: string) => {
    if (!sessionId) return;

    try {
      const turn = await dialogueApi.addTurn(sessionId, speaker, text);
      setTurns([...turns, turn]);
      
      // Re-analyze
      const analysisResult = await analysisApi.analyzeSession(sessionId);
      setAnalysis(analysisResult);
    } catch (error) {
      console.error('Failed to add turn:', error);
    }
  };

  const handleScreenshotUpload = async (uploadedSessionId: number) => {
    setSessionId(uploadedSessionId);
    const turnsData = await dialogueApi.getTurns(uploadedSessionId);
    setTurns(turnsData.turns);
    
    const analysisResult = await analysisApi.analyzeSession(uploadedSessionId);
    setAnalysis(analysisResult);
  };

  return (
    <>
      <Head>
        <title>Conflict Intelligence Platform</title>
        <meta name="description" content="AI-powered conflict analysis and mediation" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  🔥 Conflict Intelligence Platform
                </h1>
                <p className="text-gray-600 mt-1">
                  AI-powered conflict analysis and mediation system
                </p>
              </div>
              {sessionId && (
                <div className="text-sm text-gray-500">
                  Session #{sessionId}
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Tab Navigation */}
          <div className="mb-6">
            <nav className="flex space-x-4">
              {[
                { id: 'input', label: '📝 Input', icon: '💬' },
                { id: 'analysis', label: '🔍 Analysis', icon: '📊' },
                { id: 'simulation', label: '🎭 Simulation', icon: '🤖' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-6 py-3 rounded-lg font-medium transition-all ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white shadow-lg scale-105'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {tab.icon} {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Content Area */}
          <div className="space-y-6">
            {activeTab === 'input' && (
              <>
                <ScreenshotUpload
                  userId={userId}
                  onUploadSuccess={handleScreenshotUpload}
                />
                
                <DialogueInput
                  sessionId={sessionId}
                  onAddTurn={handleAddTurn}
                />

                {analysis && (
                  <ConflictThermometer
                    conflictScore={analysis.overall_conflict_score}
                    escalationProbability={analysis.escalation_probability}
                    trend={analysis.trend}
                  />
                )}
              </>
            )}

            {activeTab === 'analysis' && sessionId && (
              <AnalysisPipeline sessionId={sessionId} />
            )}

            {activeTab === 'simulation' && sessionId && (
              <SimulationPanel sessionId={sessionId} />
            )}
          </div>

          {/* Metrics Dashboard */}
          {analysis && (
            <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricCard
                label="Conflict Score"
                value={`${(analysis.overall_conflict_score * 100).toFixed(0)}%`}
                color={getColorForScore(analysis.overall_conflict_score)}
              />
              <MetricCard
                label="Escalation Risk"
                value={`${(analysis.escalation_probability * 100).toFixed(0)}%`}
                color={getColorForScore(analysis.escalation_probability)}
              />
              <MetricCard
                label="Passive Aggression"
                value={`${(analysis.passive_aggression_index * 100).toFixed(0)}%`}
                color="yellow"
              />
              <MetricCard
                label="Cognitive Biases"
                value={analysis.cognitive_biases?.length || 0}
                color="purple"
              />
            </div>
          )}
        </main>
      </div>
    </>
  );
}

function MetricCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  const colorClasses = {
    green: 'bg-green-50 border-green-200 text-green-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${colorClasses[color] || colorClasses.green}`}>
      <div className="text-sm font-medium opacity-80">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
    </div>
  );
}

function getColorForScore(score: number): string {
  if (score < 0.3) return 'green';
  if (score < 0.6) return 'yellow';
  return 'red';
}
