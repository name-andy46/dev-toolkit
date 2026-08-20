# cli-tools-drill

Practice-driven skills for learning the basic Linux command-line toolkit. Each skill turns the
agent into a drill coach for one group of tools: it poses exercises, checks your answers, and
adapts to how you're doing — so you build fluency by *doing* the commands, not by reading
reference docs.

## Skills

### text-tools-drill

Guides you through hands-on drills for the text-processing tools — `grep`, `awk`, `sed`, and the
coreutils (`cut`, `sort`, `uniq`, `tr`, `wc`, …). Ask it to quiz you, give you a drill, or let
you practice a specific tool, and it runs an interactive practice loop.

**Triggers:** "quiz me on grep", "give me a sed drill", "let's practice awk", "drill me on
coreutils", "help me learn text-processing commands".

One problem per invocation — it poses the problem, waits for your command and its output, then
verifies. It won't loop or take over the session.

## Configuration

None. The skill is self-contained (its difficulty ladder ships beside it in `CHECKLIST.md`) and
repo-agnostic — it builds problems from whatever repository you have open, and keeps no state
across sessions unless you explicitly ask it to track progress.
