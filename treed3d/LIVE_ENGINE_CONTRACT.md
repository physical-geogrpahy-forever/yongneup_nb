# TREED3D Live Engine contract

This branch is for a live model runner, not a snapshot animation viewer.

Rules:

1. The audited TREED–Direct AGB–Pelletier engine is the authoritative state generator.
2. The 3D renderer may display state, but may not invent ecological state.
3. `step_*` calls must advance model state and return the state produced by the model.
4. Renderer frame skipping must never skip model integration steps.
5. Any future PFT/cohort/understory state must exist in the model state and feed back into model calculations before it is rendered.
6. The current production temporal semantics must be preserved during the first refactor: TREED physiology/soil-water coupling remain as implemented; no fake daily biological state is introduced by interpolation.
7. Scientific extensions (explicit PFT/cohort/understory, daily hydrology/phenology) require separate validation against the pre-extension engine.
