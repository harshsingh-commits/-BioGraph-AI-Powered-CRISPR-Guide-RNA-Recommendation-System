from utils.fasta_loader import load_fasta


def gene_analyzer(state):
    data = load_fasta(state["fasta_file"])

    sequence = data["sequence"]

    length = len(sequence)

    gc_count = sequence.count("G") + sequence.count("C")
    at_count = sequence.count("A") + sequence.count("T")

    gc_content = round((gc_count / length) * 100, 2) if length else 0.0
    at_content = round((at_count / length) * 100, 2) if length else 0.0

    pam_sites = sequence.count("GG")

    return {
        "gene_name": data["gene_name"],
        "sequence": sequence,
        "length": length,
        "gc_content": gc_content,
        "at_content": at_content,
        "pam_sites": pam_sites,
    }
