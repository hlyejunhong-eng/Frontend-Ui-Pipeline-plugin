#!/usr/bin/env python3
"""Serve a Phase 2 review folder with a local HTTP server."""

from __future__ import annotations

import argparse
import functools
import html
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote


class ReviewHandler(SimpleHTTPRequestHandler):
    """HTTP handler with cache disabled for asset review iterations."""

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        if not getattr(self.server, "quiet", False):
            super().log_message(format, *args)


def find_first_html(root: Path) -> str:
    for preferred in ("index.html", "component-contact-sheet.html", "contact-sheet.html"):
        if (root / preferred).is_file():
            return preferred
    for path in sorted(root.rglob("*.html")):
        if path.is_file():
            return path.relative_to(root).as_posix()
    return ""


def validate_root(root: Path, entry: str) -> str:
    if not root.exists():
        raise SystemExit(f"Review root does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Review root must be a directory: {root}")

    resolved_entry = entry.strip().lstrip("/")
    if not resolved_entry:
        resolved_entry = find_first_html(root)
    if resolved_entry and not (root / resolved_entry).is_file():
        raise SystemExit(f"Review entry does not exist under {root}: {resolved_entry}")
    return resolved_entry


def build_url(host: str, port: int, entry: str) -> str:
    display_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    if not entry:
        return f"http://{display_host}:{port}/"
    return f"http://{display_host}:{port}/{quote(entry)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a Phase 2 review folder locally.")
    parser.add_argument("root", help="Review folder to serve.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0, help="Use 0 to choose a free port.")
    parser.add_argument(
        "--entry",
        default="",
        help="HTML entry under the review root. Defaults to the first common contact sheet.",
    )
    parser.add_argument("--check", action="store_true", help="Validate inputs and print the URL without serving forever.")
    parser.add_argument("--quiet", action="store_true", help="Suppress request logs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    entry = validate_root(root, args.entry)

    if args.check:
        port = args.port if args.port else 8000
        print(f"Serving review root: {html.escape(str(root))}")
        print(f"Review URL: {build_url(args.host, port, entry)}")
        return

    handler = functools.partial(ReviewHandler, directory=str(root))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    server.quiet = args.quiet
    url = build_url(args.host, server.server_address[1], entry)

    print(f"Serving review root: {html.escape(str(root))}")
    print(f"Review URL: {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping review server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
