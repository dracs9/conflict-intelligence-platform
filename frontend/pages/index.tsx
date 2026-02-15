import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import ConflictThermometer from '../components/ConflictThermometer';
import DialogueInput from '../components/DialogueInput';
import AnalysisPipeline from '../components/AnalysisPipeline';
import SimulationPanel from '../components/SimulationPanel';
import ScreenshotUpload from '../components/ScreenshotUpload';
import { dialogueApi, analysisApi, profileApi, ocrApi } from '../services/api';

export default function Home() {
  const [userId] = useState('demo-user-001');
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [turns, setTurns] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'input' | 'analysis' | 'simulation'>('input');

  // UI state for new template
  const [chats, setChats] = useState<any[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
  const [showAttach, setShowAttach] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [profileData, setProfileData] = useState<any>(null);
  const [creatingSession, setCreatingSession] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    initializeSession();
    loadChats();
  }, []);

  const initializeSession = async () => {
    try {
      const session = await dialogueApi.createSession(userId, 'New Conflict Session');
      setSessionId(session.session_id);
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const loadChats = async () => {
    try {
      const resp = await dialogueApi.getUserSessions(userId);
      setChats(resp || []);
    } catch (err) {
      console.warn('No chats or failed to load chats', err);
      setChats([]);
    }
  };

  // Ensure there is a session (create lazily when user interacts)
  const ensureSession = async () => {
    if (sessionId) return sessionId;
    setCreatingSession(true);
    try {
      const s = await dialogueApi.createSession(userId, 'New Conflict Session');
      setSessionId(s.session_id);
      await loadChats();
      return s.session_id;
    } catch (err) {
      console.error('Failed to create session on demand', err);
      return null;
    } finally {
      setCreatingSession(false);
    }
  };

  const handleAddTurn = async (speaker: string, text: string) => {
    if (!text.trim()) return;

    const sid = sessionId ?? (await ensureSession());
    if (!sid) return;

    try {
      const turn = await dialogueApi.addTurn(sid, speaker, text);
      setTurns((prev) => [...prev, turn]);
      
      // Re-analyze
      const analysisResult = await analysisApi.analyzeSession(sid);
      setAnalysis(analysisResult);
    } catch (error) {
      console.error('Failed to add turn:', error);
    }
  };

  const handleScreenshotUpload = async (uploadedSessionId: number) => {
    setSessionId(uploadedSessionId);
    try {
      const turnsData = await dialogueApi.getTurns(uploadedSessionId);
      setTurns(turnsData.turns || []);

      if (!turnsData.turns || turnsData.turns.length === 0) {
        // No turns to analyze yet — avoid calling analyze endpoint which returns 400
        setAnalysis(null);
        return;
      }

      const analysisResult = await analysisApi.analyzeSession(uploadedSessionId);
      setAnalysis(analysisResult);
    } catch (err) {
      console.error('Screenshot upload handling failed:', err);
      setAnalysis(null);
    }
  };

  const createNewChat = async () => {
    try {
      const s = await dialogueApi.createSession(userId, `Новый чат ${new Date().toLocaleTimeString()}`);
      await loadChats();
      setSessionId(s.session_id);
    } catch (err) {
      console.error(err);
    }
  };

  const openProfile = async () => {
    setShowProfile(true);
    try {
      const p = await profileApi.getUserProfile(userId);
      setProfileData(p);
    } catch (err) {
      console.warn('Failed to load profile', err);
    }
  };

  const handleAnalyzeNow = async () => {
    setAnalyzing(true);
    try {
      const sid = sessionId ?? (await ensureSession());
      if (!sid) throw new Error('Unable to create session for analysis');
      const a = await analysisApi.analyzeSession(sid);
      setAnalysis(a);
    } catch (err) {
      console.error('Analyze failed', err);
    } finally {
      setTimeout(() => setAnalyzing(false), 800);
    }
  };

  // Attach modal/file input handling (was missing)
  const handleAttachClick = (type: 'image' | 'audio' | 'document') => {
    if (!fileInputRef.current) return;
    if (type === 'image') fileInputRef.current.accept = 'image/*';
    else if (type === 'audio') fileInputRef.current.accept = 'audio/*';
    else fileInputRef.current.accept = '.pdf,.doc,.docx,.txt';
    fileInputRef.current.click();
    setShowAttach(false);
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Only image upload is currently supported via OCR endpoint
    if (!file.type.startsWith('image/')) {
      // TODO: support other attachment uploads
      return;
    }

    try {
      const res = await ocrApi.uploadScreenshot(userId, file);
      if (res?.session_id) {
        handleScreenshotUpload(res.session_id);
        await loadChats();
      }
    } catch (err) {
      console.error('Attach upload failed', err);
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <>
      <Head>
        <title>Conflict Translator — Conflict Intelligence Platform</title>
        <meta name="description" content="AI mediator for human communication" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div>
        {/* Sidebar */}
        <div className={`sidebar ${sidebarOpen ? 'mobile-open' : ''}`}>
          <div className="sidebar-header">
            <button id="profileBtn" className="profile-btn" onClick={openProfile}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
              <span>Профиль</span>
            </button>

            <button id="authBtn" className="auth-btn" onClick={() => setShowAuth(true)}>
              {showAuth ? 'Закрыть' : 'Войти / Регистрация'}
            </button>

            <button id="newChatBtn" className="new-chat-btn" onClick={createNewChat}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Новый чат
            </button>
          </div>

          <div className="chats-list">
            {(!Array.isArray(chats) || chats.length === 0) && <p className="text-center text-gray-400 py-4">Нет чатов</p>}
            {Array.isArray(chats) && chats.map((c: any) => (
              <div key={c.id} className={`chat-item ${sessionId === c.id ? 'active' : ''}`} onClick={async () => {
                setSessionId(c.id);
                try {
                  const turnsData = await dialogueApi.getTurns(c.id);
                  setTurns(turnsData.turns || []);

                  if (!turnsData.turns || turnsData.turns.length === 0) {
                    setAnalysis(null);
                    return;
                  }

                  const a = await analysisApi.analyzeSession(c.id);
                  setAnalysis(a);
                } catch (err) {
                  console.warn('Failed to load session turns or analysis:', err);
                  setAnalysis(null);
                }
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <span>{c.session_name || c.title || `Chat ${c.id}`}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Profile modal */}
        <div id="profileModal" className={`modal ${showProfile ? '' : 'hidden'}`} onClick={(e) => { if (e.target === e.currentTarget) setShowProfile(false); }}>
          <div className="modal-content">
            <button className="close-modal" onClick={() => setShowProfile(false)}>✕</button>
            <div className="profile-header">
              <div className="profile-avatar">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
              </div>
              <h2 className="profile-title">{profileData?.user_id ?? 'Ваш Профиль'}</h2>
            </div>

            <div className="profile-section">
              <h3 className="profile-section-title">🧠 Анализ личности</h3>
              <div className="profile-traits">
                <div className="trait-item">
                  <span className="trait-label">Коммуникативный стиль</span>
                  <span className="trait-value">{profileData?.dominant_style ?? '—'}</span>
                </div>
                <div className="trait-item">
                  <span className="trait-label">Реакция на конфликт</span>
                  <span className="trait-value">{profileData?.escalation_contribution ? 'Склонность к эскалации' : 'Стабильный'}</span>
                </div>
                <div className="trait-item">
                  <span className="trait-label">Эмоциональный интеллект</span>
                  <span className="trait-value">{profileData?.style_distribution ? 'Высокий' : 'Средний'}</span>
                </div>
                <div className="trait-item">
                  <span className="trait-label">Доминирующая потребность</span>
                  <span className="trait-value">{profileData?.dominant_style ?? 'Понимание'}</span>
                </div>
              </div>
            </div>

            <div className="profile-section">
              <h3 className="profile-section-title">🔮 Прогноз и рекомендации</h3>
              <div className="forecast-content">
                <p>{(profileData?.conflict_history?.length ? 'Последние сессии проанализированы.' : 'Профиль пока пуст.')} </p>
                <ul className="forecast-list">
                  <li>Практиковать асертивность в сложных диалогах</li>
                  <li>Не бояться выражать свои потребности напрямую</li>
                  <li>Использовать "Я-сообщения" для снижения эскалации</li>
                </ul>
              </div>
            </div>

            <div className="profile-stats">
              <div className="stat-card">
                <div className="stat-number">{profileData?.total_conflicts ?? 0}</div>
                <div className="stat-label">Разрешённых конфликтов</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{Math.round((profileData?.you_statements_percentage || 0) * 100)}%</div>
                <div className="stat-label">You statements</div>
              </div>
              <div className="stat-card">
                <div className="stat-number">{profileData?.conflict_history?.length ?? 0}</div>
                <div className="stat-label">Сессий</div>
              </div>
            </div>
          </div>
        </div>

        {/* Auth modal (placeholder) */}
        <div id="authModal" className={`modal ${showAuth ? '' : 'hidden'}`}>
          <div className="modal-content auth-modal-content">
            <button className="close-modal" onClick={() => setShowAuth(false)}>✕</button>
            <h2 className="auth-title">Вход / Регистрация</h2>
            <p className="text-sm text-gray-400">Встроенная аутентификация не настроена. Используйте демо-профиль.</p>
          </div>
        </div>

        {/* Main */}
        <div className="main-content">
          <div className="container">
            <header className="hero">
              <h1 className="title text-4xl font-extrabold">Conflict Translator</h1>
              <p className="subtitle text-lg mt-2 text-gray-300">ИИ-медиатор для человеческой коммуникации</p>
            </header>

            <div className="main-panel">
              <div className="input-wrapper">
                <button id="attachBtn" className="attach-btn" title="Прикрепить файл" onClick={() => setShowAttach(true)}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
                  </svg>
                </button>

                {/* Use existing DialogueInput and ScreenshotUpload components */}
                <div style={{ flex: 1 }}>
                  <ScreenshotUpload userId={userId} onUploadSuccess={handleScreenshotUpload} />
                  <div className="mt-4">
                    <DialogueInput sessionId={sessionId} creatingSession={creatingSession} onAddTurn={handleAddTurn} />
                  </div>
                </div>

                <button id="mobileAnalyzeBtn" className="mobile-analyze-btn" onClick={handleAnalyzeNow}>→</button>
              </div>

            <button id="analyzeBtn" className="analyze-btn" onClick={handleAnalyzeNow} disabled={analyzing || !sessionId || turns.length === 0}>
                <span className="btn-text">Анализировать</span>
                {analyzing ? (
                  <span className="loader">
                    <span className="dot" /> <span className="dot" /> <span className="dot" />
                  </span>
                ) : null}
              </button>
            </div>

            <div id="attachModal" className={`attach-modal ${showAttach ? '' : 'hidden'}`}>
              <div className="attach-modal-content">
                <button className="attach-option" data-type="image" onClick={() => handleAttachClick('image')}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                    <circle cx="8.5" cy="8.5" r="1.5" />
                    <path d="M21 15l-5-5L5 21" />
                  </svg>
                  Фото/Изображение
                </button>
                <button className="attach-option" data-type="audio" onClick={() => handleAttachClick('audio')}>
                  Аудио
                </button>
                <button className="attach-option" data-type="document" onClick={() => handleAttachClick('document')}>
                  Документ
                </button>
              </div>
            </div>

            {/* Results */}
            <motion.div id="resultsSection" initial={{ opacity: 0, y: 10 }} animate={analysis ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }} transition={{ duration: 0.33 }} className={`results-section ${analysis ? '' : 'hidden'}`}>
              <div className="analysis-card">
                <h3 className="section-title">🧠 Emotion Analysis</h3>
                <div className="analysis-grid">
                  <div className="analysis-item">
                    <span className="label">Emotion</span>
                    <span className="value" id="emotionValue">{analysis?.nvc_analysis?.emotion ?? analysis?.nvc_analysis?.dominant_emotion ?? '—'}</span>
                  </div>
                  <div className="analysis-item">
                    <span className="label">Hidden Need</span>
                    <span className="value" id="needValue">{analysis?.nvc_analysis?.likely_need ?? '—'}</span>
                  </div>
                  <div className="analysis-item">
                    <span className="label">Escalation %</span>
                    <span className="value" id="escalationValue">{Math.round((analysis?.escalation_probability || 0) * 100)}%</span>
                  </div>
                </div>
              </div>

              <div className="escalation-card">
                <h3 className="section-title">🔥 Escalation Meter</h3>
                <div className="progress-container">
                  <div id="progressBar" className={`progress-bar ${((analysis?.escalation_probability || 0) * 100) < 30 ? 'low' : ((analysis?.escalation_probability || 0) * 100) < 60 ? 'medium' : 'high'}`} style={{ width: `${Math.round((analysis?.escalation_probability || 0) * 100)}%` }} />
                </div>
              </div>

              <div className="responses-grid">
                <div className="response-card">
                  <h4 className="response-title">💙 Эмпатичный</h4>
                  <p className="response-text" id="empathetic">{analysis?.recommendations?.[0]?.description ?? 'Я понимаю, что для тебя это важно...'}</p>
                  <button className="copy-btn" onClick={() => navigator.clipboard.writeText((analysis?.recommendations?.[0]?.description ?? ''))}>Скопировать</button>
                </div>
                <div className="response-card">
                  <h4 className="response-title">🧠 Рациональный</h4>
                  <p className="response-text" id="rational">{analysis?.recommendations?.[1]?.description ?? 'Давай обсудим факты и найдём решение.'}</p>
                  <button className="copy-btn" onClick={() => navigator.clipboard.writeText((analysis?.recommendations?.[1]?.description ?? ''))}>Скопировать</button>
                </div>
                <div className="response-card">
                  <h4 className="response-title">❓ Сократовский</h4>
                  <p className="response-text" id="socratic">{analysis?.recommendations?.[2]?.description ?? 'Что именно тебя больше всего беспокоит?'}</p>
                  <button className="copy-btn" onClick={() => navigator.clipboard.writeText((analysis?.recommendations?.[2]?.description ?? ''))}>Скопировать</button>
                </div>
              </div>
            </motion.div>

            <input ref={fileInputRef} type="file" id="fileInput" className="hidden" onChange={handleFileInputChange} />
          </div>
        </div>
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
