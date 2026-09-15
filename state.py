import operator
from typing import Annotated, NotRequired, TypedDict


class OffTargetResult(TypedDict):
    guide: str
    off_targets: int
    best_mismatch_count: NotRequired[int]
    locations: NotRequired[list[dict]]


class EfficiencyResult(TypedDict):
    guide: str
    efficiency: float
    gc_content: float
    scoring_model: NotRequired[str]


class RiskResult(TypedDict):
    guide: str
    risk: str
    off_targets: int


class RankedGuide(TypedDict):
    rank: int
    guide: str
    efficiency: float
    risk: str
    risk_score: int
    gc_content: float
    off_targets: int
    final_score: float
    guide_start: NotRequired[int]
    guide_end: NotRequired[int]
    pam_position: NotRequired[int]


class BioState(TypedDict, total=False):

    fasta_file: str

    gene_name: str
    sequence: str

    length: int
    gc_content: float
    at_content: float

    pam_sites: int

    pam_positions: list[int]
    pam_count: int

    candidate_guides: list[str]
    guide_metadata: list[dict]

    off_target_results: list[OffTargetResult]
    off_target_mode: str

    efficiency_scores: list[EfficiencyResult]

    risk_report: list[RiskResult]

    ranked_guides: list[RankedGuide]

    report_path: str
    pdf_report_path: str
    optimization_attempts: int
    approval_required: bool
    approval_status: str
    recommendation_explanation: str
    scoring_model: str
    chromosomes: list[str]
    chromosome: NotRequired[str]
    chromosome_scan_results: Annotated[list[dict], operator.add]
    vector_search_mode: str
    similar_guides: list[dict]
    mutation_impacts: list[dict]
    literature_query: NotRequired[str]
    literature_results: list[dict]
    experiment_id: str
    tracking_backend: str
    tracking_path: str
