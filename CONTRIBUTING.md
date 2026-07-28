# Contributing to MedAssist

Thank you for your interest in contributing to MedAssist! This document provides guidelines and instructions for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/MedAssist.git
   cd MedAssist
   ```
3. **Run the setup script** to install dependencies:
   ```bash
   .\setup.ps1  # Windows PowerShell
   # or
   setup.bat    # Windows CMD
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running the Application

**Start both services:**
```bash
.\start.ps1  # or start.bat
```

**Or start individually:**

Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Frontend:
```bash
cd web
npm install
npm run dev
```

### Running Tests

Backend tests:
```bash
cd backend
python -m pytest tests/ -v
```

Run tests with coverage:
```bash
cd backend
python -m pytest tests/ -v --cov=. --cov-report=html
```

### Code Style

**Python:**
- Follow PEP 8 style guide
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Add docstrings to functions and classes

**JavaScript/React:**
- Use functional components with hooks
- Follow consistent naming conventions
- Keep components small and reusable
- Use meaningful variable names

### Project Structure

```
MedAssist/
├── backend/              # FastAPI backend
│   ├── main.py          # Application entry point
│   ├── auth.py          # Authentication logic
│   ├── database.py      # Database models
│   ├── predict.py       # ML prediction logic
│   ├── routers/         # API route handlers
│   │   ├── auth_routes.py
│   │   ├── patient_routes.py
│   │   ├── admin_routes.py
│   │   └── report_routes.py
│   └── tests/           # Backend tests
├── web/                 # React frontend
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Page components
│   │   ├── context/     # React context
│   │   └── lib/         # Utilities
│   └── public/          # Static assets
├── model/               # ML models and datasets
└── frontend/            # Legacy Streamlit UI
```

## Making Changes

### Adding New Features

1. **Check existing issues** to avoid duplicate work
2. **Create an issue** describing the feature
3. **Discuss the approach** before starting work
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request** with clear description

### Fixing Bugs

1. **Create an issue** describing the bug (if not exists)
2. **Write a failing test** that reproduces the bug
3. **Fix the bug** and ensure the test passes
4. **Submit a pull request** with issue reference

### Improving Documentation

Documentation improvements are always welcome! This includes:
- Fixing typos or unclear explanations
- Adding examples
- Improving setup instructions
- Adding troubleshooting tips

## Commit Messages

Write clear, descriptive commit messages:

```bash
# Good
git commit -m "Add email verification feature to auth flow"
git commit -m "Fix CORS error when frontend calls /assess endpoint"
git commit -m "Update README with Docker installation steps"

# Not so good
git commit -m "fix bug"
git commit -m "update"
git commit -m "changes"
```

Format:
- Use imperative mood ("Add feature" not "Added feature")
- Start with capital letter
- Keep first line under 72 characters
- Add detailed description after blank line if needed

## Pull Request Process

1. **Update your branch** with latest main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests** to ensure nothing broke:
   ```bash
   cd backend
   python -m pytest tests/ -v
   ```

3. **Push your branch** to your fork:
   ```bash
   git push origin your-feature-branch
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues
   - Screenshots for UI changes

5. **Address review comments** if any

6. **Wait for approval** from maintainers

## Code Review Guidelines

When reviewing code:
- Be respectful and constructive
- Focus on the code, not the person
- Explain reasoning behind suggestions
- Approve when satisfied with changes

## Areas for Contribution

### High Priority
- [ ] Email verification for new accounts
- [ ] Password reset functionality
- [ ] Enhanced test coverage
- [ ] Performance optimization
- [ ] Accessibility improvements

### Medium Priority
- [ ] Internationalization (i18n)
- [ ] Dark mode support
- [ ] Export analytics to CSV/Excel
- [ ] Mobile app version
- [ ] Integration with EHR systems

### Documentation
- [ ] API documentation examples
- [ ] Video tutorials
- [ ] Deployment guides for cloud platforms
- [ ] Architecture decision records

### Testing
- [ ] Frontend unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing

## Questions?

- Check the [README.md](./README.md) and [SETUP.md](./SETUP.md)
- Review existing issues and pull requests
- Create a new issue for questions
- Review API docs at http://127.0.0.1:8000/docs

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Thank You!

Your contributions make MedAssist better for everyone. We appreciate your time and effort!
