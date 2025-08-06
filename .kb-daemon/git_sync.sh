#!/bin/bash
# KB Git Sync - Smart commit and push for knowledge base

echo "======================================"
echo "📚 KB Git Sync"
echo "======================================"

cd /Users/fathindosunmu/DEV/knowledge-base

# Check git status
if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo ""
    echo "📝 Changes detected:"
    echo ""
    
    # Show what's new
    NEW_FILES=$(git ls-files --others --exclude-standard | grep -E "\.(md|txt)$" | head -10)
    MODIFIED_FILES=$(git diff --name-only | grep -E "\.(md|txt)$" | head -10)
    
    if [ -n "$NEW_FILES" ]; then
        echo "New KB entries:"
        echo "$NEW_FILES" | while read -r file; do
            echo "  + $file"
        done
    fi
    
    if [ -n "$MODIFIED_FILES" ]; then
        echo "Modified entries:"
        echo "$MODIFIED_FILES" | while read -r file; do
            echo "  ~ $file"
        done
    fi
    
    # Count changes
    NEW_COUNT=$(git ls-files --others --exclude-standard | grep -E "\.(md|txt)$" | wc -l | tr -d ' ')
    MOD_COUNT=$(git diff --name-only | grep -E "\.(md|txt)$" | wc -l | tr -d ' ')
    
    echo ""
    echo "📊 Summary: $NEW_COUNT new, $MOD_COUNT modified"
    echo ""
    
    # Generate commit message
    DATE=$(date +"%Y-%m-%d")
    if [ "$NEW_COUNT" -gt 0 ] && [ "$MOD_COUNT" -gt 0 ]; then
        DEFAULT_MSG="KB Update $DATE: $NEW_COUNT new entries, $MOD_COUNT updates"
    elif [ "$NEW_COUNT" -gt 0 ]; then
        DEFAULT_MSG="KB Update $DATE: Added $NEW_COUNT new entries"
    elif [ "$MOD_COUNT" -gt 0 ]; then
        DEFAULT_MSG="KB Update $DATE: Updated $MOD_COUNT entries"
    else
        DEFAULT_MSG="KB Update $DATE"
    fi
    
    # Ask for commit message
    echo "Commit message (Enter for default):"
    echo "[$DEFAULT_MSG]"
    read -r CUSTOM_MSG
    
    if [ -z "$CUSTOM_MSG" ]; then
        COMMIT_MSG="$DEFAULT_MSG"
    else
        COMMIT_MSG="$CUSTOM_MSG"
    fi
    
    # Stage changes
    echo ""
    echo "🔄 Staging changes..."
    
    # Add all markdown files
    git add "*.md"
    
    # Add daemon code changes (but not data)
    git add .kb-daemon/*.py
    git add .kb-daemon/*.sh
    git add .kb-daemon/config/
    git add .kb-daemon/capture/*.py
    git add .kb-daemon/process/*.py
    git add .kb-daemon/storage/*.py
    git add .kb-daemon/interface/*.py
    git add .kb-daemon/README.md
    git add .kb-daemon/.gitignore
    
    # Add other KB files
    git add .gitignore
    git add "*.toml"
    
    # Commit
    echo "💾 Committing..."
    git commit -m "$COMMIT_MSG"
    
    # Ask to push
    echo ""
    echo "Push to remote? [y/N]"
    read -r PUSH_CONFIRM
    
    if [ "$PUSH_CONFIRM" = "y" ] || [ "$PUSH_CONFIRM" = "Y" ]; then
        echo "⬆️  Pushing to remote..."
        git push
        echo "✅ Pushed successfully!"
    else
        echo "💡 Changes committed locally. Push later with: git push"
    fi
    
else
    echo "✨ No changes to commit"
fi

echo ""
echo "======================================"
echo "✅ Git sync complete!"
echo "======================================"
