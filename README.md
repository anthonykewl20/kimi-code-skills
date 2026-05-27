# Kimi Code Skills & Governance

Personal governance system, hooks, and skills for [Kimi Code CLI](https://github.com/moonshot-ai/Kimi-CLI).

## What's Inside

| Directory | Purpose |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Global behavioral guidelines — think-before-coding, simplicity-first, surgical changes, TDD hard gates, swarm stages |
| [`governance/`](governance/) | Defense-in-depth scanning engine (race conditions, concurrency, idempotency, dead code) |
| [`hooks/`](hooks/) | Pre/Post/SessionEnd hooks: gatekeeper, env protection, completion checks |
| [`skills/`](skills/) | 21 reusable skills (TDD, anti-patterns, diagnosis, architecture, etc.) |
| [`kimi-code-custom/`](kimi-code-custom/) | Custom skills, quick reference, and install helpers |
| [`config.toml`](config.toml) | Kimi Code configuration with portable `$HOME`-relative paths |

## Quick Start (new machine)

```bash
# Clone into ~/.kimi
git clone https://github.com/anthonykewl20/kimi-code-skills.git ~/.kimi

# Re-authenticate (tokens are NOT stored in this repo)
kimi login
```

Kimi Code will automatically pick up `config.toml` and the hooks on the next run.

## Security Note

This repo intentionally excludes all secrets and personal data:

- `credentials/` (OAuth tokens)
- `logs/`, `telemetry/`, `user-history/`, `sessions/`
- `device_id`, `kimi.json`, `mcp.json`

See [`.gitignore`](.gitignore) for the full exclusion list.

## License

Personal use. Modify freely for your own setup.
