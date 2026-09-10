# Confirmatory analysis audit

Status: **PASS**

- Canonical analysis rows: 800
- Canonical analysis dataset SHA-256: `634f4ef28c68696f8c7681fa83827bb12ab6568c5077e9ddf6c926bfe2bf6a3b`
- Bootstrap seed: `2026082207`
- Bootstrap replicates requested: `9999`
- Valid replicates: all main estimands `9999` or more
- Bootstrap unit: base prompt; stratified by task
- Recorded inclusion probabilities and inverse-probability weights used: yes
- S2 implies S0: yes
- AMBIGUOUS rows: 0
- Response generation performed by analysis: no
- Frozen human labels or scorer outputs modified: no
- Deviations from frozen SAP: none

The frozen SAP did not specify a primary bootstrap p-value. Its registered percentile-CI decision rule was applied without substituting a test. GEE p-values are robustness results.
