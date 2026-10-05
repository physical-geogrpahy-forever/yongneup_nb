# PFT5 occurrence audit for Yongneup AGB coupling

Date: 2026-10-05

## Question

Has BIOME4 PFT5 ever been a realized dominant PFT in the retained Yongneup model results?

## Canonical 21-0 ka answer

Model:
- PB4-McKenzie-nativeClimate
- canonical SHA-256: eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d
- climate: YONGNEUP_CHELSA_TRACE21k_ENVICLOUD_RAW_WIDE.csv
- 21.0-0.0 ka BP
- 0.1 kyr interval
- static 211 + dynamic 211

Full PFT coverage audit:

| mode | PFT5 timesteps present | PFT5 dominant cell-observations | max PFT5 cells in one timestep |
|---|---:|---:|---:|
| static | 0 | 0 | 0 |
| dynamic | 0 | 0 | 0 |

Therefore PFT5 is absent from the complete canonical 21-ka dominant-PFT trajectory.

## Earlier hotfix diagnostics

Earlier modified-BIOME4 diagnostics did sometimes relax PFT5 climatic constraints enough for PFT5 NPP to become positive.

This is **not** evidence of PFT5 dominance.

The retained direct competition diagnostics state that:
- native PFT5 often failed the original climate sieve at key Jang ages
- the modified PFT5 could pass after the constraint relaxation
- the strongest conifer/taiga competitor remained mainly PFT6 or PFT7
- PFT5 relaxation was not responsible for the model's validation improvement
- inspected optPFT count records contain PFT4, PFT6, PFT7 and nonvegetated states, not PFT5

No retained Yongneup output or diagnostic inspected in this audit shows PFT5 becoming selected dominant optPFT.

## Scientific consequence

PFT5 should not be used as a weakness or validation target for the Yongneup Xue/IBIS bridge.

For this domain, the AGB scientific basis should focus on:
- PFT4
- PFT6
- PFT7
- PFT10 only as a negligible-contribution structural analogue

The previously executed Xue/IBIS candidate contained a dormant PFT5 coefficient, but because the branch was never realized it changed no AGB value and no geomorphic state.

For a future production implementation:
- do not claim PFT5 is validated for Yongneup
- if PFT5 remains absent, no action is needed
- if a future forcing/model version produces dominant PFT5, fail closed and perform a dedicated literature/observation review before assigning AGB

## Evidence files

- `results/pft_coverage_audit_20261005/PFT_COVERAGE_21KA_SUMMARY.csv`
- `results/pft_coverage_audit_20261005/PFT_COVERAGE_AUDIT_KO.md`
- `results/fourway_20261004/cause_diagnostics/CAUSE_DIAGNOSIS_KO.md`
- `results/fourway_20261004/cause_diagnostics/KEY_AGES_DIRECT_PFT_DIAGNOSTICS.csv`
