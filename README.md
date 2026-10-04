# Yongneup TREED–Pelletier

Automated GitHub Actions runner for the 4 ka Yongneup TREED–Pelletier Step 8 coupling.

Use **Actions → TREED Yongneup Step 8 → Run workflow**. The workflow installs Julia 1.11.6 and Python, restores caches, extracts the audited Step 8 payload, runs the TREED spatial calculation, continues through the R2h EEMT → Pelletier stage, and uploads the result files as a GitHub Actions artifact.

Scientific equations and inputs are kept inside the versioned payload ZIP. The workflow changes orchestration only.

## PB4Studio CHELSA21K

Current Yongneup CHELSA-TraCE21k forcing, raw climate archive, and the PB4Studio model-process/validation note are stored in [`pb4_chelsa21k/`](./pb4_chelsa21k/README.md).

The exact CHELSA21K model archive is stored at [`pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K.zip`](./pb4_chelsa21k/model/PB4Studio_v6.6.3_CHELSA21K.zip).

The CHELSA21K work is kept separate from older Beyer-based PB4 results. New validation numbers must identify the exact forcing, model version, execution status, and validation sample.


## PB4Studio CHELSA21K wetland-ecology dataset

This repository now also preserves the current Yongneup **wetland ecology, palaeoecology, palaeoclimate, and biogeomorphology** PB4Studio/CHELSA21K materials. These files concern ecological and Earth-system research only; they are unrelated to pathogens, toxins, biological weapons, or harmful experimentation.

- Model and process documentation: [pb4_chelsa21k/PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md](pb4_chelsa21k/PB4_CHELSA21K_MODEL_AND_CLIMATE_KO.md)
- Raw 21–0 ka CHELSA-TraCE21k/EnviCloud climate data: `pb4_chelsa21k/data/`
- PB4Studio CHELSA21K reproducibility package: `pb4_chelsa21k/model/`
