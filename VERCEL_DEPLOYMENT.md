# MedAssist - Vercel Deployment Guide

This guide will help you deploy MedAssist to Vercel with optimized configuration.

## 🚀 Quick Deploy

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Push to GitHub** (already done!)
   ```bash
   # Your repo is at: https://github.com/tharunkumardeveloper/MedAssist
   ```

2. **Import to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/new)
   - Click "Import Project"
   - Select your GitHub repository: `tharunkumardeveloper/MedAssist`
   - Vercel will auto-detect the configuration

3. **Configure Environment Variables**
   Add these in Vercel Dashboard → Settings → Environment Variables:
   
   ```bash
   # Required
   SECRET_KEY=your-generated-secret-key-64-chars
   BOOTSTRAP_ADMIN_EMAIL=admin@yourdomain.com
   BOOTSTRAP_ADMIN_PASSWORD=YourSecurePassword123!
   
   # Optional (defaults provided)
   DATABASE_URL=sqlite:///./medassist.db
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your app will be live at: `https://your-app.vercel.app`

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd MedAssist
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? medassist
# - Directory? ./
# - Override settings? No
```

## ⚙️ Configuration Details

### What Was Optimized

#### 1. **Frontend Optimization (React/Vite)**
- ✅ Code splitting for React, Charts, and core libraries
- ✅ Minification enabled (esbuild)
- ✅ Source maps disabled for production
- ✅ Chunk size optimization
- ✅ Pre-bundled dependencies

#### 2. **Backend Optimization (FastAPI)**
- ✅ Serverless function entry point created
- ✅ Python dependencies optimized for Vercel
- ✅ Route handling configured
- ✅ CORS setup for Vercel domains

#### 3. **Deployment Configuration**
- ✅ `vercel.json` - Vercel deployment settings
- ✅ `api/index.py` - Serverless function handler
- ✅ Build scripts optimized
- ✅ Static file serving configured

### Project Structure for Vercel

```
MedAssist/
├── api/
│   └── index.py          # Serverless function entry point
├── backend/              # FastAPI backend code
│   ├── main.py
│   ├── *.py
│   └── routers/
├── web/                  # React frontend
│   ├── src/
│   ├── dist/             # Build output (generated)
│   ├── package.json
│   └── vite.config.js    # Optimized build config
├── model/                # ML models
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies (root)
└── package.json          # Node dependencies (optional)
```

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (64 chars) | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `BOOTSTRAP_ADMIN_EMAIL` | Admin account email | `admin@yourdomain.com` |
| `BOOTSTRAP_ADMIN_PASSWORD` | Admin password | `SecurePass123!` |

### Optional Variables (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./medassist.db` | Database connection string |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime (24h) |
| `CORS_ORIGINS` | Auto-configured | Comma-separated allowed origins |

### Setting Environment Variables

**Via Vercel Dashboard:**
1. Go to your project
2. Settings → Environment Variables
3. Add each variable
4. Select environments (Production, Preview, Development)
5. Save

**Via Vercel CLI:**
```bash
vercel env add SECRET_KEY
vercel env add BOOTSTRAP_ADMIN_EMAIL
vercel env add BOOTSTRAP_ADMIN_PASSWORD
```

## 📦 Build Settings

Vercel auto-detects these settings (configured in `vercel.json`):

- **Framework Preset:** Vite
- **Build Command:** `cd web && npm install && npm run build`
- **Output Directory:** `web/dist`
- **Install Command:** `npm install`
- **Development Command:** `npm run dev`

## 🗄️ Database Considerations

### SQLite (Default - Development Only)

⚠️ **Warning:** Vercel's serverless functions are stateless. SQLite file will be reset on each deployment.

**For production, use a managed database:**

### Option 1: Vercel Postgres (Recommended)

```bash
# Add Vercel Postgres to your project
vercel postgres create

# Get connection string
vercel env pull

# Update DATABASE_URL in Vercel Dashboard
DATABASE_URL=postgres://user:pass@host/db?sslmode=require
```

### Option 2: PlanetScale (MySQL)

```bash
# Create database at https://planetscale.com
# Get connection string
DATABASE_URL=mysql://user:pass@host/db?sslmode=require
```

### Option 3: Supabase (PostgreSQL)

```bash
# Create project at https://supabase.com
# Get connection string from Settings → Database
DATABASE_URL=postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres
```

### Option 4: MongoDB Atlas

```bash
# Create cluster at https://mongodb.com/atlas
# Get connection string
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/medassist
```

## 🔒 Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` files
- ✅ Use Vercel's encrypted environment variables
- ✅ Generate strong SECRET_KEY for production
- ✅ Use different secrets for preview/production

### 2. CORS Configuration
```bash
# Set specific origins in production
CORS_ORIGINS=https://your-app.vercel.app,https://www.yourdomain.com
```

### 3. Admin Account
- ✅ Change default admin credentials immediately
- ✅ Use strong password (12+ chars, mixed case, numbers, symbols)
- ✅ Enable 2FA on Vercel account

### 4. API Rate Limiting
The app includes built-in rate limiting for login/signup endpoints.

## 🚦 Deployment Process

### Automatic Deployments

Vercel automatically deploys:
- **Production:** Commits to `main` branch → `your-app.vercel.app`
- **Preview:** Pull requests → unique preview URL
- **Development:** Can test locally before push

### Manual Deployment

```bash
# Deploy to production
vercel --prod

# Deploy preview
vercel

# Check deployment status
vercel ls
```

## 📊 Performance Optimization

### Frontend Optimizations Applied

1. **Code Splitting**
   - React libraries in separate chunk
   - Chart library isolated
   - Lazy loading for routes

2. **Build Optimization**
   - Minification enabled
   - Tree shaking active
   - Dead code elimination

3. **Bundle Size**
   - Chunk size warnings configured
   - Dependencies pre-optimized
   - Source maps disabled

### Backend Optimizations Applied

1. **Serverless Function**
   - Cold start optimization
   - Minimal imports
   - Efficient routing

2. **Dependencies**
   - Only production packages
   - No dev dependencies in deployment
   - Optimized for serverless

## 🔍 Monitoring & Debugging

### View Logs

```bash
# Real-time logs
vercel logs

# Function logs
vercel logs --follow
```

### Vercel Dashboard
- Analytics → View traffic, performance
- Deployments → See build logs
- Functions → Monitor serverless functions
- Speed Insights → Performance metrics

## 🌐 Custom Domain

### Add Custom Domain

1. **Via Dashboard:**
   - Settings → Domains
   - Add domain: `medassist.yourdomain.com`
   - Follow DNS configuration steps

2. **Via CLI:**
   ```bash
   vercel domains add medassist.yourdomain.com
   ```

### Update CORS
After adding domain, update environment variable:
```bash
CORS_ORIGINS=https://medassist.yourdomain.com,https://your-app.vercel.app
```

## 🧪 Testing Deployment

### Local Preview
```bash
cd web
npm run build
npm run preview
```

### Test Production Build
```bash
vercel --prod --confirm
```

## 📱 Preview Deployments

Every pull request gets a preview URL:
- Unique URL per PR
- Test changes before merging
- Share with team for review

## ⚡ Serverless Functions

Your API runs as serverless functions:
- **Max Duration:** 10s (Hobby), 60s (Pro), 900s (Enterprise)
- **Max Payload:** 4.5MB
- **Regions:** Auto-configured edge network

### Function Size Limits
- **Source code:** 50MB
- **Dependencies:** Optimized automatically
- **Output size:** 250MB

## 🔄 Continuous Deployment

### GitHub Integration

1. **Push triggers deploy:**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Vercel automatically:**
   - Detects changes
   - Runs build
   - Deploys to production
   - Sends notification

### Rollback

```bash
# List deployments
vercel ls

# Rollback to previous
vercel rollback
```

## 💰 Cost Considerations

### Vercel Free Tier (Hobby)
- ✅ 100GB bandwidth/month
- ✅ 100 serverless function executions/day
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Preview deployments

### When to Upgrade (Pro - $20/month)
- More bandwidth (1TB)
- Unlimited serverless executions
- Longer function timeout (60s)
- Team collaboration
- Priority support

## 🐛 Troubleshooting

### Build Fails

```bash
# Check build logs in Vercel Dashboard
# Common issues:
# 1. Missing environment variables
# 2. Dependency conflicts
# 3. Build script errors
```

### Function Timeout

```bash
# Optimize database queries
# Add indexes
# Cache frequently accessed data
# Consider upgrading plan
```

### CORS Errors

```bash
# Update CORS_ORIGINS environment variable
# Include all domains (with https://)
# Redeploy after changing
```

### Database Connection Issues

```bash
# Check DATABASE_URL format
# Verify database is accessible from internet
# Check firewall rules
# Test connection string locally first
```

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/fastapi)
- [Vite on Vercel](https://vercel.com/docs/frameworks/vite)

## ✅ Deployment Checklist

Before deploying to production:

- [ ] Generate strong SECRET_KEY
- [ ] Set up production database (PostgreSQL/MySQL)
- [ ] Configure environment variables
- [ ] Update CORS_ORIGINS
- [ ] Change admin credentials
- [ ] Test all API endpoints
- [ ] Verify frontend routing
- [ ] Check mobile responsiveness
- [ ] Enable HTTPS (automatic on Vercel)
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts
- [ ] Review security settings

## 🎉 Success!

Once deployed, your MedAssist application will be:
- ✅ Globally distributed via CDN
- ✅ Auto-scaled based on traffic
- ✅ HTTPS enabled by default
- ✅ Zero-downtime deployments
- ✅ Preview URLs for each PR

**Your app URL:** `https://your-project-name.vercel.app`

---

Need help? Check the [main README](./README.md) or [create an issue](https://github.com/tharunkumardeveloper/MedAssist/issues).
