# Corporate Smart Messenger

A comprehensive corporate communication platform built with Streamlit, MongoDB, and AI-powered task management.

## 🚀 Features

- **Real-time Messaging**: Chat with individuals and groups
- **AI Task Detection**: Automatically extracts meetings and action items from conversations
- **Task Management**: Track and manage tasks with due dates and priorities
- **AI Assistant**: Semantic search through chat history for intelligent answers
- **Calendar Integration**: Visual calendar with events and task deadlines
- **User Management**: Admin panel for user registration and management
- **Theme Support**: Dark, Light, and Blue themes
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with MongoDB Atlas
- **AI**: Anthropic Claude API for task detection and assistance
- **Database**: MongoDB with ChromaDB for vector search
- **Authentication**: bcrypt password hashing with role-based access

## 📋 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Anthropic API key (optional, for AI features)

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd corporate_messenger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI and API keys
```

### Setup
```bash
# Test database connection
python backend/test_connection.py

# Seed admin accounts
python backend/setup_admins.py

# Run the application
streamlit run frontend/app.py
```

## 📁 Project Structure

```
corporate_messenger/
├── backend/
│   ├── database.py          # MongoDB operations
│   ├── auth.py             # User authentication
│   ├── rag_assistant.py     # AI assistant logic
│   ├── rag_watcher.py      # Background RAG indexing
│   └── requirements.txt      # Backend dependencies
├── frontend/
│   ├── app.py              # Main Streamlit application
│   ├── pages/               # Streamlit pages
│   │   ├── streamlit_login.py
│   │   ├── user_dashboard.py
│   │   ├── admin_dashboard.py
│   │   ├── messages.py
│   │   ├── calendar.py
│   │   └── ai_assistant.py
│   ├── styles.py            # Global CSS styles
│   └── requirements.txt      # Frontend dependencies
├── .env                   # Environment variables
├── .gitignore              # Git ignore file
└── README.md              # This file
```

## 🔐 Default Admin Accounts

| Department | Login ID | Password |
|------------|------------|----------|
| Development | devadm000000 | devadm000000 |
| HR | hrsadm000000 | hrsadm000000 |
| Finance | finadm000000 | finadm000000 |
| Marketing | mktadm000000 | mktadm000000 |
| Sales | saladm000000 | saladm000000 |
| Support | supadm000000 | supadm000000 |

## 🤖 AI Features

The AI assistant provides:
- **Task Extraction**: Automatically identifies meetings and action items from messages
- **Semantic Search**: Finds relevant information from conversation history
- **Smart Summaries**: Generates task summaries and progress reports
- **Question Answering**: Answers questions about schedules, projects, and team activities

## 🎨 Themes

- **Dark Theme**: Professional dark interface (default)
- **Light Theme**: Clean, bright interface for daytime use
- **Blue Theme**: Corporate blue color scheme

## 🔄 Development

### Adding New Features
1. Backend logic in `backend/` directory
2. Frontend pages in `frontend/pages/` directory
3. Update styles in `frontend/styles.py`
4. Test with `streamlit run frontend/app.py`
1. The message is **embedded** (sentence-transformers) and stored in **ChromaDB**.
2. The message text is scanned by the **RAG Extractor** for:
   - Meeting keywords: `meeting`, `call`, `standup`, `review`, `demo`, `presentation`, etc.
   - Action keywords: `please`, `submit`, `complete`, `deadline`, `urgent`, `deploy`, etc.
3. If detected, **tasks are auto-created** for all other conversation participants.
4. The task includes the original message, due date (auto-parsed from text like "tomorrow", "Friday", "EOD"), and task type.
5. Users see their tasks in **My Tasks** with pending/done status management.

### AI Assistant (RAG)
- Users type natural language questions.
- The system performs **semantic search** over all indexed chat messages.
- Top matching messages are sent as context to **Claude (claude-sonnet-4)**.
- Claude generates a grounded, factual answer.

### Calendar
- Tasks with due dates automatically appear on the calendar as yellow dots.
- Users can also add manual events (green dots).
- Clicking any date shows tasks due that day + saved events.

---

## 🗄️ MongoDB Collections

| Collection     | Purpose                                      |
|---------------|----------------------------------------------|
| `users`        | User accounts, roles, departments            |
| `conversations`| Direct and group conversation metadata       |
| `messages`     | All chat messages                            |
| `tasks`        | Auto-detected and manually created tasks     |
| `events`       | Calendar events saved by users               |

---

## 🔐 Login ID Format

```
<dept_code><role_code><sequence>

Examples:
  devusr000001  →  Development / User  / sequence 1
  hrsadm000000  →  HR          / Admin / sequence 0 (seeded)
  finmgr000001  →  Finance     / Manager / sequence 1
```

Department codes: `dev`, `hrs`, `fin`, `mkt`, `sal`, `sup`  
Role codes: `usr`, `mgr`, `adm`

---

## ❓ Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run from project root; activate venv |
| MongoDB connection fails | Check `.env` MONGODB_URI; whitelist your IP in Atlas |
| AI assistant returns error | Check ANTHROPIC_API_KEY in `.env` |
| No tasks auto-created | Run `seed_index.py`; check ChromaDB path permissions |
| Streamlit blank page | Clear browser cache; restart with `streamlit run frontend/app.py` |
| `chromadb` install error | Try `pip install chromadb --upgrade` |
| `sentence-transformers` slow first run | It downloads the model (~90MB) on first use — normal |
