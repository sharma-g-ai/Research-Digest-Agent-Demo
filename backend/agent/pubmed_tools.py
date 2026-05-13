"""PubMed tools for Pass 1 of the Research Digest Agent.

Wraps the NCBI E-utilities REST API (ESearch and EFetch) with LangChain @tool
functions. No SDK or subscription required — all calls are plain HTTP via
httpx. Used only in Pass 1; replaced transparently by mcp_tools.py in Pass 2
without any changes to graph.py or prompts.py.
"""

import xml.etree.ElementTree as ET

import httpx
from langchain_core.tools import tool


def _parse_articles(xml_text: str) -> list[dict]:
    """Parse a PubMed EFetch XML response into a list of article dicts.

    Extracts the relevant fields from each PubMedArticle element and returns
    them as plain dicts. Abstract text is truncated to 1500 characters to
    prevent excessive context consumption when multiple results are returned.

    Args:
        xml_text: Raw XML string returned by the NCBI EFetch endpoint.

    Returns:
        A list of dicts, each containing:
            pmid    (str)  — PubMed identifier
            title   (str)  — Article title
            abstract(str)  — Abstract text, truncated to 1500 characters
            journal (str)  — Journal name
            year    (str)  — Publication year
    """
    root = ET.fromstring(xml_text)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID") or ""
        title = article.findtext(".//ArticleTitle") or ""
        abstract = " ".join(
            el.text for el in article.findall(".//AbstractText") if el.text
        )
        if not abstract:
            continue
        journal = article.findtext(".//Journal/Title") or ""
        year = article.findtext(".//PubDate/Year") or ""
        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract[:1500],
            "journal": journal,
            "year": year,
        })
    return articles


@tool
def search_pubmed(query: str, max_results: int = 5) -> list[dict]:
    """Search PubMed and return structured metadata for matching articles.

    Calls the NCBI ESearch endpoint to retrieve PMIDs matching the query, then
    calls EFetch to download full metadata for those articles. Results are
    parsed from XML and returned as a list of article dicts.

    Use this tool to find papers on a topic. Run it at least twice per
    question: once with a broad query to establish the landscape, and once with
    a more targeted follow-up query informed by what the first search returned.

    Supports standard PubMed query syntax including MeSH terms, Boolean
    operators (AND, OR, NOT), field tags (e.g. [Title], [MeSH Terms]), and
    publication type filters (e.g. "randomized controlled trial[pt]").

    Args:
        query: A PubMed search query string.
        max_results: Maximum number of articles to return. Defaults to 5.
            Keep low to stay within context limits.

    Returns:
        A list of dicts, each containing:
            pmid    (str)  — PubMed identifier
            title   (str)  — Article title
            abstract(str)  — Abstract text, truncated to 1500 characters
            journal (str)  — Journal name
            year    (str)  — Publication year
        Returns an empty list if the query matches no articles.
    """
    import os
    email = os.getenv("PUBMED_EMAIL", "")
    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "tool": "research-agent",
        "email": email,
    }
    search_resp = httpx.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params=esearch_params,
    )
    pmids = search_resp.json()["esearchresult"]["idlist"]
    if not pmids:
        return []
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
        "tool": "research-agent",
        "email": email,
    }
    fetch_resp = httpx.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params=efetch_params,
    )
    return _parse_articles(fetch_resp.text)


@tool
def fetch_article(pmid: str) -> dict:
    """Fetch full metadata for a single PubMed article by its PMID.

    Calls the NCBI EFetch endpoint for one article and returns structured
    metadata. Use this tool when a search result looks relevant but its
    abstract is insufficient — for example, when you need to confirm a
    specific detail, check methodology, or verify publication year before
    citing a paper in the digest.

    Do not use this for bulk retrieval; use search_pubmed for that. This tool
    is for targeted follow-up on a specific paper already identified by PMID.

    Args:
        pmid: The PubMed identifier of the article to fetch. Must be a numeric
            string (e.g. "12345678").

    Returns:
        A dict containing:
            pmid    (str)  — PubMed identifier
            title   (str)  — Article title
            abstract(str)  — Abstract text, truncated to 1500 characters
            journal (str)  — Journal name
            year    (str)  — Publication year
        Returns a dict with empty string values if the PMID is not found.
    """
    import os
    email = os.getenv("PUBMED_EMAIL", "")
    efetch_params = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "abstract",
        "retmode": "xml",
        "tool": "research-agent",
        "email": email,
    }
    resp = httpx.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params=efetch_params,
    )
    results = _parse_articles(resp.text)
    if not results:
        return {"error": f"No article found for PMID {pmid}"}
    return results[0]
