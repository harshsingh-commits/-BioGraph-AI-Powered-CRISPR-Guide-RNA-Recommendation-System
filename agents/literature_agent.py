import os
from urllib.parse import quote
from urllib.request import urlopen
from xml.etree import ElementTree


def literature_agent(state):
    query = state.get("literature_query") or os.getenv("BIOGRAPH_LITERATURE_QUERY")
    if not query:
        return {"literature_results": []}

    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        f"?db=pubmed&retmode=xml&retmax=5&term={quote(query)}"
    )
    with urlopen(search_url, timeout=30) as response:
        search_root = ElementTree.fromstring(response.read())
    ids = [node.text for node in search_root.findall(".//Id") if node.text]
    if not ids:
        return {"literature_results": []}

    summary_url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        f"?db=pubmed&retmode=xml&id={','.join(ids)}"
    )
    with urlopen(summary_url, timeout=30) as response:
        summary_root = ElementTree.fromstring(response.read())
    results = []
    for doc in summary_root.findall(".//DocSum"):
        values = {item.attrib.get("Name"): item.text or "" for item in doc.findall("Item")}
        results.append({"pmid": doc.findtext("Id", ""), "title": values.get("Title", "")})
    return {"literature_results": results}
