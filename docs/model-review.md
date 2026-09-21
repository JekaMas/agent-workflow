# Configured model review

[Review modes and provider contract](../skills/verification-design/references/review-modes.md) own provider protocols, keys, inputs, provenance, result interpretation and failure limits. The current agent is the default reviewer; a separate call requires authority for disclosure and spending.

From an adopted consumer, a selected advisory call can use:

```sh
python3 -B .agents/workflow/scripts/model_review.py --provider deepseek --model <account-model-id> \
  --mode implementation --purpose judge --context 32768 --predict 8192 --timeout 120 \
  --dimension implementation_conformance --dimension evidence_completeness \
  --claim '<specific contract claim>' --input <requirement-file> --input <source-file> \
  --input <result-file> --output <new-evidence-directory>
```

Select limits for the packet and account; these example values are not universal budgets. Use `--help` and the provider contract for Claude, Codex API or GLM, URL/key-variable overrides and CA configuration. No model download/server, provider fallback or implicit call is required.
