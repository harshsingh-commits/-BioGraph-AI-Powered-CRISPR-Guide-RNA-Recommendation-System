# BioGraph Phase 3 Research Mode

## Bowtie2 off-target scanning

The default workflow remains a bounded local estimator so the demo runs without a genome download. To activate indexed alignment mode, install Bowtie2 and provide both environment variables before starting Streamlit:

```powershell
$env:BIOGRAPH_BOWTIE2_PATH = "C:\tools\bowtie2\bowtie2.exe"
$env:BIOGRAPH_BOWTIE2_INDEX = "C:\references\GRCh38\genome"
py -m streamlit run app.py
```

`BIOGRAPH_BOWTIE2_INDEX` is the Bowtie2 index prefix, not a FASTA file. The dashboard labels the active mode and shows reference, position, and mismatch data for returned alignments.

## Research datasets

`utils/research_sources.py` provides small adapters for NCBI Entrez FASTA and Ensembl REST sequence retrieval. NCBI calls require a contact email. Retrieved bytes can be written to a temporary `.fasta` file and passed to the same LangGraph workflow as uploaded data.

## Scope

The current Bowtie2 adapter is an alignment layer, not a complete CRISPR specificity model. Production studies should validate strand handling, PAM compatibility, bulges, scoring thresholds, genome build, and biological annotation against a validated tool such as Cas-OFFinder or a domain-specific pipeline.