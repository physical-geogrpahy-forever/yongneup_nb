# PFT8 canopy-opening threshold 2.70 detailed candidate

This is a sensitivity candidate, not yet production and not original BIOME4.

Rule:

    if PFT7 is woody dominant
    and best grass PFT is PFT8
    and PFT8 NPP > 0
    and PFT8 LAI >= 2.0
    and PFT7 woody LAI < 2.70:
        select PFT8

Full 21-0 ka run summary:

| mode    |   jang_correct |   jang_n |   pft8_positive_steps |   pft8_max_cells |   pft8_max_fraction |   park_2p2_2p7_positive_steps |
|:--------|---------------:|---------:|----------------------:|-----------------:|--------------------:|------------------------------:|
| static  |             24 |       62 |                     0 |                0 |           0         |                             0 |
| dynamic |             55 |       62 |                   101 |                8 |           0.0268456 |                             1 |

Selection principle: this candidate is retained for detailed inspection because it is the largest tested threshold that preserves the existing Jang dynamic 55/62 result while allowing more PFT8 than the 2.65 candidate. Park is not used to tune the threshold.
