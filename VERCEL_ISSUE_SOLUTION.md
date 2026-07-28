# Vercel Deployment Issue & Solutions

## 🔴 Current Issue

The MedAssist backend is failing on Vercel with 500 errors because:

1. **ML Models Too Large**: The scikit-learn models (~7MB) are too heavy for serverless cold starts
2. **Initialization Time**: Loading 3 ML models + pandas dataframes takes too long
3. **Function Size**: Vercel has a 250MB limit, and our dependencies are close to that
4. **Memory**: Model loading requires more memory than default allocation

## ✅ Recommended Solutions

### **Option 1: Split Deployment (RECOMMENDED)**

Deploy frontend on Vercel, backend elsewhere:

#### Frontend: Vercel ✅
- Fast, global CDN
- Perfect for React apps
- Free tier sufficient

#### Backend Options:

**A. Railway (Easiest)**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize and deploy backend
cd backend
railway init
railway up
```
- ✅ Free tier available
- ✅ Supports Python + ML models
- ✅ Persistent database
- ✅ Auto HTTPS
- 🔗 [Railway.app](https://railway.app)

**B. Render**
```bash
# 1. Connect GitHub repo to Render
# 2. Create Web Service
# 3. Set build command: pip install -r backend/requirements.txt
# 4. Set start command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```
- ✅ Free tier (with sleep)
- ✅ Easy deployment
- 🔗 [Render.com](https://render.com)

**C. Fly.io**
```bash
# 1. Install flyctl
# 2. fly launch
# 3. Deploy
```
- ✅ Good free tier
- ✅ Global edge deployment
- 🔗 [Fly.io](https://fly.io)

**D. Google Cloud Run**
- ✅ Generous free tier
- ✅ Auto-scaling
- ✅ Pay per request

**E. AWS App Runner**
- ✅ Simple container deployment
- ✅ Auto-scaling

### **Option 2: Vercel with External API**

Keep trying Vercel serverless but reduce model size:

1. **Model Optimization**
   - Compress models with joblib compression
   - Use model quantization
   - Lazy load models only when needed

2. **Increase Function Limits** (Pro Plan $20/month)
   - 1GB memory (vs 256MB free)
   - 60s timeout (vs 10s free)
   - Faster cold starts

3. **Use Vercel Edge Functions** (Experimental)
   - Faster than serverless
   - Smaller payload size

### **Option 3: Serverless + Model API**

Split ML inference to separate service:

- Frontend: Vercel
- API Backend: Vercel serverless (no ML)
- ML Inference: Modal, Banana, or Replicate
- Database: Vercel Postgres or Supabase

## 🚀 Quick Fix: Deploy to Railway (5 minutes)

### Step 1: Keep Frontend on Vercel
Your frontend is already working! Just needs backend URL.

### Step 2: Deploy Backend to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create Railway project
railway init

# Deploy backend
cd backend
railway up
```

### Step 3: Get Backend URL
```bash
railway open
# Copy your backend URL: https://your-app.railway.app
```

### Step 4: Update Vercel Environment Variable
In Vercel Dashboard:
```
VITE_API_URL=https://your-app.railway.app
```

### Step 5: Redeploy Frontend
```bash
vercel --prod
```

Done! ✅

## 📊 Comparison

| Platform | ML Models | Database | Cost | Setup Time |
|----------|-----------|----------|------|------------|
| **Railway** | ✅ Yes | ✅ Yes | Free/$5 | 5 min |
| **Render** | ✅ Yes | ✅ Yes | Free/$7 | 10 min |
| **Fly.io** | ✅ Yes | ✅ Yes | Free | 10 min |
| **Vercel Serverless** | ⚠️ Difficult | ⚠️ External | Free/$20 | Complex |
| **Google Cloud Run** | ✅ Yes | ✅ Yes | Free tier | 15 min |

## 🔧 Alternative: Optimize for Vercel

If you must use Vercel for everything:

### 1. Reduce Model Size

Update `backend/predict.py`:
```python
import joblib

# Load with compression
mlb = joblib.load(MODEL_DIR / "model1_symptom_binarizer.pkl", mmap_mode='r')
```

### 2. Lazy Loading

Only load models when endpoints are called:
```python
_models_cache = {}

def get_model(name):
    if name not in _models_cache:
        _models_cache[name] = joblib.load(MODEL_DIR / f"{name}.pkl")
    return _models_cache[name]
```

### 3. Upgrade Vercel Plan

Pro plan ($20/month):
- 1GB function memory
- 60s timeout
- Better for ML workloads

### 4. Split into Multiple Functions

Create separate serverless functions:
- `/api/auth` - Authentication (fast)
- `/api/assess` - ML predictions (heavy)
- `/api/analytics` - Data queries (medium)

## 💡 My Recommendation

**Use Railway for Backend + Vercel for Frontend**

Why?
- ✅ Quick setup (5 minutes)
- ✅ Free tier works perfectly
- ✅ No ML model size issues
- ✅ Persistent database
- ✅ Simple environment variable setup
- ✅ Railway auto-detects Python projects

## 📝 Detailed Railway Setup

### 1. Create Railway Account
Go to [Railway.app](https://railway.app) and sign up with GitHub

### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose `MedAssist` repository
- Select `backend` directory

### 3. Configure Service
Railway auto-detects:
- ✅ Python runtime
- ✅ requirements.txt
- ✅ Start command

Manual config (if needed):
```
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Add Environment Variables
In Railway dashboard:
```
SECRET_KEY=<your-secret-key>
BOOTSTRAP_ADMIN_EMAIL=admin@yourdomain.com
BOOTSTRAP_ADMIN_PASSWORD=YourSecurePass123!
DATABASE_URL=<railway-provides-this-automatically>
```

### 5. Deploy
Click "Deploy" - Railway will:
- Build your backend
- Install all dependencies
- Start the server
- Give you a URL

### 6. Update Frontend
Update `VITE_API_URL` in Vercel to your Railway backend URL.

## 🎯 Quick Commands Reference

### Railway
```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs

# Open dashboard
railway open
```

### Render
```bash
# Deploy via web dashboard
# Connect GitHub → Auto-deploy on push
```

### Fly.io
```bash
# Install
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Launch
fly launch

# Deploy
fly deploy
```

## ❓ FAQ

**Q: Why not just use Vercel for everything?**
A: Vercel serverless is optimized for lightweight APIs, not ML models. The cold start time and memory limits make it difficult for ML workloads.

**Q: Will I have to pay for Railway/Render?**
A: Both have generous free tiers. Railway free tier should handle moderate traffic. Render free tier has sleep after inactivity.

**Q: Can I keep frontend on Vercel?**
A: Yes! Vercel is perfect for React frontends. Just point `VITE_API_URL` to your backend.

**Q: What about the database?**
A: Railway/Render provide managed PostgreSQL. Or use Supabase (free tier) for both platforms.

**Q: How do I switch backends?**
A: Just change `VITE_API_URL` environment variable in Vercel and redeploy frontend.

## ✅ Next Steps

1. Choose deployment platform (I recommend Railway)
2. Deploy backend there
3. Get backend URL
4. Update `VITE_API_URL` in Vercel
5. Redeploy frontend
6. Test and enjoy! 🎉

Need help? Create an issue on GitHub!
