

from src.paper_search import search_papers


def main():
    topic = input("Enter a research topic: ")

    try:
        papers = search_papers(topic)

        for index, paper in enumerate(
            papers,
            start=1
        ):
            print(f"\nPaper {index}")
            print(f"Title: {paper['title']}")
            print(f"Year: {paper['year']}")
            print(f"Journal: {paper['journal']}")
            print(f"DOI: {paper['doi']}")
            print(f"Citations: {paper['citations']}")
            print(f"PDF: {paper['pdf_url']}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()

