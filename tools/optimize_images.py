import argparse
from pathlib import Path
from PIL import Image, ImageOps

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"} # everything BUT .webp


def optimize_and_replace(
    directory: Path,
    quality: int = 80,
    max_dimension: int = 1920,
    dry_run: bool = False,
) -> None:
    # Collect all matching files upfront so directory mutations don't affect iteration
    image_files = [
        p
        for p in directory.rglob("*")
        if p.is_file()
        and p.suffix.lower() in SUPPORTED_EXTENSIONS
        and not p.name.startswith(".tmp_")
    ]

    if not image_files:
        print("No matching images found.")
        return

    total_saved_bytes = 0

    for file_path in image_files:
        target_path = file_path.with_suffix(".webp")
        temp_path = file_path.with_name(f".tmp_{file_path.stem}.webp")
        original_size = file_path.stat().st_size

        if dry_run:
            print(f"[DRY RUN] Would convert: {file_path} -> {target_path}")
            continue

        try:
            with Image.open(file_path) as img:
                # Apply EXIF rotation before metadata is stripped during WebP conversion
                img = ImageOps.exif_transpose(img)

                # Normalize color modes for WebP (preserve alpha channel when present)
                if img.mode in ("RGBA", "LA") or (
                    img.mode == "P" and "transparency" in img.info
                ):
                    img = img.convert("RGBA")
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Downscale oversized images while preserving aspect ratio (never upscales)
                if max_dimension:
                    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

                # Write to a temporary file first for atomic replacement
                img.save(temp_path, format="WEBP", quality=quality, method=6)

            if not temp_path.exists() or temp_path.stat().st_size == 0:
                raise RuntimeError("Generated WebP file is empty.")

            new_size = temp_path.stat().st_size

            # Remove original if extension changed, then move temp file into place
            if file_path != target_path and file_path.exists():
                file_path.unlink()
            temp_path.replace(target_path)

            saved = original_size - new_size
            total_saved_bytes += saved
            pct = (saved / original_size * 100) if original_size else 0
            print(f"Optimized: {file_path.name} -> {target_path.name} ({pct:.1f}% smaller)")

        except Exception as exc:
            if temp_path.exists():
                temp_path.unlink()
            print(f"Skipped {file_path}: {exc}")

    if not dry_run:
        print(f"\nDone. Total space saved: {total_saved_bytes / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively optimize images for web and replace them with .webp."
    )
    parser.add_argument("directory", type=Path, help="Target directory containing images")
    parser.add_argument(
        "-q", "--quality", type=int, default=80, help="WebP quality 1-100 (default: 80)"
    )
    parser.add_argument(
        "-m",
        "--max-size",
        type=int,
        default=1920,
        help="Max width/height in pixels; 0 to disable resizing (default: 1920)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview files to be converted without modifying anything",
    )

    args = parser.parse_args()
    if not args.directory.is_dir():
        raise SystemExit(f"Error: '{args.directory}' is not a valid directory.")

    optimize_and_replace(
        directory=args.directory,
        quality=args.quality,
        max_dimension=args.max_size,
        dry_run=args.dry_run,
    )