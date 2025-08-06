---
title: KB Command Mastery Guide
permalink: kb-mastery-guide
tags:
  - documentation
  - workflow
  - best-practices
  - productivity
---

# KB Command Mastery Guide
## Your Personal Playbook for Knowledge-Driven Development

> Transform your development workflow with strategic knowledge management

---

## 🎯 Core Philosophy

**"Write once, reference forever"**

Your knowledge base should be:
1. **Contextual** - Captures WHY, not just WHAT
2. **Searchable** - Found in seconds, not minutes
3. **Connected** - Ideas link to ideas
4. **Actionable** - Drives real work

---

## 📅 Daily Workflow Integration

### 🌅 Morning Startup Routine (5 mins)

```bash
# 1. Check what you were working on
/kb list 1                    # Yesterday's changes
/kb read solitude-dev-log     # Project status

# 2. Load context for today
/kb context "current task"    # Find related work
/kb search "TODO"            # Find pending items

# 3. Set intentions
/kb log "Today: Working on authentication flow"
```

### 💻 Active Development Flow

#### Before Starting a Feature
```bash
# 1. Check if similar work exists
/kb search "authentication"
/kb context "jwt"

# 2. Document your approach FIRST
/kb create "Authentication Refactor Plan"
# Edit the file with your design

# 3. Link to existing knowledge
/kb log "Starting auth refactor - see [[Authentication Refactor Plan]]"
```

#### During Debugging
```bash
# When you encounter an error
/kb search "TypeError"        # Has this happened before?

# When you find the solution
/kb log "Fixed: TypeError in JWT handler - missing null check on user.role"

# For complex bugs, create a dedicated note
/kb create "JWT Handler TypeError Investigation"
```

#### After Completing a Task
```bash
# Quick log for simple tasks
/kb log "Completed: User authentication flow with role-based access"

# For significant features
/kb create "Authentication Implementation Notes"
# Document: decisions, tradeoffs, gotchas
```

### 🌙 End of Day Wrap-up (5 mins)

```bash
# 1. Document progress
/kb log "Progress: Auth 80% complete, blockers: token refresh logic"

# 2. Update statistics
/kb stats today              # See today's activity

# 3. Sync everything
/kb sync "EOD: Authentication progress"

# 4. Plan tomorrow
/kb log "Tomorrow: Complete token refresh, start testing"
```

---

## 🎨 Knowledge Capture Patterns

### 1. The Decision Record Pattern

When making architectural decisions:

```bash
/kb create "ADR: Choosing PostgreSQL over MongoDB"
```

Template content:
```markdown
## Decision
We will use PostgreSQL for user data

## Context
- Need ACID compliance for financial data
- Team has PostgreSQL expertise
- Complex relational queries required

## Consequences
- Need migration strategy from MongoDB
- Must set up connection pooling
- Requires backup strategy

## Alternatives Considered
- MongoDB: Rejected due to eventual consistency
- DynamoDB: Too expensive at scale
```

### 2. The Bug Post-Mortem Pattern

After fixing significant bugs:

```bash
/kb create "Bug: Memory Leak in Worker Pool"
```

Template content:
```markdown
## Symptoms
- Memory usage growing over time
- Server crashes after 48 hours

## Root Cause
Worker threads not properly closed

## Solution
```javascript
// Added cleanup in finally block
finally {
  await worker.terminate();
}
```

## Prevention
- Add memory monitoring alerts
- Include resource cleanup in code reviews

## Time Impact
- 6 hours investigation
- 30 mins fix
```

### 3. The Learning Log Pattern

When learning new concepts:

```bash
/kb create "Learning: Temporal Workflows"
```

Document:
- Key concepts understood
- Code examples that worked
- Resources that helped
- Questions still open

### 4. The Project Status Pattern

Weekly project updates:

```bash
/kb create "Week 45: Solitude Status"
```

Include:
- Completed this week
- Blockers encountered
- Next week's goals
- Team dependencies

---

## 🔍 Search & Discovery Strategies

### Finding Solutions

```bash
# Broad to narrow approach
/kb search "error"           # Too broad
/kb search "JWT error"       # Better
/kb search "JWT expire"      # Specific

# Use context for exploration
/kb context "authentication"  # See all auth-related notes
```

### Building Context Before Work

```bash
# Before working on a module
/kb context "payment"         # Load all payment knowledge
/kb read payment-integration  # Read specific docs
/kb graph                    # See connections
```

### Knowledge Validation

```bash
# Weekly knowledge review
/kb stats week               # What was documented?
/kb graph stats             # How connected is knowledge?
/kb list 7                  # Review recent notes
```

---

## 💡 Power User Tips

### 1. Quick Capture Aliases

Add to your `.zshrc`:

```bash
# Super quick logging
alias kbl='/kb log'
alias kbs='/kb search'
alias kbc='/kb context'
alias kbr='/kb read'

# Project-specific shortcuts
alias kbsolitude='/kb read solitude && /kb context solitude'
```

### 2. Contextual Templates

Create templates for common notes:

```bash
# Create template
/kb create "TEMPLATE-Bug-Report"

# Use template
cp ~/DEV/knowledge-base/templates/TEMPLATE-Bug-Report.md \
   ~/DEV/knowledge-base/bugs/new-bug.md
```

### 3. Time-Based Queries

```bash
# Morning review
/kb list 1 | head -5         # Yesterday's top 5

# Weekly review  
/kb stats week               # Week statistics
/kb graph stats             # Connection health
```

### 4. Integration with Claude Code Commands

Combine with other commands:

```bash
# Analyze a file and document findings
/analyze @file.go
/kb log "Analyzed file.go - found N+1 query issue"

# After building a feature
/build component
/kb log "Built new payment component with Stripe integration"
```

---

## 📊 Metrics for Success

### Daily Metrics (Aim for these)
- **3+ logs per day** - Capture decisions and solutions
- **1+ search per day** - Reuse existing knowledge
- **1 sync per day** - Never lose work

### Weekly Metrics
- **5+ new notes** - Document significant work
- **10+ new connections** - Link related concepts
- **Graph density > 2.0** - Average connections per node

### Monthly Metrics
- **90% of bugs have notes** - Learn from every issue
- **All features documented** - Maintain context
- **Graph clusters < 3** - Everything connected

---

## 🚀 Advanced Workflows

### 1. The Pre-emptive Documentation Flow

**Document BEFORE coding:**

```bash
# Monday: Design
/kb create "API Design: User Management"
# Document endpoints, schemas, decisions

# Tuesday: Implement
/kb log "Implementing user API per design doc"
# Code follows documentation

# Wednesday: Update
/kb log "API complete - updated design doc with learnings"
```

### 2. The Knowledge-Driven Debugging Flow

```bash
# 1. Search for similar issues
/kb search "similar error message"

# 2. Create investigation note
/kb create "Debugging: Connection Pool Exhaustion"

# 3. Log each hypothesis
/kb log "Hypothesis 1: Connections not released - TESTED: False"
/kb log "Hypothesis 2: Pool size too small - TESTED: True"

# 4. Document solution
/kb log "SOLVED: Increased pool size to 20, added monitoring"
```

### 3. The Learning Sprint Flow

When learning new technology:

```bash
# Day 1: Overview
/kb create "Learning Sprint: Rust Basics"
/kb log "Completed Rust tutorial chapters 1-3"

# Day 2: Hands-on
/kb log "Built first Rust CLI tool - see repo"

# Day 3: Integration
/kb create "Integrating Rust with Go Services"

# Day 4: Reflection
/kb create "Rust vs Go: Comparison Notes"
```

---

## 🎯 Specific Patterns for Your Projects

### For Solitude Project

```bash
# Daily standup prep
/kb read solitude-dev-log
/kb search "blocker"
/kb log "Standup: Completed X, blocked on Y, next Z"

# Before adding new service
/kb context "microservices"
/kb create "Service: New Analytics Engine"

# After deployment
/kb log "Deployed to staging - version 1.2.3"
/kb create "Deployment Notes: v1.2.3"
```

### For Learning & Research

```bash
# Research session
/kb create "Research: Vector Databases Comparison"
/kb log "Compared Pinecone vs Weaviate - Weaviate wins"

# Tutorial progress
/kb log "Completed Temporal tutorial section 5"
/kb create "Temporal: Key Concepts Summary"
```

---

## 🔄 Maintenance Routines

### Daily (2 mins)
```bash
/kb sync                    # Backup everything
```

### Weekly (10 mins)
```bash
/kb graph stats            # Check connectivity
/kb stats week            # Review activity
/kb search "TODO"         # Update task list
```

### Monthly (30 mins)
```bash
# Clean up
/kb search "DEPRECATED"    # Find old content
/kb graph stats           # Identify orphans

# Analyze
/kb stats month           # Month in review
/kb context "learnings"   # What did I learn?

# Plan
/kb create "Month Retrospective"
```

---

## 🎁 Quick Wins

Start with these high-impact habits:

1. **The One-Line Log**
   - After EVERY task: `/kb log "what I just did"`
   - Takes 5 seconds, saves hours later

2. **The Morning Context**
   - Before coding: `/kb context "what I'm working on"`
   - Loads mental model instantly

3. **The Solution Capture**
   - After fixing bugs: `/kb log "FIXED: problem - solution"`
   - Never solve the same problem twice

4. **The Decision Document**
   - Before big changes: `/kb create "Decision: X vs Y"`
   - Justify once, reference forever

5. **The Daily Sync**
   - End of day: `/kb sync`
   - Never lose work

---

## ⚡ Emergency Commands

When you need to:

**Find something fast:**
```bash
/kb search "error message"
/kb context "topic"
```

**Document quickly:**
```bash
/kb log "Quick note about what happened"
```

**See everything:**
```bash
/kb graph              # Visual overview
/kb stats             # Numbers
/kb list              # Recent activity
```

**Share knowledge:**
```bash
/kb read project-name  # Show to colleague
/kb sync              # Push to git
```

---

## 💭 Philosophy: Why This Works

1. **Offload Memory** - Your brain for thinking, KB for remembering
2. **Compound Learning** - Every solution builds on previous ones
3. **Contextual Switching** - Load entire mental models instantly
4. **Team Knowledge** - Your notes help future you AND your team
5. **Searchable Experience** - Turn experience into queryable data

---

## 🏆 Success Story Template

After 30 days of using this system:
- Found solutions to 80% of "new" problems in KB
- Reduced debugging time by 40%
- Never lost important decisions or context
- Onboarded new team member in hours, not days
- Built personal competitive advantage

---

## Relations

- implements [[KB Command Enhancement]]
- enhances [[Claude Code Setup]]
- documents [[Basic Memory]]
- supports [[Solitude Project]]
- improves [[Development Workflow]]

## Next Actions

- [todo] Print quick reference card
- [todo] Set up daily reminder for EOD sync
- [todo] Create project-specific templates
- [todo] Schedule weekly graph review
- [todo] Share with team
