.PHONY: check verify-go-test
CHANGE ?= require-executable-requirement-test-matrices
check:
	python3 -B scripts/test_evidence_graph_check.py
	python3 -B scripts/test_portable_policies.py
	python3 -B scripts/test_full_lifecycle.py
	python3 -B scripts/test_specialist_skills.py
	python3 -B scripts/test_audit_sources.py
	python3 -B scripts/test_bootstrap.py
	python3 -B scripts/test_model_review.py
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_verify.py workflow-tests --cwd . --scope scripts --output-dir data/checks --timeout 120
	python3 -B scripts/requirement_tests.py --root . --change "$(CHANGE)" validate
	python3 -B scripts/discovery_ledger.py --root . --change "$(CHANGE)"
	@evidence_dir=$$(mktemp -d data/checks/requirement-dag.XXXXXX); \
		python3 -B scripts/requirement_tests.py --root . --change "$(CHANGE)" run --all --require-clean --output "$$evidence_dir/result.json"

verify-go-test:
	python3 scripts/local_verify.py go-test --cwd . --package "$(VERIFY_PACKAGES)" --test '$(value VERIFY_TEST)' --scope "$(VERIFY_SCOPE)" --output-dir data/checks
