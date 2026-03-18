# Utilities

## Bookmarks

- Add: `cd BASE_DIR && uv run scripts/bookmark.py add <url> [--note "text"]`
- List: `cd BASE_DIR && uv run scripts/bookmark.py list`
- Remove: `cd BASE_DIR && uv run scripts/bookmark.py remove <url>`
- When running a recipe on a bookmarked URL, mark it as used

## Scheduled discovery

### Setup
`cd BASE_DIR && uv run scripts/schedule.py setup BASE_DIR/brand-graphs/<brand>/ --interval <1h|30m|etc>`

Writes a crontab entry. Each cycle: discovers topics, tracks engagement, checks alerts, sends summary to Discord #nemoclaw.

### Status
`cd BASE_DIR && uv run scripts/schedule.py status`

### Stop
`cd BASE_DIR && uv run scripts/schedule.py stop`

## Platform credentials

### Recommended: /setup-browser-cookies (gstack)
Tell user to run `/setup-browser-cookies`. Opens picker UI, user selects browser, imports cookies for reddit.com and x.com automatically.

### Manual fallback
1. Export cookies as JSON from browser DevTools or extension
2. Save to `BASE_DIR/creds/reddit-cookies.json` or `BASE_DIR/creds/x-cookies.json`
3. Format: `[{"name": "...", "value": "...", "domain": "...", "path": "/"}]`
4. Reddit needs: `reddit_session`, `token_v2`
5. X needs: `auth_token`, `ct0`

Cookies are gitignored and never sent to external services.

## History

Scan `BASE_DIR/content/` directories. Show recent runs with: date, recipe, brand, block count, publish status. Sort by most recent.

## Error handling

- Unreachable URL: tell user, ask for alternative
- Malformed recipe YAML: tell user which field is broken
- Failed prerequisite: report error, ask to continue with remaining steps
- Empty synthesis output: retry once, then show warning
- Never silently skip a step
