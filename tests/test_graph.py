from graph import graph


def test_graph_runs_with_small_fasta(tmp_path):
    fasta_path = tmp_path / "demo.fasta"
    fasta_path.write_text(">demo\n" + ("A" * 20) + "AGG\n", encoding="ascii")
    result = graph.invoke({"fasta_file": str(fasta_path)})
    assert result["gene_name"] == "demo"
    assert result["pam_count"] == 1
    assert result["experiment_id"]
    assert result["tracking_backend"] == "jsonl"
