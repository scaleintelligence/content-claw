# Topic Discovery

## Discover topics

Run: `cd BASE_DIR && uv run scripts/discover_topics.py BASE_DIR/brand-graphs/<brand>/ [--reddit-cookie BASE_DIR/creds/reddit-cookies.json] [--x-cookie BASE_DIR/creds/x-cookies.json]`

The script searches:
- **Exa** (always): trending news, launches, insights. Needs EXA_API_KEY.
- **Reddit** (always, better with cookies): hot discussions from past week.
- **X** (only with cookies): trending conversations.

Output JSON has: topic_count, topics (each with title, url, source, summary, relevance_score 0-100).

Present as a table: title, source, score, URL.

Ask: "Want me to run a recipe on any? Pick a number or 'all' for top 5."

Suggest recipes by source:
- Exa news: paper-breakdown-insight, what-you-might-have-missed
- Reddit: reddit-short-case-study
- X: paper-breakdown-insight
- GitHub: demo-diagram-breakdown

Save results to `BASE_DIR/topics/<date>_<brand>.json`.
