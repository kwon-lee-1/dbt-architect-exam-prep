# Topic 4: Jobs & CI/CD — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 4.1 — CI job concurrency**

Two developers each open a separate PR at the same time against the same dbt project. What does dbt Cloud do with the two CI job runs?

- A) Cancels the older run and starts only the newest one.
- B) Queues them serially — the second run waits for the first to complete.
- C) Runs them concurrently only if the account has more than 1 run slot.
- D) Runs them concurrently — each gets its own isolated temp schema.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Smart cancellation (cancelling stale builds) applies when the *same PR* receives a new commit, not when two different PRs run simultaneously. |
> | **B) ❌ Incorrect** | Serial queuing is the behavior for the *same PR* with multiple commits — not different PRs. |
> | **C) ❌ Incorrect** | CI jobs bypass the slot system — concurrent CI does not depend on run slot count. |
> | **D) ✅ Correct** | **Different PRs run concurrently** — each CI run gets its own isolated temp schema (`dbt_cloud_pr_<job_id>_<pr_id>`). CI jobs bypass the run slot system entirely, so this concurrency is not limited by available slots. |
>
> > 💡 **Key rule**: Different PRs → concurrent CI (each isolated temp schema). Same PR → serial with smart cancellation.

---

### Q2. ⭐
> **Subdomain 4.2 — Command ordering: dbt sl validate**

A CI job is configured with the following command sequence:
1. `dbt sl validate --select state:modified+`
2. `dbt build --select state:modified+`

The CI job consistently fails on step 1. What is the cause?

- A) `--select state:modified+` is not supported by `dbt sl validate`.
- B) `dbt build` must run before `dbt sl validate` — that is the order the docs list.
- C) `dbt sl validate` is not a valid command — the correct syntax is `dbt semantic-layer validate`.
- D) `dbt sl validate` must run before `dbt build` so validation happens against pre-existing models.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `--select` flags are supported by `dbt sl validate`. The ordering, not the selector, is the issue. |
> | **B) ✅ Correct** | The docs' CI setup lists `dbt build --select state:modified+` first, then `dbt sl validate --select state:modified+`. |
> | **C) ❌ Incorrect** | `dbt sl validate` is the correct command syntax. |
> | **D) ❌ Incorrect** | This has the order backwards and contradicts the actual requirement. |
>
> > 💡 **Key rule**: `dbt build` goes **before** `dbt sl validate`. That's the order in the docs' CI setup.

---

### Q3. ⭐
> **Subdomain 4.3 — Source freshness: checkbox vs command step**

A deploy job has `dbt source freshness` configured as a **checkbox** (not a command step) and `dbt build` as a command step. The freshness check fails because a source table hasn't been updated in 3 days. What happens next?

- A) The job immediately fails and `dbt build` does not run.
- B) The job continues — `dbt build` runs normally because checkbox failures are isolated from the overall job.
- C) The job pauses and waits for the source to be updated before continuing.
- D) `dbt build` runs but only for models that do not depend on the stale source.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This would be the behavior if `dbt source freshness` were a **command step** — failures in command steps block all subsequent steps. |
> | **B) ✅ Correct** | When `dbt source freshness` is configured as a **checkbox**, its failure is **isolated** — it does not propagate to the overall job status and does not prevent subsequent command steps from running. `dbt build` runs regardless of the freshness result. If you need stale sources to block the build, add `dbt source freshness` as a command step instead. |
> | **C) ❌ Incorrect** | Jobs do not pause and wait — they proceed or fail. |
> | **D) ❌ Incorrect** | `dbt build` runs the full selected scope — it does not intelligently filter out models with stale upstream sources. |
>
> > 💡 **Key rule**: Checkbox failures are **isolated**. Source freshness as checkbox = won't fail the job. As command step = blocks all subsequent steps.

---

### Q4. ⭐
> **Subdomain 4.4 — dbt retry on infrastructure failure**

A production job fails before any models run because of a warehouse connection timeout during job initialization. An on-call engineer runs `dbt retry` to recover. What happens?

- A) `dbt retry` re-runs the entire job from scratch since no nodes completed.
- B) `dbt retry` automatically detects the infrastructure failure and increases the connection timeout before retrying.
- C) `dbt retry` is a no-op — it reads `run_results.json` to find the failure point, but no nodes were recorded. The engineer must trigger a full job rerun manually.
- D) `dbt retry` reconnects to the warehouse and resumes from the last successfully compiled node.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt retry` does not do a full rerun — it reads from `run_results.json` and resumes from the recorded failure point. If there's no recorded failure point, it has nothing to do. |
> | **B) ❌ Incorrect** | `dbt retry` has no automatic timeout adjustment capability. |
> | **C) ✅ Correct** | `dbt retry` reads `run_results.json` to find which nodes failed and resumes from that point. If the job failed before **any nodes executed** (infrastructure failure, connection error during init), `run_results.json` contains no nodes to resume from — `dbt retry` is a **no-op**. The engineer must trigger a full job rerun. |
> | **D) ❌ Incorrect** | `dbt retry` works at the node level (compiled models), not at the connection level. |
>
> > 💡 **Key rule**: `dbt retry` = no-op on infrastructure failures. Only works when nodes are recorded in `run_results.json`.

---

### Q5. ⭐
> **Subdomain 4.5 — Scheduling: exact clock times**

A team needs a job to run at exactly 4:05 AM UTC every day. Which schedule type should they use?

- A) Intervals, every 24 hours.
- B) Specific hours, `4`.
- C) Cron, `5 4 * * *`.
- D) Intervals, every 2 hours.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Intervals run every N hours counted from midnight UTC. You can't pick minute 5. |
> | **B) ❌ Incorrect** | Specific hours takes a comma-separated list of whole UTC hours, so this would run at 4:00. |
> | **C) ✅ Correct** | Cron gives exact times. `5 4 * * *` runs at 4:05 AM UTC. `L` (last day of month) and `MON#1` (first Monday) also work. |
> | **D) ❌ Incorrect** | Intervals of 2 hours can't produce a 4:05 daily run. |
>
> > 💡 **Key rule**: Intervals = every N hours from midnight UTC. Specific hours = whole UTC hours. Cron = exact times. Everything is UTC, with no daylight saving adjustment.

---

### Q6. ⭐
> **Subdomain 4.6 — Advanced CI: event_time and false positives**

Advanced CI (Compare Changes) is enabled on a CI job. After every PR, the Compare tab shows hundreds of "deleted rows" even though the production data hasn't changed. What configuration is missing?

- A) The `dbt compare` toggle is set to "Continue on error" instead of "Stop on error."
- B) The model is missing a primary key constraint — without it, Advanced CI can't perform row-level comparison.
- C) The CI and production environments are on different database hosts, preventing an accurate comparison.
- D) `event_time` is not configured on the model. Without it, full tables are compared — the CI's smaller date window looks like deleted rows vs. production.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Stop/continue on error controls linting behavior — it has no effect on row comparison results. |
> | **B) ❌ Incorrect** | Missing primary key would cause a "Primary key missing" error — not false "deleted rows." |
> | **C) ❌ Incorrect** | Different database hosts would cause the comparison to **fail completely**, not produce false deletion results. |
> | **D) ✅ Correct** | Without `event_time`, dbt compares **full tables**. CI jobs typically build a smaller time window of data than production — all rows outside the CI window appear as "deleted" in production but not CI. With `event_time` configured, dbt filters both tables to the **overlapping time range** before comparing, eliminating false positives. |
>
> > 💡 **Key rule**: Without `event_time` → full table comparison → CI's smaller date window = false "deleted rows" on every run.

---

### Q7. ⭐
> **Subdomain 4.7 — Advanced CI: PII in cached rows**

A company enables Advanced CI's Compare Changes feature. A security reviewer discovers that warehouse dynamic data masking policies are not being applied to the rows visible in the Compare tab. Is this expected behavior?

- A) Yes — dynamic data masking does NOT apply to Advanced CI cached samples. All account users can see the unmasked cached rows.
- B) No — users only see masked rows unless they have the warehouse masking policy bypass privilege.
- C) No — this is a bug in Advanced CI. Report it to dbt Labs.
- D) Yes — but masking is applied after the 30-day cache expiry when data is reloaded.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Advanced CI caches up to **100 rows per model** at query time and stores them encrypted in S3/Azure Blob. **Dynamic data masking does NOT apply** to these cached rows — the cached data is not dynamically masked, and the docs say all account users can view the comparison results and cached data. Restrict the CI environment's credentials, or use synthetic data. |
> | **B) ❌ Incorrect** | The cached rows bypass masking entirely — it's not a per-user privilege question. |
> | **C) ❌ Incorrect** | This is documented, expected behavior — not a bug. |
> | **D) ❌ Incorrect** | After 30 days the cache expires — data becomes inaccessible entirely. Masking is not retroactively applied at expiry. |
>
> > 💡 **Key rule**: Advanced CI cache = **no dynamic data masking**. Restrict the CI environment's credentials, or use synthetic data.

---

### Q8.
> **Subdomain 4.8 — Cross-project refs in a job**

A downstream project's models use `ref('platform', 'dim_customers')`, a public model in an upstream project. The job runs without rebuilding the upstream project. What resolves the ref?

- A) dbt's metadata service, which points it at the upstream project's Production environment (or its Staging environment, for downstream Development and Staging runs, when Staging exists).
- B) A `--state` flag pointing at the upstream project's `manifest.json`.
- C) The downstream job rebuilds the upstream project first.
- D) `dbt deps` copies the upstream models into the downstream project.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say dbt uses a metadata service to resolve references to public models in other projects on the fly. Downstream Production resolves to upstream Production. Downstream Staging and Development resolve to upstream Staging if it exists, otherwise Production. |
> | **B) ❌ Incorrect** | Not how project dependencies work. The metadata service does the resolving. |
> | **C) ❌ Incorrect** | Upstream models are not parsed or run in the downstream project. |
> | **D) ❌ Incorrect** | `dbt deps` installs packages. Project dependencies go in `dependencies.yml`. |
>
> > 💡 **Key rule**: Cross-project `ref('project', 'model')` resolves through the metadata service to the upstream's Production (or Staging). The upstream project is not rebuilt.

---

### Q9.
> **Subdomain 4.9 — Fork PRs**

A developer forks a dbt project repository on GitHub and submits a pull request from their fork. The job fails at the Clone Git Repository step with "Failed to checkout to specified revision." What is the cause and fix?

- A) The CI job needs `--select state:new` instead of `state:modified+` to detect commits from forks.
- B) dbt Cloud cannot check out commits from fork repositories — the developer must push to the origin repository directly.
- C) The developer's fork is on a different GitHub account — add that account as a collaborator.
- D) Fork-based PRs require a service token with write access to the fork repository.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The selector has no bearing on whether dbt can access fork commits. |
> | **B) ✅ Correct** | The docs say dbt can only check out commits that belong to the **original repository**, not commits that belong to a fork. Push the branch to the original repo. |
> | **C) ❌ Incorrect** | Not a documented fix. dbt can only check out commits from the original repo. |
> | **D) ❌ Incorrect** | Not a documented fix. |
>
> > 💡 **Key rule**: dbt only checks out commits from the original repo. Push the branch there.

---

### Q10.
> **Subdomain 4.10 — PrivateLink and CI hooks**

A company enables PrivateLink for all dbt Cloud connections for security compliance. Shortly after, CI jobs stop running entirely and no error messages appear in the dbt Cloud UI. What is the cause?

- A) PrivateLink requires a VPN client on each developer's machine, which blocks CI from running.
- B) PrivateLink connections require the Enterprise+ plan for CI — the company is on Enterprise.
- C) With ingress PrivateLink or IP allowlisting, CI hooks may not be available, and the job can fail silently.
- D) PrivateLink automatically disables webhook triggers, which CI hooks rely on.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | PrivateLink is a server-side network configuration — it doesn't require VPN clients. |
> | **B) ❌ Incorrect** | This is not a documented plan-level limitation specific to PrivateLink + CI. |
> | **C) ✅ Correct** | The docs say that on Enterprise plans with ingress PrivateLink or IP allowlisting, registering CI hooks may not be available and can cause the job to fail silently. |
> | **D) ❌ Incorrect** | PrivateLink doesn't automatically disable webhooks at the networking level — the issue is at the CI hook layer specifically. |
>
> > 💡 **Key rule**: Ingress PrivateLink or IP allowlisting: CI hooks may be unavailable → CI can fail **silently**.

---

### Q11. ⭐
> **Subdomain 4.11 — Understanding when to use which type of job deferral**

A deploy job has "Compare changes against" set to **Environment** instead of **This Job**. What does that change?

- A) It defers to a hand-picked job ID in that environment.
- B) It compares against the job's own last successful run.
- C) It turns deferral off.
- D) It compares against the latest successful run in that environment, from any deploy job that updates artifacts there.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say built-in deferral targets an environment, not a hand-picked job ID. |
> | **B) ❌ Incorrect** | That is **This Job** (self-deferral), the older behavior. |
> | **C) ❌ Incorrect** | Deferral off is **No deferral**, the default for deploy jobs. |
> | **D) ✅ Correct** | Environment deferral considers all deploy jobs that run in the deferred environment. The docs call it more efficient and more accurate than deferring to one job. |
>
> > 💡 **Key rule**: Deploy job default = No deferral. CI job default = Production environment. **Environment** (recommended) = latest successful run there from any job. **This Job** = that job's own last successful run.

---

### Q12.
> **Subdomain 4.12 — State selector: --vars invisibility**

A CI job uses `dbt build --select state:modified+ --defer --state /prod/manifest`. A developer changes only the value of a runtime variable in `dbt_project.yml` (e.g., changes `default_event_window: 30` to `default_event_window: 60`). The CI job runs but doesn't build any models. Why?

- A) Variable changes require a `dbt compile` run before `state:modified` can detect them.
- B) `state:modified` only detects SQL and YAML config changes, not Python or YAML variable changes.
- C) dbt can't trace a `var()` value change into `state:modified`, so the affected models aren't flagged as modified.
- D) The variable was changed in `dbt_project.yml` instead of via `--vars` flag — this is why it wasn't detected.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `dbt compile` doesn't help — the issue is that variable values are not tracked as part of the manifest state diff. |
> | **B) ❌ Incorrect** | YAML variable definitions are not tracked even though other YAML config changes are. Variable values are evaluated at runtime, not stored in the manifest diff. |
> | **C) ✅ Correct** | The docs say that if a model uses a `var` or `env_var`, dbt can't identify that lineage in a way that puts the model in `state:modified` when the value changes. It's only likely to be marked modified if the change alters the model's configuration. |
> | **D) ❌ Incorrect** | The location doesn't matter. The docs say `var` and `env_var` value changes can't be traced into `state:modified`. |
>
> > 💡 **Key rule**: `var()` / `env_var()` value changes aren't traced by `state:modified`. A model is likely flagged only if its config changes.

---

### Q13. ⭐
> **Subdomain 4.13 — Manifest overwrite: same --state and --target-path**

A CI job is configured as:
```bash
dbt build --select state:modified+ --defer --state ./target --target-path ./target
```
Developers report that `state:modified` and `--defer` give inconsistent results. What is the root cause?

- A) The `./target` directory does not exist before the first run, causing state comparison to fail.
- B) The `--defer` flag conflicts with `--state` when they point to the same directory.
- C) CI jobs require an absolute path for `--state` — relative paths cause state comparison failures.
- D) `--state` and `--target-path` point to the same directory — dbt overwrites `manifest.json` during parse before state comparison runs, so it always compares against the freshly-written manifest.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A missing directory isn't what the docs describe. |
> | **B) ❌ Incorrect** | `--defer` and `--state` don't conflict with each other — they're designed to be used together. |
> | **C) ❌ Incorrect** | Relative paths work — the issue is the directory overlap, not the path format. |
> | **D) ✅ Correct** | The docs say dbt overwrites `manifest.json` while parsing, so setting `--state` and `--target-path` to the same path with `--defer` or `state:modified` gives non-idempotent behavior. Fix: keep the saved manifest in its own folder, use a different `--target-path`, or pass `--no-write-json`. |
>
> > 💡 **Key rule**: `--state` and `--target-path` must point to **separate directories**. Same dir = manifest overwritten = non-idempotent state comparison.

---

### Q14.
> **Subdomain 4.14 — Graph operators**

Which of the following correctly selects a model named `fct_orders` plus all of its downstream descendants AND all ancestors of those descendants (the full closure)?

- A) `2+fct_orders+2`
- B) `@fct_orders`
- C) `fct_orders+`
- D) `+fct_orders+`

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `2+fct_orders+2` is bounded depth selection — up to 2 ancestors + `fct_orders` + up to 2 descendants. Not a full closure. |
> | **B) ✅ Correct** | `@fct_orders` is the **full closure operator** — it selects: `fct_orders` + all descendants + all ancestors of those descendants. It ensures that everything needed to build the model AND all its downstream tests exists. Commonly used in CI scenarios. |
> | **C) ❌ Incorrect** | `fct_orders+` selects: `fct_orders` + all descendants only. No ancestors included. |
> | **D) ❌ Incorrect** | `+fct_orders+` selects: all ancestors of `fct_orders` + `fct_orders` + all descendants. It does NOT include ancestors of those descendants. |
>
> > 💡 **Key rule**: `@model` = full closure (model + descendants + all ancestors of descendants). Use in CI to ensure all deps exist.

---

### Q15. ⭐
> **Subdomain 4.15 — Default deferral for CI jobs**

A new CI job is created. What is "Compare changes against" set to by default?

- A) No deferral.
- B) The Production environment, if one exists.
- C) This Job.
- D) The Staging environment.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | No deferral is the default for **deploy** jobs. |
> | **B) ✅ Correct** | The docs say it's set to the Production environment if you created one. This lets dbt check the PR's code against production so it only builds modified code. |
> | **C) ❌ Incorrect** | This Job (self-deferral) is a separate, older option. |
> | **D) ❌ Incorrect** | Not the default for CI jobs. |
>
> > 💡 **Key rule**: CI job default = Production environment. Deploy job default = No deferral. State comparison needs a deferred environment selected.

---

### Q16.
> **Subdomain 4.16 — Upstream test failure and downstream SKIP**

A `dbt build` run is executing. A `not_null` test on the `stg_orders` model fails. What happens to all models that depend on `stg_orders`?

- A) They run but are flagged as "potentially unreliable" in the run results.
- B) They run normally — test failures don't affect downstream model execution.
- C) They enter **SKIP** status — they do not run at all because an upstream dependency failed.
- D) They fail with an ERROR status — inheriting the upstream test failure.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no "potentially unreliable" status in dbt run results. |
> | **B) ❌ Incorrect** | Test failures on upstream models do block downstream execution in `dbt build`. |
> | **C) ✅ Correct** | In `dbt build`, a failing test on an upstream model causes all downstream dependent models to enter **SKIP** status — they never run. To prevent this blocking behavior, set the test severity to `warn` instead of `error`. |
> | **D) ❌ Incorrect** | Downstream models are not marked as ERROR — they are marked as SKIP. The error is attributed to the failing test, not the downstream models themselves. |
>
> > 💡 **Key rule**: `dbt build` upstream test fail → downstream models = **SKIP** (not ERROR). Use `severity: warn` to prevent blocking.

---

### Q17.
> **Subdomain 4.17 — Unit tests execution order**

When does `dbt build` execute unit tests relative to model materialization?

- A) Before model materialization — so unit tests catch logic errors before any expensive table builds.
- B) Concurrently with model materialization — unit tests and builds run in parallel.
- C) After all models are materialized — so unit tests validate the final output.
- D) At the same time as data tests (schema tests) — all test types run in the same phase.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Unit tests run **before** model materialization in `dbt build`. If a unit test fails, the model never materializes — saving warehouse compute. This "fail early, fail cheap" design is intentional. |
> | **B) ❌ Incorrect** | Unit tests run in a defined sequential phase, not concurrently with builds. |
> | **C) ❌ Incorrect** | Running after materialization defeats the purpose of unit tests — you'd spend compute building a table that a unit test immediately invalidates. |
> | **D) ❌ Incorrect** | Data tests (schema tests) run after materialization. Unit tests have their own earlier phase. |
>
> > 💡 **Key rule**: Unit tests run **before** materialization. Fail early = cheaper. Data tests run after materialization.

---

### Q18.
> **Subdomain 4.18 — Monorepo CI behavior**

A company stores multiple dbt Cloud projects (Project A, Project B, Project C) in a single monorepo. A developer opens a PR that only modifies files in Project A. What does dbt Cloud do?

- A) No CI jobs trigger — monorepo setups require separate repository connections per project.
- B) CI jobs for all three projects (A, B, and C) trigger from the single PR.
- C) Project A's CI job triggers immediately; B and C trigger only if A's CI passes.
- D) Only Project A's CI job triggers — dbt detects which project's files changed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Monorepos are supported — each project has its own connection to the shared repository. |
> | **B) ✅ Correct** | In a monorepo, a **single PR triggers CI jobs for ALL connected dbt projects** — even if only one project's files changed. This is a known limitation. Workaround: use project-specific target branches (e.g., `main-project-a`) to scope CI triggers. |
> | **C) ❌ Incorrect** | There is no sequential triggering based on CI success in this scenario — all CI jobs trigger simultaneously. |
> | **D) ❌ Incorrect** | dbt Cloud does not currently perform file-path-based filtering to limit CI triggers to the affected project in a monorepo. |
>
> > 💡 **Key rule**: Monorepo = single PR triggers CI for **all** connected projects. Workaround: project-specific target branches.

---

### Q19.
> **Subdomain 4.19 — Job chaining plan requirements**

An architect wants Job B in Project B to run automatically after Job A in Project A completes. Which plans can do this?

- A) Developer or Starter.
- B) Starter and above, including cross-project chaining.
- C) Enterprise-tier plans. Chaining needs Starter or above, but Starter and Developer are limited to one project each.
- D) Enterprise+ only.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Developer doesn't support "Run when another job finishes", and neither plan allows a second project. |
> | **B) ❌ Incorrect** | Chaining is Starter and above, but Starter is limited to one project, so it can't chain across two projects. |
> | **C) ✅ Correct** | "Run when another job finishes" needs a Starter or Enterprise-tier plan. Starter and Developer are limited to one project each, so chaining between two projects needs an Enterprise-tier plan. |
> | **D) ❌ Incorrect** | The docs don't limit chaining to Enterprise+. |
>
> > 💡 **Key rule**: Chaining = Starter and above (not Developer). Cross-project chaining needs more than one project, so Enterprise-tier. "Completes on" = Success only, or all statuses.

---

### Q20. ⭐
> **Subdomain 4.20 — Slim CI**

A project has over 3,000 models and full CI runs take over an hour. Which change cuts CI time while still testing every changed model?

- A) Run `dbt build` on every PR with more threads.
- B) Disable all tests in CI and run them only after merge.
- C) Increase the CI warehouse size.
- D) Use a CI job with `dbt build --select state:modified+` that compares against the Production environment.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | It still builds every model. |
> | **B) ❌ Incorrect** | That removes the safety net CI exists for. |
> | **C) ❌ Incorrect** | Not a documented approach, and it doesn't cut the amount of work. |
> | **D) ✅ Correct** | This is the default CI command. It builds only new or changed models and their downstream dependents, and deferring to Production means unmodified upstream models aren't rebuilt. |
>
> > 💡 **Key rule**: Slim CI = `dbt build --select state:modified+` + compare against the Production environment.

---

*[End of Topic 4 — 20 questions]*
