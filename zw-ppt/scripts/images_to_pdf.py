#!/usr/bin/env python3

from pathlib import Path
import argparse
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble rendered presentation pages into a 16:9 PDF.")
    parser.add_argument("source", type=Path, help="Directory containing page-*.png images")
    parser.add_argument("output", type=Path, help="Output PDF path")
    parser.add_argument("--width", type=float, default=960, help="PDF page width in points")
    args = parser.parse_args()

    pages = sorted(args.source.glob("page-*.png"))
    if not pages:
        raise SystemExit(f"No page-*.png files found in {args.source}")

    first = ImageReader(str(pages[0]))
    image_width, image_height = first.getSize()
    page_width = args.width
    page_height = page_width * image_height / image_width

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(args.output), pagesize=(page_width, page_height), pageCompression=1)
    for page in pages:
        pdf.drawImage(
            ImageReader(str(page)),
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True,
            mask="auto",
        )
        pdf.showPage()
    pdf.save()
    print(f"Created {args.output} with {len(pages)} pages")


if __name__ == "__main__":
    main()
