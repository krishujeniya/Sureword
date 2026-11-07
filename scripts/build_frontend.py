#!/usr/bin/env python3
"""Build and validate standalone static frontend distribution for GitHub Pages.

Extracts assets from src/sureword/static, normalizes asset links for the /Sureword/
base path, injects production API configuration, and validates asset integrity
and secret prevention.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "design.css",
    "app.js",
    "experience.js",
    "logo.svg",
    "favicon.svg",
]

FORBIDDEN_EXTENSIONS = {".py", ".pyc", ".db", ".sqlite", ".sqlite3", ".env", ".key", ".pem"}


def build_frontend(
    source_dir: Path,
    output_dir: Path,
    api_base_url: str = "https://sureword.vercel.app",
    base_href: str = "/Sureword/",
) -> None:
    """Build decoupled static distribution."""
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source static directory not found: {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy required files
    for filename in REQUIRED_FILES:
        src = source_dir / filename
        dst = output_dir / filename
        if not src.is_file():
            raise FileNotFoundError(f"Missing required asset: {src}")
        shutil.copy2(src, dst)

    # 2. Process index.html
    index_file = output_dir / "index.html"
    content = index_file.read_text(encoding="utf-8")

    # Replace any legacy root-relative /static/ references with ./
    content = content.replace('href="/static/', 'href="./')
    content = content.replace('src="/static/', 'src="./')

    # Ensure canonical and OpenGraph point to GitHub Pages target
    gh_pages_url = f"https://krishujeniya.github.io{base_href}"
    content = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{gh_pages_url}">',
        content,
    )
    content = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{gh_pages_url}">',
        content,
    )
    content = re.sub(
        r'<meta property="og:image" content="[^"]*">',
        f'<meta property="og:image" content="{gh_pages_url}logo.svg">',
        content,
    )
    content = re.sub(
        r'<meta name="twitter:image" content="[^"]*">',
        f'<meta name="twitter:image" content="{gh_pages_url}logo.svg">',
        content,
    )

    # Ensure runtime configuration points to Vercel production backend
    config_snippet = (
        "  <!-- Production Client Runtime Configuration -->\n"
        "  <script>\n"
        "    window.SUREWORD_CONFIG = {\n"
        f'      apiBaseUrl: "{api_base_url}"\n'
        "    };\n"
        "  </script>\n"
    )
    if "window.SUREWORD_CONFIG" in content:
        content = re.sub(
            r"<script>\s*window\.SUREWORD_CONFIG\s*=\s*\{.*?\};\s*</script>",
            config_snippet.strip(),
            content,
            flags=re.DOTALL,
        )

    # Add .nojekyll marker to prevent GitHub Pages from ignoring files
    nojekyll_file = output_dir / ".nojekyll"
    nojekyll_file.touch(exist_ok=True)

    index_file.write_text(content, encoding="utf-8")


def validate_frontend(output_dir: Path) -> list[str]:
    """Validate asset paths, permissions, and ensure no secrets or backend code exist."""
    errors: list[str] = []

    if not output_dir.is_dir():
        return [f"Output directory does not exist: {output_dir}"]

    # Check required files
    for filename in REQUIRED_FILES:
        target = output_dir / filename
        if not target.is_file():
            errors.append(f"Missing build artifact: {filename}")
        elif target.stat().st_size == 0:
            errors.append(f"Build artifact is empty: {filename}")

    # Check for forbidden files
    for root, _, files in os.walk(output_dir):
        for f in files:
            p = Path(root) / f
            if p.suffix.lower() in FORBIDDEN_EXTENSIONS or f.startswith(".env"):
                errors.append(f"Forbidden file found in distribution: {p}")

    # Check index.html for un-substituted root-relative static paths
    index_file = output_dir / "index.html"
    if index_file.is_file():
        index_text = index_file.read_text(encoding="utf-8")
        if re.search(r'(href|src)="/static/', index_text):
            errors.append("Un-substituted root-relative '/static/' path found in index.html")

        # Scan for accidental secret patterns
        secret_patterns = [
            (r'gnani_[0-9a-zA-Z]{16,}', "Potential Gnani API key pattern"),
            (r'postgres://[^:]+:[^@]+@', "Postgres credentials with password"),
            (r'-----BEGIN (?:RSA )?PRIVATE KEY-----', "Private key block"),
        ]
        for pattern, desc in secret_patterns:
            if re.search(pattern, index_text):
                errors.append(f"Security error: {desc} detected in index.html")

    # Scan app.js for private secrets
    app_js_file = output_dir / "app.js"
    if app_js_file.is_file():
        js_text = app_js_file.read_text(encoding="utf-8")
        if "GNANI_API_KEY" in js_text:
            errors.append("GNANI_API_KEY string found in client javascript bundle")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate Sureword static frontend")
    parser.add_argument(
        "--source",
        "-s",
        type=Path,
        default=Path("src/sureword/static"),
        help="Source static directory",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("dist-static"),
        help="Target distribution directory",
    )
    parser.add_argument(
        "--api-base",
        default="https://sureword.vercel.app",
        help="Backend API base URL for GitHub Pages runtime",
    )
    parser.add_argument(
        "--base-href",
        default="/Sureword/",
        help="Deployment base path",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate output directory without building",
    )

    args = parser.parse_args()

    if not args.check_only:
        print(f"Building static frontend from {args.source} -> {args.output}...")
        build_frontend(
            source_dir=args.source,
            output_dir=args.output,
            api_base_url=args.api_base,
            base_href=args.base_href,
        )
        print("Build complete.")

    print(f"Validating static distribution in {args.output}...")
    errors = validate_frontend(args.output)
    if errors:
        print(f"Validation FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Validation PASSED: Static frontend is clean, self-contained, and deployable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
