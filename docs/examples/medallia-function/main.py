"""Bounded historical Medallia extraction for lesson 0054. No moving checkpoint."""

from datetime import datetime, timedelta, timezone
import json
import os
from uuid import uuid4

import functions_framework
from google.cloud import storage
import requests


QUERY = """
query FeedbackWindow(
  $after: ID, $timeField: ID!, $scoreField: ID!,
  $start: String!, $end: String!
) {
  feedback(
    first: 100, after: $after,
    orderBy: [
      {fieldId: $timeField, direction: ASC},
      {fieldId: "a_surveyid", direction: ASC}
    ],
    filter: {and: [
      {fieldIds: [$timeField], gte: $start},
      {fieldIds: [$timeField], lt: $end}
    ]}
  ) {
    nodes {
      id
      source_time: fieldData(fieldId: $timeField) { values }
      score: fieldData(fieldId: $scoreField) { values }
    }
    pageInfo { hasNextPage endCursor }
  }
}
"""


def parse_window(body):
    if not isinstance(body, dict):
        raise ValueError("Expected a JSON object")
    bounds = []
    for key in ("start", "end"):
        value = body.get(key)
        if not isinstance(value, str) or not value.endswith("Z"):
            raise ValueError("Use UTC timestamps ending in Z")
        bounds.append(datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc))
    start, end = bounds
    if not timedelta(0) < end - start <= timedelta(days=1):
        raise ValueError("Window must be positive and at most one day")
    return tuple(value.isoformat().replace("+00:00", "Z") for value in bounds)


def export_pages(fetch_page, put, metadata, max_pages=5):
    """Publish a manifest only after all pages succeed; put returns a GCS URI."""
    cursor = None
    seen_cursors = set()
    pages = []
    row_count = 0
    for page_number in range(max_pages):
        result = fetch_page(cursor)
        if result.get("errors"):
            raise RuntimeError("GraphQL returned errors")
        feedback = result["data"]["feedback"]
        nodes = feedback["nodes"]
        info = feedback["pageInfo"]
        if not isinstance(nodes, list) or len(nodes) > 100:
            raise RuntimeError("Invalid page rows")
        if not isinstance(info["hasNextPage"], bool):
            raise RuntimeError("Invalid page status")
        next_cursor = info.get("endCursor")
        if info["hasNextPage"]:
            if not isinstance(next_cursor, str) or not next_cursor or next_cursor in seen_cursors:
                raise RuntimeError("Missing or repeated cursor")
            seen_cursors.add(next_cursor)
        rows = []
        for node in nodes:
            if not isinstance(node.get("id"), str) or not node["id"]:
                raise RuntimeError("Missing feedback identity")
            rows.append({**metadata, "feedback_id": node["id"], "payload": node})
        if rows:
            text = "".join(json.dumps(row, allow_nan=False) + "\n" for row in rows)
            uri = put(f"page-{page_number:03d}.ndjson", text, "application/x-ndjson")
            pages.append({"uri": uri, "rows": len(rows)})
            row_count += len(rows)
        if not info["hasNextPage"]:
            manifest = {**metadata, "pages": pages, "row_count": row_count}
            uri = put("manifest.json", json.dumps(manifest), "application/json")
            return {"manifest_uri": uri, "row_count": row_count}
        cursor = next_cursor
    raise RuntimeError("Page budget exceeded; split the window")


@functions_framework.http
def extract_feedback(request):
    if request.method != "POST":
        return {"error": "Use POST"}, 405
    try:
        start, end = parse_window(request.get_json(silent=True))
    except ValueError as error:
        return {"error": str(error)}, 400

    attempt_id = uuid4().hex
    try:
        # shortcut: fixed historical windows only; recurring ingestion needs durable state.
        metadata = {
            "tenant": os.environ["MEDALLIA_TENANT"],
            "window_start": start,
            "window_end": end,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "attempt_id": attempt_id,
        }
        prefix = f"medallia/attempt={attempt_id}"
        bucket = storage.Client().bucket(os.environ["RAW_BUCKET"])

        def put(name, text, content_type):
            blob = bucket.blob(f"{prefix}/{name}")
            blob.upload_from_string(
                text, content_type=content_type, if_generation_match=0,
                timeout=15, retry=None,
            )
            return f"gs://{bucket.name}/{blob.name}"

        with requests.Session() as session:
            token_response = session.post(
                os.environ["MEDALLIA_TOKEN_URL"],
                auth=(os.environ["MEDALLIA_CLIENT_ID"], os.environ["MEDALLIA_CLIENT_SECRET"]),
                data={"grant_type": "client_credentials"},
                timeout=(5, 15), allow_redirects=False,
            )
            if token_response.status_code != 200:
                raise RuntimeError("Token request failed")
            token = token_response.json()["access_token"]

            def fetch_page(cursor):
                response = session.post(
                    os.environ["MEDALLIA_QUERY_URL"],
                    headers={"Authorization": f"Bearer {token}"},
                    json={"query": QUERY, "variables": {
                        "after": cursor, "start": start, "end": end,
                        "timeField": os.environ["MEDALLIA_TIME_FIELD"],
                        "scoreField": os.environ["MEDALLIA_SCORE_FIELD"],
                    }},
                    timeout=(5, 15), allow_redirects=False,
                )
                if response.status_code != 200:
                    raise RuntimeError(f"Query HTTP status {response.status_code}")
                return response.json()

            result = export_pages(fetch_page, put, metadata)
        print(json.dumps({"event": "extract_complete", "attempt_id": attempt_id, **result}))
        return result, 200
    except Exception as error:
        # API bodies and exception messages can contain feedback or credentials.
        print(json.dumps({"event": "extract_failed", "attempt_id": attempt_id,
                          "error_type": type(error).__name__}))
        return {"error": "Extraction failed; inspect this attempt", "attempt_id": attempt_id}, 500
