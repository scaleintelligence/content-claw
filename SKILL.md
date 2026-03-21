---
name: deepcontentskill23223
description: |
  AI content marketing pipeline. Generate branded LinkedIn, X, and Reddit posts from any URL.
  Trigger on: "make a post from this", "turn this into content", "generate content", "/dc",
  "deepcontent", any URL the user wants turned into social posts, "discover topics",
  "show my posts", "what should I write about".
version: 1.6.1
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
- User asks to discover topics or find content ideas
- User asks about their brands, credits, posts, or content history
- User wants to manage or review generated content

## Flows

### First time (no API key)

1. `POST /api/v1/connect/init` (no auth) to get a device code
2. Show the user the connect URL: `{FRONTEND_URL}/connect/{code}`
3. Poll `GET /api/v1/connect/status/{code}` until completed
4. Store the returned api_key for the session
5. If user needs to sign up first: `{FRONTEND_URL}/sign-up`

### Quick generate (single platform)

For "make me a LinkedIn post from this URL" type requests:
1. `GET /api/v1/brands` to resolve which brand to use:
   - No brands: guide them to create one first. Link: `{FRONTEND_URL}/dashboard/brands/onboarding`
   - One brand: use it automatically
   - Multiple brands: ask the user which one. Show names as options.
   - If user specified a brand by name, match it
3. `POST /api/v1/{platform}/generate` with `{url, brand_graph_id}` (SSE). Platform: linkedin, reddit, or x.
   - Reddit supports `{subreddit}` param for targeting a specific subreddit
   - X supports `{format: "thread"}` for multi-tweet threads instead of single posts
4. Show the post content
5. The SSE `done` event includes `post_id`. Build the link as EXACTLY `{FRONTEND_URL}/dashboard/posts/{post_id}`. NOT /dashboard/linkedin/, NOT /dashboard/reddit/, NOT /dashboard/x/. The path is always /dashboard/posts/.
6. Show credits from `GET /api/v1/billing/balance`. Link to top up: `{FRONTEND_URL}/dashboard/billing`

### Full synthesis (recipe-based, multi-block)

For richer content or when user wants multiple outputs from one source:
1. `GET /api/v1/recipe-graphs` to list available recipes. Show names so user can pick.
2. `POST /api/v1/enrichment/prepare` with `{recipe_graph_id, source_content, brand_graph_id?}` where source_content is the URL or text. Returns a synthesis request with an `id`.
3. `POST /api/v1/synthesis/run` with `{synthesis_request_id}` to kick off generation.
4. Poll `GET /api/v1/synthesis/status/{id}` until status is "completed".
5. Show the generated content blocks.
6. Link to: `{FRONTEND_URL}/dashboard/synthesis`

Use quick generate for simple "one post" requests. Use full synthesis when the user wants structured multi-block output, or asks to "run a recipe".

### Discover topics

When user asks "what should I write about" or "find me topics":
1. `GET /api/v1/brands` to resolve which brand (same logic as quick generate: one brand = auto, multiple = ask)
2. `POST /api/v1/topics/generate` with `{brand_graph_id}` (SSE). Discovers trending topics aligned with the brand. This endpoint scrapes multiple sources then runs Claude analysis, so it takes 60-120 seconds. Use `--max-time 180` if calling via curl.
3. Show topics with title, relevance, and source URL. Each topic has a `topic_id` in the SSE events.
4. Link each topic to: `{FRONTEND_URL}/dashboard/topics/{topic_id}`
5. Link to all topics: `{FRONTEND_URL}/dashboard/topics`
6. Ask: "Want me to generate content from any of these?"
7. If yes, feed the topic URL into quick generate or full synthesis

### Manage posts

When user asks to see, edit, or delete their content:
- List posts: `GET /api/v1/{platform}/posts` (platform: linkedin, reddit, x). Shows recent posts with status.
- Edit a post: `PATCH /api/v1/{platform}/posts/{id}` with `{body, title?}`
- Delete a post: `DELETE /api/v1/{platform}/posts/{id}`
- Link to manage all: `{FRONTEND_URL}/dashboard/linkedin` (or `/dashboard/reddit`, `/dashboard/x` depending on platform)

### Create a brand

1. First `GET /api/v1/brands` and check if a brand with a similar name or URL already exists. If it does, ask the user: "You already have a brand called {name}. Update it, or create a new one?"
   - Update: use `POST /api/v1/brands/{id}/refill` with `{source}` to refresh the existing brand
   - New: proceed with creation below
2. `POST /api/v1/brand-onboarding/generate` with `{name, source}` where source is a URL or description. This endpoint takes 30-60 seconds (scrapes + AI analysis). Use `--max-time 120` if calling via curl.
3. Response includes brand identity and an `id` (or `brand_graph_id`). Show a summary:
   - Name and industry
   - One-line description
   - Target audience
   - Voice/tone
4. ALWAYS include this link in the response: `{FRONTEND_URL}/dashboard/brands/{id}` (replace {id} with the actual brand ID). This is required, not optional.
5. Brand is created in "draft" status. Confirm with `POST /api/v1/brand-onboarding/{id}/confirm` to publish it.
6. Ask which platforms (linkedin, x, reddit)

### List brands

1. `GET /api/v1/brands`
2. Show each brand name and industry
3. Link to manage: `{FRONTEND_URL}/dashboard/brands`

### Invite a team member

1. Get the org ID from `GET /api/v1/auth/me` (returns `orgId` in the response).
2. `POST /api/v1/orgs/{orgId}/invite` with `{email, role}` where role is "admin", "member", or "viewer"
3. Confirm: "{email} invited as {role}. They'll get an email to join."
4. Link to manage team: `{FRONTEND_URL}/dashboard/settings`

### Scrape a URL

When user just wants to see what's on a page (not generate content):
1. `POST /api/v1/scrape/detect` with `{url}`
2. Show a summary of what was extracted

### Billing and upgrade

When user asks about credits, pricing, or upgrading:
1. `GET /api/v1/billing/balance` for current credits
2. `GET /api/v1/billing/plan` for current plan
3. To upgrade: link to `{FRONTEND_URL}/dashboard/billing`

### Help

When the user is lost, show what they can do:
- Generate content: share a URL
- Create a brand: "create a brand from [url or description]"
- Discover topics: "what should I write about"
- List brands: "show my brands"
- See posts: "show my recent posts"
- Check status: "how many credits do I have"
- Invite someone: "invite john@example.com as a member"
- Dashboard: `{FRONTEND_URL}/dashboard`

### Status

1. Credits from `GET /api/v1/billing/balance`. Link: `{FRONTEND_URL}/dashboard/billing`
2. Brand count from `GET /api/v1/brands`. Link: `{FRONTEND_URL}/dashboard/brands`
3. Dashboard: `{FRONTEND_URL}/dashboard`

## Learning from usage

### After content generation

After showing generated content, ask: "Want to edit anything before approving?"

If the user edits the post (changes wording, removes phrases, adjusts tone):
1. Note what they changed and why (if they explain)
2. Store the pattern as a memory: "For {brand}, user prefers {observation}. Example: changed '{original}' to '{edited}'."
3. On future generations for that brand, reference these memories to pre-apply the user's preferences

### Track preferences over time

Build a mental model of each user:
- Which platform they generate for most often
- Whether they approve posts as-is or always edit
- Common edits (removing emojis, shortening, adding hashtags, changing tone)
- Which brand they default to
- Time of day they're active

Use these to skip unnecessary questions. If a user always picks LinkedIn and always uses the same brand, don't ask every time.

### Brand voice refinement

When a user consistently edits generated content in the same way (e.g., always removes questions at the end, always adds a specific CTA), suggest updating the brand graph:

"I've noticed you always remove the closing question from LinkedIn posts. Want me to update the brand voice to skip those?"

If yes, `PATCH /api/v1/brands/{id}` to update the voice rules.

## Response style

- Lead with the generated content, not explanations
- Show each platform as a section header
- Keep previews to 300 chars in Discord
- Always end with the dashboard link and credit count
- No celebrations, no exclamation marks
