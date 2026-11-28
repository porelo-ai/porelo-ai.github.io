# User interfaces

Porelo works from the command line, and these give you the same without a terminal. The window shows your tasks,
starts and stops them and lets you review what an agent wants to hand back. The IntelliJ plugin brings that review
into the IDE you already work in.

For example, an agent has finished a change: the window shows it waiting, you read its diff and approve it, and only
then does it reach your repository. In IntelliJ, a notice says that it waits, and the diff opens in IntelliJ's own
diff view.

<!-- the repositories -->

## How to install them

The window comes from the same package repository as Porelo; on Windows as a ZIP or an MSIX, as its pages say:

```bash
sudo apt install porelo-frontend      # or: sudo dnf install porelo-frontend
```

The IntelliJ plugin is installed in IntelliJ IDEA 2026.1 or newer from Porelo's plugin repository: in *Settings*,
*Plugins*, the gear icon, *Manage Plugin Repositories*, add the address its page gives, then install *Porelo* from
the *Marketplace* tab.

To see that they work, open the window: it lists this computer's tasks. In IntelliJ, the *Porelo* tool window lists
what waits for review.

## How it works

Both reach Porelo's daemon, the background service that runs the tasks, through its socket, on this computer or on a
machine reached over ssh; neither reads Porelo's files directly. Their pages say how each finds a machine and what
it shows.
