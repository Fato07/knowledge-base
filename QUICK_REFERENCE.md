# Basic Memory Quick Reference

## Essential Commands for Claude Desktop

### Writing Notes
- "Create a note about [topic]"
- "Write a note documenting [experience/learning]"
- "Add observations about [entity]"

### Reading & Searching
- "What do I know about [topic]?"
- "Search for [keyword] in my knowledge base"
- "Show me recent notes about [topic]"
- "Build context about [project/topic]"

### Managing Relations
- "Connect [topic A] to [topic B]"
- "What relates to [topic]?"
- "Show connections for [entity]"

### Activity & Review
- "What have I worked on recently?"
- "Show me today's notes"
- "Find all todos in my knowledge base"

## File Locations

- **Knowledge Base**: `~/DEV/knowledge-base/`
- **Claude Config**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Settings**: `~/.claude/settings.json`
- **Command Log**: `~/.claude/command_log.jsonl`

## Knowledge Structure

```
~/DEV/knowledge-base/
├── projects/       # Project documentation
├── learning/       # Learning notes
├── tools/         # Tool configurations
├── people/        # Contacts and collaborators
├── architecture/  # System designs
└── daily/         # Daily logs
```

## Observation Categories

- `[fact]` - Objective information
- `[preference]` - Personal preferences
- `[decision]` - Design decisions
- `[todo]` - Action items
- `[issue]` - Problems
- `[solution]` - Solutions
- `[resource]` - Links/references
- `[learning]` - Lessons learned
- `[experiment]` - Experimental findings

## Pro Tips

1. **Link Everything**: Use [[Entity Name]] to create connections
2. **Tag Consistently**: Use tags for easy searching
3. **Daily Reviews**: Ask "What did I work on today?" regularly
4. **Context Building**: Use "build context about X" before deep work
5. **Git Backup**: Commit your knowledge base daily

## Troubleshooting

If Basic Memory isn't working:
1. Restart Claude Desktop
2. Check if uvx is in PATH: `which uvx`
3. Test manually: `uvx basic-memory mcp --base-path ~/DEV/knowledge-base`
4. Check logs: `~/DEV/knowledge-base/.basic-memory/basic-memory.log`

## Integration with Obsidian

1. Open Obsidian
2. Open Folder as Vault → Select `~/DEV/knowledge-base`
3. Enable Graph View plugin
4. Use Cmd+O to quickly open notes
5. Use Cmd+Shift+F to search across all notes
