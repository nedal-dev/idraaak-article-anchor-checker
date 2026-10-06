# IdraaakArticleAnchorChecker

A small, local **Sublime Text 4** utility for writers editing static HTML or
WordPress Gutenberg article source. It finds fragment links whose destination
is missing, duplicate HTML IDs, and links pointing to duplicate IDs.

For example, a button with `href="#comparison"` stops working after the section
is renamed to `id="compare"`. This package points to that button in the source
so you can fix it yourself before publishing.

## Installation

Package Control submission is pending; the package is not listed yet.

For manual installation:

1. In Sublime Text, choose **Preferences > Browse Packages**.
2. Download this repository's tagged release and extract its contents into
   a folder named **IdraaakArticleAnchorChecker** inside that Packages folder.
3. The Python files and `Default.sublime-commands` must be directly inside
   that folder, rather than in a second nested directory.

Requires Sublime Text 4, build 4107 or later. No third-party Python dependencies.
The package is free and MIT licensed; Sublime Text has its own licensing terms.

## Use

1. Open your article's HTML source, including the actual `id` and `href`
   attributes. Unsaved editor buffers also work.
2. Open the Command Palette (`Ctrl+Shift+P`, or `Cmd+Shift+P` on macOS).
3. Choose **Idraaak Article Anchors: Check Current File**.
4. If issues exist, a list shows each problem and its line and column.
   Select an entry to jump to the exact attribute value. Problem attributes
   are also highlighted in the source.
5. Correct the HTML yourself and run the check again. Editing clears old
   highlights and results immediately, because their positions are stale.

**Show Issues** reopens the latest valid list. **Clear Highlights** removes it.
The status bar reports the number of issues and checked fragment links.
No default keybindings or context-menu entries are installed.

Try [examples/article.html](examples/article.html): the two Arabic links work,
the missing link is reported, and both duplicate IDs plus their link are reported.

## What is checked

- Fragment-only links such as `<a href="#section">` (and HTML image-map areas).
- All nonempty HTML `id` attributes in the static article source.
- Arabic IDs, UTF-8 percent-encoded fragments, and HTML character references.
- Exact, case-sensitive matching. IDs are not normalized or percent-decoded.
  A fragment matches literally first, then after one percent-decoding pass.
- Legacy `<a name="section">` targets when no ID matches the same candidate.
  Literal ID/name matches precede percent-decoded ID/name matches.
- `#`, document-top fallback `#top`, and text-only browser fragments do not
  require a matching ID. An ordinary target preceding `:~:text=` is checked.
- Markup-looking text in HTML comments, scripts, styles, and common raw-text
  elements is ignored. Inert `<template>` content is excluded.
- A nonempty `<base href>` produces a warning and skips fragment checks,
  because a fragment could refer to a different document. Duplicate IDs are
  still checked.

## Limits and privacy

This is a static-source check, **not a WordPress validator or a full browser**.
It does not check external links, `page.html#section`, generated IDs, JavaScript
click handlers, Markdown headings, Gutenberg block-comment validity, or whether
a target is hidden by CSS. A Gutenberg JSON `"anchor"` value alone does not
count as an HTML target: the exported heading needs its actual `id` attribute.
The standard-library HTML parser is forgiving but does not reproduce every
HTML5 error-recovery rule; badly malformed markup can produce misleading results.
Files over 2,097,152 characters are skipped to keep the editor responsive.

Checking is manual. The package never changes article text, writes article
files, sends network requests, transmits content, or collects telemetry.

## Tests and maintenance

Run the parser tests with Python 3.8 or later:

```sh
python -m unittest discover -s tests -v
```

`tests/sublime_smoke.py` provides a reproducible check inside an isolated
portable Sublime Text instance; see [tests/README.md](tests/README.md).
Tests and example files are excluded from installation through `.gitattributes`.
Report reproducible problems in this repository's Issues with a small sanitized
HTML example and the Sublime Text build number. Do not upload private articles.

Developed for article editing at [Idraaak](https://idraaak.com/).
