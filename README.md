# DataChat - Day 1 Setup

AI-powered conversational data analysis web app - Initial skeleton setup.

## Project Structure

```
datachat/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── analysis/
│   │   ├── ai/
│   │   └── main.py
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── next.config.js
│   └── .gitignore
└── README.md
```

## Setup Instructions

### Backend Setup

1. **Create Python virtual environment:**

```bash
cd backend
python -m venv venv
```

2. **Activate virtual environment:**

On Windows (PowerShell):
```bash
.\venv\Scripts\Activate.ps1
```

On Windows (Command Prompt):
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

### Frontend Setup

1. **Install dependencies:**

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Port 8000)

From the `backend` directory with virtual environment activated:

```bash
uvicorn app.main:app --reload
```

Backend will be available at: `http://127.0.0.1:8000`

Health check endpoint: `http://127.0.0.1:8000/health`

### Start Frontend (Port 3000)

From the `frontend` directory:

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Verification

When both servers are running:

1. Open `http://localhost:3000` in your browser
2. You should see "DataChat" title
3. You should see "DataChat Status: Backend running"

If you see "DataChat Status: Backend connection failed", ensure:
- Backend is running on `http://127.0.0.1:8000`
- CORS is properly configured
- No firewall is blocking the connection

## Endpoints

### Backend API

- **GET /health** - Health check endpoint
  - Response: `{"status": "Backend running"}`

## Tech Stack

**Backend:**
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pandas 2.1.1
- Python 3.8+

**Frontend:**
- Next.js 14.0.0
- React 18.2.0
- TypeScript 5.2.0
- Tailwind CSS 3.3.5

## Day 1 Scope

This is the initial skeleton setup with:
- ✅ Frontend (Next.js + TypeScript + Tailwind)
- ✅ Backend (FastAPI)
- ✅ Frontend-Backend connection
- ✅ Health check verification

Not included in Day 1:
- Gemini API
- CSV upload
- Plotly
- AI logic
- Authentication
- Database
