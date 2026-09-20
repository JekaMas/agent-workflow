.PHONY: check verify-go-test
check:
	python3 -B scripts/test_full_lifecycle.py
	python3 -B scripts/test_specialist_skills.py
	python3 -B scripts/test_audit_sources.py
	python3 -B scripts/test_bootstrap.py
	python3 -B scripts/test_model_review.py
	PYTHONDONTWRITEBYTECODE=1 python3 scripts/local_verify.py workflow-tests --cwd . --scope scripts --output-dir data/checks --timeout 120

verify-go-test:
	python3 scripts/local_verify.py go-test --cwd . --package "$(VERIFY_PACKAGES)" --test '$(value VERIFY_TEST)' --scope "$(VERIFY_SCOPE)" --output-dir data/checks
