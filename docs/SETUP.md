# Ratatouille Setup Guide

Complete installation and configuration instructions for running Ratatouille locally.

## Prerequisites

- **Python 3.10 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 18+ and npm** ([Download](https://nodejs.org/))
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Tavily API key** ([Get one here](https://tavily.com))

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/brooondooon/ratatouille.git
cd ratatouille-project
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

#### Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor
```

Required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Tavily Configuration
TAVILY_API_KEY=tvly-your-actual-key-here

# Python Path
PYTHONPATH=/absolute/path/to/ratatouille-project
```

**Getting API Keys:**

1. **OpenAI API Key**:
   - Visit https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-proj-`)
   - Add billing information (required for API usage)

2. **Tavily API Key**:
   - Visit https://tavily.com
   - Sign up for a free account
   - Navigate to API section
   - Copy your API key (starts with `tvly-`)

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint
cp .env.example .env.local
```

Edit `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend Server

```bash
# From project root
export PYTHONPATH=/absolute/path/to/ratatouille-project
python3 backend/app.py
```

Backend will start on http://localhost:8000

You should see:

```
============================================================
🐀 Starting Ratatouille API Server
============================================================
   URL: http://localhost:8000
   Docs: http://localhost:8000/docs
   OpenAI: ✓
   Tavily: ✓
============================================================
```

### Start Frontend Server

In a new terminal:

```bash
cd frontend
npm run dev
```

Frontend will start on http://localhost:3000

## Verification

### Test Backend API

Visit http://localhost:8000/docs to see the interactive API documentation.

Test a simple request:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to learn pan sauces for beginners",
    "is_follow_up": false
  }'
```

Expected response time: ~30-32 seconds

### Test Frontend

1. Open http://localhost:3000 in your browser
2. You should be redirected to `/chat`
3. Type: "I want to learn pan sauces for beginners"
4. Click Send
5. Wait ~30 seconds for results

## Troubleshooting

### Backend Issues

**Error: `ModuleNotFoundError: No module named 'backend'`**

```bash
# Set PYTHONPATH
export PYTHONPATH=/absolute/path/to/ratatouille-project

# Or add to your shell profile (~/.bashrc or ~/.zshrc)
echo 'export PYTHONPATH=/absolute/path/to/ratatouille-project' >> ~/.zshrc
source ~/.zshrc
```

**Error: `openai.AuthenticationError: Incorrect API key`**

- Verify your API key is correct in `.env`
- Check that `.env` is in the project root
- Ensure the key starts with `sk-proj-`
- Verify billing is set up on OpenAI account

**Error: `tavily.exceptions.InvalidAPIKeyError`**

- Verify your Tavily API key in `.env`
- Ensure the key starts with `tvly-`
- Check your Tavily account is active

**Port 8000 already in use:**

```bash
# Find and kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn backend.app:app --host 0.0.0.0 --port 8001
```

### Frontend Issues

**Error: `ECONNREFUSED` or API not reachable**

- Ensure backend is running on http://localhost:8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Verify CORS is enabled in backend (already configured)

**Port 3000 already in use:**

```bash
# Use a different port
npm run dev -- -p 3001
```

**Blank screen or hydration errors:**

- Clear browser cache and localStorage
- Try incognito/private mode
- Check console for errors

### Performance Issues

**Requests timing out (>60s):**

- Check internet connection
- Verify Tavily API is responding (test at https://tavily.com)
- Check OpenAI API status (https://status.openai.com)

**Slow response times (>45s):**

This is normal. The system makes:
- 5 Tavily API calls (~10s)
- 12 OpenAI API calls (~20s)
- Total: ~30-32s average

### Common Errors

**`422 Unprocessable Entity`**

Your request is malformed. Check:
- Message is a string
- `is_follow_up` is a boolean
- All required fields are present

**`500 Internal Server Error`**

Check backend logs for details. Common causes:
- API key issues
- Network connectivity
- LLM parsing failures (retries automatically)

## Development Workflow

### Backend Development

```bash
# Run with auto-reload
python3 -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Changes to Python files will auto-reload the server.

### Frontend Development

```bash
cd frontend
npm run dev
```

Changes to TypeScript/React files will hot-reload automatically.

### Testing

**Backend**:
```bash
# Visit interactive docs
open http://localhost:8000/docs

# Run example requests
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "pan sauces", "is_follow_up": false}'
```

**Frontend**:
- Open http://localhost:3000
- Use browser DevTools (Network tab) to inspect requests
- Check Console for errors

## Project Structure

```
ratatouille-project/
├── backend/
│   ├── agents/               # 4 specialized agents
│   │   ├── research_planner.py
│   │   ├── recipe_hunter.py
│   │   ├── personalization.py
│   │   ├── nutrition_analyzer.py
│   │   └── intent_extractor.py
│   ├── app.py               # FastAPI server
│   ├── graph.py             # LangGraph workflow
│   ├── state.py             # State schema
│   ├── config.py            # Configuration
│   └── logger.py            # Logging setup
├── frontend/
│   ├── app/                 # Next.js pages
│   │   ├── chat/           # Main chat interface
│   │   ├── cook/           # Cooking mode
│   │   └── cookbook/       # Saved recipes
│   ├── components/         # React components
│   ├── lib/                # Utilities and types
│   └── public/             # Static assets
├── docs/                   # Documentation
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── README.md              # Main documentation
```

## Next Steps

1. **Read the Architecture** - See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
2. **Explore the API** - See [API_REFERENCE.md](API_REFERENCE.md) for endpoint documentation
3. **Understand the Frontend** - See [FRONTEND.md](FRONTEND.md) for UI component details
4. **Try Example Queries**:
   - "I want to learn pan sauces for beginners"
   - "easy knife skills for vegetables"
   - "sushi recipes for intermediate cooks"
   - "gluten-free bread baking"

## Support

- **Issues**: https://github.com/brooondooon/ratatouille/issues
- **Tavily Docs**: https://docs.tavily.com
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph
- **OpenAI Docs**: https://platform.openai.com/docs

## Cost Estimates

Per request (~30-32 seconds):
- Tavily API: 5 calls × $0.001 = **$0.005**
- OpenAI GPT-3.5-turbo: ~12k tokens = **$0.012**
- **Total**: **~$0.017 per recipe request**

For 100 requests/day: ~$1.70/day or ~$50/month

## Production Deployment

This project can be deployed to:
- **Backend**: Render, Railway, Fly.io, AWS Lambda
- **Frontend**: Vercel, Netlify, Cloudflare Pages

See deployment configuration in:
- `render.yaml` - Render backend config
- `vercel.json` - Vercel frontend config

Note: Production deployment requires:
- Setting environment variables in hosting platform
- Updating `NEXT_PUBLIC_API_URL` to production backend URL
- (Optional) MongoDB for chat history persistence
