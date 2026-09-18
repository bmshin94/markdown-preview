import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from run_performance import prepare_sources, source_paths


class PerformanceSourceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.controller = self.directory / "controller"
        self.snapshot = self.directory / "baseline"
        self.renderer = "md-preview/Rendering/MarkdownHTML.swift"
        self.write(self.controller, "tests/performance/sources.json", json.dumps([self.renderer]))
        self.write(self.controller, self.renderer, "candidate renderer")
        self.write(self.controller, "tests/swift-tests/Sources/MarkdownHelpers/MarkdownAssetSchemeStub.swift", "asset stub")
        self.write(self.snapshot, self.renderer, "baseline renderer")
        patched = patch("run_performance.ROOT", self.controller)
        patched.start()
        self.addCleanup(patched.stop)

    def write(self, root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_pr_only_unit_helpers_do_not_enter_baseline_or_candidate_probe(self):
        # Reproduce #408: the PR adds production files and helper symlinks that
        # have never existed in the base revision. Also cover ordinary helpers.
        helpers = self.controller / "tests/swift-tests/Sources/MarkdownHelpers"
        for name in ["ProjectFileIndex.swift", "FileSearchMatcher.swift"]:
            production = self.write(self.controller, f"md-preview/Features/FileSearch/{name}", "unrelated Swift source")
            (helpers / name).symlink_to(production)
        (helpers / "UnrelatedHelper.swift").write_text("unrelated test support")
        for label, snapshot in [("baseline", self.snapshot), ("candidate", self.controller)]:
            sources = self.directory / label / "probe"
            prepare_sources(snapshot, sources)
            self.assertEqual({path.name for path in sources.iterdir()},
                             {"MarkdownHTML.swift", "MarkdownAssetSchemeStub.swift"})
            self.assertEqual((sources / "MarkdownHTML.swift").read_text(), f"{label} renderer")
            self.assertEqual((sources / "MarkdownAssetSchemeStub.swift").read_text(), "asset stub")

    def test_each_revision_can_declare_its_own_rendering_dependencies(self):
        new_dependency = "md-preview/Rendering/NewRendererDependency.swift"
        self.write(self.controller, "tests/performance/sources.json", json.dumps([self.renderer, new_dependency]))
        self.write(self.controller, new_dependency, "new rendering dependency")
        self.write(self.snapshot, "tests/performance/sources.json", json.dumps([self.renderer]))
        for label, snapshot in [("baseline", self.snapshot), ("candidate", self.controller)]:
            sources = self.directory / label / "probe"
            prepare_sources(snapshot, sources)
            self.assertEqual((sources / "NewRendererDependency.swift").exists(), label == "candidate")

    def test_missing_required_production_source_still_fails(self):
        (self.snapshot / self.renderer).unlink()
        with self.assertRaisesRegex(ValueError, "Production source missing:.*MarkdownHTML.swift"):
            prepare_sources(self.snapshot, self.directory / "probe")

    def test_invalid_manifests_are_not_replaced_by_the_fallback(self):
        for entries in [[], {}, [None], [""], ["/tmp/outside.swift"], ["md-preview/../outside.swift"],
                        ["tests/Helper.swift"], [self.renderer, self.renderer],
                        [self.renderer, "md-preview/Other/MarkdownHTML.swift"]]:
            with self.subTest(entries=entries):
                self.write(self.snapshot, "tests/performance/sources.json", json.dumps(entries))
                with self.assertRaises(ValueError):
                    source_paths(self.snapshot)

    def test_resource_adapter_keeps_using_the_snapshot_source(self):
        source = "md-preview/Rendering/MarkdownHTML+Utils.swift"
        self.write(self.snapshot, "tests/performance/sources.json", json.dumps([source]))
        self.write(self.snapshot, source, "// baseline lookup\n        var bundles = [Bundle.main]\n")
        destination = self.directory / "probe"
        prepare_sources(self.snapshot, destination)
        result = (destination / "MarkdownHTML+Utils.swift").read_text()
        self.assertIn("// baseline lookup", result)
        self.assertIn("Bundle.module.url", result)

    def test_pre_extraction_editor_still_uses_legacy_adapter(self):
        source = "md-preview/Features/Editor/EditorHTML.swift"
        self.write(self.snapshot, "tests/performance/sources.json", json.dumps([source]))
        destination = self.directory / "probe"
        with patch("run_performance.legacy_editor", return_value="legacy page") as adapter:
            prepare_sources(self.snapshot, destination)
        adapter.assert_called_once_with(self.snapshot)
        self.assertEqual((destination / "EditorHTML.swift").read_text(), "legacy page")


if __name__ == "__main__":
    unittest.main()
