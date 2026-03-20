---
name: deepcontentskill23223
description: |
  AI content marketing pipeline. Generate branded LinkedIn, X, and Reddit posts from any URL.
  Trigger on: "make a post from this", "turn this into content", "generate content", "/dc", "deepcontent", any URL the user wants turned into social posts.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: []
      env:
        - DEEPCONTENT_API_KEY
    primaryEnv: DEEPCONTENT_API_KEY
    emoji: "\U0001F4DD"
    homepage: https://deepcontent-frontend.scaleintelligence.workers.dev
allowed-tools:
  - Bash
  - AskUserQuestion
---

# DeepContent

Generate branded social media posts from any URL. One source in, LinkedIn + X + Reddit posts out.

## Docs

API reference and guides: https://deepcontent-api.scaleintelligence.workers.dev/api/docs
OpenAPI spec: https://deepcontent-api.scaleintelligence.workers.dev/api/docs/openapi.json
Dashboard: https://deepcontent-frontend.scaleintelligence.workers.dev/dashboard

## Config

- `DEEPCONTENT_API_KEY`: Bearer token (dc_*). Obtained via device auth flow. Stored in session memory only (not persisted to disk). If missing, run device auth.
- `DEEPCONTENT_API_URL`: defaults to `https://deepcontent-api.scaleintelligence.workers.dev`
- `DEEPCONTENT_FRONTEND_URL`: defaults to `https://deepcontent-frontend.scaleintelligence.workers.dev`

## When to use this skill

- User shares a URL and wants social posts
- User says "make a post", "generate content", "turn this into a LinkedIn post"
- User says "/dc" followed by a URL
- User asks about their brands, credits, or content history

## Flows

### First time (no API key)

1. `POST /api/v1/connect/init` (no auth) to get a device code
2. Show the user the connect URL: `{FRONTEND_URL}/connect/{code}`
3. Poll `GET /api/v1/connect/status/{code}` until completed
4. Store the returned api_key for the session
5. If user needs to sign up first: `{FRONTEND_URL}/sign-up`

### Generate content

1. `GET /api/v1/brands` to find the user's brand
2. If no brand, guide them to create one first. Link: `{FRONTEND_URL}/dashboard/brands/onboarding`
3. `POST /api/v1/linkedin/generate` with `{url, brand_graph_id}` (SSE)
4. Same for `/api/v1/reddit/generate` and `/api/v1/x/generate`
5. Show each post with platform name and content preview
6. Link to view/edit: `{FRONTEND_URL}/dashboard/history`
7. Show credits from `GET /api/v1/billing/balance`. Link to top up: `{FRONTEND_URL}/dashboard/billing`

### Create a brand

1. `POST /api/v1/brand-onboarding/generate` with `{name, source}` where source is a URL or description
2. Response includes brand identity (name, industry, description, positioning, audience, voice). Show a summary:
   - Name and industry
   - One-line description
   - Target audience
   - Voice/tone
   - Edit link: `{FRONTEND_URL}/dashboard/brands/{id}`
3. Ask which platforms (linkedin, x, reddit)
4. Tell user they can review and edit the full brand graph at the link

### List brands

1. `GET /api/v1/brands`
2. Show each brand name and industry
3. Link to manage: `{FRONTEND_URL}/dashboard/brands`

### Invite a team member

1. `POST /api/v1/orgs/{orgId}/invite` with `{email, role}` where role is "admin", "member", or "viewer"
2. Confirm: "{email} invited as {role}. They'll get an email to join."
3. Link to manage team: `{FRONTEND_URL}/dashboard/settings`

### Scrape a URL

When user just wants to see what's on a page (not generate content):
1. `POST /api/v1/scrape/detect` with `{url}`
2. Show a summary of what was extracted

### Help

When the user is lost, show what they can do:
- Generate content: share a URL
- Create a brand: "create a brand from [url or description]"
- List brands: "show my brands"
- Check status: "how many credits do I have"
- Invite someone: "invite john@example.com as a member"
- Dashboard: `{FRONTEND_URL}/dashboard`

### Status

1. Credits from `GET /api/v1/billing/balance`. Link: `{FRONTEND_URL}/dashboard/billing`
2. Brand count from `GET /api/v1/brands`. Link: `{FRONTEND_URL}/dashboard/brands`
3. Dashboard: `{FRONTEND_URL}/dashboard`

## Response style

- Lead with the generated content, not explanations
- Show each platform as a section header
- Keep previews to 300 chars in Discord
- Always end with the dashboard link and credit count
- No celebrations, no exclamation marks
