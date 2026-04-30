# Topic 3: Environments & Schema Generation — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 3.1 — Default schema generation behavior**

A developer's dbt Cloud IDE is configured with a target schema of `dbt_alice`. A model has the following config:

```yaml
config:
  schema: 'finance'
```

When the developer runs this model in the IDE, which schema does the model land in?

- A) `finance` — the custom schema replaces the target schema.
- B) `dbt_alice` — the custom schema config is ignored in development.
- C) `dbt_alice_finance` — the default macro prepends the target schema.
- D) `dbt_finance` — the target schema prefix is shortened to match the `dbt_` prefix convention.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | In the default `generate_schema_name` macro, custom schema does NOT replace target schema — it appends to it. Replacing would cause multi-developer collisions. |
> | **B) ❌ Incorrect** | The custom schema config IS honored — it just appends rather than replaces. |
> | **C) ✅ Correct** | Default behavior: `<target.schema>_<custom_schema>` = `dbt_alice_finance`. This ensures isolation when multiple developers have models with the same `schema: finance` config — `dbt_alice_finance` and `dbt_bob_finance` are distinct. |
> | **D) ❌ Incorrect** | There is no `dbt_` prefix shortening behavior in dbt's default logic. |
>
> > 💡 **Key rule**: Default formula = `<target.schema>_<custom_schema>`. Custom schema APPENDS, does NOT replace.

---

### Q2. ⭐
> **Subdomain 3.2 — Schema generation override for production**

A team wants models with `schema: 'core'` to land in the `core` schema in production (not `analytics_core`), while still having developer isolation in dev. Where must the override macro be placed and what logic should it use?

- A) Override `generate_target_schema` in `dbt_project.yml` using an environment variable check.
- B) Override `generate_schema_name` in `macros/` — check `target.name == 'prod'` and return only `custom_schema_name` in that case.
- C) Override `generate_schema_name` in `dbt_project.yml` — check the environment type and return only `custom_schema_name` for production.
- D) Set `schema: 'core'` directly in `dbt_project.yml` under the `models:` key for the production environment.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `generate_target_schema` macro in dbt. The macro to override is `generate_schema_name`. |
> | **B) ✅ Correct** | Place `generate_schema_name` in the `macros/` directory (any `.sql` filename — dbt detects by macro name). The correct logic: when `target.name == 'prod'`, return `custom_schema_name \| trim` only. Otherwise return `default_schema ~ '_' ~ custom_schema_name`. The `target.name` is set via the job's Advanced Settings → Target name field. |
> | **C) ❌ Incorrect** | Macros cannot be defined in `dbt_project.yml`. Macro overrides must live in the `macros/` directory as `.sql` files. |
> | **D) ❌ Incorrect** | Setting `schema: 'core'` in `dbt_project.yml` still goes through the same `generate_schema_name` logic — it doesn't bypass it. |
>
> > 💡 **Key rule**: Override location = `macros/generate_schema_name.sql`. Signal = `target.name` set in job Advanced Settings.

---

### Q3.
> **Subdomain 3.3 — Developer collision with custom schema override**

A developer overrides `generate_schema_name` to always return only `custom_schema_name` (stripping the target schema prefix entirely) in all environments. Two developers — Alice (`dbt_alice`) and Bob (`dbt_bob`) — both have models with `schema: 'finance'`. What is the consequence?

- A) Alice and Bob's models will land in `dbt_alice_finance` and `dbt_bob_finance` respectively, as intended.
- B) Both developers' models will write to the same `finance` schema — they will overwrite each other's data.
- C) dbt will throw a compile-time error when two developers use the same custom schema.
- D) Models will land in `dbt_alice` and `dbt_bob` respectively because the custom schema config is ignored.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The override strips the target schema prefix entirely — so it returns `finance`, not `dbt_alice_finance`. |
> | **B) ✅ Correct** | When the prefix is stripped, all developers with `schema: 'finance'` write to the exact same `finance` schema. Alice's run overwrites Bob's models and vice versa. This is the core reason the default macro preserves the `target.schema` prefix in development. |
> | **C) ❌ Incorrect** | dbt does not detect multi-user collisions at compile time — it only runs for one user at a time. The collision is a runtime data problem. |
> | **D) ❌ Incorrect** | The custom schema config is respected by the override — the override returns `finance`, not the target schema. |
>
> > 💡 **Key rule**: Always preserve `target.schema` as a prefix in dev. Stripping it causes multi-developer schema collisions.

---

### Q4. ⭐
> **Subdomain 3.4 — CI PR schema cleanup and custom macros**

After merging a PR, a team notices that the temporary CI schema (`dbt_cloud_pr_123_456`) is not being deleted from the warehouse. They recently added a custom `generate_schema_name` macro. What is the most likely cause?

- A) CI schema cleanup only works on Snowflake — the team must be using a different warehouse.
- B) The custom `generate_schema_name` macro returns a name that doesn't match the expected `dbt_cloud_pr_<job_id>_<pr_id>` pattern, so dbt cannot identify the schema to delete.
- C) The PR was merged instead of closed — only closing (not merging) a PR triggers schema cleanup.
- D) The CI job is missing the `--target-path` flag, preventing dbt from tracking the PR schema.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | CI schema auto-cleanup works across supported warehouses — it is not Snowflake-only. |
> | **B) ✅ Correct** | dbt auto-deletes the PR temp schema on PR close/merge by matching the schema name to the `dbt_cloud_pr_<job_id>_<pr_id>` pattern. If a custom `generate_schema_name` macro overrides the naming to something else (e.g., `ci_schema`), dbt cannot identify the PR schema and leaves it orphaned in the warehouse. |
> | **C) ❌ Incorrect** | Both closing and merging a PR trigger schema cleanup — merge is the normal flow and cleanup is expected. |
> | **D) ❌ Incorrect** | `--target-path` controls where artifacts are written — it has no bearing on PR schema identification. |
>
> > 💡 **Key rule**: Custom schema macros that change CI schema naming break auto-cleanup → orphaned PR schemas in the warehouse.

---

### Q5. ⭐
> **Subdomain 3.5 — Connection immutability**

A production environment is currently connected to Redshift. The team has decided to migrate to Snowflake. An admin tries to edit the production environment to change the connection from Redshift to Snowflake. What will happen?

- A) The admin can change the connection via Account Settings → Connections, and the existing environment will update automatically.
- B) The connection field is immutable after environment creation — the admin must create a new Snowflake environment, migrate all jobs, and delete the Redshift environment.
- C) The connection can be changed in the environment's Edit screen by selecting a new connection from the dropdown.
- D) The admin must delete the environment and re-create it with the new connection — existing jobs can be migrated using the dbt API.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Changing the connection object in Account Settings does not cascade to environments — environments hold an immutable reference to the connection they were created with. |
> | **B) ✅ Correct** | Once a connection is assigned to an environment, it **cannot be changed** — there is no "edit connection" option on an existing environment. The correct migration path: create a new environment with the Snowflake connection → migrate all jobs to the new environment → delete the old Redshift environment. |
> | **C) ❌ Incorrect** | The connection dropdown is not editable on an existing environment's Edit screen — the field is greyed out or absent. |
> | **D) ❌ Incorrect** | Deleting and recreating the environment is operationally the same as B, but B is more precise — it correctly identifies immutability as the reason and the migration pattern. |
>
> > 💡 **Key rule**: Connection = **immutable** after environment creation. To change: create new env → migrate jobs → delete old env.

---

### Q6. ⭐
> **Subdomain 3.6 — Staging environment and Mesh dev resolution**

A platform team adds a Staging environment to an upstream project in their dbt Mesh. No deployment jobs have run in the new Staging environment yet. Immediately after creating it, downstream team developers report that their IDE jobs fail to resolve cross-project references that were working fine an hour ago. What happened?

- A) The Staging environment has a configuration error — it should be deleted and re-created.
- B) Once a Staging environment exists, dbt immediately routes all development cross-project ref resolution to it — even with no successful runs. With no metadata, resolution fails and does NOT fall back to Production.
- C) dbt falls back to Production when Staging has no successful runs — the failure is caused by something else.
- D) The Staging environment requires a manual "activate" step before dbt uses it for resolution.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is expected behavior — the Staging environment is not misconfigured. |
> | **B) ✅ Correct** | The critical gotcha: the moment a Staging environment is created and linked to the metadata service, dbt **immediately routes all development cross-project ref resolution to it** — with zero fallback to Production. Because no jobs have populated Staging's metadata, all cross-project refs fail outright. Fix: run at least one successful deployment job in Staging before downstream teams rely on it. |
> | **C) ❌ Incorrect** | This is explicitly wrong. Fallback to Production only occurs when the Staging environment **type doesn't exist at all**. Once Staging exists (even empty), dbt routes to it and fails rather than falling back. |
> | **D) ❌ Incorrect** | There is no "activate" step — creation and linking is automatic. |
>
> > 💡 **Key rule**: Adding Staging = **immediate routing**. No fallback to Production. Run at least one successful job in Staging immediately after creating it.

---

### Q7.
> **Subdomain 3.7 — Extended attributes and nested overrides**

An architect tries to override a nested key in `profiles.yml` using an environment's extended attributes. They add a partial YAML snippet targeting only the nested key. The override does not apply. Why?

- A) Extended attributes only work for Snowflake environments — not for other warehouse types.
- B) Extended attributes accept top-level keys only. Partial nested overrides are **silently ignored** — the entire parent key must be provided as a JSON object.
- C) Extended attributes require a dbt Cloud restart to take effect.
- D) Nested overrides require the `+override: true` flag in the YAML snippet.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Extended attributes work across warehouse types — they're not Snowflake-specific. |
> | **B) ✅ Correct** | Extended attributes (YAML snippets that override `profiles.yml`) only accept **top-level keys**. If you try to override a nested key directly, the change is **silently ignored** — no error is raised. To override a nested value, you must provide the entire parent key block as a complete JSON object. |
> | **C) ❌ Incorrect** | Extended attributes take effect at job runtime — no restart required. |
> | **D) ❌ Incorrect** | There is no `+override: true` flag — this is not a dbt concept for extended attributes. |
>
> > 💡 **Key rule**: Extended attributes = top-level keys only. Partial nested overrides = **silently ignored**. Provide full parent block.

---

### Q8.
> **Subdomain 3.8 — Environment counts per project**

Which of the following correctly describes how many of each environment type a single dbt project can have?

- A) Development: unlimited, Production: 1, Staging: 1, General: unlimited.
- B) Development: 1, Production: 1, Staging: 1, General: unlimited.
- C) Development: 1, Production: unlimited, Staging: unlimited, General: unlimited.
- D) Development: 1, Production: 1, Staging: unlimited, General: unlimited.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Development is limited to exactly 1 per project — it drives the IDE and controls which branch developers fork from. Multiple Development environments would create conflicts. |
> | **B) ✅ Correct** | **Development: exactly 1** (IDE/CLI); **Production: exactly 1** (Catalog source of truth, cross-project ref resolver); **Staging: exactly 1** (pre-prod, mandatory in Mesh); **General: unlimited** (experimental/non-critical). |
> | **C) ❌ Incorrect** | Production and Staging are each limited to exactly 1 — having multiples of either would create ambiguity in Catalog and cross-project resolution. |
> | **D) ❌ Incorrect** | Staging is also limited to exactly 1 per project. |
>
> > 💡 **Key rule**: Dev=1, Prod=1, Staging=1, General=unlimited. Environment type field is greyed out in UI if that type already exists.

---

### Q9. ⭐
> **Subdomain 3.9 — Deferral breaks on failed last run**

A CI job is configured with deferral against the Production environment. The production deployment job failed 4 days ago and has not run successfully since. A developer opens a new PR and the CI job builds the entire DAG instead of only modified models. What is the cause?

- A) Deferral is not supported for CI jobs — only for deploy jobs.
- B) The deferral is misconfigured — it must point to a General environment, not Production.
- C) Deferral requires a successful manifest from the reference environment. With no recent successful run, there is no valid manifest — CI falls back to a full DAG build.
- D) The developer's PR contains too many modified files, exceeding the deferral threshold.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deferral is explicitly a CI job feature — it's the primary use case for CI optimization. |
> | **B) ❌ Incorrect** | Deferral against Production is the standard configuration for CI jobs. |
> | **C) ✅ Correct** | Deferral works by reading the `manifest.json` from the reference environment's last **successful** run. If the production job last failed, there is no valid manifest to defer against — dbt falls back to building the full DAG. This is a critical operational concern: a failed prod job breaks CI optimization. |
> | **D) ❌ Incorrect** | There is no "deferral threshold" based on number of modified files. |
>
> > 💡 **Key rule**: Deferral requires a **successful** manifest. Failed last run = no valid manifest = full rebuild.

---

### Q10.
> **Subdomain 3.10 — Release tracks**

A team prioritizes stability and does not want to receive new dbt version upgrades until they've been thoroughly vetted. They manage a mission-critical production pipeline with strict change management processes. Which release track should they choose?

- A) Latest — ensures they always have the newest features and security patches.
- B) Compatible — lags slightly behind Latest; the standard choice for most teams.
- C) Extended — the slowest to upgrade; longest support window; designed for strict change management.
- D) Pinned — set a specific dbt version and never auto-upgrade.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Latest auto-upgrades immediately to every new release — the highest change frequency, not suitable for strict change management. |
> | **B) ❌ Incorrect** | Compatible is the default for most teams but still upgrades ahead of Extended. It's suitable for most teams but not for strictest change management. |
> | **C) ✅ Correct** | **Extended** is the slowest to upgrade and has the longest support window. It's designed for risk-averse teams with strict change management processes — upgrades happen last, giving maximum time to validate changes in other environments first. |
> | **D) ❌ Incorrect** | "Pinned" is not a named release track in dbt Cloud — the three options are Latest, Compatible, and Extended. |
>
> > 💡 **Key rule**: Latest = always newest; Compatible = slight lag (most teams); Extended = slowest, longest support (strictest change management).

---

### Q11.
> **Subdomain 3.11 — Custom branch behavior**

A deploy job's environment has a custom branch set to `release/2024-q4`. What does this mean for how the job executes?

- A) The job will merge `release/2024-q4` into `main` before running.
- B) The job will clone the `release/2024-q4` branch at runtime and run against that code — it does not merge into any other branch.
- C) The job will create a new branch called `release/2024-q4` from `main` each time it runs.
- D) The custom branch setting only applies to the dbt Cloud IDE — deploy jobs always use `main`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud jobs do not perform git merges as part of job execution. |
> | **B) ✅ Correct** | For deployment environments, a custom branch specifies which branch is **cloned at job runtime** — dbt checks out that branch and runs against it. No merging occurs. The branch is used as-is. |
> | **C) ❌ Incorrect** | dbt never creates new branches as part of job execution. |
> | **D) ❌ Incorrect** | The custom branch setting on a deployment environment directly affects deploy jobs — it's not just an IDE setting. |
>
> > 💡 **Key rule**: Deploy env custom branch = branch **cloned at runtime**. Dev env custom branch = branch devs **fork from** in IDE.

---

### Q12.
> **Subdomain 3.12 — Environment variable precedence**

A dbt project has an environment variable `DBT_TARGET_SCHEMA` set at three levels: project default = `analytics`, environment level = `analytics_staging`, and job-level override = `analytics_ci`. When the job runs, which value is used?

- A) `analytics` — project-level defaults always win for consistency.
- B) `analytics_staging` — environment-level settings override project defaults.
- C) `analytics_ci` — job-level overrides always win; they are the most specific.
- D) All three values are merged — the most recently set one takes precedence.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Project default is the lowest precedence — it is overridden by environment and job levels. |
> | **B) ❌ Incorrect** | Environment level overrides project default, but is itself overridden by job level. |
> | **C) ✅ Correct** | Environment variable precedence (highest to lowest): **Job > Environment > Project > Account**. The job-level override always wins when present. |
> | **D) ❌ Incorrect** | Values are not merged — the most specific (highest precedence) level wins entirely. |
>
> > 💡 **Key rule**: Env var precedence = **Job > Environment > Project > Account**. Job always wins.

---

---

### Q13.
> **Subdomain 3.13 — `target.name` vs environment type**

A data engineer sets the **Target name** field in a dbt Cloud job's Advanced Settings to `prod`. They expect this to automatically designate the job as a "Production" environment type. An architect corrects them. What is the distinction?

- A) `target.name` and environment type are synonyms — setting one automatically sets the other.
- B) `target.name` is a string value in job Advanced Settings that feeds into Jinja macros (e.g., `generate_schema_name`). Environment type is a dbt Cloud concept controlling Catalog behavior and cross-project ref resolution. They are independent.
- C) `target.name` controls which dbt Cloud environment a job runs in. Setting it to `prod` routes the job to the Production environment.
- D) Environment type is set via `target.name` — you must set `target.name = production` (full word, not abbreviation) for dbt Cloud to recognize the Production environment type.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | They are completely independent settings. Changing one has no effect on the other. |
> | **B) ✅ Correct** | **`target.name`** is a runtime string you control, readable in Jinja as `target.name`. It is most commonly used in custom macros like `generate_schema_name` to distinguish dev from prod schema behavior. **Environment type** (Development, Production, Staging, General) is a dbt Cloud platform concept that determines which job is the Catalog source of truth, how cross-project refs resolve, and what the environment is used for. Setting `target.name = prod` on a job in a General environment does NOT make it a Production environment. |
> | **C) ❌ Incorrect** | `target.name` is an arbitrary string — it does not route jobs to different environments. The job's environment is fixed at job creation. |
> | **D) ❌ Incorrect** | `target.name` has no effect on environment type designation in dbt Cloud. The environment type is set in the environment configuration, not through any job field. |
>
> > 💡 **Key rule**: `target.name` = runtime string for macro logic (set in job Advanced Settings). Environment type = dbt Cloud platform concept. Completely independent.

---

### Q14.
> **Subdomain 3.14 — Dev cross-project ref with no upstream Staging**

A dbt Mesh has a consumer project (`marketing`) and a producer project (`platform`). The `platform` project has only a **Production** environment — no Staging environment exists. A developer working in the `marketing` IDE opens a run and references a public model from `platform`. Which environment does the cross-project ref resolve against?

- A) The ref fails — development jobs cannot resolve against Production environments.
- B) It resolves against the `platform` project's **Production** environment — this is the only scenario where a development IDE job resolves cross-project refs against Production.
- C) It resolves against the `marketing` project's Staging environment as a proxy.
- D) It prompts the developer to select an environment from the `platform` project.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Dev jobs CAN resolve against Production — this is the documented fallback when no Staging environment exists in the upstream project. |
> | **B) ✅ Correct** | Cross-project ref resolution follows this rule: dev jobs resolve against **Staging if it exists**, else **Production**. When the upstream (`platform`) project has no Staging environment, the developer's IDE job resolves directly against `platform`'s **Production** environment. This is the **only** scenario where a development job legitimately resolves against Production. It is a data-access risk — developers may inadvertently query production data. |
> | **C) ❌ Incorrect** | The consumer project's Staging environment is irrelevant to resolving refs in the upstream project. Resolution is always within the upstream project. |
> | **D) ❌ Incorrect** | Environment selection is automatic — there is no manual prompt. |
>
> > 💡 **Key rule**: Dev cross-project ref → Staging (if exists) else Production. No upstream Staging = dev resolves against Production (only time this happens).

---

### Q15. ⭐
> **Subdomain 3.15 — Staging environment and dev resolution (no fallback)**

An architect adds a **new Staging environment** to an upstream dbt Mesh project. No deployment jobs have been run in this Staging environment yet. What immediately happens to developer IDE jobs in downstream consumer projects that reference this upstream project?

- A) Nothing changes immediately — downstream dev jobs continue resolving against Production until the first Staging job succeeds.
- B) Downstream dev IDE jobs immediately start failing to resolve cross-project references because dbt routes all dev resolution to the new Staging environment, which has no metadata yet. There is no fallback to Production.
- C) Downstream dev jobs now resolve against both Staging and Production simultaneously, merging metadata from both.
- D) dbt detects the empty Staging environment and temporarily routes to Production until the first Staging run succeeds, then switches automatically.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The transition is immediate, not gradual. As soon as the Staging environment is created and linked to the metadata service, dbt routes to it — even with no runs. |
> | **B) ✅ Correct** | The moment a Staging environment exists and is linked to the metadata service, dbt **immediately** routes all downstream dev cross-project ref resolution to it — with **no fallback to Production**. Since no deployment jobs have run in Staging, there is no metadata for the upstream models, and resolution fails. This is a critical architect gotcha: always run at least one successful deployment job in the new Staging environment before downstream teams depend on it. |
> | **C) ❌ Incorrect** | dbt does not merge metadata from multiple environments. Resolution is to one environment only. |
> | **D) ❌ Incorrect** | There is no automatic fallback mechanism once a Staging environment exists. The fallback to Production only applies when no Staging environment exists at all. |
>
> > 💡 **Key rule**: Adding Staging immediately breaks downstream dev resolution if no jobs have run in it yet. Always run one successful job in Staging before downstream teams depend on it.

---

### Q16.
> **Subdomain 3.16 — Deleting an environment**

An architect plans to delete a General environment that was used for experimental jobs. Before deleting, what must they do to avoid data loss?

- A) Archive the environment first — dbt Cloud auto-archives all jobs before deletion.
- B) Transfer all jobs configured in that environment to another environment first — deleting an environment deletes all jobs in it.
- C) Export the run history to CSV, since it cannot be recovered after deletion.
- D) Nothing — job definitions are stored at the project level and persist after environment deletion.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no auto-archive step — dbt Cloud does not preserve jobs in an archived state when an environment is deleted. |
> | **B) ✅ Correct** | When an environment is deleted, **all jobs configured in that environment are also deleted**. There is no recovery path. The architect must **transfer jobs to another environment** before deleting. This is an irreversible action — always confirm there are no jobs you want to keep before proceeding. |
> | **C) ❌ Incorrect** | Run history export is not a documented concern here — job definitions are the critical thing to preserve. |
> | **D) ❌ Incorrect** | Jobs are not stored at the project level independently of environments — they belong to an environment. |
>
> > 💡 **Key rule**: Deleting an environment = all jobs in it are also deleted. Transfer jobs first — no recovery after deletion.

---

### Q17.
> **Subdomain 3.17 — Service account key pair rotation**

A platform team needs to rotate the key pair used by a production service account Snowflake connection. An admin looks in the dbt Cloud UI under Account Settings → Connections but cannot find a way to update the key. What is the correct process?

- A) Delete and recreate the connection with the new key pair.
- B) Key pair rotation for service accounts must be done via the **dbt Admin API** — there is no UI path.
- C) Update the key in the environment's Extended Attributes field.
- D) Key pair rotation is automatic in dbt Cloud — the system generates new keys on a 90-day cycle.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deleting and recreating the connection would break all environments and jobs referencing it. This is not the recommended approach. |
> | **B) ✅ Correct** | Service account key pair rotation has **no UI path** in dbt Cloud. The rotation flow must go through the **dbt Admin API**: generate a new key pair → POST the new public key to the API → verify → invalidate the old key. This is a documented operational procedure for production key management. |
> | **C) ❌ Incorrect** | Extended attributes override `profiles.yml` fields at the environment level, but key pair credentials for service accounts are not configurable via extended attributes. |
> | **D) ❌ Incorrect** | Key pair rotation is not automatic — it is a manual process initiated by the team. |
>
> > 💡 **Key rule**: Service account key pair rotation = **dbt Admin API only**. No UI path exists.

---

### Q18.
> **Subdomain 3.18 — Environment editable fields by platform**

A team uses a **BigQuery** connection in their dbt Cloud project. They want to override the BigQuery dataset (the equivalent of a schema) at the environment level for a staging environment, so staging models land in a different dataset than production. They navigate to the environment's connection settings but see no editable dataset field. What should they do?

- A) The dataset field for BigQuery is found under the Environment Credentials section, not the Connection Settings section.
- B) BigQuery environments have no editable connection fields in the UI — the dataset override must be configured using **extended attributes** in the environment settings.
- C) BigQuery dataset overrides require creating a separate BigQuery connection per environment.
- D) Use the `target_schema` environment variable to override the BigQuery dataset.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | BigQuery environment credentials have a Dataset field, but the question is about the connection-level override. The deployment credentials dataset field IS editable — but this question is testing knowledge of the environment connection settings section, where BigQuery has no editable fields. |
> | **B) ✅ Correct** | For **BigQuery, Postgres, Redshift, and Spark**, the environment connection settings panel has **no editable fields** — everything is inferred from the project-level connection. To override values like the target dataset, use **extended attributes** (a YAML snippet in the environment settings). Snowflake is the exception, with editable Role, Database, and Warehouse fields. |
> | **C) ❌ Incorrect** | A separate connection is not required — extended attributes are the correct override mechanism. |
> | **D) ❌ Incorrect** | There is no built-in `target_schema` environment variable that overrides the BigQuery dataset. |
>
> > 💡 **Key rule**: BigQuery/Postgres/Redshift/Spark = no UI editable fields in environment connection settings. Use extended attributes to override.

---

### Q19.
> **Subdomain 3.19 — Developer plan scheduling interval**

A team on the **Developer plan** wants to schedule a dbt job to run every 5 minutes to keep their data as fresh as possible. Will this work?

- A) Yes — there is no minimum scheduling interval documented for the Developer plan.
- B) No — the Developer plan has a minimum scheduling interval of **10 minutes**. A 5-minute schedule cannot be set.
- C) No — the Developer plan does not support scheduled jobs at all; only manual triggers are available.
- D) Yes — 5-minute intervals are supported on Developer plan but require cron syntax.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A minimum interval is documented for the Developer plan. |
> | **B) ✅ Correct** | The **Developer plan** enforces a minimum scheduling interval of **10 minutes**. A 5-minute schedule cannot be configured on this plan. Teams that need sub-10-minute freshness must upgrade or use an alternative triggering mechanism via the API. Starter, Enterprise, and Enterprise+ do not have a documented minimum scheduling interval. |
> | **C) ❌ Incorrect** | Developer plan does support scheduled jobs — it just has a 10-minute minimum interval. |
> | **D) ❌ Incorrect** | Cron syntax does not bypass the 10-minute minimum on Developer plan. |
>
> > 💡 **Key rule**: Developer plan = 10-minute minimum scheduling interval. Other plans have no documented minimum.

---

### Q20.
> **Subdomain 3.20 — Credential security in environment settings**

While reviewing a team's dbt Cloud setup, an architect finds that Snowflake passwords are hardcoded directly in the environment's deployment credentials form. What is the risk and what is the recommended practice?

- A) There is no risk — credentials in the deployment credentials form are encrypted at rest and never exposed.
- B) Hardcoded secrets in the credentials form may appear in build logs and are harder to rotate. The best practice is to reference **environment variables** instead of hardcoding values.
- C) Credentials in the deployment form are visible to all Account Admin users, creating an insider threat risk.
- D) Hardcoded credentials automatically expire after 30 days in dbt Cloud, creating operational risk.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Hardcoded credentials can surface in build logs or debug output, especially if extended attributes or profiles are printed during verbose logging. Encryption at rest does not prevent runtime exposure. |
> | **B) ✅ Correct** | The best practice is to **wrap credential values in environment variables** (e.g., `{{ env_var('SNOWFLAKE_PASSWORD') }}`) rather than hardcoding them. This reduces the risk of secrets appearing in logs, simplifies credential rotation (update the env var, not the form), and follows the principle of least exposure. This applies especially to passwords, private keys, and tokens. |
> | **C) ❌ Incorrect** | While access control is important, this is not the primary documented risk. The key concern is log exposure and rotation complexity. |
> | **D) ❌ Incorrect** | Hardcoded credentials do not auto-expire in dbt Cloud. |
>
> > 💡 **Key rule**: Wrap secrets in environment variables — never hardcode passwords or keys in credential forms. Values can appear in logs.

---

*[End of Topic 3 — 20 questions]*

