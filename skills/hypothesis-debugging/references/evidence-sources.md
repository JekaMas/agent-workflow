# Choosing diagnostic evidence

Use the smallest source that distinguishes the hypotheses: exact assertion/fixture for a test mismatch; state/transition records for lifecycle; request/receipt correlation for external action; raw rows and join keys for analyzer errors; readiness and targeted errors for service failure; matched timestamps and policy configuration for latency.

Record confidence with its basis, not a label alone. Direct current source-of-truth observations are stronger than derived reports with unknown inputs. Missing correlation, stale identities and broad timing inference cannot confirm a cause alone. Prefer typed readers and structured outputs; do not expose secrets. Instrument only the missing signal at its owner within current authority.

Before a costly run, state the unresolved hypothesis, why existing/smaller evidence is insufficient, expected distinguishing signals, selection and budget. Use the consumer's runbook, exact run/config identity, gates and cleanup ownership. Do not restart infrastructure reflexively or discard useful failure artifacts. Preserve producer exits while collecting diagnostics; setup failure, missing signals or incomplete collection are inconclusive, never success.

Use passive waits and bounded logs. Choose inspection timing from expected phase/readiness/timeout boundaries and back off on unchanged results. A concrete crash, missed deadline or hang warrants focused inspection. Filter by time/correlation at the source where possible, keep large data incremental and retain bounded failure artifacts with replay/access limits. No universal polling cadence or minimum delay.
