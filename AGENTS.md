# Codex Instructions for GeoAI

## Project Context

- Treat `/Users/rudy/Documents/Codex/2026-05-20-geoai` as the canonical GeoAI project directory.
- Read `PROJECT_CONTEXT.md` before making non-trivial project decisions.
- Keep `PROJECT_CONTEXT.md` current when the active route, important decisions, blockers, or next tasks change.
- Prefer the existing OMBRIA pilot structure unless Rudy explicitly changes direction.

## Research Integrity

- Do not fabricate data, experiments, citations, metrics, or paper claims.
- Do not promote pilot or sanity-check numbers into manuscript results without committed scripts/configs and auditable logs.
- Keep raw data, downloaded datasets, credentials, model checkpoints, and large generated outputs out of git.
- Verify time-sensitive journal, indexing, dependency, and cloud platform details before relying on them.

## Implementation Style

- Keep changes scoped to the current experiment or manuscript task.
- Prefer existing scripts, docs, and package layout over adding a new framework.
- Update docs alongside code when behavior, commands, assumptions, or project direction changes.

## GitHub Uploads

- Prefer SSH for pushing Rudy's local projects to GitHub.
- Check authentication with `ssh -T git@github.com`.
- Use `git@github.com:NewRudy/<repo>.git` remotes when the repository already exists.
- Avoid relying on `gh auth login` browser authentication as the first path; it can time out in this environment.
- Never expose, copy, or commit private SSH keys. Only public keys may be shown for GitHub Settings.
