"""Score scope compatibility and catalog regression checks."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import serve


class ScoreAssessmentTests(unittest.TestCase):
    def assess(self, data):
        scores = serve.read_scores(None, data)
        return serve.score_assessment("004", data, scores)

    def test_legacy_scores_keep_their_average(self):
        result = self.assess({"claude": {"score": 58}, "chatgpt": {"score": 62}})
        self.assertEqual(result["average"], 60)
        self.assertEqual(result["assessment"]["targets"], ["004"])
        self.assertEqual(result["eligible_scorers"], ["claude", "chatgpt"])

    def test_bundle_excludes_previous_single_claim_score(self):
        data = {"assessment": {"targets": ["004", "004-3"], "label": "연구 묶음"},
                "claude": {"score": 58, "reason": "old"},
                "chatgpt": {"score": 62, "targets": ["004", "004-3"]}}
        result = self.assess(data)
        self.assertEqual(result["average"], 62)
        self.assertEqual(result["eligible_scorers"], ["chatgpt"])
        self.assertEqual(result["score_targets"]["claude"], ["004"])
        self.assertEqual(data["claude"], {"score": 58, "reason": "old"})

    def test_same_bundle_order_does_not_change_eligibility(self):
        result = self.assess({
            "assessment": {"targets": ["004-3", "004"]},
            "claude": {"score": 60, "targets": ["004", "004-3", "004"]},
            "chatgpt": {"score": 62, "targets": ["004-3", "004"]},
        })
        self.assertEqual(result["average"], 61)
        self.assertEqual(result["eligible_scorers"], ["claude", "chatgpt"])

    def test_old_scores_do_not_supply_an_unscored_bundle(self):
        result = self.assess({"assessment": {"targets": ["004", "004-3"]},
                              "claude": {"score": 58}, "chatgpt": None})
        self.assertIsNone(result["average"])
        self.assertEqual(result["eligible_scorers"], [])

    def test_explicit_invalid_scope_is_not_treated_as_a_match(self):
        result = self.assess({"claude": {"score": 58, "targets": []},
                              "chatgpt": {"score": 62}})
        self.assertEqual(result["average"], 62)
        self.assertEqual(result["eligible_scorers"], ["chatgpt"])

    def test_tree_keeps_original_scores_and_exports_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "conjectures" / "004-test"
            folder.mkdir(parents=True)
            (folder / "conjectures.md").write_text("# 004 · Test\n", encoding="utf-8")
            old = {"score": 58, "version": "0.6", "reason": "preserved"}
            data = {"assessment": {"targets": ["004", "004-3"]},
                    "claude": old, "chatgpt": {"score": 62, "targets": ["004", "004-3"]}}
            (folder / "score.json").write_text(json.dumps(data), encoding="utf-8")
            with patch.object(serve, "ROOT", root):
                card = serve.tree()["conjectures"][0]
            self.assertEqual(card["average"], 62)
            self.assertEqual(card["scores"]["claude"], old)
            self.assertEqual(card["eligible_scorers"], ["chatgpt"])


if __name__ == "__main__":
    unittest.main()
