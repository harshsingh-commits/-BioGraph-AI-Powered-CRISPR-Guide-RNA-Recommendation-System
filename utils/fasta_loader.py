from pathlib import Path

from Bio import SeqIO

VALID_BASES = set("ACGTN")


def load_fasta(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {file_path}")

    records = list(SeqIO.parse(path, "fasta"))
    if records:
        record = records[0]
        gene_name = record.id or path.stem
        sequence = str(record.seq).upper().replace(" ", "").replace("\n", "")
    else:
        sequence = (
            path.read_text(encoding="utf-8")
            .replace("\r", "")
            .replace("\n", "")
            .replace(" ", "")
            .upper()
        )
        gene_name = path.stem

    if not sequence:
        raise ValueError("The uploaded sequence is empty.")

    invalid_bases = sorted(set(sequence) - VALID_BASES)
    if invalid_bases:
        invalid = ", ".join(invalid_bases)
        raise ValueError(f"Invalid DNA symbols found: {invalid}. Use A, C, G, T, or N.")

    return {
        "gene_name": gene_name,
        "sequence": sequence,
    }
