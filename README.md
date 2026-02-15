# 🔥 Conflict Intelligence Platform (CIP)

> **Production-Grade MVP** - AI-powered conflict analysis and mediation system

A sophisticated digital intelligence platform that acts as an AI mediator between humans during conflicts. Uses advanced ML pipelines, cognitive bias detection, passive aggression analysis, and digital twin simulation to provide actionable conflict resolution insights.

---

## 🎯 Product Vision

The Conflict Intelligence Platform transforms how people navigate difficult conversations by providing:

- **Real-time conflict scoring** while typing
- **Cognitive bias detection** in dialogue
- **Passive aggression identification**
- **Digital Twin simulation** of opponent responses
- **NVC (Nonviolent Communication) mapping**
- **Escalation prediction** with trend analysis
- **OCR chat screenshot analysis**
- **Personal conflict behavior profiling**

---

## ✨ Core Features

### 1️⃣ **Dialogue Intelligence Engine**
- Sentiment analysis with transformer models
- Aggression and passive aggression detection
- Cognitive bias identification (overgeneralization, mind-reading, gaslighting, etc.)
- Linguistic feature extraction

### 2️⃣ **Conflict Thermometer**
- Real-time scoring as you type
- Visual gradient indicator (Green → Yellow → Red)
- Instant feedback on message tone

### 3️⃣ **Digital Twin Simulator**
- Learns opponent communication patterns
- Simulates likely responses to your drafts
- Predicts escalation probability
- Suggests optimal messaging strategies

### 4️⃣ **OCR Vision Module**
- Upload chat screenshots
- Automatic speaker detection (left/right alignment)
- Text extraction and structuring
- Instant analysis of imported conversations

### 5️⃣ **Analysis Pipeline**
- Visual flow: Said → Emotion → Bias → Need → Risk → Recommendations
- NVC (Nonviolent Communication) interpretation
- Actionable de-escalation strategies

### 6️⃣ **User Conflict Profile**
- Tracks your behavioral patterns
- Identifies dominant communication style
- Measures blame frequency and "you" statements
- Shows improvement trends over time

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                      │
│  ┌───────────┐  ┌────────────┐  ┌──────────────┐           │
│  │   Home    │  │  Analysis  │  │  Simulation  │           │
│  │   Page    │  │  Pipeline  │  │    Panel     │           │
│  └───────────┘  └────────────┘  └──────────────┘           │
│  ┌───────────────────────────────────────────────────┐     │
│  │   Real-time Conflict Thermometer (WebSocket)      │     │
│  └───────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │ HTTP/WS
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│  ┌─────────────────────────────────────────────────┐       │
│  │              API Routes Layer                    │       │
│  │  /dialogue  /analysis  /simulation  /ocr  ...   │       │
│  └─────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────┐       │
│  │          Intelligence Services Layer             │       │
│  │  • ML Service (HuggingFace Transformers)        │       │
│  │  • Conflict Analyzer                             │       │
│  │  • Simulation Service (Digital Twin)             │       │
│  │  • OCR Service (Tesseract + OpenCV)             │       │
│  └─────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────┐       │
│  │            Database Layer (SQLAlchemy)           │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
    ┌──────────────────────┴──────────────────────┐
    │                                              │
┌───────────┐                               ┌──────────┐
│ PostgreSQL│                               │  Redis   │
│ Database  │                               │  Cache   │
└───────────┘                               └──────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum (for ML models)
- 10GB disk space

### Installation

1. **Clone and setup:**
```bash
cd conflict-intelligence-platform
cp .env.example .env
```

2. **Launch the platform:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First-Time Setup

The system will automatically:
- Initialize PostgreSQL database
- Download ML models (distilbert, emotion-english-distilroberta-base)
- Install spaCy language model
- Start all services

**⏱️ First startup takes 2-5 minutes** for model downloads.

---

## 📊 ML Models & Technologies

### Machine Learning
- **Sentiment Analysis**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Emotion Detection**: `j-hartmann/emotion-english-distilroberta-base`
- **NLP Processing**: `spaCy en_core_web_sm`
- **OCR**: Tesseract + OpenCV

### Backend Stack
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy
- **WebSocket**: Native FastAPI WebSocket support

### Frontend Stack
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Charts**: Recharts
- **State**: Zustand

---

## 🎮 Usage Guide

### 1. Manual Text Input
1. Select speaker (You / Other Person)
2. Type message
3. See real-time conflict score
4. Add to conversation
5. View analysis

### 2. Screenshot Upload
1. Click "Upload Chat Screenshot"
2. Select image from messaging app
3. System extracts dialogue automatically
4. Instant analysis generated

### 3. Simulation Mode
1. Navigate to "Simulation" tab
2. Draft your response
3. Click "Simulate Response"
4. Review predicted reaction
5. Adjust based on feedback

### 4. Analysis Pipeline
1. Go to "Analysis" tab
2. See visual pipeline for each turn
3. Review cognitive biases detected
4. Read personalized recommendations

---

## 📡 API Endpoints

### Dialogue Management
```
POST   /api/dialogue/session/create
POST   /api/dialogue/session/{id}/turn
GET    /api/dialogue/session/{id}/turns
GET    /api/dialogue/sessions/user/{user_id}
```

### Analysis
```
POST   /api/analysis/session/{id}/analyze
GET    /api/analysis/session/{id}/analysis/latest
GET    /api/analysis/session/{id}/pipeline
```

### Simulation (Digital Twin)
```
POST   /api/simulation/session/{id}/simulate
GET    /api/simulation/session/{id}/opponent-profile
```

### OCR
```
POST   /api/ocr/upload-screenshot
POST   /api/ocr/extract-text
```

### Real-time
```
POST   /api/realtime/score
WS     /api/realtime/ws/{client_id}
```

### User Profile
```
GET    /api/profile/user/{user_id}
GET    /api/profile/user/{user_id}/dashboard
```

Full API documentation: http://localhost:8000/docs

---

## 🧠 Intelligence Modules

### Passive Aggression Detector
Hybrid approach combining:
- Rule-based pattern matching ("sure.", "whatever", "do what you want")
- Emotion analysis (low anger + high disgust)
- Sarcasm markers detection

### Cognitive Bias Engine
Detects:
- **Overgeneralization**: "always", "never", "everyone"
- **Mind Reading**: Assuming others' intentions
- **Catastrophizing**: Exaggerating negative outcomes
- **Personalization**: Unfair blame attribution
- **Gaslighting**: Reality distortion patterns

### Escalation Prediction
Formula:
```python
Escalation = (
    0.4 × recent_conflict_avg +
    0.4 × positive_trend_slope +
    0.2 × volatility
)
```

### NVC Interpreter
Maps messages to:
- **Observation**: What was said
- **Evaluation**: Judgment detected
- **Emotion**: Underlying feeling
- **Need**: Likely unmet need

---

## 💎 Differentiators

1. **Digital Twin Technology**: First-of-its-kind opponent response simulation
2. **Multi-Modal Input**: Text + Screenshot OCR
3. **Real-Time Scoring**: Instant feedback while typing
4. **Cognitive Bias Detection**: Academic-grade pattern recognition
5. **Passive Aggression Engine**: Specialized detection system
6. **Visual Pipeline**: Explainable AI analysis flow
7. **Personal Analytics**: Track improvement over time

---

## 📈 Scalability & Roadmap

### Current MVP Capabilities
- Single-user sessions
- Local model inference
- SQLite/PostgreSQL database
- REST API + WebSocket

### Production Scaling Plan
- Multi-tenant architecture
- Model serving with TorchServe
- Redis caching layer
- Horizontal API scaling
- CDN for frontend assets

### Future Integrations
- **Slack Plugin**: Real-time workplace mediation
- **MS Teams Integration**: Corporate conflict resolution
- **Couples Therapy Assistant**: Relationship counseling support
- **Executive AI Coach**: Leadership communication training
- **HR SaaS Platform**: Employee relations management

---

## 🔧 Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

---

## 🐛 Troubleshooting

### Models Not Loading
```bash
# Re-download models
docker-compose down
docker-compose up --build
```

### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up
```

### Port Conflicts
Edit `docker-compose.yml` to change ports:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

---

## 📄 License

This project is a production-grade MVP for demonstration and educational purposes.

---

## 🙏 Acknowledgments

Built with:
- HuggingFace Transformers
- spaCy NLP
- FastAPI
- Next.js
- PostgreSQL
- Redis
- Tesseract OCR

---

## 💼 Commercial Applications

This MVP demonstrates enterprise-ready capabilities for:

- **HR Tech**: Employee conflict resolution
- **Mental Health**: Therapy support tools
- **Education**: Communication skills training
- **Customer Service**: De-escalation assistance
- **Legal Tech**: Mediation support systems

---

## 📧 Contact & Support

For questions, feedback, or partnership inquiries:
- Open an issue on GitHub
- Email: support@conflictintelligence.ai (demo)

---

**Built with ❤️ for better human communication**
