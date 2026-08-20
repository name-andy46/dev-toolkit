# Contributing

## Layout

```
.claude-plugin/marketplace.json   # the marketplace manifest — lists every plugin
plugins/<plugin>/
├── .claude-plugin/plugin.json    # the plugin manifest
├── README.md                     # what the plugin does, its skills, its env vars
├── skills/<skill>/SKILL.md       # one directory per skill
├── commands/                     # optional slash commands
├── hooks/                        # optional hooks
├── scripts/ references/ assets/  # optional supporting files
scripts/scan.sh                   # secret / private-identifier scanner
```

One plugin can hold many skills. Group skills by the job they serve, not by who wrote them.

## Adding a plugin

1. Create `plugins/<plugin>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<plugin>",
     "version": "1.0.0",
     "description": "One line — what it does, for whom.",
     "author": { "name": "..." }
   }
   ```

2. Add the matching entry to `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "<plugin>",
     "version": "1.0.0",
     "source": "./plugins/<plugin>",
     "description": "Same description as plugin.json."
   }
   ```

3. Write `plugins/<plugin>/README.md` — skills table, trigger phrases, required env vars.
4. Add the plugin to the table in the root `README.md`.

**Keep `version` in both files, in sync.** `claude plugin validate . --strict` warns when a
`plugin.json` has no version, and `claude plugin tag` refuses to cut a release tag when the
plugin manifest and the marketplace entry disagree.

Stick to fields the validator recognizes — `--strict` treats unknown keys as errors.

## Versioning

Semver, per plugin. Patch for wording and fixes, minor for a new skill or a new capability in an
existing skill, major for renaming or removing a skill (that breaks anyone's muscle memory and
any cross-skill references).

## No environment-specific values

Nothing in this repo may name a private company, person, host, account, cloud id, database,
repository, or ticket project. Where a skill needs such a value:

- read it from an **environment variable** in `UPPER_SNAKE_CASE`, and
- document it in the plugin's README (name, what it's for, how to find it), and
- fail with a clear message telling the user which variable to set — never guess, never fall back
  to a value that happened to work for the author.

In prose and examples, use obvious placeholders: `YOUR_CLOUD_ID`, `your-workspace`,
`/path/to/your/notes`.

## Before you commit

```bash
python3 scripts/check-manifests.py   # manifests agree with each other and with plugins/
bash scripts/scan.sh                 # no secrets or private identifiers
claude plugin validate . --strict    # the runtime's own schema check
```

The first two run in CI on every push and pull request — they're dependency-free and need no
credentials. `claude plugin validate` needs the Claude Code CLI, so it stays a local step.

Private identifiers specific to your own employer or hosts belong in an untracked `.scan-local`
denylist (one `label|regex` per line), not in `scripts/scan.sh` — writing them into a tracked file
would publish the very strings you're trying to keep out.

## Testing a change locally

Point a marketplace at your working copy, install from it, and start a fresh session:

```bash
claude plugin marketplace add /absolute/path/to/this/checkout
claude plugin install <plugin>@dev-toolkit
```

Then exercise the skill the way a user would — say the trigger phrase in a scratch project and
check that it actually fires, not just that the files parse.
