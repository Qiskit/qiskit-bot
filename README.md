# qiskit-bot

qiskit-bot is a bot to automate some tasks in the [Qiskit GitHub organization](https://github.com/Qiskit/), like tagging maintainers in issues and handling releases.

This repo contains a wsgi app for running for GitHub automation of the 
Qiskit organization. It performs many functions to automate the workflow of the
various aspect of managing the repositories in the Qiskit GitHub organization.
For example, release automation to automatically generate a GitHub release with
a full changelog from just a git tag and then generate a PR to bump the
meta-repository based on that tag. The goal of this project is to minimize the
number of manual actions needed as part of daily maintenance of qiskit.

As of right now the bot concentrates on release process automation. It handles
3 key aspects of that. First it generates release notes based on the git log
and pull request tags. This generated changelog is added to the GitHub releases
page. The next step is branch creation. If a project is configured to branch
on minor releases, the bot will automatically create the branch. These steps are triggered by tag creation. This
means with the bot all that is required for a Qiskit project maintainer is to
push a git tag to GitHub. When coupled with pypi artifact (wheel and sdist)
CI jobs pushing a tag becomes the only required manual step to push a release
everything else will now be done automatically.

The other main feature the bot offers is to automatically leave a message on
all new PRs when they are opened. This can be useful to leave a comment to set
expectations for contributors but also be used to notify particular people to
review the PR. The bot is configurable for each project so that subsets of
GitHub users can be mentioned in this comment automatically based on the files
changed in the PR.

In the future, the bot may be expanded to automate additional aspects of
the GitHub workflow for the Qiskit community.

## Configuration

### Github side configuration

You will need to configure the bot to work with an GitHub user account. This
account will need permission to create releases, push to the repo, etc.

There are two pieces of information needed from that account for the bot to
work. First, you need the GitHub bot user to have an ssh key configured for the
local user the daemon is run as. This is needed for git based commands like
pushing branches. Then an access key is needed to be setup for the GitHub api
access. This is used for API access to GitHub for the repositories.

The last piece of GitHub side configuration needed is to configure the webhook.
You need to configure a webhook for each repository that uses the bot. Setup
the webhook to send all necessary event types to the endpoint where the bot
is running. Two things to remember is that make sure you send the webhook events
to the `/postreceive` endpoint off of the server's address and that the
`Content type` is set to `application/json`.


### Per repo configuration

qiskit-bot gives projects some local configuration options that can be set in
the repository. To set a local configuration file a file `qiskit_bot.yaml` must
be created in the root of the git repository. If this file is present then
qiskit-bot will read it before every action and adjust behavior based on its
contents. Currently this configuration file is used to control two things:
the changelog generation behavior, and whether the bot will leave comments
on new pull requests when they're opened (and the exact behavior of that
comment). An example of a fully populated configuration file is:

```yaml
---
categories:
    "Changelog: Custom": Special category
    "Changelog: Custom 2": Less special category
    "Nothing": null
notifications:
    ".*":
        - @core-team
    qiskit/transpiler:
        - @user1
        - @user2
    qiskit/transpiler/passes:
        # You can escape usernames with ` so that they don't get
        # GitHub notifications.
        - `@user3`
        - `@user4`
always_notify: true
notification_prelude: |
    This is a custom prelude

    I include whitespace:

```

The details on each option are as follows:

- `categories`: This contains a nested mapping of GitHub labels to changelog
  sections. If specified at release time when qiskit-bot generates the changelog
  it will look at each merged PR in the release and if any have any matching
  labels that commit summary message will be put under the corresponding
  sections in the changelog used for the release page. If a value for any label
  is set to `null` this means that this label is counted as matching but will
  not be included in the generated changelog. By default any labels outside this
  set will not be included in the changelog but when the
  `tools/generate_changelog.py` script is run it flags any merged PRs for a pending
  release that don't have a matching label. By setting one or more labels to `null`
  these PRs will not show up in that script.

  If this field is not specified the following default values are used:
  ```yaml
  "Changelog: Deprecation": Deprecated
  "Changelog: New Feature": Added
  "Changelog: API Change": Changed
  "Changelog: Removal": Removed
  "Changelog: Bugfix": Fixed
  "Changelog: None": null
  ```

- `notifications`: This contains a mapping of path regexes to a list of usernames
  to notify if an opened PR touches files that match a particular regex (as found
  by Python's stdlib `re.search()` function). For example if you set the path regex
  to `".*"` this would match everything, but using a regex gives you control over
  exactly how and what matches a particular group. If a path matches, the listed
  usernames will be listed in the notification comment left by the bot on a new PR
  being opened. The specified usernames will receive a GitHub mention notification, so you can instead escape the usernames with \` so that instead the reviewer only knows those are relevant people to ping if necessary.
  The matching is additive, so if there is more than 1 match the users
  from all the matches will be listed in that comment. If this is not specified (and
  `always_notify` is not set) then no comment will be left by the bot when new PRs
  are opened.
- `always_notify`: If this is specified, a notification/comment is always left on PR
  opening even if there are no matching notification paths. In the case of no
  matching paths just the notification prelude is used.
- `notification_prelude`: If this is specified, the text used for this field will
  be used as the beginning of every notification comment. If this is not specified
  the following prelude is used:

  ```
  Thank you for opening a new pull request.

  Before your PR can be merged it will first need to pass continuous
  integration tests and be reviewed. Sometimes the review process can be slow,
  so please be patient.

  While you're waiting, please feel free to review other open PRs. While only a
  subset of people are authorized to approve pull requests for merging,
  everyone is encouraged to review open pull requests. Doing reviews helps
  reduce the burden on the core team and helps make the project's code better
  for everyone.
  ```
