# BioGraph Phase 4 Research Extensions

The Phase 4 nodes are opt-in and expose provenance in the returned state.

## Parallel chromosome fan-out

Set a comma-separated chromosome list to activate LangGraph `Send()` fan-out:

```powershell
$env:BIOGRAPH_CHROMOSOMES = "chr1,chr2,chr3,chrX,chrY"
py -m streamlit run app.py
```

The fan-out summarizes indexed off-target locations by reference name. It requires Bowtie2 mode for meaningful chromosome-level results.

## Scoring and retrieval

`BIOGRAPH_SCORING_MODEL` is recorded in every efficiency result. The current built-in model is `gc_heuristic`; replacing it with a validated Rule Set 2, Azimuth, DeepCRISPR, or CRISPR-Net adapter should happen behind the same scoring contract rather than silently calling a proxy.

Set `BIOGRAPH_VECTOR_BACKEND=faiss` when `faiss-cpu` is installed. Otherwise BioGraph uses a transparent NumPy fallback over guide composition vectors.

## Mutation and literature analysis

Mutation impact is currently a position-based coding-frame heuristic and is labeled as such in the dashboard. For research use, provide transcript/CDS annotations before interpreting frameshift, missense, nonsense, or silent consequences.

Set `BIOGRAPH_LITERATURE_QUERY` to activate the PubMed agent, for example:

```powershell
$env:BIOGRAPH_LITERATURE_QUERY = "BRCA1 CRISPR guide RNA off-target"
```