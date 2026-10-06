"""Copy to an isolated portable Sublime's Data/Packages/User to run checks."""
import io
import json
import os
import traceback
import unittest

import sublime
import sublime_plugin
from IdraaakArticleAnchorChecker import idraaak_article_anchor_checker as plugin
from IdraaakArticleAnchorChecker.tests import test_anchors


class IdraaakAnchorSmokeCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        results = {"build": sublime.version(), "runtime": __import__('sys').version,
                   "checks": [], "errors": []}
        view = None
        try:
            output = io.StringIO()
            suite = unittest.defaultTestLoader.loadTestsFromModule(test_anchors)
            tested = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
            results['parser_tests'] = tested.testsRun
            results['parser_success'] = tested.wasSuccessful()
            results['parser_output'] = output.getvalue()
            window = sublime.active_window()
            view = window.new_file()
            view.set_scratch(True)
            source = 'عربي 😀\n<a href="#gone">g</a>\n<h2 id="x">x</h2>\n<h3 id="x">x</h3>'
            view.run_command('append', {'characters': source})
            view.set_read_only(True)
            before = view.change_count()
            view.run_command('idraaak_article_anchor_check', {'show_list': False})
            issues = view.settings().get(plugin._RESULTS)
            assert len(issues) == 3, repr(issues)
            results['checks'].append('registered command reports missing target and both duplicate IDs')
            assert view.substr(sublime.Region(0, view.size())) == source
            assert view.change_count() == before and view.is_read_only()
            results['checks'].append('read-only buffer and content remain unchanged')
            regions = view.get_regions(plugin._REGIONS)
            assert len(regions) == 3
            assert view.substr(regions[0]) == '#gone'
            assert [view.substr(x) for x in regions[1:]] == ['x', 'x']
            results['checks'].append('real Sublime region offsets remain correct after Arabic and emoji')
            plugin._navigate(view, 0, before)
            assert view.substr(view.sel()[0]) == '#gone'
            results['checks'].append('selection jumps to exact problem attribute')
            selection = view.sel()[0]
            plugin._navigate(view, -1, before)
            plugin._navigate(view, 999, before)
            assert view.sel()[0] == selection
            results['checks'].append('cancel and invalid selection do not move cursor')
            view.set_read_only(False)
            view.run_command('append', {'characters': '\n<!-- changed -->'})
            sublime.set_timeout(lambda: self.finish(results, view, before, selection), 100)
            return
        except Exception:
            results['errors'].append(traceback.format_exc())
        self.write_results(results)

    def finish(self, results, view, old_version, old_selection):
        try:
            assert not view.settings().has(plugin._RESULTS)
            assert not view.get_regions(plugin._REGIONS)
            results['checks'].append('editing automatically removes stale diagnostics and highlights')
            plugin._navigate(view, 0, old_version)
            assert view.sel()[0] == old_selection
            results['checks'].append('old quick-panel callback cannot navigate after source changes')
            view.run_command('select_all')
            view.run_command('insert', {'characters': '<a href="#مقارنة">g</a><h2 id="مقارنة">OK</h2>'})
            view.run_command('idraaak_article_anchor_check', {'show_list': False})
            assert view.settings().get(plugin._RESULTS) == []
            assert not view.get_regions(plugin._REGIONS)
            results['checks'].append('valid Arabic article returns no issues inside Sublime')
            view.run_command('idraaak_article_anchor_clear')
            assert not view.settings().has(plugin._RESULTS)
            results['checks'].append('clear command removes saved results')
            view.close()
        except Exception:
            results['errors'].append(traceback.format_exc())
        self.write_results(results)

    def write_results(self, results):
        target = os.path.join(sublime.packages_path(), '..', 'anchor-smoke-results.json')
        results['success'] = bool(results.get('parser_success')) and not results['errors']
        with open(target, 'w', encoding='utf-8') as handle:
            json.dump(results, handle, ensure_ascii=False, indent=2)
        sublime.set_timeout(lambda: sublime.run_command('exit'), 200)
