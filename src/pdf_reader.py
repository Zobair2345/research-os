
import requests
import pymupdf


def extract_pdf_text(pdf_url):
    response = requests.get(
        pdf_url,
        timeout=30,
        headers={
            "User-Agent": "ResearchOS/0.1"
        }
    )

    response.raise_for_status()

    pdf_bytes = response.content

    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError(
            "The URL did not return a valid PDF file."
        )

    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        for page_number, page in enumerate(
            document,
            start=1
        ):
            text = page.get_text("text")

            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

    return pages
