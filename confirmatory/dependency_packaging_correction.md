# Confirmatory dependency-packaging correction

Discovery date: 2026-08-19 (America/Toronto)

Classification: **implementation/packaging correction; not a scientific protocol deviation**

## Timing and observed failure

This inconsistency was discovered after external preregistration at https://osf.io/9jrab and before generation of any confirmatory victim-model response. The external submission timestamp is preserved as August 19, 2026, 7:06:59 PM. No confirmatory outcome existed or was inspected.

The generic repository file `requirements.txt` pins `transformers==4.52.4`. Installing that file in Google Colab unintentionally downgraded the preflight environment from Transformers 5.15.0 to 4.52.4. The confirmatory runner then stopped before generation with the intended guard: `Transformers must be 5.15.0; found 4.52.4`.

## Dependency-history audit

Git history shows that `requirements.txt` was created in commit `f3bbc613004e3860ffc5e652c9520242854f4787` (`Build reproducible 50-item pilot dataset`) and received only a Matplotlib addition in commit `0731755b87c1cb03b525025d02d39c6b7f3562a2` (`Implement preregistered pilot analysis`). The contemporaneous README places `pip` dependencies from that file under the heading `Pilot workflow`. The file is byte-identical at the externally preregistered commit `853eb6aa7c61e03896cdca3eb991fcf8debdc9cc` and the preparation commit `fc8b78be09c1f742913cdae5190300e395e5bf19`; it was never designated the confirmatory Colab environment.

The authoritative confirmatory records instead specify Transformers 5.15.0:

- `protocol/final_generation_config.yaml` freezes `transformers_version: 5.15.0` for BillSum prompt eligibility.
- `protocol/final_hardware_preflight.md` records the successful Colab preflight with Transformers 5.15.0.
- `protocol/final_preregistration.md` records that same successful environment.
- `scripts/run_confirmatory_generation.py` requires exactly 5.15.0 and fails before model loading or generation on mismatch.

`protocol/final_model_revisions.yaml` lists Transformers 4.52.4 only inside `design_host_reference_software_2026_08_18`, which explicitly says those versions belonged to the insufficient local M3 audit host and are not the successful Colab runtime. Its `confirmed_colab_preflight` section records Transformers 5.15.0.

## Correction

`requirements-confirmatory.txt` is now the only dependency file authorized by the confirmatory Colab instructions. It pins `transformers==5.15.0`. PyTorch is deliberately absent so installing the file cannot replace Colab's CUDA-enabled PyTorch with a CPU or incompatible wheel. The actual CUDA, PyTorch, Hugging Face Hub, NumPy, PyYAML, Accelerate (if present), and other package versions remain runtime provenance unless already frozen elsewhere; no new scientific version requirement is invented.

The historical `requirements.txt` remains unchanged for Pilot 1/Pilot 2 and exploratory reproducibility. It must not be installed for confirmatory generation.

This correction makes execution conform to the externally preregistered environment. H1, RQ2, H3, model/tokenizer identities and revisions, source datasets, 1,680 prompts, 5,040 planned responses, 800-person human sample, injections, targets, S0/S2, annotation rules, generation settings, seeds, exclusions, sampling, statistical methods, multiplicity, and fallbacks are unchanged.

The private prompt manifest remains unchanged at SHA-256 `b183828691c53bd65965cba0c0959f5b5855bd400714ce1724a7b57e885e32ed`. The frozen generation config remains unchanged at SHA-256 `3ddc4670633ad054403a12275f489869e7af689c5daae175b525f3a302b21284`.
