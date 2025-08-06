# Claude Code + Claude Desktop + Basic Memory
## Complete Configuration Guide

## 🎯 What's Configured Where

### 1. **Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`)
- ✅ All MCP servers (GitHub, Brave Search, Memory, Puppeteer, Sequential Thinking, Basic Memory)
- ✅ Secure wrapper for environment variables
- ✅ Basic Memory with knowledge base path

### 2. **Claude Code** (`~/.claude/settings.json`)
- ✅ Permissions for all MCP tools including Basic Memory
- ✅ Basic Memory MCP server configuration
- ✅ Hooks for logging, formatting, notifications
- ✅ Environment variables for performance

### 3. **Project-Specific Claude Code** (`<project>/.claude/settings.json`)
- ✅ Project-specific permissions
- ✅ Project environment variables
- ✅ Custom tool permissions

## 📁 File Structure

```
~/.claude/                              # Claude Code configuration
├── settings.json                       # Global Claude Code settings
├── .env.secret                         # Secure API keys
├── mcp-secure-wrapper.sh               # Environment loader
├── validate-system.sh                  # System health check
├── command_log.jsonl                   # Command history (created on use)
└── test-env.sh                         # Environment tester

~/Library/Application Support/Claude/   # Claude Desktop configuration
└── claude_desktop_config.json          # MCP server configurations

~/DEV/knowledge-base/                   # Basic Memory knowledge base
├── projects/                           # Project documentation
├── architecture/                       # System designs
├── tools/                             # Tool configurations
├── learning/                          # Learning notes
├── people/                           # Contacts
└── daily/                             # Daily logs

~/DEV/MyProjects/solitude/.claude/      # Project-specific Claude Code
└── settings.json                       # Solitude-specific settings
```

## 🔧 How Basic Memory Works

### In Claude Desktop:
1. MCP server runs via `uvx basic-memory mcp`
2. Creates/reads markdown files in `~/DEV/knowledge-base`
3. Maintains SQLite index for searching
4. Real-time sync between files and memory

### In Claude Code:
1. Same MCP server configuration
2. Additional hooks capture development activities
3. Auto-documents code changes
4. Integrates with git workflow

## 🚀 Usage Examples

### Claude Desktop Commands:
```
"Create a note about our authentication system"
"What do I know about the Solitude project?"
"Build context about Temporal workflows"
"Search for all database-related notes"
```

### Claude Code Commands:
```
/chat What's the architecture of this project?
/chat Document this function in our knowledge base
/chat Find similar patterns we've used before
/chat Update the development log with today's progress
```

## 🔄 Synchronization

Both Claude Desktop and Claude Code:
- Use the SAME knowledge base (`~/DEV/knowledge-base`)
- Share the SAME Basic Memory instance
- Can read/write to the SAME notes
- Build on each other's context

## ✅ Verification Commands

```bash
# Check Claude Code configuration
cat ~/.claude/settings.json | jq '.mcpServers'

# Check Claude Desktop configuration  
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq '.mcpServers."basic-memory"'

# Test Basic Memory directly
uvx basic-memory mcp --base-path ~/DEV/knowledge-base

# Validate entire system
~/.claude/validate-system.sh
```

## 🎯 Key Benefits

1. **Unified Knowledge**: Same knowledge base across all Claude interfaces
2. **Project Context**: Never lose context between sessions
3. **Code Intelligence**: Claude Code understands your entire codebase
4. **Cross-Tool Memory**: Desktop discoveries available in Code and vice versa
5. **Git Integration**: Knowledge base can be versioned and shared

## 🔐 Security Features

- API keys in `.env.secret` (never in configs)
- Secure wrapper loads environment variables
- File permissions 600 on sensitive files
- .gitignore prevents accidental commits
- Dangerous operations blocked by permissions

## 📊 What Gets Captured

### Automatically Logged:
- All bash commands with timestamps
- File modifications and locations
- Test results and outcomes
- Sequential thinking processes

### Manually Created:
- Project documentation
- Architecture decisions
- Bug solutions
- Learning notes

## 🎪 Advanced Features

### Knowledge Graph Navigation:
- Relations between entities
- Semantic search across notes
- Context building from multiple sources
- Memory URLs for direct references

### Workflow Integration:
- Pre-commit hooks can update notes
- CI/CD can read project context
- Team members can share knowledge base
- Obsidian provides visual graph

## 💡 Pro Tips

1. **Start each session**: "What did I work on last time?"
2. **Before debugging**: "Find similar issues we've solved"
3. **After solving**: "Document this solution for future"
4. **Project planning**: "Build context about our architecture"
5. **Code review**: "What patterns have we established?"

## 🚨 Troubleshooting

If Basic Memory isn't working:

1. **In Claude Desktop**: Restart the app
2. **In Claude Code**: Run `claude restart`
3. **Check MCP server**: `ps aux | grep basic-memory`
4. **View logs**: Check `~/DEV/knowledge-base/.basic-memory/`
5. **Validate setup**: `~/.claude/validate-system.sh`

## 🎉 You're All Set!

Your Claude Code AND Claude Desktop are now:
- ✅ Fully integrated with Basic Memory
- ✅ Sharing the same knowledge base
- ✅ Configured with all security best practices
- ✅ Ready for production development

The most sophisticated AI-assisted development environment possible! 🚀
