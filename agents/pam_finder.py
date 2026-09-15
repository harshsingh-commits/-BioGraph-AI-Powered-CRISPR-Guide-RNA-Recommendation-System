def pam_finder(state):
    sequence = state["sequence"]

    pam_positions = []

    for i in range(len(sequence) - 2):
        triplet = sequence[i : i + 3]

        if triplet[1:] == "GG":
            pam_positions.append(i)

    return {"pam_positions": pam_positions, "pam_count": len(pam_positions)}
