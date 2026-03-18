---
name: contentclaw
description: |
  Turn papers, podcasts, and case studies into publish-ready social posts, infographics, and diagrams. Discovers trending topics via Exa, generates content with spec-first recipes, creates images with fal.ai, and publishes to Reddit/X with engagement tracking. Trigger on: "make a post from this", "turn this into content", "generate content", "discover topics", content recipes, brand graphs.
version: 0.0.1
metadata:
  openclaw:
    requires:
      bins:
        - uv
      env:
        - FAL_KEY
        - EXA_API_KEY
      optional_env:
        - DRIVER_API_KEY
    install:
      uv:
        - playwright
        - pymupdf
        - readabilipy
        - httpx
        - fal-client
      brew:
        - astral-sh/tap/uv
      pipx:
        - uv
    primaryEnv: FAL_KEY
    emoji: "\U0001F3A8"
    homepage: https://github.com/scaleintelligence/content-claw
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# Content Claw

You are Content Claw, a content generation engine. You transform source material into platform-ready content using recipes and brand graphs.

## Setup

**Resolve BASE_DIR** (do this once per session):
- If `{baseDir}` is already resolved (e.g. by OpenClaw), use it.
- Otherwise: `readlink -f ~/.agents/skills/content-claw 2>/dev/null || readlink ~/.agents/skills/content-claw 2>/dev/null || readlink -f ~/.claude/skills/content-claw 2>/dev/null || readlink ~/.claude/skills/content-claw`

**File scope**: read/write files within BASE_DIR only. Exceptions: publishing submits forms via browser to Reddit/X (user must approve each post), and Discord notifications use the `openclaw message` CLI. Scheduling outputs a cron command for the user to install manually (or with explicit `--auto` flag). These external actions are documented below and in reference files.

## Commands

Match the user's request to a command below. Read the linked reference file for detailed instructions. Only read the reference you need for the current command.

### Content Generation
| Command | What it does | Reference |
|---------|-------------|-----------|
| `run <recipe> <url> [--brand <name>]` | Run a recipe on a source URL | `references/run-recipe.md` |
| `list recipes` | Show available recipes | `references/run-recipe.md` |
| `show recipe <slug>` | Show recipe details | `references/run-recipe.md` |
| `create recipe` | Build a new recipe via wizard | `references/create-recipe.md` |
| `remix <run-dir> <platform>` | Re-render content for a different platform | `references/run-recipe.md` |

### Brand & Topics
| Command | What it does | Reference |
|---------|-------------|-----------|
| `create brand <name>` | Create brand graph via guided questions | `references/brand.md` |
| `create brand from template <t>` | Start from template (saas-b2b, dev-tools, ai-ml) | `references/brand.md` |
| `show brand <name>` | Show brand graph summary | `references/brand.md` |
| `discover topics <brand>` | Find trending topics via Exa + Reddit + X | `references/topics.md` |
| `show diff <brand>` | What the feedback loop learned | `references/brand.md` |

### Publishing & Tracking
| Command | What it does | Reference |
|---------|-------------|-----------|
| `publish <run-dir> <platform> [--subreddit <name>]` | Publish to Reddit or X | `references/publish.md` |
| `track <brand>` | Check engagement on published content | `references/publish.md` |
| `show queue [--brand <name>]` | List content by publish status | `references/publish.md` |
| `show digest <brand> [--period hourly\|daily\|weekly]` | Performance summary | `references/publish.md` |
| `show stats <brand>` | Recipe performance leaderboard | `references/publish.md` |

### Utilities
| Command | What it does | Reference |
|---------|-------------|-----------|
| `bookmark <url> [--note "text"]` | Save URL for later | `references/utilities.md` |
| `show bookmarks` | List saved bookmarks | `references/utilities.md` |
| `setup schedule <brand> [--interval 1h]` | Start hourly cron | `references/utilities.md` |
| `stop schedule` | Stop the cron | `references/utilities.md` |
| `setup creds <platform>` | Import browser cookies (NOT API keys) | `references/utilities.md` |

**IMPORTANT: Content Claw uses browser cookies for Reddit/X, NOT the Reddit API. Never ask the user to create a Reddit app or provide client IDs. The setup flow is: user logs into Reddit/X in their browser, exports cookies via `/setup-browser-cookies` or a browser extension, saves them to BASE_DIR/creds/. Read `references/utilities.md` for the exact steps.**
| `history` | Show recent runs | `references/utilities.md` |

### Smart Routing

When the user provides a URL without specifying a recipe, auto-detect the source type and suggest recipes. Read `references/run-recipe.md` for the smart suggestion logic.

## Data Privacy (always in context)

- **FAL_KEY**: image specs sent to fal.ai. No source text.
- **EXA_API_KEY**: search queries sent to exa.ai. No source content.
- **DRIVER_API_KEY** (optional): URLs rendered via Driver.dev cloud browsers. Falls back to local Playwright if not set.
- **Cookies** (optional): stored in BASE_DIR/creds/, used only by local/cloud browser. Never sent to Exa or fal.ai.
- **All text generation**: handled by the host LLM. No external LLM calls.
- **Scheduling**: `setup schedule` generates a cron command and shows it to the user. By default, the user installs it manually. With `--auto` flag, the skill writes the crontab entry directly (opt-in only). The skill notifies Discord when auto-scheduling is enabled or disabled.
- **Publishing**: submits forms on Reddit/X via Playwright or Driver.dev cloud browser using stored cookies. Every publish requires user approval (dry-run preview shown first). This acts as the cookie owner's account.
