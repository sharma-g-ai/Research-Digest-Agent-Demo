"""arXiv tools for the Research Digest Agent.

Wraps the arxiv Python package to search and fetch papers from arXiv.
The arxiv package handles its own HTTP internally — no httpx or requests needed.
"""

import re

import arxiv
from langchain_core.tools import tool


def _format_result(result: arxiv.Result) -> dict:
    """Format a single arxiv.Result into a standardised dict."""
    # Extract stable ID from entry_id, e.g. http://arxiv.org/abs/2301.07041v2
    raw_id = result.entry_id.split("/abs/")[-1]
    arxiv_id = re.sub(r"v\d+$", "", raw_id)

    # Strip newlines from title
    title = result.title.replace("\n", " ").strip()

    # Normalise abstract: replace newlines with spaces, truncate to 1500 chars
    abstract = result.summary.replace("\n", " ").strip()
    if len(abstract) > 1500:
        truncated = abstract[:1500]
        last_space = truncated.rfind(" ")
        abstract = truncated[:last_space] if last_space != -1 else truncated

    authors = [a.name for a in result.authors]
    first_author = authors[0] if authors else "Unknown"

    year = str(result.published.year)

    categories = result.categories

    pc = getattr(result, "primary_category", None)
    if pc is not None:
        primary_category = pc.term if hasattr(pc, "term") else str(pc)
    elif categories:
        primary_category = categories[0]
    else:
        primary_category = "unknown"

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "first_author": first_author,
        "year": year,
        "categories": categories,
        "primary_category": primary_category,
        "pdf_url": result.pdf_url,
    }


@tool
def search_arxiv(query: str, max_results: int = 5) -> list[dict]:
    """Search arXiv for academic papers matching a query.

    Returns a list of paper dicts, each containing: arxiv_id, title, abstract,
    first_author, year, primary_category, and pdf_url.

    Supports arXiv field syntax:
    - ti: for title search (e.g. ti:transformer)
    - au: for author name (e.g. au:Vaswani)
    - abs: for abstract keyword (e.g. abs:attention)
    - cat: for subject category (e.g. cat:cs.LG for machine learning,
      cat:cs.AI for AI, cat:physics.comp-ph for computational physics)

    Use AND / OR for boolean queries, e.g. ti:diffusion AND cat:cs.CV.
    Default max_results is 5; increase for broader coverage.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    results = []
    try:
        for result in client.results(search):
            results.append(_format_result(result))
    except Exception:
        return []
    if not results:
        return []
    return results


@tool
def fetch_paper(arxiv_id: str) -> dict:
    """Fetch full metadata for a specific arXiv paper by its ID.

    arxiv_id should be in the format 2301.07041 — without a version suffix.
    Returns a single paper dict with all available metadata fields.
    Use this when you need more detail on a specific paper found in search
    results and the abstract alone is insufficient.
    """
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    try:
        result = next(client.results(search))
        return _format_result(result)
    except (StopIteration, Exception):
        return {"error": f"No paper found for arXiv ID {arxiv_id}"}
