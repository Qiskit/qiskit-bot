# qiskit-bot

This repo contains a wsgi app for running for github automation of the 
qiskit community. It performs many functions to automate the workflow of the
qiskit community.

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
is running.
