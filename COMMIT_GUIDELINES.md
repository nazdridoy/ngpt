# Commit Message Guidelines

## Introduction

Consistent and well-formatted commit messages provide a better project history, make it easier to understand changes, facilitate automatic changelog generation, and help identify bugs. These guidelines ensure that our commit messages remain uniform, descriptive, and useful to all project contributors.

## Message Format

```
type: <brief summary (max 50 chars)>

- [type] key change 1 (max 60 chars per line)
- [type] key change 2
- [type] key change N (include all significant changes)
```

## Best Practices

- Use the imperative mood in the subject line (e.g., "Add feature" not "Added feature")
- Don't end the subject line with a period
- Start with a capital letter
- Separate subject from body with a blank line
- Wrap body text at 72 characters
- Use the body to explain what and why vs. how

## Atomic Commits

Each commit should represent a single logical change:
- Make focused commits that address a single concern
- Split work into multiple commits when appropriate
- Avoid mixing unrelated changes in the same commit

## Issue References

Link to issues in your commit messages:
- Use "Fixes #123" to automatically close an issue
- Use "Relates to #123" for changes related to but not resolving an issue
- Always include issue numbers for bug fixes

## Valid Types

Choose the most specific type for your changes:

- `feat`: New user features (not for new files without user features)
- `fix`: Bug fixes/corrections to errors
- `refactor`: Restructured code (no behavior change) 
- `style`: Formatting/whitespace changes
- `docs`: Documentation only
- `test`: Test-related changes
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI pipeline changes
- `chore`: Routine maintenance tasks
- `revert`: Reverting previous changes
- `add`: New files/resources with no user-facing features
- `remove`: Removing files/code
- `update`: Changes to existing functionality
- `security`: Security-related changes
- `i18n`: Internationalization
- `a11y`: Accessibility improvements
- `api`: API-related changes
- `ui`: User interface changes
- `data`: Database changes
- `config`: Configuration changes
- `init`: Initial commit/project setup

## Examples

### Good Examples

#### Bug Fix:
```
fix: Address memory leak in data processing pipeline

- [fix] Release resources in DataProcessor.cleanUp()
- [fix] Add null checks to prevent NPE in edge cases
- [perf] Optimize large dataset handling

Fixes #456
```

#### New Feature:
```
feat: Add user profile export functionality

- [feat] Create export button in profile settings
- [feat] Implement JSON and CSV export options
- [security] Apply rate limiting to prevent abuse

Relates to #789
```

#### Refactoring:
```
refactor: Simplify authentication flow

- [refactor] Extract login logic to separate service
- [refactor] Reduce complexity in AuthManager
- [test] Add unit tests for new service

Part of #234
```

### Poor Example:
```
Made some changes to fix stuff

Changed a bunch of files to make the login work better.
Also fixed that other bug people were complaining about.
```

## Additional Resources

- [Conventional Commits](https://www.conventionalcommits.org/)
- [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)
- [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html)
- [GitHub Commit Labels](https://greasyfork.org/en/scripts/526153-github-commit-labels) - A userscript that adds colorful labels to conventional commits on GitHub