"""Patch stalomeow/metrics action to fix bugs caused by GitHub API returning
undefined/null values in PushEvent commit payloads, and to fix the most-used
languages section not showing data for users whose owned repositories have no
GitHub-detected language data."""


def patch_file(path, replacements):
    with open(path, "r") as f:
        content = f.read()

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"Patched {path}: replaced '{old[:60]}...'")
        else:
            print(f"Skip {path}: pattern not found (may already be patched)")

    with open(path, "w") as f:
        f.write(content)


# Fix activity plugin:
# Bug: TypeError: Cannot read properties of undefined (reading 'filter')
# Cause: payload.commits can be undefined in some PushEvent payloads
patch_file(
    ".metrics-action/source/plugins/activity/index.mjs",
    [
        (
            "commits = commits.filter(({author: {email}}) => imports.filters.text(email, ignored))",
            "commits = (commits || []).filter(commit => commit && commit.author && imports.filters.text(commit.author.email, ignored))",
        )
    ],
)

# Fix habits plugin:
# Bug: TypeError: Cannot destructure property 'author' of 'undefined'
# Cause: payload.commits can contain null/undefined items in some PushEvent payloads
patch_file(
    ".metrics-action/source/plugins/habits/index.mjs",
    [
        (
            ".flatMap(({payload}) => payload.commits)",
            ".flatMap(({payload}) => payload?.commits ?? [])",
        ),
        (
            '.filter(({author}) => data.shared["commits.authoring"]',
            '.filter(commit => commit && commit.author).filter(({author}) => data.shared["commits.authoring"]',
        ),
    ],
)

# Fix languages plugin:
# Bug: most-used section shows no languages for users whose owned repos have no
#      GitHub-detected language data (e.g. profile repos with only YAML/Markdown/SVG).
# Cause: the stats loop only iterates over data.user.repositories.nodes (owned repos),
#        while repositoriesContributedTo.nodes (contributed repos) is already available
#        in the in-scope `repositories` variable used for the unique count. Using the
#        combined list ensures the most-used section reflects the user's actual language
#        usage, consistent with how the unique count is already computed.
patch_file(
    ".metrics-action/source/plugins/languages/index.mjs",
    [
        (
            "console.debug(`metrics/compute/${login}/plugins > languages > processing ${data.user.repositories.nodes.length} repositories`)",
            "console.debug(`metrics/compute/${login}/plugins > languages > processing ${repositories.length} repositories`)",
        ),
        (
            "for (const repository of data.user.repositories.nodes) {",
            "for (const repository of repositories) {",
        ),
    ],
)

print("Patching complete.")
