.PHONY: prepare-pilot score-pilot blind-pilot validate-pilot analyze-pilot prepare-pilot2 generate-pilot2 score-pilot2 sample-pilot2 validate-pilot2 analyze-pilot2 analyze-scorer-sensitivity test

prepare-pilot:
	python3 scripts/prepare_pilot.py

score-pilot:
	PYTHONPATH=. python3 scripts/score_substring.py

blind-pilot:
	python3 scripts/create_blinded_annotation.py

validate-pilot:
	python3 scripts/validate_annotation.py annotations/pilot_annotation_blinded.csv

analyze-pilot:
	PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=.matplotlib-cache python3 scripts/analyze_pilot.py

prepare-pilot2:
	PYTHONPATH=. python3 scripts/prepare_pilot2.py --batch-index 0

generate-pilot2:
	PYTHONPATH=. python3 scripts/generate_pilot2.py --batch-index 0

score-pilot2:
	PYTHONPATH=. python3 scripts/score_pilot2.py

sample-pilot2:
	PYTHONPATH=. python3 scripts/sample_pilot2_annotations.py

validate-pilot2:
	PYTHONPATH=. python3 scripts/validate_pilot2_annotation.py

analyze-pilot2:
	PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=.matplotlib-cache python3 scripts/analyze_pilot2.py

analyze-scorer-sensitivity:
	PYTHONPATH=. MPLBACKEND=Agg MPLCONFIGDIR=.matplotlib-cache python3 scripts/analyze_scorer_sensitivity.py

test:
	PYTHONPATH=. pytest -q
