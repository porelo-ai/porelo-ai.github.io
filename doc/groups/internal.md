# Internal

How Porelo itself is made: the tools its repositories build and test with, and the rules of the project as a whole.
Nothing here is needed to use Porelo; it is for someone who wants to work on it.

For example, before a change goes in, the build checks that every download a workflow makes is pinned by its
checksum, and the acceptance tests run on a test machine the build tools rent for an hour.

<!-- the repositories -->

## How to install it

There is nothing to install for using Porelo. A Porelo repository's build takes the build tools from Maven Central
by itself, under `org.fuin.porelo`; [Contributing](../../porelo-project/contributing.md) says how to make a change.

## How it works

The build tools are Java programs every repository's build runs: one rents test machines, one checks a release and
the shared rules. The project's own pages hold its decisions and how its repositories are tested.
