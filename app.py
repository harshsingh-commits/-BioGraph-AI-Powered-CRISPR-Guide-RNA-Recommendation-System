import os
import tempfile
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

from graph import graph

st.set_page_config(
    page_title="BioGraph | CRISPR Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --ink:#102a43; --muted:#627d98; --line:#d9e2ec; --teal:#087f8c; --navy:#12344d; --paper:#f6f9fb; }
    .stApp { background:var(--paper); color:var(--ink); }
    [data-testid="stHeader"] { background:rgba(246,249,251,.92); }
    [data-testid="stSidebar"] { background:#102a43; }
    [data-testid="stSidebar"] * { color:#f0f4f8; }
    [data-testid="stSidebar"] .stCaption { color:#bcccdc; }
    .brand-mark { color:var(--teal); font-size:3rem; line-height:1; margin-bottom:.5rem; }
    .eyebrow { color:var(--teal); font-size:.74rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
    .hero { border-bottom:1px solid var(--line); padding:.6rem 0 1.7rem; margin-bottom:1.7rem; }
    .hero h1 { color:var(--navy); font-size:3.1rem; letter-spacing:0; margin:0; }
    .hero p { color:var(--muted); font-size:1.08rem; margin:.35rem 0 0; }
    .section-title { color:var(--navy); font-size:1.35rem; font-weight:750; margin:1.55rem 0 .8rem; }
    [data-testid="stMetric"] { background:white; border:1px solid var(--line); border-top:3px solid var(--teal); padding:1rem 1.05rem; box-shadow:0 5px 18px rgba(16,42,67,.05); }
    [data-testid="stMetricLabel"] p { color:var(--muted); }
    [data-testid="stMetricValue"] { color:var(--navy); }
    .recommendation { background:linear-gradient(110deg,#e7f6f7 0%,#fff 72%); border:1px solid #9dd9dc; border-left:5px solid var(--teal); padding:1.15rem 1.35rem; }
    .recommendation strong { color:var(--navy); font-size:1.1rem; }
    .recommendation code { color:var(--teal); font-size:1rem; }
    .risk-badge { border-radius:999px; display:inline-block; font-size:.74rem; font-weight:800; letter-spacing:.06em; padding:.25rem .65rem; }
    .risk-low { background:#d9f2e6; color:#146c43; }
    .risk-medium { background:#fff0c2; color:#9a6700; }
    .risk-high { background:#ffe0e0; color:#b42318; }
    .stage { border-left:2px solid #2cb1bc; margin:.65rem 0; padding-left:.75rem; }
    .stage small { color:#9fb3c8; display:block; font-size:.7rem; letter-spacing:.08em; text-transform:uppercase; }
    div[data-testid="stFileUploader"] { border:1px dashed #9fb3c8; padding:.25rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def frame_guides(guides):
    return pd.DataFrame(
        [{"Guide RNA": guide, "Length": len(guide)} for guide in guides],
        columns=["Guide RNA", "Length"],
    )


def frame_off_targets(results):
    return pd.DataFrame(
        [
            {
                "Guide": item.get("guide", ""),
                "Off Target Hits": item.get("off_targets", 0),
                "Best Mismatch Count": item.get("best_mismatch_count", 0),
            }
            for item in results
        ],
        columns=["Guide", "Off Target Hits", "Best Mismatch Count"],
    )


def frame_locations(results):
    rows = []
    for item in results:
        for location in item.get("locations", []):
            rows.append(
                {
                    "Guide": item.get("guide", ""),
                    "Reference": location.get("reference", ""),
                    "Position": location.get("position", 0),
                    "Mismatches": location.get("mismatches", 0),
                }
            )
    return pd.DataFrame(rows, columns=["Guide", "Reference", "Position", "Mismatches"])


def frame_efficiency(scores):
    return pd.DataFrame(
        [
            {
                "Guide": item.get("guide", ""),
                "Efficiency %": item.get("efficiency", 0),
                "Guide GC %": item.get("gc_content", 0),
            }
            for item in scores
        ],
        columns=["Guide", "Efficiency %", "Guide GC %"],
    ).sort_values("Efficiency %", ascending=False, ignore_index=True)


def frame_ranking(ranked_guides):
    return pd.DataFrame(
        [
            {
                "Rank": item.get("rank", 0),
                "Guide": item.get("guide", ""),
                "Final Score": item.get("final_score", 0),
                "Efficiency %": item.get("efficiency", 0),
                "Risk": item.get("risk", "UNKNOWN"),
                "GC %": item.get("gc_content", 0),
                "Mismatch Hits": item.get("off_targets", 0),
                "Guide Start": item.get("guide_start", 0) + 1,
                "Guide End": item.get("guide_end", 0),
                "PAM Position": item.get("pam_position", 0) + 1,
            }
            for item in ranked_guides
        ],
        columns=[
            "Rank",
            "Guide",
            "Final Score",
            "Efficiency %",
            "Risk",
            "GC %",
            "Mismatch Hits",
            "Guide Start",
            "Guide End",
            "PAM Position",
        ],
    )


def risk_rank(value):
    return {"LOW": 0, "MEDIUM": 1, "HIGH": 2}.get(value, 3)


def render_risk_table(risks):
    if not risks:
        st.info("No risk assessment records were returned.")
        return
    rows = []
    for item in risks:
        risk = str(item.get("risk", "UNKNOWN")).upper()
        risk_class = {"LOW": "low", "MEDIUM": "medium", "HIGH": "high"}.get(risk, "high")
        rows.append(
            f'<tr><td><code>{item.get("guide", "")}</code></td><td><span class="risk-badge risk-{risk_class}">{risk}</span></td></tr>'
        )
    st.markdown(
        '<table style="width:100%;border-collapse:collapse;background:white;">'
        '<thead><tr><th style="text-align:left;padding:.7rem;border-bottom:1px solid #d9e2ec;">Guide</th>'
        '<th style="text-align:left;padding:.7rem;border-bottom:1px solid #d9e2ec;">Risk Level</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>',
        unsafe_allow_html=True,
    )


def run_analysis(uploaded_file):
    api_url = os.getenv("BIOGRAPH_API_URL")
    if api_url:
        token = os.getenv("BIOGRAPH_API_TOKEN")
        if not token:
            login_response = requests.post(
                f"{api_url.rstrip('/')}/auth/login",
                json={
                    "username": os.getenv("BIOGRAPH_API_USER", "researcher"),
                    "password": os.getenv("BIOGRAPH_API_PASSWORD", "researcher"),
                },
                timeout=15,
            )
            login_response.raise_for_status()
            token = login_response.json()["access_token"]
        response = requests.post(
            f"{api_url.rstrip('/')}/analyze",
            files={
                "file": (uploaded_file.name, uploaded_file.getvalue(), "application/octet-stream")
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    suffix = Path(uploaded_file.name).suffix or ".fasta"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        uploaded_path = temp_file.name
    try:
        chromosomes = [
            item.strip()
            for item in os.getenv("BIOGRAPH_CHROMOSOMES", "").split(",")
            if item.strip()
        ]
        return graph.invoke({"fasta_file": uploaded_path, "chromosomes": chromosomes})
    finally:
        Path(uploaded_path).unlink(missing_ok=True)


with st.sidebar:
    st.markdown('<div class="brand-mark">🧬</div>', unsafe_allow_html=True)
    st.markdown("## BioGraph")
    st.caption("Autonomous CRISPR/Cas9 design and mutation risk analysis")
    st.markdown("### Project Description")
    st.caption(
        "A LangGraph workflow that turns a gene sequence into ranked guide RNA candidates and an interpretable off-target risk report."
    )
    st.markdown("### Workflow Stages")
    stages = [
        "Gene Analyzer",
        "PAM Finder",
        "gRNA Generator",
        "Off-Target Detector",
        "Efficiency Predictor",
        "Risk Assessor",
        "Report Generator",
    ]
    for index, stage in enumerate(stages, start=1):
        st.markdown(
            f'<div class="stage"><small>Stage {index:02d}</small>{stage}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("### Upload FASTA File")
    uploaded_files = st.file_uploader(
        "Choose gene sequences",
        type=["fasta", "fa", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )


st.markdown(
    '<div class="hero"><div class="eyebrow">Autonomous sequence intelligence</div><h1>🧬 BioGraph</h1><p>AI-Powered CRISPR Guide RNA Design &amp; Off-Target Risk Analysis</p></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="section-title">Gene Upload</div>', unsafe_allow_html=True)
if not uploaded_files:
    st.info("Upload one or more FASTA, FA, or TXT sequences from the sidebar to begin an analysis.")
    st.stop()

st.success(f"Ready for analysis: **{len(uploaded_files)} gene sequence(s)**")
if st.button("Run CRISPR Analysis", type="primary", use_container_width=True):
    try:
        with st.spinner("Running the BioGraph workflow across seven analysis stages..."):
            results = []
            for uploaded_file in uploaded_files:
                results.append((uploaded_file.name, run_analysis(uploaded_file)))
            st.session_state["analysis_results"] = results
    except Exception as error:
        st.error(f"Analysis failed: {error}")
        st.stop()

analysis_results = st.session_state.get("analysis_results", [])
if not analysis_results:
    st.caption("The workflow is ready. Start the analysis to populate the dashboard.")
    st.stop()

if len(analysis_results) > 1:
    st.markdown('<div class="section-title">Batch Analysis</div>', unsafe_allow_html=True)
    batch_rows = [
        {
            "File": filename,
            "Gene": result.get("gene_name", "N/A"),
            "Length": result.get("length", 0),
            "PAM Count": result.get("pam_count", 0),
            "Top Guide": (result.get("ranked_guides") or [{}])[0].get("guide", "N/A"),
            "Top Score": (result.get("ranked_guides") or [{}])[0].get("final_score", 0),
        }
        for filename, result in analysis_results
    ]
    st.dataframe(pd.DataFrame(batch_rows), use_container_width=True, hide_index=True)
    selected_filename = st.selectbox("Inspect gene", [filename for filename, _ in analysis_results])
    result = next(result for filename, result in analysis_results if filename == selected_filename)
else:
    selected_filename, result = analysis_results[0]

st.caption(f"Analysis complete for **{selected_filename}**")
st.caption(f"Efficiency model: **{result.get('scoring_model', 'gc_heuristic')}**")
st.caption(
    f"Experiment: **{result.get('experiment_id', 'not recorded')}** · Tracking: **{result.get('tracking_backend', 'jsonl')}**"
)
st.markdown('<div class="section-title">Gene Analysis Results</div>', unsafe_allow_html=True)
metric_columns = st.columns(5)
metric_values = [
    ("Gene Name", result.get("gene_name", "N/A")),
    ("Sequence Length", f'{result.get("length", 0):,} bp'),
    ("GC Content", f'{result.get("gc_content", 0):.2f}%'),
    ("AT Content", f'{result.get("at_content", 0):.2f}%'),
    ("PAM Count", result.get("pam_count", result.get("pam_sites", 0))),
]
for column, (label, value) in zip(metric_columns, metric_values, strict=True):
    column.metric(label, value)

st.markdown('<div class="section-title">PAM Finder Results</div>', unsafe_allow_html=True)
st.caption("SpCas9 NGG motifs identified in the uploaded sequence.")
pam_positions = result.get("pam_positions", [])
st.metric("PAM Count", len(pam_positions))
st.dataframe(
    pd.DataFrame({"PAM Position": [position + 1 for position in pam_positions]}),
    use_container_width=True,
    hide_index=True,
)
if pam_positions:
    pam_distribution = (
        pd.cut(
            pd.Series(pam_positions),
            bins=min(20, max(1, len(set(pam_positions)))),
            include_lowest=True,
        )
        .value_counts()
        .sort_index()
    )
    pam_chart = pd.DataFrame(
        {"Position bin": pam_distribution.index.astype(str), "PAM count": pam_distribution.values}
    )
    st.bar_chart(pam_chart.set_index("Position bin"), height=180, color="#2cb1bc")

st.markdown('<div class="section-title">Candidate gRNA Results</div>', unsafe_allow_html=True)
guides = result.get("candidate_guides", [])
st.dataframe(frame_guides(guides), use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Off Target Analysis</div>', unsafe_allow_html=True)
mode = result.get("off_target_mode", "local_estimate")
if mode == "bowtie2":
    st.success("Bowtie2 genome-index scan active.")
else:
    st.warning(
        "Local estimate active. Set BIOGRAPH_BOWTIE2_PATH and BIOGRAPH_BOWTIE2_INDEX for genome-indexed research mode."
    )
st.dataframe(
    frame_off_targets(result.get("off_target_results", [])),
    use_container_width=True,
    hide_index=True,
)
location_table = frame_locations(result.get("off_target_results", []))
if not location_table.empty:
    st.markdown("#### Off-target locations", unsafe_allow_html=True)
    st.dataframe(location_table, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Efficiency Scores</div>', unsafe_allow_html=True)
efficiency_table = frame_efficiency(result.get("efficiency_scores", []))
if efficiency_table.empty:
    st.info("No efficiency scores were returned.")
else:
    st.dataframe(efficiency_table, use_container_width=True, hide_index=True)
    st.bar_chart(efficiency_table.set_index("Guide")["Efficiency %"], height=280, color="#087f8c")
    st.vega_lite_chart(
        efficiency_table,
        {
            "mark": {"type": "bar", "color": "#2cb1bc"},
            "encoding": {
                "x": {"field": "Efficiency %", "bin": {"step": 10}, "title": "Efficiency %"},
                "y": {"aggregate": "count", "title": "Guides"},
            },
            "height": 180,
        },
        use_container_width=True,
    )

st.markdown('<div class="section-title">Risk Assessment</div>', unsafe_allow_html=True)
risk_report = result.get("risk_report", [])
render_risk_table(risk_report)
if risk_report:
    risk_counts = pd.Series([item.get("risk", "UNKNOWN") for item in risk_report]).value_counts()
    risk_chart = pd.DataFrame({"Risk": risk_counts.index, "Guides": risk_counts.values})
    st.vega_lite_chart(
        risk_chart,
        {
            "mark": {"type": "arc", "innerRadius": 35},
            "encoding": {
                "theta": {"field": "Guides", "type": "quantitative"},
                "color": {
                    "field": "Risk",
                    "type": "nominal",
                    "scale": {
                        "domain": ["LOW", "MEDIUM", "HIGH"],
                        "range": ["#10b981", "#f59e0b", "#ef4444"],
                    },
                },
                "tooltip": [{"field": "Risk"}, {"field": "Guides"}],
            },
            "height": 220,
        },
        use_container_width=True,
    )

st.markdown('<div class="section-title">Guide Ranking</div>', unsafe_allow_html=True)
ranking_table = frame_ranking(result.get("ranked_guides", []))
st.dataframe(ranking_table.head(10), use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Research Extensions</div>', unsafe_allow_html=True)
chromosome_results = pd.DataFrame(result.get("chromosome_scan_results", []))
if not chromosome_results.empty:
    st.markdown("#### Parallel chromosome fan-out", unsafe_allow_html=True)
    st.dataframe(chromosome_results, use_container_width=True, hide_index=True)
else:
    st.caption(
        "Chromosome fan-out is opt-in. Set BIOGRAPH_CHROMOSOMES=chr1,chr2,... before starting the app."
    )

similar_guides = pd.DataFrame(result.get("similar_guides", []))
if not similar_guides.empty:
    st.markdown(
        f"#### Similar-guide retrieval ({result.get('vector_search_mode', 'disabled')})",
        unsafe_allow_html=True,
    )
    st.dataframe(similar_guides, use_container_width=True, hide_index=True)

impact_table = pd.DataFrame(result.get("mutation_impacts", []))
if not impact_table.empty:
    st.markdown("#### Mutation impact (heuristic)", unsafe_allow_html=True)
    st.caption(
        "Impact labels are position-based heuristics and require transcript/CDS annotation for biological interpretation."
    )
    st.dataframe(impact_table.head(10), use_container_width=True, hide_index=True)

literature = pd.DataFrame(result.get("literature_results", []))
if not literature.empty:
    st.markdown("#### PubMed evidence", unsafe_allow_html=True)
    st.dataframe(literature, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">Human Approval</div>', unsafe_allow_html=True)
st.caption(
    "Review the ranked recommendation before treating it as approved for experimental planning."
)
approval_key = f"approved_{selected_filename}"
approved = st.checkbox("Approve top-ranked guide", key=approval_key)

st.markdown('<div class="section-title">Final Recommendation</div>', unsafe_allow_html=True)
risk_by_guide = {item.get("guide"): item.get("risk", "UNKNOWN") for item in risk_report}
efficiency_by_guide = {
    item.get("guide"): item.get("efficiency", 0) for item in result.get("efficiency_scores", [])
}
ranked_guides = result.get("ranked_guides", [])
if ranked_guides:
    recommendation = ranked_guides[0]
    recommended_guide = recommendation["guide"]
    recommendation_risk = recommendation["risk"]
    recommendation_efficiency = recommendation["efficiency"]
    st.markdown(
        f'<div class="recommendation"><strong>Recommended guide RNA</strong><br><code>{recommended_guide}</code><br><span>Efficiency: <b>{recommendation_efficiency:.2f}%</b> &nbsp; · &nbsp; Risk: <b>{recommendation_risk}</b></span></div>',
        unsafe_allow_html=True,
    )
    st.info(result.get("recommendation_explanation", "Ranking explanation unavailable."))
else:
    st.warning("No candidate guide was generated for this sequence.")

st.markdown('<div class="section-title">Report Download</div>', unsafe_allow_html=True)
report_path = Path(result.get("report_path", "reports/analysis_report.txt"))
pdf_report_path = Path(result.get("pdf_report_path", "reports/BioGraph_Report.pdf"))
if approved and report_path.exists():
    st.download_button(
        "Download Analysis Report",
        data=report_path.read_bytes(),
        file_name="biograph_analysis_report.txt",
        mime="text/plain",
        type="primary",
    )
    if pdf_report_path.exists():
        st.download_button(
            "Download PDF Report",
            data=pdf_report_path.read_bytes(),
            file_name="BioGraph_Report.pdf",
            mime="application/pdf",
        )
elif not approved:
    st.info("Approve the top-ranked guide to enable report downloads.")
else:
    st.warning("The workflow completed, but no report file was found.")
