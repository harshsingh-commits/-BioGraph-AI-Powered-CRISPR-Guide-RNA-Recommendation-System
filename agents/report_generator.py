from datetime import UTC, datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def report_generator(state):

    reports_dir = Path(__file__).resolve().parents[1] / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / "analysis_report.txt"
    pdf_report_path = reports_dir / "BioGraph_Report.pdf"
    ranked_guides = state.get("ranked_guides", [])

    report = f"""
=============================
BioGraph Analysis Report
=============================

Generated:
{datetime.now(UTC).isoformat()}

Gene Name:
{state.get("gene_name", "N/A")}

Sequence Length:
{state.get("length", 0)}

GC Content:
{state.get("gc_content", 0)} %

AT Content:
{state.get("at_content", 0)} %

PAM Sites:
{state.get("pam_count", state.get("pam_sites", 0))}

Off-target mode:
{state.get("off_target_mode", "local_estimate")}

--------------------------------
Candidate gRNAs
--------------------------------
"""

    guides = state.get("candidate_guides", [])

    for idx, guide in enumerate(guides, start=1):

        report += f"\n{idx}. {guide}"

    report += "\n\n--------------------------------\n"
    report += "Risk Assessment\n"
    report += "--------------------------------\n"

    risks = state.get("risk_report", [])

    for item in risks:

        report += (
            f"\nGuide: {item['guide']}"
            f"\nRisk: {item['risk']}"
            f"\nOff-target hits: {item.get('off_targets', 0)}\n"
        )

    report += "\n--------------------------------\n"
    report += "Guide Ranking\n"
    report += "--------------------------------\n"
    for item in ranked_guides[:10]:
        report += (
            f"\nRank: {item['rank']} | Guide: {item['guide']}"
            f" | Final score: {item['final_score']}"
            f" | Efficiency: {item['efficiency']}%"
            f" | Risk: {item['risk']}\n"
        )

    report += f"\nExplanation:\n{state.get('recommendation_explanation', 'N/A')}\n"

    report += "\n=============================\n"

    with report_path.open("w", encoding="utf-8") as f:
        f.write(report)

    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(
        str(pdf_report_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    elements = [
        Paragraph("BioGraph Analysis Report", styles["Title"]),
        Paragraph(f"Generated: {datetime.now(UTC).isoformat()}", styles["Normal"]),
        Spacer(1, 12),
        Table(
            [
                ["Gene", state.get("gene_name", "N/A")],
                ["Sequence length", f"{state.get('length', 0):,} bp"],
                ["GC content", f"{state.get('gc_content', 0)}%"],
                ["PAM sites", str(state.get("pam_count", state.get("pam_sites", 0)))],
            ],
            colWidths=[1.5 * inch, 4.5 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e7f6f7")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9e2ec")),
                    ("PADDING", (0, 0), (-1, -1), 7),
                ]
            ),
        ),
        Spacer(1, 16),
        Paragraph("Top Guide Recommendations", styles["Heading2"]),
        Paragraph(
            state.get("recommendation_explanation", "Ranking explanation unavailable."),
            styles["Normal"],
        ),
        Spacer(1, 10),
    ]
    ranking_rows = [["Rank", "Guide", "Final score", "Efficiency", "Risk"]]
    ranking_rows.extend(
        [
            [
                item["rank"],
                item["guide"],
                item["final_score"],
                f"{item['efficiency']}%",
                item["risk"],
            ]
            for item in ranked_guides[:10]
        ]
    )
    elements.append(
        Table(
            ranking_rows,
            repeatRows=1,
            colWidths=[0.5 * inch, 2.5 * inch, 1 * inch, 1 * inch, 0.8 * inch],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12344d")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9e2ec")),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        )
    )
    document.build(elements)

    return {
        "report_path": str(report_path),
        "pdf_report_path": str(pdf_report_path),
    }
