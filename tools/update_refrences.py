import argparse
import re
from pathlib import Path

IMAGE_EXTS = r"jpe?g|png|bmp|tiff?"

# Matches local image paths with optional ?query or #hash, skipping external URLs
IMAGE_REF_PATTERN = re.compile(
    rf"""(?P<external>(?:https?:)?//)?(?P<path>[^\s"'`<>()?#]+?)\.(?P<ext>{IMAGE_EXTS})(?=[?#"'`\s),]|$)""",
    re.IGNORECASE,
)

TEXT_EXTENSIONS = {
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".vue", ".svelte", ".astro", ".md", ".mdx",
    ".json", ".yaml", ".yml", ".xml", ".svg",
    ".py", ".php", ".rb", ".twig", ".njk", ".ejs", ".hbs", ".liquid",
}

IGNORE_DIRS = {
    ".git", "node_modules", ".next", ".nuxt", "dist", "build",
    "__pycache__", ".venv", "venv", ".idea", ".vscode", "coverage",
}


def iter_repo_files(root: Path):
    for path in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def update_references(
    repo_root: Path,
    dry_run: bool = False,
    force_all: bool = False,
) -> None:
    # Index all .webp filenames currently on disk so we don't rewrite unconverted assets
    existing_webp = {
        p.name.lower()
        for p in iter_repo_files(repo_root)
        if p.suffix.lower() == ".webp"
    }

    if not existing_webp and not force_all:
        print("No .webp files found in repository. Use --all to rewrite references anyway.")
        return

    files_changed = 0
    total_replacements = 0

    for file_path in iter_repo_files(repo_root):
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            # newline="" preserves existing LF / CRLF line endings
            with file_path.open("r", encoding="utf-8", newline="") as f:
                content = f.read()
        except UnicodeDecodeError:
            continue

        file_replacements = 0

        def replace_match(match: re.Match) -> str:
            nonlocal file_replacements

            if match.group("external"):
                return match.group(0)

            raw_path = match.group("path")
            webp_filename = f"{Path(raw_path).name}.webp".lower()

            if not force_all and webp_filename not in existing_webp:
                return match.group(0)

            file_replacements += 1
            return f"{raw_path}.webp"

        updated_content = IMAGE_REF_PATTERN.sub(replace_match, content)

        if file_replacements > 0:
            files_changed += 1
            total_replacements += file_replacements
            rel_path = file_path.relative_to(repo_root)

            if dry_run:
                print(f"[DRY RUN] {rel_path}: {file_replacements} reference(s)")
            else:
                with file_path.open("w", encoding="utf-8", newline="") as f:
                    f.write(updated_content)
                print(f"Updated {rel_path}: {file_replacements} reference(s)")

    action = "Would update" if dry_run else "Updated"
    print(f"\nDone. {action} {total_replacements} reference(s) across {files_changed} file(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update image references in code/markup files to .webp."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all local image references even if no matching .webp file is found on disk",
    )

    args = parser.parse_args()
    if not args.directory.is_dir():
        raise SystemExit(f"Error: '{args.directory}' is not a valid directory.")

    update_references(
        repo_root=args.directory.resolve(),
        dry_run=args.dry_run,
        force_all=args.all,
    )