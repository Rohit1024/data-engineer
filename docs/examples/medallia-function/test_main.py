"""Offline publication checks. No Medallia or Google Cloud credentials needed."""

import json
import unittest
from unittest.mock import Mock

from main import export_pages, parse_window


def page(ids, has_next=False, cursor=None):
    return {"data": {"feedback": {
        "nodes": [{"id": value} for value in ids],
        "pageInfo": {"hasNextPage": has_next, "endCursor": cursor},
    }}}


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.objects = {}
        self.metadata = {"tenant": "synthetic", "attempt_id": "fixture"}

    def put(self, name, text, content_type):
        self.assertNotIn(name, self.objects)
        self.objects[name] = text
        return f"gs://fixture/attempt=fixture/{name}"

    def test_two_pages_publish_exact_manifest(self):
        fetch = Mock(side_effect=[page(["f1", "f2"], True, "next"), page(["f3"])])
        result = export_pages(fetch, self.put, self.metadata)
        self.assertEqual([call.args[0] for call in fetch.call_args_list], [None, "next"])
        manifest = json.loads(self.objects["manifest.json"])
        self.assertEqual(result["row_count"], 3)
        self.assertEqual([item["rows"] for item in manifest["pages"]], [2, 1])
        rows = [json.loads(line) for name, text in self.objects.items()
                if name.endswith(".ndjson") for line in text.splitlines()]
        self.assertEqual([row["feedback_id"] for row in rows], ["f1", "f2", "f3"])

    def test_partial_graphql_errors_do_not_publish(self):
        partial = {**page(["f2"]), "errors": [{"message": "restricted field"}]}
        fetch = Mock(side_effect=[page(["f1"], True, "next"), partial])
        with self.assertRaisesRegex(RuntimeError, "GraphQL"):
            export_pages(fetch, self.put, self.metadata)
        self.assertIn("page-000.ndjson", self.objects)
        self.assertNotIn("manifest.json", self.objects)

    def test_storage_failure_does_not_publish(self):
        def fail_second_page(name, text, content_type):
            if name == "page-001.ndjson":
                raise OSError("Simulated upload failure")
            return self.put(name, text, content_type)

        fetch = Mock(side_effect=[page(["f1"], True, "next"), page(["f2"])])
        with self.assertRaises(OSError):
            export_pages(fetch, fail_second_page, self.metadata)
        self.assertNotIn("manifest.json", self.objects)

    def test_bad_cursor_does_not_publish(self):
        for cursor in (None, "", "repeat"):
            with self.subTest(cursor=cursor):
                self.objects.clear()
                fetch = Mock(side_effect=[page(["f1"], True, "repeat"),
                                          page(["f2"], True, cursor)])
                with self.assertRaisesRegex(RuntimeError, "cursor"):
                    export_pages(fetch, self.put, self.metadata)
                self.assertNotIn("manifest.json", self.objects)

    def test_budget_exhaustion_does_not_publish(self):
        fetch = Mock(return_value=page(["f1"], True, "next"))
        with self.assertRaisesRegex(RuntimeError, "budget"):
            export_pages(fetch, self.put, self.metadata, max_pages=1)
        self.assertNotIn("manifest.json", self.objects)

    def test_missing_identity_does_not_publish(self):
        fetch = Mock(return_value=page([None]))
        with self.assertRaisesRegex(RuntimeError, "identity"):
            export_pages(fetch, self.put, self.metadata)
        self.assertFalse(self.objects)

    def test_empty_window_publishes_empty_manifest(self):
        result = export_pages(Mock(return_value=page([])), self.put, self.metadata)
        self.assertEqual(result["row_count"], 0)
        self.assertEqual(json.loads(self.objects["manifest.json"])["pages"], [])

    def test_window_validation(self):
        start = "2026-10-01T00:00:00Z"
        end = "2026-10-02T00:00:00Z"
        self.assertEqual(parse_window({"start": start, "end": end}), (start, end))
        for body in (None, {}, {"start": end, "end": start},
                     {"start": start, "end": "2026-10-03T00:00:00Z"},
                     {"start": "2026-10-01T00:00:00", "end": end}):
            with self.subTest(body=body), self.assertRaises(ValueError):
                parse_window(body)


if __name__ == "__main__":
    unittest.main()
