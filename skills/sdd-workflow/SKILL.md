---
name: sdd-workflow
description: Develop substantial tasks with adaptive planning, meaningful checks and repair across repositories.
---

# Personal SDD router

Resolve the current repository and its applicable instructions first. If it has a
workflow adapter, use that adapter and its selected revision; do not combine a
personal release's runner with another project pin. In an adopted project read
`.agents/workflow-project.json` and `.agents/workflow/docs/project-flow.md`.
In other configured projects follow their declared workflow. Missing dependencies
are reported, not silently replaced by a different checkout.

For an unconfigured repository, use this package's `docs/adoption.md` only when
workflow setup is requested or needed within the authorized task. Do not install
or modify project conventions simply because this skill was selected. Small work
can proceed directly. For substantial authorized work, establish intent and evidence,
then use `skills/openspec-delivery/SKILL.md` from the selected package. Locate package
files relative to this skill's real source directory (resolve symlinks), not cwd.

Select `sdd-go` or `sdd-rust` only for actual language work without an adequate
project equivalent. Load verification-design for consequential evidence/review.
Keep one task list, update plans within intent, continue authorized repair, and
retain exact blockers. No automatic model call, delegation or external action.
