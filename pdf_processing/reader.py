from pathlib import Path

import pymupdf


DEFAULT_PDF = Path(__file__).resolve().parent.parent / "samples" / "Report1_process.pdf"


def read_pdf(file_path: str | Path) -> str:
    """
    Read text from a PDF file.
    """

    with pymupdf.open(file_path) as document:
        return "".join(page.get_text() for page in document)


def main() -> None:
    text = read_pdf(DEFAULT_PDF)

    print("========== CBC REPORT ==========")
    print(text)


if __name__ == "__main__":
    main()