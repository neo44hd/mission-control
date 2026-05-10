# Gentleman-Skills Installation for OpenCode

## Source
- **Repository**: https://github.com/Gentleman-Programming/Gentleman-Skills.git
- **License**: MIT
- **Target directory**: `~/.config/opencode/skills/`

## Installation Steps
1. Clone the repository
2. Create the target directory (`mkdir -p ~/.config/opencode/skills/`)
3. Copy curated skills (`cp -r Gentleman-Skills/curated/* ~/.config/opencode/skills/`)
4. Remove the cloned repository

## Installed Skills (15)

### Frontend
- `angular` — Standalone components, signals, inject, zoneless
- `react-19` — React 19 patterns with React Compiler
- `nextjs-15` — Next.js 15 App Router patterns
- `typescript` — TypeScript strict patterns
- `tailwind-4` — Tailwind CSS 4 patterns
- `zod-4` — Zod 4 schema validation
- `zustand-5` — Zustand 5 state management

### Backend & AI
- `ai-sdk-5` — Vercel AI SDK 5 patterns
- `django-drf` — Django REST Framework patterns

### Testing
- `playwright` — Playwright E2E testing
- `pytest` — Python pytest patterns

### Workflow
- `github-pr` — Create quality PRs with conventional commits
- `jira-epic` — Jira epic creation
- `jira-task` — Jira task creation
- `skill-creator` — Create new AI agent skills

## Update Command
```bash
git clone https://github.com/Gentleman-Programming/Gentleman-Skills.git /tmp/Gentleman-Skills \
  && cp -r /tmp/Gentleman-Skills/curated/* ~/.config/opencode/skills/ \
  && rm -rf /tmp/Gentleman-Skills
```

## Installed On
2026-05-10
