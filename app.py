
import streamlit as st
import requests
import pymupdf

from src.paper_search import search_papers
from src.pdf_reader import extract_pdf_text


# ----------------------------------
# PAGE CONFIGURATION
# ----------------------------------

st.set_page_config(
    page_title="ResearchOS",
    page_icon="📚",
    layout="wide"
)


# ----------------------------------
# HEADER
# ----------------------------------

st.title("📚 ResearchOS")

st.caption(
    "AI-Powered Academic Research Reader"
)

st.write(
    "Discover academic papers, explore publications, "
    "and read research papers directly inside ResearchOS."
)

st.divider()


# ----------------------------------
# SESSION STATE
# ----------------------------------

if "papers" not in st.session_state:
    st.session_state.papers = []

if "selected_paper" not in st.session_state:
    st.session_state.selected_paper = None

if "pages" not in st.session_state:
    st.session_state.pages = []


# ----------------------------------
# SEARCH SECTION
# ----------------------------------

st.header("🔎 Discover Research Papers")

topic = st.text_input(
    "Enter a research topic",
    placeholder="e.g. Retrieval Augmented Generation"
)

limit = st.slider(
    "Number of results",
    min_value=5,
    max_value=30,
    value=10
)

if st.button("Search Papers", type="primary"):

    if not topic.strip():
        st.warning(
            "Please enter a research topic."
        )

    else:
        try:
            with st.spinner(
                "Searching academic publications..."
            ):
                papers = search_papers(
                    topic,
                    limit
                )

            st.session_state.papers = papers
            st.session_state.selected_paper = None
            st.session_state.pages = []

            if not papers:
                st.info(
                    "No papers found for this topic."
                )

        except requests.RequestException as error:
            st.error(
                f"Search failed: {error}"
            )


# ----------------------------------
# SEARCH RESULTS
# ----------------------------------

if st.session_state.papers:

    st.subheader("Search Results")

    st.write(
        f"Found {len(st.session_state.papers)} papers."
    )

    for index, paper in enumerate(
        st.session_state.papers
    ):

        with st.container(border=True):

            st.subheader(
                paper["title"] or "Untitled paper"
            )

            col1, col2, col3 = st.columns(3)

            col1.write(
                f"**Year:** {paper['year'] or 'N/A'}"
            )

            col2.write(
                f"**Journal:** {paper['journal'] or 'N/A'}"
            )

            col3.write(
                f"**Citations:** {paper['citations']}"
            )

            if paper["doi"]:
                st.link_button(
                    "View Publication",
                    paper["doi"]
                )

            if paper["pdf_url"]:

                if st.button(
                    "📖 Read in ResearchOS",
                    key=f"read_{index}"
                ):

                    try:
                        with st.spinner(
                            "Downloading and extracting PDF..."
                        ):
                            pages = extract_pdf_text(
                                paper["pdf_url"]
                            )

                        st.session_state.selected_paper = paper
                        st.session_state.pages = pages

                        st.success(
                            f"Successfully extracted "
                            f"{len(pages)} pages."
                        )

                    except (
                        requests.RequestException,
                        ValueError,
                        pymupdf.FileDataError
                    ) as error:

                        st.error(
                            f"Unable to read this PDF: {error}"
                        )

            else:
                st.caption(
                    "No open-access PDF available."
                )


# ----------------------------------
# PAPER READER
# ----------------------------------

if st.session_state.selected_paper:

    st.divider()

    st.header("📖 ResearchOS Paper Reader")

    selected = st.session_state.selected_paper

    st.subheader(
        selected["title"] or "Untitled paper"
    )

    st.write(
        f"**Publication Year:** "
        f"{selected['year'] or 'N/A'}"
    )

    st.write(
        f"**Journal:** "
        f"{selected['journal'] or 'N/A'}"
    )

    pages = st.session_state.pages

    st.info(
        f"Total pages: {len(pages)}"
    )

    for page in pages:

        with st.expander(
            f"Page {page['page_number']}"
        ):

            if page["text"]:
                st.text(
                    page["text"]
                )
            else:
                st.warning(
                    "No extractable text found "
                    "on this page."
                )


# ----------------------------------
# FOOTER
# ----------------------------------

st.divider()

st.caption(
    "ResearchOS | Academic Paper Discovery "
    "and Reading Platform"
)
