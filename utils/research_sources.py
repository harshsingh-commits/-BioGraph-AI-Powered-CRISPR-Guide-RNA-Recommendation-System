from urllib.parse import quote
from urllib.request import Request, urlopen


def fetch_ncbi_fasta(accession: str, email: str) -> bytes:
    """Fetch a FASTA record from NCBI Entrez using an explicit contact email."""
    if not accession.strip() or not email.strip():
        raise ValueError("NCBI accession and contact email are required.")
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        f"?db=nuccore&id={quote(accession.strip())}&rettype=fasta&retmode=text"
        f"&email={quote(email.strip())}"
    )
    with urlopen(url, timeout=30) as response:
        payload = response.read()
    if not payload.startswith(b">"):
        raise ValueError("NCBI did not return a FASTA record.")
    return payload


def fetch_ensembl_fasta(identifier: str) -> bytes:
    """Fetch a genomic FASTA record from the Ensembl REST endpoint."""
    if not identifier.strip():
        raise ValueError("An Ensembl identifier is required.")
    url = f"https://rest.ensembl.org/sequence/id/{quote(identifier.strip())}?content-type=text/x-fasta"
    request = Request(url, headers={"Content-Type": "text/x-fasta", "Accept": "text/x-fasta"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    if not payload.startswith(b">"):
        raise ValueError("Ensembl did not return a FASTA record.")
    return payload
