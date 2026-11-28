# Build readers

When an agent pushes its work, your build server builds it somewhere the agent cannot see. A build reader lets the
agent see how that build went: whether it passed, and if not, the log of the job that failed, so the agent can fix
it without you copying the error over.

For example, an agent's push breaks a test on GitHub Actions: Porelo asks the build reader about that commit and
hands the agent the failed job's log, and the agent's next push fixes the test.

<!-- the repositories -->

## How to install it

From the same package repository as Porelo, then named in the project's `project.yml`:

```bash
sudo apt install porelo-adapter-github      # or: sudo dnf install porelo-adapter-github
```

```yaml
builds: { forge: github }
```

To see that it is there and answers: `/usr/libexec/porelo/builds/github describe`. The reader's page says which
token it reads the build server with.

## How it works

A build reader is a program of its own, installed on the host, which Porelo starts and asks over a socket; it never
runs inside a task, and the token it reads the build server with never enters one. Porelo's
[Writing a build reader](../../core/build-readers.md) describes the contract.
