
import requests
import pymupdf


def load_research_pdf(pdf_url):
    response = requests.get(
        pdf_url,
        timeout=30,
        headers={"User-Agent": "ResearchOS/0.1"}
    )

    response.raise_for_status()

    pdf_bytes = response.content

    if not pdf_bytes.startswith(b"%PDF"):
        raise ValueError("The URL did not return a valid PDF.")

    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        for page_number, page in enumerate(
            document,
            start=1
        ):
            pages.append({
                "page_number": page_number,
                "text": page.get_text("text").strip()
            })

    return {
        "pdf_bytes": pdf_bytes,
        "pages": pages
    }


# Preserve compatibility with existing code
def extract_pdf_text(pdf_url):
    return load_research_pdf(pdf_url)["pages"]
