# Exhaustive investigation policy

Optional preserved investigation policy; applies only where selected by project/user instructions. State missing semantic/index coverage honestly; it is not a required setup step in every adopter.

## Related-code investigation

- Every search for cases, every issue investigation, and every review or check
  of a proposed or implemented fix requires all three searches before any
  completeness, root-cause, sufficiency, verdict, PLAN-freeze, case-freeze, or
  sole-blocker claim: (1) a full related-code search that finds, reads, and
  dispositions every related line across definitions, references, callers,
  callees, constructors, registries, adapters, validators, codecs, persistence,
  lifecycle, observability, recovery, cleanup, tests, templates/generated
  consumers, configuration, and contracts; (2) a full semantic search using the
  applicable index, reference, and call-hierarchy tools and following every
  reachable behavior/ownership edge to closure; and (3) a full similar-case
  search covering every same-failure-class and analogous owner, product, venue,
  protocol, operation, lifecycle state, positive/negative edge, historical fix,
  sibling consumer, and sibling test that can share or contradict the behavior.
  Named files, supplied scopes, representative owners, sampled paths, first
  matches, or the initially suspected owner are starting points, never evidence
  of completeness. Classify every result as changed, preserved, proved,
  irrelevant with an exact reason, or blocked. If any of the three searches
  cannot be completed, state the exact blocker and do not claim completeness.
  This rule takes precedence over read-minimization or context-budget guidance:
  output may be bounded and summarized, but discovery and disposition may not
  be sampled or narrowed.

