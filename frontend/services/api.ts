/**
 * API Service Layer
 * Centralized API communication
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dialogueApi = {
  createSession: async (userId: string, sessionName?: string) => {
    const response = await api.post('/api/dialogue/session/create', {
      user_id: userId,
      session_name: sessionName,
    });
    return response.data;
  },

  addTurn: async (sessionId: number, speaker: string, text: string) => {
    const response = await api.post(`/api/dialogue/session/${sessionId}/turn`, {
      speaker,
      text,
    });
    return response.data;
  },

  getTurns: async (sessionId: number) => {
    const response = await api.get(`/api/dialogue/session/${sessionId}/turns`);
    return response.data;
  },

  getSession: async (sessionId: number) => {
    const response = await api.get(`/api/dialogue/session/${sessionId}`);
    return response.data;
  },

  getUserSessions: async (userId: string) => {
    const response = await api.get(`/api/dialogue/sessions/user/${userId}`);
    return response.data;
  },
};

export const analysisApi = {
  analyzeSession: async (sessionId: number) => {
    const response = await api.post(`/api/analysis/session/${sessionId}/analyze`);
    return response.data;
  },

  getLatestAnalysis: async (sessionId: number) => {
    const response = await api.get(`/api/analysis/session/${sessionId}/analysis/latest`);
    return response.data;
  },

  getPipeline: async (sessionId: number) => {
    const response = await api.get(`/api/analysis/session/${sessionId}/pipeline`);
    return response.data;
  },
};

export const simulationApi = {
  simulateResponse: async (sessionId: number, userDraft: string) => {
    const response = await api.post(`/api/simulation/session/${sessionId}/simulate`, {
      user_draft: userDraft,
    });
    return response.data;
  },

  getOpponentProfile: async (sessionId: number) => {
    const response = await api.get(`/api/simulation/session/${sessionId}/opponent-profile`);
    return response.data;
  },
};

export const ocrApi = {
  uploadScreenshot: async (userId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/api/ocr/upload-screenshot?user_id=${userId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  extractText: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/ocr/extract-text', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const realtimeApi = {
  getScore: async (text: string, sessionId?: number) => {
    const response = await api.post('/api/realtime/score', {
      text,
      session_id: sessionId,
    });
    return response.data;
  },
};

export const profileApi = {
  getUserProfile: async (userId: string) => {
    const response = await api.get(`/api/profile/user/${userId}`);
    return response.data;
  },

  getDashboard: async (userId: string) => {
    const response = await api.get(`/api/profile/user/${userId}/dashboard`);
    return response.data;
  },
};

export default api;
