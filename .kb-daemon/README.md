# KB Daemon - Intelligent Knowledge Base Automation

## 🚀 Quick Start

```bash
# 1. Install
cd /Users/fathindosunmu/DEV/knowledge-base/.kb-daemon
python3 setup.py

# 2. Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH=$PATH:~/.local/bin

# 3. Install shell integration
~/.kb-daemon/install_shell.sh
source ~/.bashrc  # or ~/.zshrc

# 4. Test
kb-daemon test

# 5. Start daemon (shadow mode by default)
kb-daemon start
```

## 📋 Commands

- `kb-daemon start` - Start the daemon
- `kb-daemon stop` - Stop the daemon
- `kb-daemon status` - Check daemon status
- `kb-daemon review` - Run daily review
- `kb-daemon test` - Test configuration

## 🎯 What It Does

The KB Daemon automatically captures:

1. **Git Activity**
   - Commits with smart categorization
   - Branch switches and creations
   - Merges and external changes
   - PR reviews and integrations

2. **Shell Commands**
   - Important commands (npm, docker, etc.)
   - Error patterns and fixes
   - Long-running operations
   - Project switches

3. **File Changes**
   - Code creation and modifications
   - Test file changes
   - Configuration updates
   - Documentation changes

4. **Patterns**
   - Debugging sessions
   - Feature development
   - Test-driven development
   - Learning sessions

## 🔧 Configuration

Edit `~/.kb-daemon/config/settings.yml` to customize:

- Which commands to track
- Importance thresholds
- Processing intervals
- Privacy settings

## 🌟 Shadow Mode

The daemon starts in **shadow mode** by default:
- Captures everything
- Doesn't interrupt you
- Logs to `~/.kb-daemon/logs/shadow_*.json`
- Review captured data with `kb-daemon review`

## 📊 Daily Review

Run `kb-daemon review` to:
- See summary of activities
- Approve/edit KB entries
- Skip unimportant items
- Auto-generate documentation

## 🔒 Privacy

- 100% local processing
- Sensitive data filtered
- No external services (unless configured)
- Complete control over your data

## 🐛 Troubleshooting

### Daemon won't start
```bash
# Check Python packages
pip install pyyaml watchdog

# Check permissions
chmod +x ~/.kb-daemon/kb_daemon.py
```

### Shell commands not captured
```bash
# Reinstall shell integration
~/.kb-daemon/install_shell.sh
source ~/.bashrc
```

### Git hooks not working
```bash
# Check git config
git config --global init.templatedir

# Reinstall hooks
python3 -c "from capture.git_hooks import GitHooks; GitHooks(None, {}).install_hooks()"
```

## 📈 Phase 1 Status

✅ Completed:
- Core daemon infrastructure
- Git hooks integration
- Shell command capture
- File watching system
- Activity categorization
- Event summarization
- Database storage
- CLI review interface

🚧 Next Steps (Phase 2):
- Claude API integration for better summaries
- Real-time dashboard
- Team knowledge sync
- Advanced pattern detection

## 📝 Notes

This is Phase 1 of the KB Intelligence System. It provides:
- 50% automation of knowledge capture
- Zero-friction operation
- Daily review workflow
- Foundation for future enhancements

The system is designed to grow with you, learning your patterns and becoming more intelligent over time.
