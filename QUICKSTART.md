# MedAssist - Quick Start Guide

Get MedAssist running in under 5 minutes!

## TL;DR - One Command Installation

```bash
# Clone and setup
git clone https://github.com/tharunkumardeveloper/MedAssist.git
cd MedAssist
.\setup.ps1  # Windows PowerShell (or setup.bat for CMD)

# Start the application
.\start.ps1  # Windows PowerShell (or start.bat for CMD)
```

That's it! Open http://localhost:5173 in your browser.

## Default Login

```
Email:    admin@medassist.local
Password: ChangeMe123!
```

## What You Need

- **Python 3.12+** → [Download](https://www.python.org/downloads/)
- **Node.js 18+** → [Download](https://nodejs.org/)

## Quick Commands

### Setup (One Time)
```bash
.\setup.ps1     # Install all dependencies
```

### Start Application
```bash
.\start.ps1     # Start both backend and frontend
```

### Verify Installation
```bash
.\verify-installation.ps1  # Check if everything is working
```

### Manual Start
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --reload

# Terminal 2 - Frontend
cd web
npm run dev
```

### Run Tests
```bash
cd backend
python -m pytest tests/ -v
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main application UI |
| Backend | http://127.0.0.1:8000 | API server |
| API Docs | http://127.0.0.1:8000/docs | Interactive API documentation |
| Legacy UI | http://localhost:8501 | Streamlit interface (optional) |

## User Roles

| Role | What They Can Do |
|------|------------------|
| **Patient** | Submit symptoms, view results, download reports |
| **Provider** | View analytics dashboard, access triage queue |
| **Admin** | Everything + manage users and roles |

## Common Issues

### "Python not found"
Install Python and make sure it's in your PATH:
```bash
python --version  # Should show Python 3.12+
```

### "Node not found"
Install Node.js and make sure it's in your PATH:
```bash
node --version  # Should show v18+
```

### "Port already in use"
Change ports in your terminal:
```bash
# Backend on different port
cd backend
python -m uvicorn main:app --reload --port 8001

# Frontend on different port
cd web
$env:PORT=5174; npm run dev
```

### "CORS error"
Check `backend/.env` has correct origin:
```
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Quick Feature Tour

### 1. Symptom Checker
- Select symptoms from 183-term vocabulary
- Get ranked disease predictions
- View emergency flags for critical symptoms

### 2. Risk Screening
- Optional lifestyle questionnaire
- Screens for 10 chronic conditions
- Based on CDC BRFSS data

### 3. Treatment References
- Real medication references from MIMIC-IV
- Based on similar cases
- Educational reference only

### 4. Reports
- Downloadable PDF reports
- Complete assessment history
- Shareable with healthcare providers

### 5. Analytics (Provider/Admin)
- Risk distribution charts
- Disease trends over time
- Demographics breakdown

### 6. Triage Queue (Provider/Admin)
- Emergency case identification
- Priority-based sorting
- Quick patient overview

## Project Structure

```
MedAssist/
├── backend/          # FastAPI + SQLAlchemy + ML models
├── web/              # React + Vite + Tailwind
├── model/            # Pre-trained ML models (.pkl files)
├── frontend/         # Legacy Streamlit UI
├── setup.ps1         # Automated installation
├── start.ps1         # Start all services
├── README.md         # Full documentation
└── SETUP.md          # Detailed setup guide
```

## Next Steps

- ✅ Change admin password
- ✅ Create test user accounts
- ✅ Try the symptom checker
- ✅ Explore the analytics dashboard
- ✅ Review API documentation
- ✅ Read the full [README.md](./README.md)

## Getting Help

1. **Check documentation:**
   - [README.md](./README.md) - Full documentation
   - [SETUP.md](./SETUP.md) - Detailed setup guide
   - [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guide

2. **Verify installation:**
   ```bash
   .\verify-installation.ps1
   ```

3. **Check logs:**
   - Backend logs show in the terminal
   - Frontend errors in browser console (F12)

4. **API Documentation:**
   - http://127.0.0.1:8000/docs (when backend is running)

## Development

Want to contribute? Check out [CONTRIBUTING.md](./CONTRIBUTING.md)

```bash
# Fork repo, clone, and create branch
git checkout -b feature/my-feature

# Make changes and test
cd backend
python -m pytest tests/ -v

# Commit and push
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

## Security Note

⚠️ **This is for development/demo purposes**

Before production:
- Change SECRET_KEY
- Change admin password
- Use PostgreSQL/MySQL (not SQLite)
- Enable HTTPS
- Set up proper CORS
- Add rate limiting
- Enable logging and monitoring

---

**Need more details?** See [SETUP.md](./SETUP.md) for comprehensive instructions.

**Ready to contribute?** See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.
