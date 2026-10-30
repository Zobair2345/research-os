
from pathlib import Path
import html

import requests
import pymupdf
import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from ollama import ResponseError, RequestError

from src.paper_search import search_papers
from src.pdf_reader import load_research_pdf
from src.ai_explainer import explain_word, simplify_paragraph


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ResearchOS | Academic Workspace",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    css_content = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(
        "<style>" + css_content + "</style>",
        unsafe_allow_html=True
    )

# Additional layout corrections
st.markdown(
    "<style>"
    "[data-testid='stMainBlockContainer'] {"
    "padding-top: 2.5rem !important;"
    "padding-bottom: 2rem !important;"
    "}"
    "[data-testid='stHeader'] {"
    "background: #F8FAFD !important;"
    "}"
    ".researchos-topbar {"
    "display: flex;"
    "align-items: center;"
    "justify-content: space-between;"
    "gap: 16px;"
    "min-height: 28px;"
    "padding: 0;"
    "margin-bottom: 0.5rem;"
    "}"
    ".researchos-eyebrow {"
    "color: #345DE3;"
    "font-size: 12px;"
    "font-weight: 700;"
    "letter-spacing: 1.2px;"
    "line-height: 1.6;"
    "}"
    ".researchos-topbar-description {"
    "color: #667085;"
    "font-size: 13px;"
    "line-height: 1.6;"
    "text-align: right;"
    "}"
    ".hero {"
    "padding: 0.75rem 0 1rem !important;"
    "}"
    ".hero-title {"
    "margin: 0 0 0.5rem !important;"
    "}"
    ".hero-description {"
    "margin: 0 !important;"
    "}"
    "@media (max-width: 768px) {"
    ".researchos-topbar {flex-wrap: wrap;}"
    ".researchos-topbar-description {text-align: left;}"
    "}"
    "</style>",
    unsafe_allow_html=True
)


# =====================================================
# 2. SESSION STATE
# =====================================================

DEFAULT_STATE = {
    "papers": [],
    "selected_paper": None,
    "pages": [],
    "pdf_bytes": None,
    "view": "Discover",
    "ai_result": None,
    "ai_task": None,
    "ai_page": None,
    "ai_level": None,
    "ai_original": None
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


def reset_ai():
    """Clear previous AI explanations."""
    st.session_state.ai_result = None
    st.session_state.ai_task = None
    st.session_state.ai_page = None
    st.session_state.ai_level = None
    st.session_state.ai_original = None


def reset_reader():
    """Clear the currently loaded paper."""
    st.session_state.selected_paper = None
    st.session_state.pages = []
    st.session_state.pdf_bytes = None
    reset_ai()


def open_paper(paper):
    """Download and prepare a research paper."""

    pdf_url = paper.get("pdf_url")

    if not pdf_url:
        st.error("No PDF is available for this paper.")
        return

    try:
        with st.spinner("Preparing your research paper..."):
            document = load_research_pdf(pdf_url)

        st.session_state.selected_paper = paper
        st.session_state.pages = document["pages"]
        st.session_state.pdf_bytes = document["pdf_bytes"]

        reset_ai()

        st.session_state.view = "Reader"
        st.rerun()

    except (
        requests.RequestException,
        ValueError,
        pymupdf.FileDataError
    ) as error:
        st.error(f"Could not open this PDF: {error}")


# =====================================================
# 3. SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("## 📚 ResearchOS")
    st.caption("Your academic workspace")

    st.divider()

    if st.button(
        "🔎 Discover Papers",
        use_container_width=True
    ):
        st.session_state.view = "Discover"
        st.rerun()

    if st.button(
        "📖 Paper Reader",
        use_container_width=True,
        disabled=st.session_state.selected_paper is None
    ):
        st.session_state.view = "Reader"
        st.rerun()

    st.divider()

    st.markdown("#### Reading preferences")

    english_level = st.selectbox(
        "Explanation level",
        ["A1", "A2", "B1", "B2", "C1"],
        index=2,
        key="english_level"
    )

    st.caption(
        "A1 is the simplest English. "
        "C1 uses more advanced academic language."
    )

    st.divider()

    st.caption("Local AI · Ollama")
    st.caption("ResearchOS v0.4")


# =====================================================
# 4. TOP HEADER
# =====================================================

# HTML is written without multiline indentation
# to prevent Markdown treating it as code.

st.markdown(
    '<div class="researchos-topbar">'
    '<span class="researchos-eyebrow">'
    'RESEARCH WORKSPACE'
    '</span>'
    '<span class="researchos-topbar-description">'
    'AI-assisted academic reading'
    '</span>'
    '</div>',
    unsafe_allow_html=True
)


# =====================================================
# 5. DISCOVER PAGE
# =====================================================

if st.session_state.view == "Discover":

    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">'
        'Your research, simplified.'
        '</div>'
        '<div class="hero-description">'
        'Discover academic papers, read original '
        'publications, and understand complex research '
        'with your personal AI assistant.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------------------------------------
    # SEARCH FORM
    # ---------------------------------------------

    with st.container(border=True):

        st.markdown("### Find research papers")

        with st.form("paper_search_form"):

            topic = st.text_input(
                "What are you researching?",
                placeholder=(
                    "Search topics, methods, "
                    "or research questions..."
                )
            )

            search_col, button_col = st.columns(
                [3, 1],
                vertical_alignment="bottom"
            )

            with search_col:

                limit = st.slider(
                    "Results",
                    min_value=5,
                    max_value=30,
                    value=10
                )

            with button_col:

                submitted = st.form_submit_button(
                    "Search Papers",
                    type="primary",
                    use_container_width=True
                )

        if submitted:

            if not topic.strip():
                st.warning("Please enter a research topic.")

            else:
                try:
                    with st.spinner(
                        "Searching academic publications..."
                    ):
                        papers = search_papers(
                            topic.strip(),
                            limit
                        )

                    st.session_state.papers = papers
                    reset_reader()

                    if not papers:
                        st.info("No papers found for this topic.")

                except requests.RequestException as error:
                    st.error(f"Search failed: {error}")

    # ---------------------------------------------
    # SEARCH RESULTS
    # ---------------------------------------------

    if st.session_state.papers:

        st.markdown(
            '<div class="section-heading">'
            'Search results'
            '</div>',
            unsafe_allow_html=True
        )

        st.caption(
            f"{len(st.session_state.papers)} publications found"
        )

        for index, paper in enumerate(
            st.session_state.papers
        ):

            with st.container(border=True):

                title_col, action_col = st.columns(
                    [4, 1],
                    vertical_alignment="center"
                )

                with title_col:

                    safe_title = html.escape(
                        paper.get("title") or "Untitled paper"
                    )

                    st.markdown(f"### {safe_title}")

                    year = paper.get("year") or "N/A"

                    journal = html.escape(
                        paper.get("journal") or "N/A"
                    )

                    citations = paper.get("citations", 0)

                    st.markdown(
                        f'<div class="paper-meta">'
                        f'{year} &nbsp;·&nbsp; '
                        f'{journal} &nbsp;·&nbsp; '
                        f'{citations} citations'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with action_col:

                    if paper.get("pdf_url"):

                        if st.button(
                            "Read Paper",
                            key=f"open_{index}",
                            type="primary",
                            use_container_width=True
                        ):
                            open_paper(paper)

                    else:
                        st.caption("PDF unavailable")

                if paper.get("doi"):
                    st.link_button(
                        "View publication",
                        paper["doi"]
                    )

    else:
        st.info(
            "Search for a topic to begin exploring "
            "academic literature."
        )


# =====================================================
# 6. PAPER READER
# =====================================================

elif st.session_state.view == "Reader":

    paper = st.session_state.selected_paper

    if paper is None:
        st.info("Choose a paper from Discover first.")

    else:

        safe_title = html.escape(
            paper.get("title") or "Untitled paper"
        )

        st.markdown(
            f'<div class="reader-heading">'
            f'{safe_title}'
            f'</div>',
            unsafe_allow_html=True
        )

        year = paper.get("year") or "N/A"

        journal = html.escape(
            paper.get("journal") or "N/A"
        )

        citations = paper.get("citations", 0)

        st.markdown(
            f'<div class="paper-meta">'
            f'{year} &nbsp;·&nbsp; '
            f'{journal} &nbsp;·&nbsp; '
            f'{citations} citations'
            f'</div>',
            unsafe_allow_html=True
        )

        st.write("")

        pages = st.session_state.pages
        pdf_bytes = st.session_state.pdf_bytes

        # ---------------------------------------------
        # TWO-COLUMN LAYOUT
        # ---------------------------------------------

        reader_col, assistant_col = st.columns(
            [1.8, 1],
            gap="large"
        )

        # =============================================
        # LEFT — ORIGINAL PDF
        # =============================================

        with reader_col:

            with st.container(border=True):

                toolbar_left, toolbar_right = st.columns(
                    [3, 1],
                    vertical_alignment="center"
                )

                with toolbar_left:
                    st.markdown("#### Original paper")

                with toolbar_right:
                    st.caption(f"{len(pages)} pages")

                if pdf_bytes:

                    pdf_viewer(
                        input=pdf_bytes,
                        width="100%",
                        height=780
                    )

                    st.download_button(
                        "Download PDF",
                        data=pdf_bytes,
                        file_name="research_paper.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )

                else:
                    st.warning("PDF not available.")

        # =============================================
        # RIGHT — AI ASSISTANT
        # =============================================

        with assistant_col:

            with st.container(border=True):

                st.markdown("### ✨ AI Reading Assistant")

                st.caption(
                    "Understand difficult academic "
                    "language without leaving the paper."
                )

                readable_pages = [
                    page
                    for page in pages
                    if page["text"].strip()
                ]

                if readable_pages:

                    page_numbers = [
                        page["page_number"]
                        for page in readable_pages
                    ]

                    selected_page_number = st.selectbox(
                        "Source page",
                        page_numbers
                    )

                    selected_page = next(
                        page
                        for page in readable_pages
                        if page["page_number"]
                        == selected_page_number
                    )

                    with st.expander(
                        "View extracted page text"
                    ):
                        st.text_area(
                            "Extracted source",
                            value=selected_page["text"],
                            height=230,
                            disabled=True
                        )

                    passage = st.text_area(
                        "Selected sentence or paragraph",
                        placeholder=(
                            "Paste a passage from the "
                            "PDF to explain it..."
                        ),
                        height=140,
                        key=f"passage_{selected_page_number}"
                    )

                    tab1, tab2 = st.tabs([
                        "Vocabulary",
                        "Simplify"
                    ])

                    # =================================
                    # VOCABULARY EXPLANATION
                    # =================================

                    with tab1:

                        word = st.text_input(
                            "Difficult word or phrase",
                            placeholder="e.g. mitigates"
                        )

                        if st.button(
                            "Explain word",
                            type="primary",
                            use_container_width=True
                        ):

                            if not passage.strip():
                                st.warning(
                                    "Paste the surrounding "
                                    "sentence first."
                                )

                            elif not word.strip():
                                st.warning(
                                    "Enter a word or phrase."
                                )

                            else:
                                try:
                                    with st.spinner(
                                        "Generating explanation..."
                                    ):
                                        result = explain_word(
                                            word=word,
                                            context=passage,
                                            level=english_level
                                        )

                                    st.session_state.ai_result = result
                                    st.session_state.ai_task = "Vocabulary"
                                    st.session_state.ai_page = selected_page_number
                                    st.session_state.ai_level = english_level
                                    st.session_state.ai_original = passage

                                except (
                                    RequestError,
                                    ResponseError,
                                    ValueError,
                                    ConnectionError
                                ) as error:
                                    st.error(f"AI error: {error}")

                    # =================================
                    # PARAGRAPH SIMPLIFICATION
                    # =================================

                    with tab2:

                        st.caption(
                            "Rewrite complex academic "
                            "language at your chosen level."
                        )

                        if st.button(
                            "Simplify passage",
                            type="primary",
                            use_container_width=True
                        ):

                            if not passage.strip():
                                st.warning(
                                    "Paste a paragraph first."
                                )

                            else:
                                try:
                                    with st.spinner(
                                        "Simplifying text..."
                                    ):
                                        result = simplify_paragraph(
                                            paragraph=passage,
                                            level=english_level
                                        )

                                    st.session_state.ai_result = result
                                    st.session_state.ai_task = "Simplification"
                                    st.session_state.ai_page = selected_page_number
                                    st.session_state.ai_level = english_level
                                    st.session_state.ai_original = passage

                                except (
                                    RequestError,
                                    ResponseError,
                                    ValueError,
                                    ConnectionError
                                ) as error:
                                    st.error(f"AI error: {error}")

                    # =================================
                    # AI OUTPUT
                    # =================================

                    if (
                        st.session_state.ai_result
                        and st.session_state.ai_page == selected_page_number
                    ):

                        st.divider()

                        st.markdown("#### AI explanation")

                        st.write(st.session_state.ai_result)

                        st.caption(
                            f"{st.session_state.ai_task} · "
                            f"{st.session_state.ai_level} · "
                            f"Page {selected_page_number}"
                        )

                        with st.expander("Compare with original"):
                            st.write(st.session_state.ai_original)

                else:
                    st.warning(
                        "This PDF has no extractable text."
                    )

        st.caption(
            "ResearchOS preserves the original paper. "
            "AI explanations are generated separately "
            "and should be checked for accuracy."
        )
