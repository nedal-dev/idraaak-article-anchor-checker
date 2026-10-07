"""Sublime Text commands for local article-anchor diagnostics."""

import sublime
import sublime_plugin

from .lib.anchor_core import check_html


_REGIONS = "idraaak_article_anchor_issues"
_RESULTS = "idraaak_article_anchor_results"
_VERSION = "idraaak_article_anchor_change_count"
_STATUS = "idraaak_article_anchor_status"
_MAX_SIZE = 2 * 1024 * 1024


def clear_results(view):
    view.erase_regions(_REGIONS)
    view.erase_status(_STATUS)
    view.settings().erase(_RESULTS)
    view.settings().erase(_VERSION)


def _navigate(view, index, version):
    if index < 0 or not view.is_valid() or view.change_count() != version:
        return
    issues = view.settings().get(_RESULTS, [])
    if index >= len(issues):
        return
    item = issues[index]
    view.sel().clear()
    view.sel().add(sublime.Region(item["start"], item["end"]))
    view.show(item["start"])
    if view.window():
        view.window().focus_view(view)


def _show_list(view):
    issues = view.settings().get(_RESULTS, [])
    version = view.settings().get(_VERSION)
    window = view.window()
    if not window or not issues or version != view.change_count():
        return
    items = [[x["message"], "Line {line}, column {column}".format(**x)] for x in issues]
    window.show_quick_panel(items, lambda i: _navigate(view, i, version))


class IdraaakArticleAnchorCheckCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return not self.view.settings().get("is_widget", False)

    def run(self, edit, show_list=True):
        view = self.view
        clear_results(view)
        if view.size() > _MAX_SIZE:
            view.set_status(_STATUS, "Article anchors: file exceeds 2 MiB character limit")
            sublime.status_message("Article anchor check skipped: file is too large")
            return
        source = view.substr(sublime.Region(0, view.size()))
        report = check_html(source)
        issues = [x._asdict() for x in report.issues]
        view.settings().set(_RESULTS, issues)
        view.settings().set(_VERSION, view.change_count())
        summary = "Article anchors: {0} issue(s), {1} fragment link(s) checked".format(
            len(issues), report.links_checked)
        if report.links_skipped:
            summary += ", {0} skipped".format(report.links_skipped)
        view.set_status(_STATUS, summary)
        sublime.status_message(summary)
        if issues:
            view.add_regions(_REGIONS,
                             [sublime.Region(x["start"], x["end"]) for x in issues],
                             "invalid", "dot", sublime.DRAW_NO_FILL)
            if show_list:
                _show_list(view)


class IdraaakArticleAnchorShowIssuesCommand(sublime_plugin.TextCommand):
    def is_enabled(self):
        return bool(self.view.settings().get(_RESULTS)) and (
            self.view.settings().get(_VERSION) == self.view.change_count())

    def run(self, edit):
        _show_list(self.view)


class IdraaakArticleAnchorClearCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        clear_results(self.view)


class IdraaakArticleAnchorListener(sublime_plugin.EventListener):
    def on_modified(self, view):
        # Source positions stop being valid as soon as the article changes.
        if view.settings().has(_RESULTS):
            clear_results(view)
