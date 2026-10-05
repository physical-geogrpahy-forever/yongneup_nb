from run_pelletier_agb_eq5_candidate import reconstruct, patch_candidate, build_candidate_zip

EXPECTED = "3f632362aa9c18786a6e49b84bdd5f9a93653e52287d60ceb67593cffc5de7e8"

z = reconstruct()
root = patch_candidate(z)
got = build_candidate_zip(root)
if got != EXPECTED:
    raise SystemExit(f"candidate ZIP SHA mismatch: {got} != {EXPECTED}")
print(f"CANDIDATE_SHA256={got}")
