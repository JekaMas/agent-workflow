# Extraction evidence

Shared source includes uncommitted extraction files at the time of these checks; Git commits identify the delivered snapshot.

- OpenSpec 1.13.1: `openspec validate --specs --strict --no-interactive`: all three transferred baselines passed.
- `openspec validate share-evidence-language-guidance --type change --strict --no-interactive`: passed.
- `make check`: passed (native lifecycle, specialist graph, source audit, bootstrap, model fixtures and local runner tests); no hosted inference.
- `python3 -B scripts/test_specialist_skills.py`: four tests passed, including missing-reference rejection and shared config/source correspondence.
- Smart Example `make workflow-check`: passed with the initial extraction pin; packaging, 14 operation routes, publication checks, 6 route fixtures, 7 publication fixtures and native/runner tests.
- Consumer `make spec-check CHANGE=generalize-workflow-defaults`: passed.
- `git diff --check`: passed after normalizing inventory CSV newlines. No product tests or live behavior claims.

Preservation: seven wholly generic consumer references become relative links. Mixed Go references retain SDKError/correlation, assertion/helper/context, suppression and command contracts. Rust retains gateway selectors, signing/live gates and command order. Generic test-double rules move to the shared test-boundaries reference; campaign approvals remain local. Review-only authority stays intact; authorized repair no longer requires a separate testing stage.

Baseline provenance: portable-workflow, adaptive-development-workflow and assurance-routing are transferred from the consumer's three workflow migration deltas. Product E2E scenarios and native proof-generator/target obligations remain there. Historical captures are not copied or treated as active procedures.
