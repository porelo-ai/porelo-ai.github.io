# Agents

An agent is the AI coding assistant that does the work inside a Porelo task: Claude Code, Pi, Codex and the others.
Porelo itself contains none of them. Each comes as a small package of its own, the agent's adapter, which tells
Porelo how to install that assistant into a task and how to drive it there. You install the adapters for the
assistants you want to use, and choose one when you start a task.

For example, with the adapters for Claude Code and Pi installed, `porelo task start --agent claude` runs Claude Code,
and `porelo task start --agent pi` runs Pi on the same repository, in the same kind of locked-down container.

<!-- the repositories -->

## How to install an agent

Each adapter comes from the same package repository as Porelo, under the name `porelo-agent-<name>`:

```bash
sudo apt install porelo-agent-claude      # or: sudo dnf install porelo-agent-claude
```

The others are `porelo-agent-pi`, `porelo-agent-omp`, `porelo-agent-codex` and `porelo-agent-agy`. Setting a machine
up from Porelo's window offers them too. To see that it worked, run `porelo agents`: it lists every adapter it found,
at once, with no restart.

## How it works

An adapter is a program of its own that Porelo finds in its agents directory at runtime and talks to through the
agent API, a published contract; nothing in Porelo names an agent. Each adapter lives in a repository of its own,
and its pages say which sign-in it supports and what it can and cannot do; Porelo's
[What each agent can and cannot do](../../core/agents.md) compares them.
