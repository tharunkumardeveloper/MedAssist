# MedAssist - Quick Setup Guide

This guide will help you get MedAssist running on your local machine in minutes.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.12+** - [Download here](https://www.python.org/downloads/)
- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Git** - [Download here](https://git-scm.com/downloads)

## Quick Start (Recommended)

### Windows Users

1. **Clone the repository**
   ```bash
   git clone https://github.com/tharunkumardeveloper/MedAssist.git
   cd MedAssist
   ```

2. **Run the automated setup script**
   ```bash
   .\start.ps1
   ```
   
   This script will:
   - Set up the backend environment
   - Install Python dependencies
   - Configure environment variables
   - Set up the frontend
   - Install Node.js dependencies
   - Start both servers

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://127.0.0.1:8000
   - API Documentation: http://127.0.0.1:8000/docs

### Alternative: Using start.bat (Windows CMD)

If PowerShell doesn't work, use:
```bash
start.bat
```

## Manual Setup

If you prefer to set things up manually or the automated script doesn't work:

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows CMD:
venv\Scripts\activate.bat
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env

# Generate a secure SECRET_KEY and update .env file
python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"

# Start the backend server
python -m uvicorn main:app --reload
```

The backend will be available at: http://127.0.0.1:8000

### 2. Frontend Setup (New Terminal/Command Prompt)

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Set up environment variables (optional - defaults work)
copy .env.example .env

# Start the development server
npm run dev
```

The frontend will be available at: http://localhost:5173

## Docker Setup (Alternative)

If you prefer using Docker:

```bash
# Clone the repository
git clone https://github.com/tharunkumardeveloper/MedAssist.git
cd MedAssist

# Set up environment variables
copy .env.example .env

# Generate SECRET_KEY and add to .env
python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"

# Build and start all services
docker compose up --build
```

Services will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Legacy Streamlit UI (optional): http://localhost:8501

## Default Admin Account

On first startup, an admin account is automatically created:
- **Email**: admin@medassist.local
- **Password**: ChangeMe123!

**⚠️ IMPORTANT**: Change these credentials immediately in production!

## Troubleshooting

### Python not found
Make sure Python is installed and added to PATH. Test with: `python --version`

### Node/npm not found
Make sure Node.js is installed and added to PATH. Test with: `node --version`

### Port already in use
If ports 8000 or 5173 are already in use:
- Backend: Change the port with `python -m uvicorn main:app --reload --port 8001`
- Frontend: Change in `vite.config.js` or set `PORT=5174 npm run dev`

### CORS errors in browser console
Make sure `backend/.env` has the correct `CORS_ORIGINS`:
```
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Dependencies installation fails
Try upgrading pip first:
```bash
python -m pip install --upgrade pip
```

### Module not found errors
Make sure you activated the virtual environment (for backend) and installed all dependencies.

## Next Steps

1. **Login** to the application with the admin credentials
2. **Explore** the symptom checker and risk assessment features
3. **Create test users** with different roles (patient, provider, admin)
4. **Review** the API documentation at http://127.0.0.1:8000/docs
5. **Check out** the analytics dashboard (admin/provider only)

## Project Structure

```
MedAssist/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application entry
│   ├── requirements.txt # Python dependencies
│   ├── routers/         # API endpoints
│   └── tests/           # Backend tests
├── web/                 # React frontend
│   ├── src/             # React components
│   ├── package.json     # Node dependencies
│   └── vite.config.js   # Vite configuration
├── model/               # ML models and datasets
├── frontend/            # Legacy Streamlit UI
└── docker-compose.yml   # Docker configuration
```

## Getting Help

- Check the main [README.md](./README.md) for detailed documentation
- Review API docs at http://127.0.0.1:8000/docs when backend is running
- Check browser console and backend logs for error messages

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

## Production Deployment

Before deploying to production:

1. Generate a strong `SECRET_KEY`
2. Change `BOOTSTRAP_ADMIN_PASSWORD`
3. Use PostgreSQL/MySQL instead of SQLite
4. Set up proper CORS origins
5. Use environment-specific `.env` files
6. Enable HTTPS
7. Set up proper logging and monitoring
8. Review security settings in `config.py`
