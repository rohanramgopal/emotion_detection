<div align="center">

# 🎭 Fresh Emotion
### *AI-Powered Emotion Intelligence Platform*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Gemini AI](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> Detect human emotions from **text**, **voice**, **images**, and **live webcam** in real-time — powered entirely by Google's Gemini 2.5 Flash multimodal AI. No third-party emotion APIs. No datasets. Just raw AI inference.

</div>

---

## ✨ What Makes This Different

Most emotion detection projects use pre-trained ML models like DeepFace or FER that only work on faces in images. **Fresh Emotion** goes further:

- 📝 **Text** → Semantic emotion understanding (not just sentiment positive/negative)
- 🎤 **Voice** → Speech-to-text + emotion inference on the transcript
- 🖼️ **Image** → Gemini Vision reads facial geometry and context
- 📹 **Live Webcam** → Continuous frame-by-frame scanning every 4 seconds
- 🎵 **Music Response** → Spotify + YouTube playlists matched to your detected mood
- 💡 **Quote Engine** → Motivational quotes curated per emotion to shift your state

**Single AI provider architecture** — 100% powered by Gemini 2.5 Flash. No fallbacks to third-party APIs cluttering the codebase.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRESH EMOTION                        │
│                                                         │
│  ┌─────────────┐    ┌───────────────────────────────┐  │
│  │  Frontend   │    │         Django Backend         │  │
│  │  (Vanilla)  │    │                               │  │
│  │             │    │  ┌─────────────────────────┐  │  │
│  │  index.html │───▶│  │   REST API (DRF)        │  │  │
│  │  login.html │    │  │  /api/analyze/text/     │  │  │
│  │  analysis   │    │  │  /api/analyze/voice/    │  │  │
│  │  dashboard  │    │  │  /api/analyze/image/    │  │  │
│  │             │    │  └──────────┬──────────────┘  │  │
│  │  auth.js    │    │             │                  │  │
│  │  analysis.js│    │  ┌──────────▼──────────────┐  │  │
│  └─────────────┘    │  │   Provider Manager      │  │  │
│                     │  │   (Single: Gemini)      │  │  │
│  JWT Tokens         │  └──────────┬──────────────┘  │  │
│  localStorage       │             │                  │  │
│                     │  ┌──────────▼──────────────┐  │  │
│                     │  │   Gemini 2.5 Flash      │  │  │
│                     │  │   - analyze_text()      │  │  │
│                     │  │   - analyze_image()     │  │  │
│                     │  └──────────┬──────────────┘  │  │
│                     │             │                  │  │
│                     │  ┌──────────▼──────────────┐  │  │
│                     │  │  Recommendation Engine  │  │  │
│                     │  │  - MusicEngine (10 mood)│  │  │
│                     │  │  - QuoteEngine          │  │  │
│                     │  └─────────────────────────┘  │  │
│                     │                               │  │
│                     │  SQLite DB (Django ORM)        │  │
│                     └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input
    │
    ▼
Frontend (HTML/JS) ──JWT──▶ Django REST API
                                    │
                         ┌──────────▼──────────┐
                         │  GeminiProvider     │
                         │  google.genai SDK   │
                         │  gemini-2.5-flash   │
                         └──────────┬──────────┘
                                    │ JSON response
                         ┌──────────▼──────────┐
                         │  Emotion + Confidence│
                         │  + Reasoning         │
                         │  + Suggestions       │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             Music Engine     Quote Engine    DB Record
           Spotify/YouTube    10 emotions    Analysis +
             search URLs      curated        History
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [Gemini API Key](https://aistudio.google.com/) (free tier works)

### 1. Clone & Setup

```bash
git clone https://github.com/rohanramgopal/emotion_detection.git
cd emotion_detection/backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

```env
GEMINI_API_KEY=your_key_from_aistudio.google.com
SECRET_KEY=any-long-random-string
DEBUG=True
```

### 3. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run

```bash
python manage.py runserver
```

Open **http://localhost:8000** → Login → Start analyzing emotions 🎯

---

## 📁 Project Structure

```
emotion_detection/
├── backend/
│   ├── emotion_detection/          # Django project root
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ai_engine/
│   │       ├── providers/
│   │       │   ├── base_provider.py
│   │       │   └── gemini_provider.py   # Core AI logic
│   │       └── provider_manager.py
│   ├── api/                        # REST API
│   │   ├── models.py               # EmotionAnalysis, Recommendation...
│   │   ├── serializers.py
│   │   ├── views.py                # Analysis endpoints
│   │   └── urls.py
│   └── recommendations/
│       ├── music_engine.py         # Spotify + YouTube by emotion
│       └── quote_engine.py         # Motivational quotes by emotion
├── frontend/
│   ├── templates/
│   │   ├── index.html              # Landing page
│   │   ├── login.html
│   │   ├── analysis.html           # Main scanner UI
│   │   └── dashboard.html
│   └── static/
│       ├── css/style.css           # Premium dark UI
│       └── js/
│           ├── auth.js             # JWT handling
│           └── analysis.js         # All 4 analysis modes
└── README.md
```

---

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/token/` | Login → get JWT |
| `POST` | `/api/auth/register/` | Register new user |
| `POST` | `/api/analyze/text/` | Analyze emotion from text |
| `POST` | `/api/analyze/voice/` | Analyze emotion from transcript |
| `POST` | `/api/analyze/image/` | Analyze emotion from image file |
| `GET`  | `/api/analyses/` | User's analysis history |
| `GET`  | `/api/recommendations/?emotion=happy` | Get music + quotes |

### Sample Request

```bash
curl -X POST http://localhost:8000/api/analyze/text/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel absolutely amazing today, everything is going great!"}'
```

### Sample Response

```json
{
  "emotion": "happy",
  "confidence": 0.94,
  "reasoning": "The text contains strong positive language ('absolutely amazing', 'everything is going great') indicating high happiness.",
  "provider_used": "gemini",
  "recommendations": {
    "music": {
      "spotify": ["https://open.spotify.com/search/happy%20music/playlists"],
      "youtube": ["https://www.youtube.com/results?search_query=happy+songs+playlist"]
    },
    "quotes": [
      "Happiness is not something ready-made. It comes from your own actions.",
      "The most wasted of days is one without laughter."
    ]
  }
}
```

---

## 🧠 Supported Emotions

| Emotion | Emoji | Music Response |
|---------|-------|---------------|
| Happy | 😊 | Upbeat hits, feel-good playlists |
| Sad | 😢 | Melancholic healing music |
| Angry | 😠 | Heavy workout / metal |
| Fear | 😨 | Peaceful, calming piano |
| Disgust | 🤢 | Mood-lifting pop |
| Surprise | 😲 | New releases, trending |
| Neutral | 😐 | Lofi, focus music |
| Stressed | 😰 | Meditation, stress relief |
| Motivated | 💪 | Gym, pump-up anthems |
| Confused | 🤔 | Deep focus, clarity |

---

## 🔐 Authentication Flow

```
1. POST /api/auth/token/ → { access, refresh }
2. Store tokens in localStorage
3. Every API request: Authorization: Bearer <access>
4. Token expires → refresh via /api/auth/token/refresh/
5. Logout → clear localStorage
```

JWT tokens use HS256 algorithm. Access tokens expire in 60 minutes, refresh tokens in 7 days.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Engine | Google Gemini 2.5 Flash (`google.genai`) |
| Backend | Django 4.2 + Django REST Framework |
| Auth | JWT via `djangorestframework-simplejwt` |
| Database | SQLite (swappable to PostgreSQL) |
| Frontend | Vanilla HTML/CSS/JavaScript |
| UI Style | Custom dark glassmorphic design |
| Voice | Web Speech API (browser-native) |
| Camera | MediaDevices API + Canvas frame capture |

---

## 🌟 Key Design Decisions

**Why Gemini only?**
Instead of chaining multiple AI providers with fallbacks (Groq, OpenRouter, etc.), this project uses a single high-quality provider. Gemini 2.5 Flash handles both text and vision in one API, making the codebase cleaner and the results more consistent.

**Why no facial emotion ML model?**
Traditional models like DeepFace require OpenCV, dlib, large model files, and only work on clear frontal faces. Gemini Vision understands context — it can analyze facial expressions, body language, and image context together for richer results.

**Why Vanilla JS?**
No build tools, no npm, no bundler complexity. The frontend loads instantly and is easy to understand and extend.

---

## 📸 Screenshots

> Run the app locally and explore all 4 analysis modes: Text, Voice, Image, and Live Webcam.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

Built by **Rohan Ramgopal** · [GitHub](https://github.com/rohanramgopal)

⭐ Star this repo if you found it useful!

</div>
