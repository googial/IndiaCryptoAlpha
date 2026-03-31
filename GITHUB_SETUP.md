# IndiaCryptoAlpha - GitHub Repository Setup

Complete guide to push the IndiaCryptoAlpha project to GitHub.

## Prerequisites

- GitHub account (https://github.com)
- Git installed locally
- SSH key configured (optional but recommended)

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `IndiaCryptoAlpha`
   - **Description**: Multi-agent paper trading system for CoinDCX
   - **Visibility**: Private (recommended) or Public
   - **Initialize**: Leave unchecked (we have existing code)

3. Click "Create repository"

## Step 2: Get Repository URL

After creating, GitHub will show you the repository URL:

```
https://github.com/yourusername/IndiaCryptoAlpha.git
```

Or for SSH:
```
git@github.com:yourusername/IndiaCryptoAlpha.git
```

## Step 3: Add Remote to Local Repository

```bash
cd ~/IndiaCryptoAlpha

# Using HTTPS (easier if no SSH key)
git remote set-url origin https://github.com/yourusername/IndiaCryptoAlpha.git

# Or using SSH (if you have SSH key configured)
git remote set-url origin git@github.com:yourusername/IndiaCryptoAlpha.git
```

Verify:
```bash
git remote -v
```

Should show:
```
origin  https://github.com/yourusername/IndiaCryptoAlpha.git (fetch)
origin  https://github.com/yourusername/IndiaCryptoAlpha.git (push)
```

## Step 4: Push to GitHub

```bash
# Push all commits to GitHub
git push -u origin main

# If you get authentication error:
# - For HTTPS: Enter your GitHub username and personal access token
# - For SSH: Make sure SSH key is configured
```

## Step 5: Verify on GitHub

1. Go to https://github.com/yourusername/IndiaCryptoAlpha
2. You should see all files and commits
3. Check the commit history

## Step 6: Clone from GitHub (For Others)

Anyone can now clone the repository:

```bash
# Using HTTPS
git clone https://github.com/yourusername/IndiaCryptoAlpha.git

# Using SSH
git clone git@github.com:yourusername/IndiaCryptoAlpha.git

cd IndiaCryptoAlpha
```

## Workflow: Making Changes

### 1. Make Changes
```bash
# Edit files
nano main.py

# Check status
git status
```

### 2. Stage Changes
```bash
# Stage specific file
git add main.py

# Or stage all changes
git add -A
```

### 3. Commit Changes
```bash
git commit -m "Description of changes"
```

### 4. Push to GitHub
```bash
git push origin main
```

### 5. Pull Latest Changes (if working with others)
```bash
git pull origin main
```

## GitHub Features

### Branches
Create a branch for new features:
```bash
# Create and switch to new branch
git checkout -b feature/new-strategy

# Make changes and commit
git add -A
git commit -m "Add new strategy agent"

# Push branch to GitHub
git push origin feature/new-strategy

# Create Pull Request on GitHub to merge into main
```

### Issues & Discussions
- Use GitHub Issues to track bugs and features
- Use Discussions for questions and ideas

### Actions (CI/CD)
Create `.github/workflows/test.yml` for automated testing:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: python verify_install.py
```

### Releases
Tag releases for version control:
```bash
# Create tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0

# Create Release on GitHub with release notes
```

## GitHub Authentication

### HTTPS (Personal Access Token)
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select scopes: `repo` (full control of private repositories)
4. Copy token and use as password when pushing

### SSH (Recommended)
1. Generate SSH key:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add to GitHub:
   - Go to GitHub Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste public key from `~/.ssh/id_ed25519.pub`

3. Test connection:
   ```bash
   ssh -T git@github.com
   ```

## Troubleshooting

### "Permission denied (publickey)"
- SSH key not configured
- Solution: Use HTTPS or configure SSH key

### "fatal: 'origin' does not appear to be a 'git' repository"
- Remote not set correctly
- Solution: `git remote set-url origin <correct-url>`

### "Updates were rejected because the tip of your current branch is behind"
- Remote has changes you don't have locally
- Solution: `git pull origin main` then `git push origin main`

### "fatal: The current branch main has no upstream branch"
- First push to new branch
- Solution: `git push -u origin main`

## Best Practices

1. **Commit Often**: Small, logical commits are easier to review
2. **Meaningful Messages**: Describe what and why, not just what
3. **Pull Before Push**: Always `git pull` before `git push`
4. **Use Branches**: Keep main stable, use branches for features
5. **Review Changes**: Check `git diff` before committing
6. **Document Changes**: Update README.md when adding features

## Repository Structure

```
IndiaCryptoAlpha/
├── main.py                    # Main orchestrator
├── requirements.txt           # Dependencies
├── setup.sh                   # Setup script
├── verify_install.py          # Verification script
├── .env                       # Configuration (don't commit secrets!)
├── .gitignore                 # Git ignore rules
├── config/                    # Configuration module
├── core/                      # Core system
├── agents/                    # Strategy agents
├── logger/                    # Logging system
├── monitor/                   # Monitoring system
├── researcher/                # Research engine
├── dashboard/                 # Dashboard UI
├── data/                      # Data directory (in .gitignore)
├── logs/                      # Logs directory (in .gitignore)
├── README.md                  # Main documentation
├── QUICKSTART.md              # Quick start guide
├── INSTALL_GUIDE.md           # Installation guide
├── DOCUMENTATION.md           # API documentation
└── .github/                   # GitHub configuration
    └── workflows/             # CI/CD workflows
```

## Sharing with Others

### Public Repository
- Anyone can view and clone
- Great for open-source projects
- Use for sharing with community

### Private Repository
- Only invited collaborators can access
- Great for personal/team projects
- Recommended for trading systems

### Adding Collaborators
1. Go to repository Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username
4. Select permission level

## Next Steps

1. Create GitHub repository
2. Add remote: `git remote set-url origin <url>`
3. Push to GitHub: `git push -u origin main`
4. Share repository URL with others
5. Set up CI/CD workflows (optional)
6. Create releases for versions

## Useful Commands

```bash
# View commit history
git log --oneline

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Create and switch to branch
git checkout -b feature-name

# List branches
git branch -a

# Delete branch
git branch -d feature-name

# Stash changes (save for later)
git stash

# Apply stashed changes
git stash pop

# View remote info
git remote -v

# Update remote URL
git remote set-url origin <new-url>
```

## Support

For GitHub help:
- GitHub Docs: https://docs.github.com
- GitHub CLI: https://cli.github.com
- Git Documentation: https://git-scm.com/doc

---

**Status**: Ready for GitHub
**Version**: 1.0.0
**Last Updated**: March 31, 2026
