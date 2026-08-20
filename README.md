# dev-toolkit

A [Claude Code](https://claude.com/claude-code) plugin marketplace: reusable skills, commands, and
hooks for everyday software work — spec-driven change workflows, service knowledge bases, AWS
operations, git guardrails, note-taking, and command-line drills.

This repo is a *pure marketplace*. It contains nothing but plugins and the manifest that lists
them — no application code, no container images, no infrastructure.

## Install

In a Claude Code session:

```
/plugin marketplace add YOUR_GITHUB_USER/dev-toolkit
/plugin install <plugin-name>@dev-toolkit
```

Or from your shell:

```bash
claude plugin marketplace add YOUR_GITHUB_USER/dev-toolkit
claude plugin install <plugin-name>@dev-toolkit
```

Restart the session (or start a new one) after installing so the plugin's skills load.

## What's inside

| Plugin | What it gives you |
| --- | --- |
| [`cli-tools-drill`](plugins/cli-tools-drill) | Practice drills for the Unix text-processing toolkit — `grep`, `sed`, `awk`, `find`/`xargs`, coreutils. Poses one real problem from your own repo and checks your answer instead of running the command for you. |

Each plugin has its own `README.md` describing its skills, when they trigger, and any
configuration it expects.

## Configuration

Plugins here never hardcode anything specific to one company, host, or account. Where a skill
needs an environment-specific value, it reads an **environment variable** and documents it in the
plugin's README. Set them once in your user settings, `~/.claude/settings.json`:

```json
{
  "env": {
    "NOTES_PATH": "/absolute/path/to/your/notes",
    "ATLASSIAN_CLOUD_ID": "your-atlassian-site-id",
    "BITBUCKET_WORKSPACE": "your-workspace-slug"
  }
}
```

Anything a skill can't infer and can't default sensibly, it asks you for rather than guessing.
Values shown as `YOUR_...` in docs are placeholders — replace them, don't commit them.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the repo layout, the plugin manifest conventions, and
the checks that run in CI.

## License

[MIT](LICENSE). Provided as-is, with no warranty — read a skill before you let it run against
anything you care about.
