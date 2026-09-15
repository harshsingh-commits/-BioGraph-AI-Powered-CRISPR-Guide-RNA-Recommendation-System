import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _configured_bowtie2():
    executable = os.getenv("BIOGRAPH_BOWTIE2_PATH") or shutil.which("bowtie2")
    index_prefix = os.getenv("BIOGRAPH_BOWTIE2_INDEX")
    if executable and index_prefix:
        return executable, index_prefix
    return None


def _parse_nm(fields):
    for field in fields:
        if field.startswith("NM:i:"):
            return int(field.split(":")[-1])
    return 0


def _bowtie2_scan(guides, executable, index_prefix):
    with tempfile.TemporaryDirectory(prefix="biograph-bowtie2-") as temp_dir:
        query_path = Path(temp_dir) / "guides.fasta"
        sam_path = Path(temp_dir) / "alignments.sam"
        query_path.write_text(
            "\n".join(f">guide_{index}\n{guide}" for index, guide in enumerate(guides)),
            encoding="ascii",
        )
        command = [
            executable,
            "-x",
            index_prefix,
            "-f",
            "-U",
            str(query_path),
            "-S",
            str(sam_path),
            "--very-sensitive",
            "-N",
            "1",
            "-L",
            "10",
            "-k",
            "100",
            "--no-unal",
            "--quiet",
        ]
        subprocess.run(command, check=True, capture_output=True, text=True)
        locations = {guide: [] for guide in guides}
        with sam_path.open(encoding="utf-8") as sam_file:
            for line in sam_file:
                if line.startswith("@"):
                    continue
                fields = line.rstrip("\n").split("\t")
                if len(fields) < 11 or fields[2] == "*":
                    continue
                guide = guides[int(fields[0].split("_")[-1])]
                locations[guide].append(
                    {
                        "reference": fields[2],
                        "position": int(fields[3]),
                        "mismatches": _parse_nm(fields[11:]),
                    }
                )
        return locations


def _local_scan(guides, sequence):
    window_count = max(0, len(sequence) - 19)
    scan_budget = 5000
    stride = max(1, window_count // scan_budget)
    windows = {(index, sequence[index : index + 20]) for index in range(0, window_count, stride)}
    results = {}
    for guide in guides:
        locations = []
        for index, window in windows:
            if len(window) != len(guide):
                continue
            mismatches = sum(
                base != candidate for base, candidate in zip(guide, window, strict=True)
            )
            if 0 < mismatches <= 2:
                locations.append(
                    {
                        "reference": "uploaded_sequence",
                        "position": index + 1,
                        "mismatches": mismatches,
                    }
                )
        results[guide] = locations
    return results


def off_target_detector(state):
    guides = state["candidate_guides"]
    configured = _configured_bowtie2()
    mode = "bowtie2" if configured else "local_estimate"
    location_map = (
        _bowtie2_scan(guides, *configured) if configured else _local_scan(guides, state["sequence"])
    )

    results = []
    for guide in guides:
        locations = location_map.get(guide, [])
        mismatch_counts = [location["mismatches"] for location in locations]
        results.append(
            {
                "guide": guide,
                "off_targets": len(locations),
                "best_mismatch_count": min(mismatch_counts) if mismatch_counts else 0,
                "locations": locations[:100],
            }
        )

    return {"off_target_results": results, "off_target_mode": mode}
