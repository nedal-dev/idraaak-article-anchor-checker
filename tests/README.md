# Testing inside Sublime Text

Use an isolated portable copy of Sublime Text, not your usual editor profile.

1. Create its `Data/Packages` directory before launching.
2. Copy the repository to `Data/Packages/IdraaakArticleAnchorChecker`, including
   tests and examples (these are normally excluded from installed releases).
3. Copy `tests/sublime_smoke.py` to `Data/Packages/User/sublime_smoke.py`.
4. Launch the portable executable with `--command idraaak_anchor_smoke`.
5. The command runs the parser tests and actual editor checks, writes
   `Data/anchor-smoke-results.json`, and quits the isolated application.

It verifies registered commands, unchanged read-only buffers, Arabic/emoji
source positions, highlighting, navigation, stale-result invalidation, clean
results, and clearing. It uses only temporary scratch views in this profile.
