"""Load text from all gardening PDF documents."""

from pathlib import Path
from typing import Any

from pypdf import PdfReader


def load_pdf_documents(
    folder_path: str = "data/raw_documents",
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """
    Read every PDF and extract text page by page.

    Returns:
        documents: Successfully extracted PDF pages.
        errors: Files that could not be processed.
    """

    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"Document folder was not found: {folder.resolve()}"
        )

    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files were found inside: {folder.resolve()}"
        )

    documents: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for pdf_path in pdf_files:
        try:
            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(
                reader.pages,
                start=1,
            ):
                extracted_text = page.extract_text() or ""

                # Remove unnecessary spaces and line breaks.
                cleaned_text = " ".join(extracted_text.split())

                # Ignore pages with no readable text.
                if not cleaned_text:
                    continue

                documents.append(
                    {
                        "text": cleaned_text,
                        "source": pdf_path.name,
                        "page": page_number,
                    }
                )

        except Exception as error:
            errors.append(
                {
                    "source": pdf_path.name,
                    "error": str(error),
                }
            )

    return documents, errors


if __name__ == "__main__":
    loaded_documents, loading_errors = load_pdf_documents()

    successful_files = {
        document["source"]
        for document in loaded_documents
    }

    print("=" * 50)
    print("HomeGarden LK PDF Loading Results")
    print("=" * 50)

    print(
        f"PDF files successfully read: "
        f"{len(successful_files)}"
    )

    print(
        f"Pages containing readable text: "
        f"{len(loaded_documents)}"
    )

    print(
        f"PDF files with errors: "
        f"{len(loading_errors)}"
    )

    if loading_errors:
        print("\nFiles with errors:")

        for item in loading_errors:
            print(
                f"- {item['source']}: "
                f"{item['error']}"
            )

    print("=" * 50)