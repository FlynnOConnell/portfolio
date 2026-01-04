# /// script
# dependencies = ["markdown"]
# ///

import os
import subprocess
import markdown
from pathlib import Path

# --- Configuration ---
SRC_DIR = Path("./src")
PDF_DIR = Path("./pdf")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Professional Academic CSS Styles
CSS = """
<style>
    :root {
        --primary-color: #000;
        --line-height: 1.4;
        --font-family: "Times New Roman", Times, serif;
    }
    body {
        font-family: var(--font-family);
        line-height: var(--line-height);
        color: var(--primary-color);
        max-width: 850px;
        margin: 0 auto;
        padding: 40px;
        background: #fff;
        font-size: 11pt;
    }
    header {
        text-align: center;
        margin-bottom: 25px;
        /* border-bottom: 2px solid #000; REMOVED */
        padding-bottom: 15px;
    }
    h1 {
        font-size: 24pt;
        margin: 0 0 5px 0;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
    }
    h2 {
        font-size: 14pt;
        /* border-bottom: 1px solid #000; REMOVED */
        padding-bottom: 2px;
        margin-bottom: 12px;
        text-transform: uppercase;
        font-weight: bold;
        margin-top: 20px;
    }
    h3 {
        font-size: 11pt;
        font-weight: bold;
        margin-top: 1.25em;
        margin-bottom: 2px;
        page-break-after: avoid;
    }
    h3 + p {
        margin-top: 0;
        margin-bottom: 6px;
        page-break-before: avoid;
    }
    .date {
        float: right;
    }
    /* Simple list styling */
    ul { margin: 2px 0 0 0; padding-left: 1.2em; }
    li { margin-bottom: 2px; text-align: justify; }
    p { margin: 5px 0; }
    a { color: #000; text-decoration: none; }
    
    @media print {
        body { padding: 0; max-width: 100%; }
        @page { size: letter; margin: 0.75in; }
    }
</style>
"""


def convert_md_to_pdf(md_file: Path):
    """Converts a single markdown file to PDF via HTML intermediate."""
    stem = md_file.stem
    pdf_file = PDF_DIR / f"{stem}.pdf"

    # Validating overwrite behavior
    if pdf_file.exists():
        print(f"[OVERWRITE] {pdf_file.name} already exists, regenerating...")

    print(f"[BUILD] Converting {md_file.name}...")

    # 1. Read Markdown
    try:
        text = md_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {md_file}: {e}")
        return

    # 2. Convert to HTML
    html_body = markdown.markdown(text, extensions=["extra", "smarty"])

    # 3. Wrap in full HTML document with CSS
    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{stem}</title>
        {CSS}
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    temp_html = PDF_DIR / f"{stem}.tmp.html"
    try:
        temp_html.write_text(full_html, encoding="utf-8")
    except Exception as e:
        print(f"Error writing temp html: {e}")
        return

    # 4. Generate PDF using Headless Edge
    try:
        if not os.path.exists(EDGE_PATH):
            raise FileNotFoundError(f"Edge executable not found at: {EDGE_PATH}")

        # Edge print-to-pdf command
        cmd = [
            EDGE_PATH,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={str(pdf_file.absolute())}",
            str(temp_html.absolute()),
        ]

        result = subprocess.run(
            cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if result.returncode == 0:
            print(f"[DONE] Created {pdf_file.name}")
        else:
            print(f"[FAIL] Edge exited with code {result.returncode}")

    except Exception as e:
        print(f"[FAIL] Could not generate PDF: {e}")
    finally:
        # Cleanup temp file
        if temp_html.exists():
            temp_html.unlink()


def main():
    if not SRC_DIR.exists():
        print(f"Source directory '{SRC_DIR}' not found.")
        return

    if not PDF_DIR.exists():
        PDF_DIR.mkdir(parents=True, exist_ok=True)

    md_files = list(SRC_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {SRC_DIR}")
        return

    print(f"Found {len(md_files)} markdown files to process.")
    for md_file in md_files:
        convert_md_to_pdf(md_file)


if __name__ == "__main__":
    main()
