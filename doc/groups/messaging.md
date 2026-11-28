# Messaging

The tasks of one project can talk to each other, and you can talk to them: they meet in the project's room, a chat
room that any Matrix chat app, such as Element, can open. Every message an agent writes passes a filter first, so
that an agent cannot send your data out hidden in a message.

For example, one task writes the code and another reviews it: the first writes "ready for review" in the room, the
second answers there with what it found, and you read along and step in with a line of your own.

<!-- the repositories -->

## How to install it

The filter is installed with Porelo, which recommends it. The Matrix part, and a chat server on this machine for
the room, come from the same package repository:

```bash
sudo apt-get install porelo-message-transport-matrix porelo-matrix-homeserver
```

Then name it in the project's `project.yml`:

```yaml
mail:
  transports:
    matrix: {}
```

To see that it works, start a task of that project: its first start makes the project's room and an account for
each task, and the Matrix page says how you join that room yourself.

## How it works

The Matrix part carries the messages between a task's mailbox and the room. The filter is a fixed set of rules, with
no language model inside: it passes plain English and refuses a message that carries data, such as an encoded
payload or a file. Porelo's [Messages between tasks](../../core/messages.md) says what a task may write and to whom.
