# qiskit-bot

This repo contains a wsgi app for running for github automation of the 
qiskit organization. It performs many functions to automate the workflow of the
various aspect of managing the repositories in the qiskit github organization.
For example, release automation to automatically generate a github release with
a full changelog from just a git tag and then generate a PR to bump the
meta-repository based on that tag. The goal of this project is to minimize the
number of manual actions needed as part of daily maintenance of qiskit.

As of right now the bot concentrates on release process automation. It handles
3 key aspects of that. First it generates release notes based on the git log
and pull request tags. This generated changelog is added to the github releases
page. The next step is branch creation. If a project is configured to branch
on minor releases the bot will automatically create the branch. The last step
is bumping the meta repository to include the new version of the released
element. This will handle increasing the meta-package version, the requirements
version of the element, the docs version, and regenerating the authors list
and bibtex file. All 3 of these steps are triggered by tag creation. This
means with the bot all that is required for a qiskit project maintainer is to
push a git tag to github. When coupled with pypi artifact (wheel and sdist)
CI jobs pushing a tag becomes the only required manual step to push a release
everything else will now be done automatically.

In the future the bot may be expanded to automate additional aspects of
the github workflow for the qiskit community.

## Configuration

### Github side configuration

You will need to configure the bot to work with an github user account. This
account will need permission to create releases, push to the repo, etc.

There are two pieces of information needed from that account for the bot to
work. First you need the github bot user to have an ssh key configured for the
local user the daemon is run as. This is needed for git based commands like
pushing branches. Then an access key is needed to be setup for the github api
access. This is used for API access to github for the repositories.

The last piece of github side configuration needed is to configure the webhook.
You need to configure a webhook for each repository that uses the bot. Setup
the webhook to send all necessary event types to the endpoint where the bot
is running. Two things to remember is that make sure you send the webhook events
to the `/postreceive` endpoint off of the server's address and that the
`Content type` is set to `application/json`.
