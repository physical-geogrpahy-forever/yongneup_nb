# Yongneup TREED–Pelletier

Automated GitHub Actions runner for the 4 ka Yongneup TREED–Pelletier Step 8 coupling.

Use **Actions → TREED Yongneup Step 8 → Run workflow**. The workflow installs Julia 1.11.6 and Python, restores caches, extracts the audited Step 8 payload, runs the TREED spatial calculation, continues through the R2h EEMT → Pelletier stage, and uploads the result files as a GitHub Actions artifact.

Scientific equations and inputs are kept inside the versioned payload ZIP. The workflow changes orchestration only.
