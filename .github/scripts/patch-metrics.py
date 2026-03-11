"""Patch stalomeow/metrics action to fix bugs caused by GitHub API returning
undefined/null values in PushEvent commit payloads."""


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

print("Patching complete.")
