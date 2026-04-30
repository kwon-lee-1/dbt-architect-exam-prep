# Topic 4: Jobs & CI/CD — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 4.1 — CI job concurrency**

Two developers each open a separate PR at the same time against the same dbt project. What does dbt Cloud do with the two CI job runs?

- A) Queues them serially — the second run waits for the first to complete.
- B) Cancels the older run and starts only the newest one.
- C) Runs them concurrently — each gets its own isolated temp schema.
- D) Runs them concurrently only if the account has more than 1 run slot.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Serial queuing is the behavior for the *same PR* with multiple commits — not different PRs. |
> | **B) ❌ Incorrect** | Smart cancellation (cancelling stale builds) applies when the *same PR* receives a new commit, not when two different PRs run simultaneously. |
> | **C) ✅ Correct** | **Different PRs run concurrently** — each CI run gets its own isolated temp schema (`dbt_cloud_pr_<job_id>_<pr_id>`). CI jobs bypass the run slot system entirely, so this concurrency is not limited by available slots. |
> | **D) ❌ Incorrect** | CI jobs bypass the slot system — concurrent CI does not depend on run slot count. |
>
> > 💡 **Key rule**: Different PRs → concurrent CI (each isolated temp schema). Same PR → serial with smart cancellation.

---

### Q2. ⭐
> **Subdomain 4.2 — Command ordering: dbt sl validate**

A CI job is configured with the following command sequence:
1. `dbt sl validate --select state:modified+`
2. `dbt build --select state:modified+`

The CI job consistently fails on step 1. What is the cause?

- A) `dbt sl validate` is not a valid command — the correct syntax is `dbt semantic-layer validate`.
- B) `dbt sl validate` must run before `dbt build` so validation happens against pre-existing models.
- C) `dbt build` must run before `dbt sl validate` — models must be materialized in the CI schema before semantic validation can run.
- D) `--select state:modified+` is not supported by `dbt sl validate`.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt sl validate` is the correct command syntax. |
> | **B) ❌ Incorrect** | This has the order backwards and contradicts the actual requirement. |
> | **C) ✅ Correct** | `dbt sl validate` validates the Semantic Layer against **materialized models in the CI schema**. If `dbt build` hasn't run yet, the models don't exist in the CI schema and semantic validation has nothing to validate against — it fails. `dbt build` must always precede `dbt sl validate`. |
> | **D) ❌ Incorrect** | `--select` flags are supported by `dbt sl validate`. The ordering, not the selector, is the issue. |
>
> > 💡 **Key rule**: `dbt build` must **precede** `dbt sl validate`. Models must exist in CI schema before semantic validation.

---

### Q3. ⭐
> **Subdomain 4.3 — Source freshness: checkbox vs command step**

A deploy job has `dbt source freshness` configured as a **checkbox** (not a command step) and `dbt build` as a command step. The freshness check fails because a source table hasn't been updated in 3 days. What happens next?

- A) The job immediately fails and `dbt build` does not run.
- B) The job continues — `dbt build` runs normally because checkbox failures are isolated from the overall job.
- C) `dbt build` runs but only for models that do not depend on the stale source.
- D) The job pauses and waits for the source to be updated before continuing.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This would be the behavior if `dbt source freshness` were a **command step** — failures in command steps block all subsequent steps. |
> | **B) ✅ Correct** | When `dbt source freshness` is configured as a **checkbox**, its failure is **isolated** — it does not propagate to the overall job status and does not prevent subsequent command steps from running. `dbt build` runs regardless of the freshness result. If you need stale sources to block the build, add `dbt source freshness` as a command step instead. |
> | **C) ❌ Incorrect** | `dbt build` runs the full selected scope — it does not intelligently filter out models with stale upstream sources. |
> | **D) ❌ Incorrect** | Jobs do not pause and wait — they proceed or fail. |
>
> > 💡 **Key rule**: Checkbox failures are **isolated**. Source freshness as checkbox = won't fail the job. As command step = blocks all subsequent steps.

---

### Q4. ⭐
> **Subdomain 4.4 — dbt retry on infrastructure failure**

A production job fails before any models run because of a warehouse connection timeout during job initialization. An on-call engineer runs `dbt retry` to recover. What happens?

- A) `dbt retry` re-runs the entire job from scratch since no nodes completed.
- B) `dbt retry` is a no-op — it reads `run_results.json` to find the failure point, but no nodes were recorded. The engineer must trigger a full job rerun manually.
- C) `dbt retry` automatically detects the infrastructure failure and increases the connection timeout before retrying.
- D) `dbt retry` reconnects to the warehouse and resumes from the last successfully compiled node.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt retry` does not do a full rerun — it reads from `run_results.json` and resumes from the recorded failure point. If there's no recorded failure point, it has nothing to do. |
> | **B) ✅ Correct** | `dbt retry` reads `run_results.json` to find which nodes failed and resumes from that point. If the job failed before **any nodes executed** (infrastructure failure, connection error during init), `run_results.json` contains no nodes to resume from — `dbt retry` is a **no-op**. The engineer must trigger a full job rerun. |
> | **C) ❌ Incorrect** | `dbt retry` has no automatic timeout adjustment capability. |
> | **D) ❌ Incorrect** | `dbt retry` works at the node level (compiled models), not at the connection level. |
>
> > 💡 **Key rule**: `dbt retry` = no-op on infrastructure failures. Only works when nodes are recorded in `run_results.json`.

---

### Q5. ⭐
> **Subdomain 4.5 — Scheduling drift**

A team schedules a dbt job to run "every 2 hours" using interval scheduling. The first run starts at 3:05 AM. When will the next two runs start?

- A) 4:00 AM and 6:00 AM — interval mode aligns to clock hours.
- B) 5:05 AM and 7:05 AM — interval mode tracks elapsed time from the previous run start.
- C) 5:05 AM and 7:05 AM only if the previous run completed within 2 hours.
- D) 4:05 AM and 6:05 AM — the 2-hour interval starts from when the previous run completes, not when it starts.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Interval mode does NOT align to clock hours. That behavior requires cron syntax. |
> | **B) ✅ Correct** | Interval scheduling measures **elapsed time from the previous run start** — it is not clock-aligned. A first run at 3:05 AM → next at 5:05 AM → next at 7:05 AM. This "scheduling drift" is why teams that need exact clock-aligned schedules should use **cron syntax** instead of interval mode. |
> | **C) ❌ Incorrect** | The interval is from run *start*, not run *completion*. Though if a run exceeds the interval, the scheduler cancels queued runs and keeps only the newest. |
> | **D) ❌ Incorrect** | The interval is from run start, not completion. |
>
> > 💡 **Key rule**: Interval scheduling **drifts** — it's elapsed time, not clock-aligned. Use **cron syntax** for fixed clock times.

---

### Q6. ⭐
> **Subdomain 4.6 — Advanced CI: event_time and false positives**

Advanced CI (Compare Changes) is enabled on a CI job. After every PR, the Compare tab shows hundreds of "deleted rows" even though the production data hasn't changed. What configuration is missing?

- A) The model is missing a primary key constraint — without it, Advanced CI can't perform row-level comparison.
- B) `event_time` is not configured on the model. Without it, full tables are compared — the CI's smaller date window looks like deleted rows vs. production.
- C) The CI and production environments are on different database hosts, preventing an accurate comparison.
- D) The `dbt compare` toggle is set to "Continue on error" instead of "Stop on error."

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Missing primary key would cause a "Primary key missing" error — not false "deleted rows." |
> | **B) ✅ Correct** | Without `event_time`, dbt compares **full tables**. CI jobs typically build a smaller time window of data than production — all rows outside the CI window appear as "deleted" in production but not CI. With `event_time` configured, dbt filters both tables to the **overlapping time range** before comparing, eliminating false positives. |
> | **C) ❌ Incorrect** | Different database hosts would cause the comparison to **fail completely**, not produce false deletion results. |
> | **D) ❌ Incorrect** | Stop/continue on error controls linting behavior — it has no effect on row comparison results. |
>
> > 💡 **Key rule**: Without `event_time` → full table comparison → CI's smaller date window = false "deleted rows" on every run.

---

### Q7. ⭐
> **Subdomain 4.7 — Advanced CI: PII in cached rows**

A company enables Advanced CI's Compare Changes feature. A security reviewer discovers that warehouse dynamic data masking policies are not being applied to the rows visible in the Compare tab. Is this expected behavior?

- A) No — this is a bug in Advanced CI. Report it to dbt Labs.
- B) Yes — dynamic data masking does NOT apply to Advanced CI cached samples. All users with job access see the same unmasked cached rows.
- C) No — users only see masked rows unless they have the warehouse masking policy bypass privilege.
- D) Yes — but masking is applied after the 30-day cache expiry when data is reloaded.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is documented, expected behavior — not a bug. |
> | **B) ✅ Correct** | Advanced CI caches up to **100 rows per model** at query time and stores them encrypted in S3/Azure Blob. **Dynamic data masking does NOT apply** to these cached rows — all users with job access see the same unmasked data regardless of their warehouse masking privileges. Sensitive models containing PII should be excluded from Advanced CI comparisons using `--exclude tag:pii`. |
> | **C) ❌ Incorrect** | The cached rows bypass masking entirely — it's not a per-user privilege question. |
> | **D) ❌ Incorrect** | After 30 days the cache expires — data becomes inaccessible entirely. Masking is not retroactively applied at expiry. |
>
> > 💡 **Key rule**: Advanced CI cache = **no dynamic data masking**. Exclude PII models with `--exclude tag:pii`.

---

### Q8.
> **Subdomain 4.8 — Implementing run commands in the correct order**

You are managing a dbt Mesh architecture with an upstream "Platform" project and a downstream "Marketing" project. The Marketing project's CI job fails because an upstream public model in Platform was dropped. You need to adjust the Marketing CI/CD pipeline to handle upstream dependencies without rebuilding the Platform project. Which command configuration is correct?

- A) Use `dbt clone` to copy the Platform project into the Marketing directory before running.
- B) Run `dbt deps` followed by `dbt run` — dbt will automatically build the upstream Platform models.
- C) Configure the Marketing CI job to use `dbt build --defer --state ...` pointing to the Platform production manifest. This allows Marketing models to read from Platform's production tables without rebuilding them.
- D) Add a step to run `dbt run --select source:platform+` to rebuild the upstream dependencies.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt clone` creates zero-copy clones of existing tables in a target schema — it is not designed to copy cross-project source code or manage cross-project manifest references in a Mesh architecture. |
> | **B) ❌ Incorrect** | `dbt deps` only installs package code. Running `dbt run` in Marketing will not build Platform models — `dbt build --select` does NOT trigger upstream project builds across project boundaries. |
> | **C) ✅ Correct** | Using `--defer --state` pointing to the Platform project's production `manifest.json` allows unbuilt upstream models (in Platform) to be resolved against their **production tables** without rebuilding them. This is the standard Mesh CI pattern for consuming downstream projects. |
> | **D) ❌ Incorrect** | `source:platform+` targets source nodes, not cross-project public model nodes. And even if it could, rebuilding Platform in Marketing's CI environment is not the goal. |
>
> > 💡 **Key rule**: Mesh CI pattern = `--defer --state <upstream_manifest>` to resolve cross-project refs against production tables.

---

### Q9.
> **Subdomain 4.9 — Fork PRs**

A developer forks a dbt project repository on GitHub and submits a pull request from their fork. The CI job fails with an error saying it cannot check out the commit. What is the cause and fix?

- A) The developer's fork is on a different GitHub account — add that account as a collaborator.
- B) dbt Cloud cannot check out commits from fork repositories — the developer must push to the origin repository directly.
- C) The CI job needs `--select state:new` instead of `state:modified+` to detect commits from forks.
- D) Fork-based PRs require a service token with write access to the fork repository.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Adding as a collaborator doesn't resolve the fundamental limitation — dbt cannot check out fork commits regardless of permissions. |
> | **B) ✅ Correct** | dbt Cloud cannot check out commits from **forked repositories** — this is a documented limitation. Contributors must push their changes to the **origin (upstream) repository** directly, either as a branch or with write access. Fork-based PRs are not supported for CI. |
> | **C) ❌ Incorrect** | The selector has no bearing on whether dbt can access fork commits. |
> | **D) ❌ Incorrect** | Service tokens don't enable fork checkout — the limitation is architectural, not credential-based. |
>
> > 💡 **Key rule**: Fork PRs = unsupported. Contributors must push to origin repo directly.

---

### Q10.
> **Subdomain 4.10 — PrivateLink and CI hooks**

A company enables PrivateLink for all dbt Cloud connections for security compliance. Shortly after, CI jobs stop running entirely and no error messages appear in the dbt Cloud UI. What is the cause?

- A) PrivateLink requires a VPN client on each developer's machine, which blocks CI from running.
- B) CI hooks are not available with Virtual Private dbt (PrivateLink) — jobs fail silently.
- C) PrivateLink automatically disables webhook triggers, which CI hooks rely on.
- D) PrivateLink connections require the Enterprise+ plan for CI — the company is on Enterprise.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | PrivateLink is a server-side network configuration — it doesn't require VPN clients. |
> | **B) ✅ Correct** | CI hooks (the mechanism that triggers CI jobs from git provider events) are **not available with Virtual Private dbt (PrivateLink)**. The jobs fail silently — no error messages appear in the dbt UI. Check the PrivateLink security settings to identify the conflict. |
> | **C) ❌ Incorrect** | PrivateLink doesn't automatically disable webhooks at the networking level — the issue is at the CI hook layer specifically. |
> | **D) ❌ Incorrect** | This is not a documented plan-level limitation specific to PrivateLink + CI. |
>
> > 💡 **Key rule**: PrivateLink + CI = hooks not available → CI fails **silently**. Plan ahead before enabling PrivateLink.

---

### Q11. ⭐
> **Subdomain 4.11 — Understanding when to use which type of job deferral**

An organization is implementing a dbt Mesh architecture with three separate dbt projects: `staging`, `marts`, and `finance_specific`. The `marts` project depends on models from `staging`. A developer makes a change to a model in the `staging` project. Which of the following is required to correctly implement deferral in the `staging` project's CI job to test the change against the production versions of its downstream dependencies? **Select TWO correct answers.**

- A) The `dbt_project.yml` of the `staging` project must define the `marts` and `finance_specific` projects in its `dependencies.yml` file.
- B) Deferral cannot be used across different dbt projects; each project's entire dependency chain must be fully rebuilt within its own CI job.
- C) The CI job command must use the `--state` flag to point to the production `manifest.json` artifacts of `marts` and `finance_specific`.
- D) The CI job must execute a command that includes the `--defer` flag.

> [!success]- Answer & Explanations
> **✅ Correct: C, D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | In a Mesh architecture, the upstream project (`staging`) does not list its consumers in `dependencies.yml`. The downstream project (`marts`) lists its dependencies. The upstream project's CI job simply tests its own changes. |
> | **B) ❌ Incorrect** | Cross-project deferral is a fundamental feature of dbt Mesh — specifically designed to allow independent projects to interact and test against each other's production state without a monolithic rebuild. |
> | **C) ✅ Correct** | The `--state` flag is used to specify the directory containing the production `manifest.json` artifacts. In dbt Mesh, providing the state of downstream projects allows the CI job to reference production `manifest.json` artifacts of `marts` and `finance_specific`. |
> | **D) ✅ Correct** | The `--defer` flag is used to specify that unselected upstream parents should be resolved against production tables (not rebuilt). This is the core mechanism for deferral in any CI job. |
>
> > 💡 **Key rule**: Standard CI deferral pattern = `dbt build --select state:modified+ --defer --state /path/to/prod/manifest`. Both `--defer` AND `--state` are required.

---

### Q12.
> **Subdomain 4.12 — State selector: --vars invisibility**

A CI job uses `dbt build --select state:modified+ --defer --state /prod/manifest`. A developer changes only the value of a runtime variable in `dbt_project.yml` (e.g., changes `default_event_window: 30` to `default_event_window: 60`). The CI job runs but doesn't build any models. Why?

- A) Variable changes require a `dbt compile` run before `state:modified` can detect them.
- B) `--vars` and `dbt_project.yml` variable changes are **invisible to `state:modified`** — dbt cannot diff variable values between manifests.
- C) The variable was changed in `dbt_project.yml` instead of via `--vars` flag — this is why it wasn't detected.
- D) `state:modified` only detects SQL and YAML config changes, not Python or YAML variable changes.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt compile` doesn't help — the issue is that variable values are not tracked as part of the manifest state diff. |
> | **B) ✅ Correct** | `state:modified` compares node-level SQL content and configs — it **cannot detect changes to variable values** in `dbt_project.yml` or via `--vars`. Only SQL body changes, config changes, or structural changes are diffable. If only a var value changes, affected models will not appear as modified and will not rebuild. |
> | **C) ❌ Incorrect** | The location of the variable change (`dbt_project.yml` vs `--vars`) doesn't matter — neither is tracked by `state:modified`. |
> | **D) ❌ Incorrect** | YAML variable definitions are not tracked even though other YAML config changes are. Variable values are evaluated at runtime, not stored in the manifest diff. |
>
> > 💡 **Key rule**: `--vars` / variable changes are **invisible to `state:modified`**. Only SQL body, configs, and structure are diffable.

---

### Q13. ⭐
> **Subdomain 4.13 — Manifest overwrite: same --state and --target-path**

A CI job is configured as:
```bash
dbt build --select state:modified+ --defer --state ./target --target-path ./target
```
Developers report that every CI run rebuilds the full DAG regardless of how many models were changed. What is the root cause?

- A) The `./target` directory does not exist before the first run, causing state comparison to fail.
- B) `--state` and `--target-path` point to the same directory — dbt overwrites `manifest.json` during parse before state comparison runs, so it always compares against the freshly-written manifest.
- C) The `--defer` flag conflicts with `--state` when they point to the same directory.
- D) CI jobs require an absolute path for `--state` — relative paths cause state comparison failures.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | If the directory doesn't exist, the job would fail with an error — not rebuild the full DAG silently. |
> | **B) ✅ Correct** | This is a critical gotcha: dbt writes a **new `manifest.json`** to `--target-path` during the parse phase, *before* comparing against `--state`. When both point to the same directory, dbt overwrites the production manifest with the freshly-compiled manifest — then compares the fresh manifest against itself. Result: zero differences detected → `state:modified` selects nothing → full build is triggered as fallback. Fix: use **separate directories** for `--state` and `--target-path`. |
> | **C) ❌ Incorrect** | `--defer` and `--state` don't conflict with each other — they're designed to be used together. |
> | **D) ❌ Incorrect** | Relative paths work — the issue is the directory overlap, not the path format. |
>
> > 💡 **Key rule**: `--state` and `--target-path` must point to **separate directories**. Same dir = manifest overwrite = no diff detected.

---

### Q14.
> **Subdomain 4.14 — Graph operators**

Which of the following correctly selects a model named `fct_orders` plus all of its downstream descendants AND all ancestors of those descendants (the full closure)?

- A) `+fct_orders+`
- B) `fct_orders+`
- C) `@fct_orders`
- D) `2+fct_orders+2`

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `+fct_orders+` selects: all ancestors of `fct_orders` + `fct_orders` + all descendants. It does NOT include ancestors of those descendants. |
> | **B) ❌ Incorrect** | `fct_orders+` selects: `fct_orders` + all descendants only. No ancestors included. |
> | **C) ✅ Correct** | `@fct_orders` is the **full closure operator** — it selects: `fct_orders` + all descendants + all ancestors of those descendants. It ensures that everything needed to build the model AND all its downstream tests exists. Commonly used in CI scenarios. |
> | **D) ❌ Incorrect** | `2+fct_orders+2` is bounded depth selection — up to 2 ancestors + `fct_orders` + up to 2 descendants. Not a full closure. |
>
> > 💡 **Key rule**: `@model` = full closure (model + descendants + all ancestors of descendants). Use in CI to ensure all deps exist.

---

### Q15. ⭐
> **Subdomain 4.15 — Self-deferral**

A new CI job is configured with self-deferral (defers against its own previous successful run). On its very first execution, what happens?

- A) The job fails with an error because no prior manifest exists to defer against.
- B) The job runs successfully but builds only the models that `state:modified` identifies.
- C) The job falls back to a full DAG build because there is no prior manifest from a previous run of the same job.
- D) The job skips deferral and uses the production environment's manifest instead.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The job does not fail — it falls back gracefully to a full build. |
> | **B) ❌ Incorrect** | Without a prior manifest, `state:modified` has nothing to compare against — it cannot selectively identify modified models. |
> | **C) ✅ Correct** | Self-deferral requires a prior successful run of the **same job** to produce a manifest. On the first-ever run, no manifest exists — the job falls back to a full DAG build. This is expected behavior, not an error. |
> | **D) ❌ Incorrect** | Self-deferral does not fall back to the production environment's manifest — it falls back to a full build. |
>
> > 💡 **Key rule**: Self-deferral first run = **full DAG build** (no prior manifest). Cost savings only kick in from run 2 onward.

---

### Q16.
> **Subdomain 4.16 — Upstream test failure and downstream SKIP**

A `dbt build` run is executing. A `not_null` test on the `stg_orders` model fails. What happens to all models that depend on `stg_orders`?

- A) They run normally — test failures don't affect downstream model execution.
- B) They fail with an ERROR status — inheriting the upstream test failure.
- C) They enter **SKIP** status — they do not run at all because an upstream dependency failed.
- D) They run but are flagged as "potentially unreliable" in the run results.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Test failures on upstream models do block downstream execution in `dbt build`. |
> | **B) ❌ Incorrect** | Downstream models are not marked as ERROR — they are marked as SKIP. The error is attributed to the failing test, not the downstream models themselves. |
> | **C) ✅ Correct** | In `dbt build`, a failing test on an upstream model causes all downstream dependent models to enter **SKIP** status — they never run. To prevent this blocking behavior, set the test severity to `warn` instead of `error`. |
> | **D) ❌ Incorrect** | There is no "potentially unreliable" status in dbt run results. |
>
> > 💡 **Key rule**: `dbt build` upstream test fail → downstream models = **SKIP** (not ERROR). Use `severity: warn` to prevent blocking.

---

### Q17.
> **Subdomain 4.17 — Unit tests execution order**

When does `dbt build` execute unit tests relative to model materialization?

- A) After all models are materialized — so unit tests validate the final output.
- B) Before model materialization — so unit tests catch logic errors before any expensive table builds.
- C) Concurrently with model materialization — unit tests and builds run in parallel.
- D) At the same time as data tests (schema tests) — all test types run in the same phase.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Running after materialization defeats the purpose of unit tests — you'd spend compute building a table that a unit test immediately invalidates. |
> | **B) ✅ Correct** | Unit tests run **before** model materialization in `dbt build`. If a unit test fails, the model never materializes — saving warehouse compute. This "fail early, fail cheap" design is intentional. |
> | **C) ❌ Incorrect** | Unit tests run in a defined sequential phase, not concurrently with builds. |
> | **D) ❌ Incorrect** | Data tests (schema tests) run after materialization. Unit tests have their own earlier phase. |
>
> > 💡 **Key rule**: Unit tests run **before** materialization. Fail early = cheaper. Data tests run after materialization.

---

### Q18.
> **Subdomain 4.18 — Monorepo CI behavior**

A company stores multiple dbt Cloud projects (Project A, Project B, Project C) in a single monorepo. A developer opens a PR that only modifies files in Project A. What does dbt Cloud do?

- A) Only Project A's CI job triggers — dbt detects which project's files changed.
- B) CI jobs for all three projects (A, B, and C) trigger from the single PR.
- C) No CI jobs trigger — monorepo setups require separate repository connections per project.
- D) Project A's CI job triggers immediately; B and C trigger only if A's CI passes.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not currently perform file-path-based filtering to limit CI triggers to the affected project in a monorepo. |
> | **B) ✅ Correct** | In a monorepo, a **single PR triggers CI jobs for ALL connected dbt projects** — even if only one project's files changed. This is a known limitation. Workaround: use project-specific target branches (e.g., `main-project-a`) to scope CI triggers. |
> | **C) ❌ Incorrect** | Monorepos are supported — each project has its own connection to the shared repository. |
> | **D) ❌ Incorrect** | There is no sequential triggering based on CI success in this scenario — all CI jobs trigger simultaneously. |
>
> > 💡 **Key rule**: Monorepo = single PR triggers CI for **all** connected projects. Workaround: project-specific target branches.

---

### Q19.
> **Subdomain 4.19 — Job chaining plan requirements**

An architect wants to configure Job B in Project B to automatically trigger after Job A in Project A completes. What is the minimum dbt Cloud plan required for this configuration?

- A) Developer plan — job chaining is available on all plans.
- B) Starter plan — job chaining is available on Starter and above.
- C) Enterprise plan — cross-project job chaining requires Enterprise.
- D) Enterprise+ plan — cross-project references require Enterprise+.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Developer plan does **not** support job chaining — it's explicitly excluded. |
> | **B) ✅ Correct** | Job chaining (triggering a job when another job finishes) is available on **Starter and above** — including cross-project chaining. Developer plan is the only tier that doesn't support it. |
> | **C) ❌ Incorrect** | Enterprise is not required — Starter is sufficient for job chaining. |
> | **D) ❌ Incorrect** | Enterprise+ is required for cross-project *ref resolution* (dbt Mesh), not for job chaining. These are different features. |
>
> > 💡 **Key rule**: Job chaining = **Starter+** (not Developer). Can chain across projects. Cross-project *refs* = Enterprise+.

---

### Q20. ⭐
> **Subdomain 4.20 — Configuring Advanced CI**

An organization's dbt project has grown to over 3,000 models, and the full CI run on every pull request now takes over an hour. An architect needs to implement a "Slim CI" strategy to drastically reduce run times while ensuring data quality and integrity for all changes. Which of the following actions should the architect take? **Select TWO correct answers.**

- A) Cache the `dbt_packages` and `target` directories between CI runs to speed up dependency installation and compilation.
- B) Implement a CI job that runs the command `dbt build --select state:modified+ --defer --state ./prod_manifest`.
- C) Configure the CI job to only run `dbt test` for pull requests, relying on developers to test locally.
- D) Increase the size of the data warehouse used for the CI environment to improve query performance.
- E) Disable all tests in the CI environment and run them only in the production job after merging.

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Caching `dbt_packages` avoids repetitive downloads via `dbt deps`, which can take several minutes. Caching the `target` directory enables "Partial Parsing" — dbt only re-parses modified files, significantly reducing compilation phase time. |
> | **B) ✅ Correct** | `dbt build --select state:modified+` runs only modified models and their downstream dependents. `--defer --state` resolves unmodified upstream parents against production tables instead of rebuilding them. This is the canonical "Slim CI" command. |
> | **C) ❌ Incorrect** | Relying on developers to test locally is not a robust strategy for a project of this size. CI ensures project-wide integrity and prevents human error or environmental inconsistencies from entering the production branch. |
> | **D) ❌ Incorrect** | Scaling up the warehouse is a brute-force approach that addresses query speed but not the architectural inefficiency. It also increases costs significantly. |
> | **E) ❌ Incorrect** | Disabling tests in CI removes the safety net that prevents broken code from reaching production. Tests are the point of CI. |
>
> > 💡 **Key rule**: Slim CI = `state:modified+` + `--defer --state` + package/target caching for fastest feedback loop.

---

*[End of Topic 4 — 20 questions]*
