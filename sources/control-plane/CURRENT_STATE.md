# Current State

**As of:** 2026-06-26  
**Profile:** Monocle Man React + ChatGPT-Lab GitHub Pages delivery  
**Overall readiness:** `PARTIAL_USABLE_WITH_GAPS`  
**Benchmark:** Monocle Man SPA

The control plane is active in `grahama1970/chatgpt-lab`. The Monocle Man benchmark fixture has been migrated into the control-plane repository, built, deployed to GitHub Pages, and verified through deterministic GitHub Actions live proof. The previous `snippets` Pages observability blocker is superseded by the self-contained `chatgpt-lab` deployment proof.

## Readiness

| Capability | State | Evidence / caveat |
|---|---|---|
| Persistent ChatGPT Project | `READY` | Project `ChatGPT-Lab` was created by the user and this conversation was moved into it. |
| Dedicated control-plane repository | `READY` | `grahama1970/chatgpt-lab`, branch `main`. |
| Control-plane source check | `PASS` | Source Check run `28245666829` passed at head SHA `064f5fd5b2b52bd1874c205edaeb616f7eae0533` after the WebGPT-requested safe mutation. |
| Self-improvement requirements | `DRAFT_V0.2` | Slice 001 scope, benchmark evidence layout, local-subagent request contract, and schema stubs are recorded. |
| GitHub source read/write | `READY` | ChatGPT Web and project-agent bridge have written to the control-plane repository. Earlier `snippets` writes remain historical bootstrap evidence only. |
| Skill discovery | `READY` | `grahama1970/agent-skills` registry is accessible; latest observed content hash: `2cb9ea5b36cef21e7c2d69e52cfd36da7b2e4f54895b03cbc878b37a64a83025`. |
| Monocle Man benchmark CI | `PASS` | Benchmark run `28245666824` passed at head SHA `064f5fd5b2b52bd1874c205edaeb616f7eae0533`. |
| Monocle Man GitHub Pages workflow | `PASS` | Pages run `28245666963` passed at head SHA `064f5fd5b2b52bd1874c205edaeb616f7eae0533`; build job, configure/upload Pages, deploy, Playwright live proof, artifact upload, and proof commit all succeeded. |
| Verified live deployment | `PASS_WITH_THIRD_PARTY_CAVEAT` | `delivery-proof/monocle-man/latest/deployment-proof.json` records `status: PASS`, page URL `https://grahama1970.github.io/chatgpt-lab/`, HTTP 200, hero assertion true, normal animation `spin`, zero console errors, and committed screenshot paths. Caveat: three aborted third-party `youtube-nocookie.com` telemetry requests after modal interaction; no first-party asset failure observed. |
| Live proof artifact | `READY` | Artifact `monocle-man-live-pages-proof`, ID `7908610801`, digest `sha256:4d5578b91865b52bbdedb1bfef7ca795c9101f515837f0528627b94f33dcae56`, size `5736754`, not expired as of the GitHub artifacts API check. |
| GitHub dispatcher agent-state | `READY_NARROW` | WebGPT wrote `agent-state/next-command.json` as commit `1d2a5e58ff185fdbc6e18042cac980cbb41a94c2`; `webgpt-command-dispatcher.yml` run `28238572045` dispatched `agent-dispatch.yml`; executor run `28238575766` passed and committed `agent-state/last-result.json` as `59e44c80d1acb864b6583bd17c1369d873692030`. |
| Safe mutation command | `PASS_NARROW` | WebGPT wrote `apply-text-patch-proof-001` as commit `5450331fcf932ddcbf79cbea490005f250c7d29e`; dispatcher run `28245510581` triggered executor run `28245515891`; result commit `064f5fd5b2b52bd1874c205edaeb616f7eae0533` changed `monocle-man-site/src/main.jsx` and committed `agent-state/last-result.json` with `status: PASS`. |
| Copilot cloud-agent handoff | `DRAFT_UNPROVEN` | `.github/workflows/assign-copilot-agent.yml` and `scripts/start_copilot_agent_task.py` draft the minimal on-demand Agent Tasks API test. Proof requires `COPILOT_AGENT_TASK_TOKEN` and a run against issue #5. |
| OpenCode GitHub event loop | `SOURCE_ADDED_UNPROVEN` | `.github/workflows/opencode-phatgpt.yml` can start OpenCode from issue/PR events or manual dispatch. It defaults to OpenCode OAuth model `opencode/gpt-5.5` with `medium` reasoning and allows dispatch overrides such as `opencode/deepseek-v4-flash` or `zen-deepseek/deepseek-v4-flash`. `.opencode/agents/phatgpt-dispatcher.md` is the primary agent and routes to coder/reviewer/researcher subagents. A live event run is still required. |
| OpenCode server control surface | `DESIGNED_UNPROVEN` | `opencode serve` is the preferred local/Tailscale HTTP/OpenAPI surface for external broker control. No local server run has been recorded yet. |
| Local worker fallback path | `DRY_RUN_CONTRACT_READY` | `scripts/phatgpt_local_worker_cycle.py` inspects one PR/issue, requires a `phatgpt-task:v1` block, validates `schemas/pr-local-task.schema.json`, and writes a local-subagent receipt. It remains a deterministic smoke/fallback harness rather than the preferred trigger. |
| Shared PhatGPT subagents | `CONTRACTS_ADDED` | Agent contracts exist under `/home/graham/workspace/experiments/agent-skills/agents/phatgpt-coder`, `phatgpt-reviewer`, and `phatgpt-researcher`. They define one-target-per-invocation event workers but are not yet proven in a live OpenCode GitHub/server run. |
| Local/project-agent involvement | `USED_AS_EXECUTION_BRIDGE` | The migration/proof was reported by the project agent and verified through repo artifacts. This proves the self-contained GitHub Actions path, not pure ChatGPT-Web-only autonomy. |
| `$ask webgpt` collaboration | `NEEDS_ATTENTION` | Prior plan-collab attempts were blocked by ambiguous ChatGPT tab identity. |
| Local subagent bridge | `NOT_ESTABLISHED` | Only schema/refusal examples exist. |
| Bounded loop controller | `NOT_ESTABLISHED` | Manual ChatGPT-driven loop and narrow GitHub dispatcher proof exist; deterministic controller script still needs implementation. |

## Current source locations

- Control plane: `grahama1970/chatgpt-lab`, branch `main`
- Requirements: `docs/requirements/SELF_IMPROVEMENT_REQUIREMENTS.md`
- Benchmark source: `grahama1970/chatgpt-lab`, branch `main`, path `monocle-man-site/`
- Migration commit: `05e2ea40f5be30c8b4c494f362cf7624caa408b8`
- Live proof commit: `35125263d78bc4e4b8b3c48485c44568691ba6d1`
- Live site: `https://grahama1970.github.io/chatgpt-lab/`
- GitHub Pages live proof run: `https://github.com/grahama1970/chatgpt-lab/actions/runs/28245666963`
- Benchmark run: `https://github.com/grahama1970/chatgpt-lab/actions/runs/28245666824`
- Source check run: `https://github.com/grahama1970/chatgpt-lab/actions/runs/28245666829`
- Proof JSON: `delivery-proof/monocle-man/latest/deployment-proof.json`
- Screenshots: `delivery-proof/monocle-man/latest/screenshots/`
- Historical React contract benchmark PR: `https://github.com/grahama1970/snippets/pull/3`
- Historical GitHub Pages delivery PR: `https://github.com/grahama1970/snippets/pull/4`
- Historical live delivery proof PR: `https://github.com/grahama1970/snippets/pull/5`
- Historical no-local-agent proof workflow PR: `https://github.com/grahama1970/snippets/pull/6`

## Immediate blockers to a closed project-agent-replacement claim

1. Configure a user-to-server `COPILOT_AGENT_TASK_TOKEN` secret and run `Assign Copilot Agent` for issue #5.
2. Observe whether Copilot cloud opens a scoped PR, records an auth/API blocker, or produces an unscoped output.
3. Run persona-bound `review-design` over committed live screenshots if design readiness is claimed.
4. Run scoped `review-code` over the migrated `chatgpt-lab` Monocle source, workflows, and safe mutation executor.
5. Reconcile the three third-party YouTube telemetry aborts as expected/non-blocking or patch the proof filter to classify them explicitly.
6. Trigger `.github/workflows/opencode-phatgpt.yml` from a real PR comment and preserve the OpenCode PR comment trace.
7. Validate `opencode serve` locally as the Tailscale/broker control surface.
8. Run the role-specific local worker against a real PR/issue only as fallback/smoke evidence.
9. Implement a bounded loop controller script so ChatGPT invokes a deterministic loop rather than acting as the loop in prose.
10. Reduce or explicitly record local project-agent intervention in follow-on workflow dispatch and evidence normalization.

## Next admissible milestone

`USABLE_WITH_GAPS` can be claimed for the **self-contained Monocle deployment** after review artifacts are added or explicitly waived. A broader **project-agent replacement** claim requires:

- repeatable ChatGPT/WebGPT-driven dispatcher command execution without local semantic intervention;
- preserved `$ask webgpt` review artifacts;
- design/code review receipts;
- no live-site claim without proof JSON and screenshots;
- local/project-agent involvement limited to execution receipts, not semantic ownership.
