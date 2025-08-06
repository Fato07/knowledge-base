---
title: Claude Code Setup
permalink: claude-code-setup
tags:
  - configuration
  - development-tools
  - mcp
---

# Claude Code Setup

## Observations

- [configuration] Claude Code uses hierarchical settings with user, project, and enterprise levels
- [tool] Basic Memory MCP server installed via uvx for persistent knowledge management
- [preference] Auto-formatting enabled for JS/TS (Prettier), Python (Black), Go (gofmt), Rust (rustfmt)
- [security] Dangerous operations blocked: sudo, rm -rf /*, SSH key modifications
- [permission] Curl, grep, find commands globally allowed for development flexibility
- [integration] MCP tools include sequential-thinking, filesystem operations, and firecrawl
- [hook] Command logging tracks all bash executions to ~/.claude/command_log.jsonl
- [hook] Auto-git-add stages modified files after edits
- [notification] macOS notifications with sound enabled for attention requests
- [performance] 30-second timeout for long-running operations
- [storage] Knowledge base located at ~/DEV/knowledge-base
- [sync] Real-time sync between Markdown files and knowledge graph
- [setup_date] Configuration completed on 2025-08-06

## Relations

- uses [[Basic Memory]]
- configures [[MCP Servers]]
- integrates_with [[Obsidian]]
- depends_on [[Node.js]]
- manages [[Development Environment]]
- relates_to [[Claude Desktop]]

## Configuration Files

- [location] User settings: ~/.claude/settings.json
- [location] Project settings: .claude/settings.json
- [location] Claude Desktop config: ~/Library/Application Support/Claude/claude_desktop_config.json

## Key Commands

- [command] `claude config list` - View all settings
- [command] `claude config set -g <key> <value>` - Set global config
- [command] `/hooks` - Manage hook configurations
- [command] `/config` - Interactive configuration menu
- [command] `/terminal-setup` - Optimize terminal for Claude Code

## Next Steps

- [todo] Test Basic Memory integration with Claude Desktop
- [todo] Create knowledge templates for common project types
- [todo] Set up Obsidian for visual graph navigation
- [todo] Configure git backup for knowledge base
- [todo] Document current active projects in knowledge base
