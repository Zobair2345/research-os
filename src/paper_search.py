
import requests

BASE_URL = "https://api.openalex.org/works"


def search_papers(query, limit=5):
    params = {
        "search": query,
        "per-page": limit
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    papers = []

    for work in data.get("results", []):
        source = work.get("primary_location") or {}
        journal = source.get("source") or {}
        best_oa = work.get("best_oa_location") or {}

        pdf_url = (
            best_oa.get("pdf_url")
            or source.get("pdf_url")
        )

        paper = {
            "title": work.get("title"),
            "year": work.get("publication_year"),
            "journal": journal.get("display_name"),
            "doi": work.get("doi"),
            "citations": work.get("cited_by_count", 0),
            "pdf_url": pdf_url,
        }

        papers.append(paper)

    return papers
