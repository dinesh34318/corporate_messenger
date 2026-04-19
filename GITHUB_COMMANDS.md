# Git Commands for GitHub Setup

## Correct Remote Add Command
```bash
# Remove any existing remote first
git remote remove origin

# Add your GitHub repository (note the corrected URL without space)
git remote add origin https://github.com/dinesh34318/corporate-messenger.git

# Verify the remote was added correctly
git remote -v
```

## Add Files and Commit
```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Corporate Smart Messenger with AI features"

# Push to GitHub (first time may ask for credentials)
git push -u origin main
```

## Troubleshooting

### If you get "fatal: not a git repository" error:
- Make sure you're in the correct directory: `cd c:\Users\DELL\Downloads\corporate_messenger\corporate_messenger`
- Run `git init` first (even if it says already exists)

### If you get authentication errors:
- First push may ask for GitHub username and password
- This is normal - GitHub will guide you through the process
- Use GitHub Desktop as an alternative if command line gives issues

### Verify Repository
After successful push:
1. Go to https://github.com/dinesh34318/corporate-messenger
2. Check that all files are visible
3. Verify the README.md displays correctly

The corrected URL removes the space that was causing the error.
