# dev-toolkit

A [Claude Code](https://claude.com/claude-code) plugin marketplace: reusable skills, commands, and
hooks for everyday software work — spec-driven change workflows, service knowledge bases, AWS
operations, git guardrails, note-taking, and command-line drills.

This repo is a *pure marketplace*. It contains nothing but plugins and the manifest that lists
them — no application code, no container images, no infrastructure.

## Start here

Never used Claude Code before? This section assumes nothing. If you already use it, skip to
[Install](#install).

**1. Install Claude Code and sign in.** Follow the official instructions at
[claude.com/claude-code](https://claude.com/claude-code). When it's working, you can open a
terminal, type `claude`, press Enter, and get a prompt that talks back.

**2. Open a terminal in a folder you want to work in.** Claude Code always runs *somewhere* — the
folder you start it from is what it can see and change. For note-taking, any folder is fine; for
working on code, start it inside that project's folder.

**3. Start Claude Code and add this collection.** Type `claude`, press Enter, then type:

```
/plugin marketplace add name-andy46/dev-toolkit
```

A *marketplace* is just a list of available add-ons. Adding it downloads nothing but the list.

**4. Install the ones you want.** [Which ones do I want?](#which-ones-do-i-want) matches them to what
you're actually doing. For example:

```
/plugin install spec-workflow@dev-toolkit
/plugin install git-guardrails@dev-toolkit
```

The part after `@` says which marketplace it came from. Installing several is fine — see
[What's inside](#whats-inside) for the full list.

**5. Restart.** Type `/exit`, then run `claude` again. New skills only load when a session starts,
so this step isn't optional — skipping it is the single most common reason nothing seems to happen.

**6. Just ask for what you want, in plain English.** You don't run these add-ons by name or
remember any commands. Each one describes the situations it's for, and Claude picks it up when
your request matches. For notes, try:

> create today's note

or

> what did I work on this week?

Each plugin's own page (linked in the table below) lists the kinds of phrases it responds to.

### If something doesn't work

| What you see | What to do |
| --- | --- |
| `claude: command not found` | Claude Code isn't installed yet — back to step 1. |
| Nothing happens when you ask | You probably skipped step 5. Restart the session. |
| "unknown plugin" on install | Check the marketplace was added: type `/plugin` to see what's available. |
| You want to see what's installed | Type `/plugin`, or run `claude plugin list` in a terminal. |
| You want to remove one | `/plugin uninstall <name>@dev-toolkit` |

## Install

The short version, in a Claude Code session:

```
/plugin marketplace add name-andy46/dev-toolkit
/plugin install <plugin-name>@dev-toolkit
```

Or from your shell:

```bash
claude plugin marketplace add name-andy46/dev-toolkit
claude plugin install <plugin-name>@dev-toolkit
```

Restart the session (or start a new one) after installing so the plugin's skills load.

## Which ones do I want?

Find the row that sounds like you. Installing several is normal — they don't overlap or interfere,
and each one only wakes up when what you're asking for matches it.

| If you're… | Install | Why |
| --- | --- | --- |
| **building an app or tool with Claude** and can't review the code yourself | `spec-workflow` + `git-guardrails` | Write down what it should do in sentences you *can* check, then keep Claude from losing your work while it builds |
| **analysing markets in Python** — screeners, indicators, technical analysis | `market-analysis` | Catches the data and indicator faults that make results look better than they are |
| doing both of the above | all three | Define what the screener should do, then check that it actually does it |
| **keeping track of your work** — what you did, what's next, what was decided | `notes-workflow` | Daily logs and a task list Claude maintains for you, in plain markdown you own |
| letting Claude run **git** on a repo you care about | `git-guardrails` | Blocks the handful of commands that destroy work irreversibly, and blocks pushing a leaked API key |
| wanting to **learn the command line** properly | `cli-tools-drill` | Hands you one real exercise at a time. Needs macOS, Linux, WSL or Git Bash — not PowerShell |

**Not sure?** `spec-workflow` and `git-guardrails` are the two that pay off regardless of what you're
building. Then say *"walk me through the spec workflow"* and it teaches itself on your own project.

## What's inside

| Plugin | What it gives you |
| --- | --- |
| [`market-analysis`](plugins/market-analysis) | For people who analyse markets with Python but don't read Python: audits technical-analysis and stock-screening code for the data, indicator, and screener faults that make results look cleaner than reality — and explains what it found in terms of the result, not the code. |
| [`spec-workflow`](plugins/spec-workflow) | Decide what your application should do in writing you can read — requirements as GIVEN/WHEN/THEN scenarios, proposed as a change, implemented against a checklist, verified, then merged into a source-of-truth spec. Includes a tutorial that teaches the whole loop on your own repo. |
| [`notes-workflow`](plugins/notes-workflow) | A markdown notes vault Claude keeps current for you — daily logs, a `current_tasks.md` command center, meeting and people notes, weekly summaries, and a remember/recall memory. Creates the vault on first use; no setup. |
| [`git-guardrails`](plugins/git-guardrails) | Safety rails on Claude's git access: blocks the commands that lose work you can't recover, and blocks a push whose commits add an API key. Hooks only, no skills. Pure Python. |
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
