# Content Claw - Project Rules

## ClawHub Security Scan Compliance

These rules exist to prevent the skill from being flagged as suspicious on ClawHub/NemoClaw security scans.

### Credential handling
- NEVER reference Reddit API, client IDs, client secrets, or OAuth tokens. Content Claw uses browser cookies only.
- NEVER ask users to create Reddit/X apps or register API keys for platforms. The only keys needed are FAL_KEY, EXA_API_KEY, and optionally DRIVER_API_KEY.
- All env loading must use the scoped loader in `scripts/env.py`. Only declared keys (FAL_KEY, EXA_API_KEY, DRIVER_API_KEY) are loaded. Never use a blanket env loader.
- Never hardcode credentials in source code, test files, or documentation. Use placeholders.

### File scope and system access
- SKILL.md must accurately declare ALL actions that touch anything outside BASE_DIR. If the skill writes crontab, sends network requests, or uses external CLIs, it must be documented in the Privacy section.
- Never claim "only reads/writes within BASE_DIR" if the skill also does network calls, crontab writes, or Discord notifications. Be explicit about every external action.
- System-level actions (crontab) must be opt-in. Default to outputting commands for the user to run manually. Only write crontab with explicit `--auto` flag.

### Consistency between SKILL.md and code
- Every env var in the `requires.env` metadata must be used in at least one script. Don't declare unused keys.
- Every env var marked as required must actually be required. Optional keys go in `optional_env`.
- The `install` block in SKILL.md must list all Python dependencies that appear in pyproject.toml.
- If a script loads cookies, the SKILL.md must document that cookies grant account-level access.

### Publishing safety
- Every publish action must show a dry-run preview first and ask for user confirmation.
- Never auto-publish without explicit user approval.
- Always document that publishing acts as the cookie owner's account.

### Privacy documentation
- Document every external service the skill communicates with: what data is sent, what is not.
- Be specific: "image specs (titles, headings)" not "some data."
- If using cloud browsers (Driver.dev), document that visited URLs are processed by the cloud provider.
- Stealth scraping (webdriver hiding) must be acknowledged in the privacy section.

## Coding Style

### Python scripts
- All scripts use the shared `scripts/env.py` for env loading and `scripts/browser.py` for Playwright/Driver.dev.
- Use `sys.path.insert(0, str(Path(__file__).parent))` at the top to enable `from env import load_env` and `from browser import create_browser`.
- All scripts output JSON to stdout for the host LLM to parse.
- Error output goes to stderr or as `{"error": "..."}` JSON.

### SKILL.md
- Keep under 200 lines. The Nemotron model on NemoClaw cannot follow instructions from files longer than this.
- Critical instructions (credentials, core commands, common flows) must be inline, not in reference files. Nemotron does not reliably read reference files.
- Only use `references/` for rarely-used wizard flows (create-recipe, brand graph creation).
- Match the style of built-in OpenClaw skills (github, clawhub, xurl): self-contained, concise, direct commands.

### Testing
- Tests go in `tests/`. Use pytest.
- Test pure functions directly. Mock Playwright for browser tests.
- Network-dependent tests must handle timeouts gracefully.

### Git and versioning
- ClawHub does not allow version reuse. Always increment.
- After pushing to GitHub, publish to ClawHub, then update VPS.
- VPS update: `clawhub install content-claw --force` then fix the nested `skills/skills/` path if it occurs.
