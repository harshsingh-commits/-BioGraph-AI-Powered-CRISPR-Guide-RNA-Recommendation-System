from langgraph.graph import StateGraph
from langgraph.types import Send

from agents.approval_gate import approval_gate
from agents.chromosome_scan import chromosome_scan
from agents.efficiency_predictor import efficiency_predictor
from agents.experiment_tracking import experiment_tracking
from agents.gene_analyzer import gene_analyzer
from agents.grna_generator import grna_generator
from agents.literature_agent import literature_agent
from agents.mutation_impact import mutation_impact
from agents.off_target_detector import off_target_detector
from agents.pam_finder import pam_finder
from agents.ranking_engine import ranking_engine
from agents.report_generator import report_generator
from agents.risk_assessor import risk_assessor
from agents.vector_search import vector_search
from state import BioState

builder = StateGraph(BioState)

# Nodes
builder.add_node("gene_analyzer", gene_analyzer)

builder.add_node("pam_finder", pam_finder)

builder.add_node("grna_generator", grna_generator)

builder.add_node("off_target_detector", off_target_detector)

builder.add_node("efficiency_predictor", efficiency_predictor)

builder.add_node("risk_assessor", risk_assessor)

builder.add_node("ranking_engine", ranking_engine)

builder.add_node("report_generator", report_generator)

builder.add_node("approval_gate", approval_gate)

builder.add_node("vector_search", vector_search)
builder.add_node("mutation_impact", mutation_impact)
builder.add_node("literature_agent", literature_agent)
builder.add_node("chromosome_scan", chromosome_scan)
builder.add_node("experiment_tracking", experiment_tracking)

# Entry Point
builder.set_entry_point("gene_analyzer")

# Flow
builder.add_edge("gene_analyzer", "pam_finder")

builder.add_edge("pam_finder", "grna_generator")

builder.add_edge("grna_generator", "off_target_detector")

builder.add_edge("off_target_detector", "efficiency_predictor")


def optimization_route(state):
    scores = state.get("efficiency_scores", [])
    max_efficiency = max((item.get("efficiency", 0) for item in scores), default=0)
    if max_efficiency < 60 and state.get("optimization_attempts", 0) < 2:
        return "optimize"
    return "continue"


builder.add_conditional_edges(
    "efficiency_predictor",
    optimization_route,
    {"optimize": "grna_generator", "continue": "risk_assessor"},
)

builder.add_edge("risk_assessor", "ranking_engine")

builder.add_edge("ranking_engine", "vector_search")

builder.add_edge("vector_search", "mutation_impact")

builder.add_edge("mutation_impact", "literature_agent")


def chromosome_route(state):
    chromosomes = state.get("chromosomes", [])
    if not chromosomes:
        return "continue"
    return [
        Send(
            "chromosome_scan",
            {
                "chromosome": chromosome,
                "off_target_results": state.get("off_target_results", []),
            },
        )
        for chromosome in chromosomes
    ]


builder.add_conditional_edges(
    "literature_agent",
    chromosome_route,
    {"continue": "approval_gate", "chromosome_scan": "chromosome_scan"},
)

builder.add_edge("chromosome_scan", "approval_gate")

builder.add_edge("approval_gate", "report_generator")

builder.add_edge("report_generator", "experiment_tracking")

# Finish Point
builder.set_finish_point("experiment_tracking")

graph = builder.compile()
