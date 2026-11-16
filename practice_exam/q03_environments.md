# Topic 3: Environments & Schema Generation — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 21 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 3.1 — Default schema generation behavior**

A developer's dbt Cloud IDE is configured with a target schema of `dbt_alice`. A model has the following config:

```yaml
config:
  schema: 'finance'
```

When the developer runs this model in the IDE, which schema does the model land in?

- A) `dbt_alice` — the custom schema config is ignored in development.
- B) `finance` — the custom schema replaces the target schema.
- C) `dbt_finance` — the target schema prefix is shortened to match the `dbt_` prefix convention.
- D) `dbt_alice_finance` — the default macro prepends the target schema.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The custom schema config IS honored — it just appends rather than replaces. |
> | **B) ❌ Incorrect** | In the default `generate_schema_name` macro, custom schema does NOT replace target schema — it appends to it. Replacing would cause multi-developer collisions. |
> | **C) ❌ Incorrect** | There is no `dbt_` prefix shortening behavior in dbt's default logic. |
> | **D) ✅ Correct** | Default behavior: `<target.schema>_<custom_schema>` = `dbt_alice_finance`. This ensures isolation when multiple developers have models with the same `schema: finance` config — `dbt_alice_finance` and `dbt_bob_finance` are distinct. |
>
> > 💡 **Key rule**: Default formula = `<target.schema>_<custom_schema>`. Custom schema APPENDS, does NOT replace.

---

### Q2. ⭐
> **Subdomain 3.2 — Schema generation override for production**

A team wants models with `schema: 'core'` to land in the `core` schema in production (not `analytics_core`), while still having developer isolation in dev. Where must the override macro be placed and what logic should it use?

- A) Override `generate_schema_name` in `dbt_project.yml` — check the environment type and return only `custom_schema_name` for production.
- B) Set `schema: 'core'` directly in `dbt_project.yml` under the `models:` key for the production environment.
- C) Override `generate_schema_name` in `macros/` — check `target.name == 'prod'` and return only `custom_schema_name` in that case.
- D) Override `generate_target_schema` in `dbt_project.yml` using an environment variable check.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Macros cannot be defined in `dbt_project.yml`. Macro overrides must live in the `macros/` directory as `.sql` files. |
> | **B) ❌ Incorrect** | Setting `schema: 'core'` in `dbt_project.yml` still goes through the same `generate_schema_name` logic — it doesn't bypass it. |
> | **C) ✅ Correct** | Put the override in `macros/generate_schema_name.sql`. When `target.name == 'prod'`, return the custom schema. In other targets, keep the target schema so developers don't collide (the docs' version ignores the custom schema in dev/CI; appending it also keeps developers apart). Set **Target name = `prod`** on the production job. |
> | **D) ❌ Incorrect** | There is no `generate_target_schema` macro in dbt. The macro to override is `generate_schema_name`. |
>
> > 💡 **Key rule**: Override location = `macros/generate_schema_name.sql`. Signal = `target.name` set in job Advanced Settings.

---

### Q3.
> **Subdomain 3.3 — Developer collision with custom schema override**

A developer overrides `generate_schema_name` to always return only `custom_schema_name` (stripping the target schema prefix entirely) in all environments. Two developers — Alice (`dbt_alice`) and Bob (`dbt_bob`) — both have models with `schema: 'finance'`. What is the consequence?

- A) Both developers' models will write to the same `finance` schema — they will overwrite each other's data.
- B) Alice and Bob's models will land in `dbt_alice_finance` and `dbt_bob_finance` respectively, as intended.
- C) Models will land in `dbt_alice` and `dbt_bob` respectively because the custom schema config is ignored.
- D) dbt will throw a compile-time error when two developers use the same custom schema.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | When the prefix is stripped, all developers with `schema: 'finance'` write to the exact same `finance` schema. Alice's run overwrites Bob's models and vice versa. This is the core reason the default macro preserves the `target.schema` prefix in development. |
> | **B) ❌ Incorrect** | The override strips the target schema prefix entirely — so it returns `finance`, not `dbt_alice_finance`. |
> | **C) ❌ Incorrect** | The custom schema config is respected by the override — the override returns `finance`, not the target schema. |
> | **D) ❌ Incorrect** | dbt does not detect multi-user collisions at compile time — it only runs for one user at a time. The collision is a runtime data problem. |
>
> > 💡 **Key rule**: Always preserve `target.schema` as a prefix in dev. Stripping it causes multi-developer schema collisions.

---

### Q4. ⭐
> **Subdomain 3.4 — CI PR schema cleanup and custom macros**

After merging a PR, a team notices that the temporary CI schema (`dbt_cloud_pr_123_456`) is not being deleted from the warehouse. They recently added a custom `generate_schema_name` macro. What is the most likely cause?

- A) The custom `generate_schema_name` macro returns a name that doesn't keep the `dbt_cloud_pr_` prefix, so dbt doesn't drop the schema.
- B) CI schema cleanup only works on Snowflake — the team must be using a different warehouse.
- C) The CI job is missing the `--target-path` flag, preventing dbt from tracking the PR schema.
- D) The PR was merged instead of closed — only closing (not merging) a PR triggers schema cleanup.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say that if you overrode `generate_schema_name` and it isn't using `dbt_cloud_pr_` as the prefix, the temporary schemas aren't dropped. ✅ `dbt_cloud_pr_123_456_marketing`, ❌ `marketing`. |
> | **B) ❌ Incorrect** | CI schema auto-cleanup works across supported warehouses — it is not Snowflake-only. |
> | **C) ❌ Incorrect** | `--target-path` controls where artifacts are written — it has no bearing on PR schema identification. |
> | **D) ❌ Incorrect** | Both closing and merging a PR trigger schema cleanup — merge is the normal flow and cleanup is expected. |
>
> > 💡 **Key rule**: An overridden `generate_schema_name` must keep the `dbt_cloud_pr_` prefix, or temp PR schemas are not dropped.

---

### Q5. ⭐
> **Subdomain 3.5 — Connection profiles**

A team needs a deployment environment to use different warehouse credentials. How do they change it?

- A) They change it in the job's Advanced Settings.
- B) They create a new dbt project.
- C) They assign a different connection profile in the environment's settings (Edit → swap icon → Assign profile → Save).
- D) They can't. Profiles can only be assigned when the environment is created.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The environment determines the settings its jobs run with. Jobs don't pick the profile. |
> | **B) ❌ Incorrect** | Profiles live at the project level. No new project is needed. |
> | **C) ✅ Correct** | Deployment environments get their connection and credentials from a project-level **profile**. Edit the environment, click the swap icon, pick a profile, Assign profile, Save. |
> | **D) ❌ Incorrect** | The docs describe swapping the profile on an existing deployment environment. |
>
> > 💡 **Key rule**: Profiles = project level, **deployment environments only** (not dev). Swap them in the environment settings. Older material says an environment's connection can't be changed; the current docs don't say that.

---

### Q6. ⭐
> **Subdomain 3.6 — Staging environment and Mesh dev resolution**

A platform team adds a Staging environment to an upstream project in their dbt Mesh. No deployment jobs have run in the new Staging environment yet. Immediately after creating it, downstream team developers report that their IDE jobs fail to resolve cross-project references that were working fine an hour ago. What happened?

- A) dbt falls back to Production when Staging has no successful runs — the failure is caused by something else.
- B) The Staging environment requires a manual "activate" step before dbt uses it for resolution.
- C) The Staging environment has a configuration error — it should be deleted and re-created.
- D) Once a Staging environment exists, dbt immediately routes all development cross-project ref resolution to it — even with no successful runs. With no metadata, resolution fails and does NOT fall back to Production.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is explicitly wrong. Fallback to Production only occurs when the Staging environment **type doesn't exist at all**. Once Staging exists (even empty), dbt routes to it and fails rather than falling back. |
> | **B) ❌ Incorrect** | There is no "activate" step — creation and linking is automatic. |
> | **C) ❌ Incorrect** | This is expected behavior — the Staging environment is not misconfigured. |
> | **D) ✅ Correct** | The docs say dbt uses the Staging environment as soon as it exists, with no fail-over to Production, even if Staging has had no successful runs. Downstream refs then fail. Fix: run a successful deployment job in Staging. Safer order: create the environment without marking it Staging, run a job, then mark it Staging. |
>
> > 💡 **Key rule**: Adding Staging = **immediate routing**. No fallback to Production. Create it unmarked, run a job, then mark it Staging.

---

### Q7.
> **Subdomain 3.7 — Extended attributes and nested overrides**

An architect tries to override a nested key in `profiles.yml` using an environment's extended attributes. They add a partial YAML snippet targeting only the nested key. The override does not apply. Why?

- A) Extended attributes require a dbt Cloud restart to take effect.
- B) Extended attributes accept top-level keys only. To change a sub-key, provide the entire top-level key as a JSON block.
- C) Extended attributes only work for Snowflake environments — not for other warehouse types.
- D) Nested overrides require the `+override: true` flag in the YAML snippet.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not a documented step. |
> | **B) ✅ Correct** | The docs say only **top-level keys** are accepted. To change a specific sub-key, provide the entire top-level key as a JSON block (e.g. all of BigQuery `keyfile_json`). |
> | **C) ❌ Incorrect** | Extended attributes work across warehouse types — they're not Snowflake-specific. |
> | **D) ❌ Incorrect** | There is no `+override: true` flag — this is not a dbt concept for extended attributes. |
>
> > 💡 **Key rule**: Extended attributes = top-level keys only. To change a sub-key, give the whole top-level key as JSON.

---

### Q8.
> **Subdomain 3.8 — Environment counts per project**

Which of the following correctly describes how many of each environment type a single dbt project can have?

- A) Development: 1, Production: 1, Staging: unlimited, General: unlimited.
- B) Development: 1, Production: 1, Staging: 1, General: unlimited.
- C) Development: unlimited, Production: 1, Staging: 1, General: unlimited.
- D) Development: 1, Production: unlimited, Staging: unlimited, General: unlimited.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Staging is also limited to exactly 1 per project. |
> | **B) ✅ Correct** | **Development: exactly 1** (IDE/CLI); **Production: exactly 1** (Catalog source of truth, cross-project ref resolver); **Staging: exactly 1** (pre-prod, optional); **General: unlimited** (experimental/non-critical). |
> | **C) ❌ Incorrect** | Development is limited to exactly 1 per project — it drives the IDE and controls which branch developers fork from. Multiple Development environments would create conflicts. |
> | **D) ❌ Incorrect** | Production and Staging are each limited to exactly 1 — having multiples of either would create ambiguity in Catalog and cross-project resolution. |
>
> > 💡 **Key rule**: Dev=1, Prod=1, Staging=1, General=unlimited.

---

### Q9. ⭐
> **Subdomain 3.9 — What deferral compares against**

A CI job is set to compare changes against the Production environment. Which run provides the state it compares against?

- A) The latest successful run in Production, from any job that updates artifacts there.
- B) The previous run of the CI job itself.
- C) The most recent production run, even if it failed.
- D) A specific production job picked by job ID.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say the latest successful run in the environment can come from any job that updates artifacts there. |
> | **B) ❌ Incorrect** | That's the separate "This Job" (self-deferral) option. |
> | **C) ❌ Incorrect** | The state comes from the latest **successful** run. |
> | **D) ❌ Incorrect** | Built-in deferral targets an environment, not a hand-picked job ID. |
>
> > 💡 **Key rule**: Deferral to an environment = state from the latest **successful** run there. You need a successful run first. CI jobs default to Production.

---

### Q10.
> **Subdomain 3.10 — Release tracks**

A team prioritizes stability and does not want to receive new dbt version upgrades until they've been thoroughly vetted. They manage a mission-critical production pipeline with strict change management processes. They are on dbt v1 and the Enterprise plan. Which release track should they choose?

- A) Latest — ensures they always have the newest features and security patches.
- B) Pinned — set a specific dbt version and never auto-upgrade.
- C) Extended — the previous month's Compatible release (Enterprise/Enterprise+).
- D) Compatible — a monthly release aligned with open source dbt v1.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Latest is a continuous release with early access to new features. It's the v1 default, not the cautious choice. |
> | **B) ❌ Incorrect** | "Pinned" isn't a release track. The v1 tracks are Latest, Compatible, Extended and Fallback. |
> | **C) ✅ Correct** | **Extended** is the previous month's Compatible release, so it gives the most testing time. Enterprise/Enterprise+ only. |
> | **D) ❌ Incorrect** | Compatible is monthly (Starter and up). Extended trails it by a month. |
>
> > 💡 **Key rule**: v1: Latest (default, continuous) → Compatible (monthly, Starter+) → Extended (previous month's Compatible, Enterprise+) → Fallback (Enterprise+, rollback). v2: Nightly, Stable (default), Extended, Fallback.

---

### Q11.
> **Subdomain 3.11 — Custom branch behavior**

A deploy job's environment has a custom branch set to `release/2024-q4`. What does this mean for how the job executes?

- A) The custom branch setting only applies to the dbt Cloud IDE — deploy jobs always use `main`.
- B) The job will merge `release/2024-q4` into `main` before running.
- C) The job will create a new branch called `release/2024-q4` from `main` each time it runs.
- D) The job will clone the `release/2024-q4` branch at runtime and run against that code — it does not merge into any other branch.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The custom branch setting on a deployment environment directly affects deploy jobs — it's not just an IDE setting. |
> | **B) ❌ Incorrect** | dbt Cloud jobs do not perform git merges as part of job execution. |
> | **C) ❌ Incorrect** | dbt never creates new branches as part of job execution. |
> | **D) ✅ Correct** | For deployment environments, a custom branch specifies which branch is **cloned at job runtime** — dbt checks out that branch and runs against it. No merging occurs. The branch is used as-is. |
>
> > 💡 **Key rule**: Deploy env custom branch = branch **cloned at runtime**. Dev env custom branch = branch devs **fork from** in IDE.

---

### Q12.
> **Subdomain 3.12 — Environment variable precedence**

A dbt project has an environment variable `DBT_TARGET_SCHEMA` set at three levels: project default = `analytics`, environment level = `analytics_staging`, and job-level override = `analytics_ci`. When the job runs, which value is used?

- A) `analytics_staging` — environment-level settings override project defaults.
- B) `analytics_ci` — job-level overrides always win; they are the most specific.
- C) All three values are merged — the most recently set one takes precedence.
- D) `analytics` — project-level defaults always win for consistency.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Environment level overrides project default, but is itself overridden by job level. |
> | **B) ✅ Correct** | Precedence, highest first: job override (or personal IDE override) > environment > project default > the default argument in `env_var()`. There is no account-level scope. |
> | **C) ❌ Incorrect** | Values are not merged — the most specific (highest precedence) level wins entirely. |
> | **D) ❌ Incorrect** | Project default is the lowest precedence — it is overridden by environment and job levels. |
>
> > 💡 **Key rule**: Env var precedence = **Job (or personal IDE) > Environment > Project default**. No account level. Names start with `DBT_` or `DBT_ENV_SECRET_`.

---

---

### Q13.
> **Subdomain 3.13 — `target.name` vs environment type**

A data engineer sets the **Target name** field in a dbt Cloud job's Advanced Settings to `prod`. They expect this to automatically designate the job as a "Production" environment type. An architect corrects them. What is the distinction?

- A) `target.name` controls which dbt Cloud environment a job runs in. Setting it to `prod` routes the job to the Production environment.
- B) Environment type is set via `target.name` — you must set `target.name = production` (full word, not abbreviation) for dbt Cloud to recognize the Production environment type.
- C) `target.name` and environment type are synonyms — setting one automatically sets the other.
- D) `target.name` is a string value in job Advanced Settings that feeds into Jinja macros (e.g., `generate_schema_name`). Environment type is a dbt Cloud concept controlling Catalog behavior and cross-project ref resolution. They are independent.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `target.name` is an arbitrary string — it does not route jobs to different environments. The job's environment is fixed at job creation. |
> | **B) ❌ Incorrect** | `target.name` has no effect on environment type designation in dbt Cloud. The environment type is set in the environment configuration, not through any job field. |
> | **C) ❌ Incorrect** | They are completely independent settings. Changing one has no effect on the other. |
> | **D) ✅ Correct** | **`target.name`** is a runtime string you control, readable in Jinja as `target.name`. It is most commonly used in custom macros like `generate_schema_name` to distinguish dev from prod schema behavior. **Environment type** (Development, Production, Staging, General) is a dbt Cloud platform concept that determines which job is the Catalog source of truth, how cross-project refs resolve, and what the environment is used for. Setting `target.name = prod` on a job in a General environment does NOT make it a Production environment. |
>
> > 💡 **Key rule**: `target.name` = runtime string for macro logic (set in job Advanced Settings). Environment type = dbt Cloud platform concept. Completely independent.

---

### Q14.
> **Subdomain 3.14 — Dev cross-project ref with no upstream Staging**

A dbt Mesh has a consumer project (`marketing`) and a producer project (`platform`). The `platform` project has only a **Production** environment — no Staging environment exists. A developer working in the `marketing` IDE opens a run and references a public model from `platform`. Which environment does the cross-project ref resolve against?

- A) It resolves against the `platform` project's **Production** environment — this is the only scenario where a development IDE job resolves cross-project refs against Production.
- B) The ref fails — development jobs cannot resolve against Production environments.
- C) It resolves against the `marketing` project's Staging environment as a proxy.
- D) It prompts the developer to select an environment from the `platform` project.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Cross-project ref resolution follows this rule: dev jobs resolve against **Staging if it exists**, else **Production**. When the upstream (`platform`) project has no Staging environment, the developer's IDE job resolves directly against `platform`'s **Production** environment. This is the **only** scenario where a development job legitimately resolves against Production. It is a data-access risk — developers may inadvertently query production data. |
> | **B) ❌ Incorrect** | Dev jobs CAN resolve against Production — this is the documented fallback when no Staging environment exists in the upstream project. |
> | **C) ❌ Incorrect** | The consumer project's Staging environment is irrelevant to resolving refs in the upstream project. Resolution is always within the upstream project. |
> | **D) ❌ Incorrect** | Environment selection is automatic — there is no manual prompt. |
>
> > 💡 **Key rule**: Dev cross-project ref → Staging (if exists) else Production. No upstream Staging = dev resolves against Production (only time this happens).

---

### Q15. ⭐
> **Subdomain 3.15 — Staging environment and dev resolution (no fallback)**

An architect adds a **new Staging environment** to an upstream dbt Mesh project. No deployment jobs have been run in this Staging environment yet. What immediately happens to developer IDE jobs in downstream consumer projects that reference this upstream project?

- A) Nothing changes immediately — downstream dev jobs continue resolving against Production until the first Staging job succeeds.
- B) Downstream dev jobs now resolve against both Staging and Production simultaneously, merging metadata from both.
- C) Downstream dev IDE jobs immediately start failing to resolve cross-project references because dbt routes all dev resolution to the new Staging environment, which has no metadata yet. There is no fallback to Production.
- D) dbt detects the empty Staging environment and temporarily routes to Production until the first Staging run succeeds, then switches automatically.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The transition is immediate, not gradual. As soon as the Staging environment is created and linked to the metadata service, dbt routes to it — even with no runs. |
> | **B) ❌ Incorrect** | dbt does not merge metadata from multiple environments. Resolution is to one environment only. |
> | **C) ✅ Correct** | The moment a Staging environment exists and is linked to the metadata service, dbt **immediately** routes all downstream dev cross-project ref resolution to it — with **no fallback to Production**. Since no deployment jobs have run in Staging, there is no metadata for the upstream models, and resolution fails. This is a critical architect gotcha: always run at least one successful deployment job in the new Staging environment before downstream teams depend on it. |
> | **D) ❌ Incorrect** | There is no automatic fallback mechanism once a Staging environment exists. The fallback to Production only applies when no Staging environment exists at all. |
>
> > 💡 **Key rule**: Adding Staging immediately breaks downstream dev resolution if no jobs have run in it yet. Always run one successful job in Staging before downstream teams depend on it.

---

### Q16.
> **Subdomain 3.16 — Deleting an environment**

An architect plans to delete a General environment that was used for experimental jobs. Before deleting, what must they do to avoid data loss?

- A) Export the run history to CSV, since it cannot be recovered after deletion.
- B) Archive the environment first — dbt Cloud auto-archives all jobs before deletion.
- C) Transfer all jobs configured in that environment to another environment first — deleting an environment deletes all jobs in it.
- D) Nothing — job definitions are stored at the project level and persist after environment deletion.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Run history export is not a documented concern here — job definitions are the critical thing to preserve. |
> | **B) ❌ Incorrect** | There is no auto-archive step — dbt Cloud does not preserve jobs in an archived state when an environment is deleted. |
> | **C) ✅ Correct** | When an environment is deleted, **all jobs configured in that environment are also deleted**. There is no recovery path. The architect must **transfer jobs to another environment** before deleting. This is an irreversible action — always confirm there are no jobs you want to keep before proceeding. |
> | **D) ❌ Incorrect** | Jobs are not stored at the project level independently of environments — they belong to an environment. |
>
> > 💡 **Key rule**: Deleting an environment = all jobs in it are also deleted. Transfer jobs first — no recovery after deletion.

---

### Q17.
> **Subdomain 3.17 — Snowflake key pair credentials**

A team sets up Snowflake key pair authentication for a deployment environment. Where do the keys go?

- A) The private key goes on the Snowflake user. The public key goes in dbt.
- B) The private key goes in a dbt environment variable.
- C) Both keys go in dbt.
- D) The public key goes on the Snowflake user (`rsa_public_key`). The private key and passphrase go in the dbt Credentials page.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Reversed. |
> | **B) ❌ Incorrect** | The docs say specifying the private key through an environment variable is not supported. |
> | **C) ❌ Incorrect** | Only the private key (and passphrase) go in dbt. |
> | **D) ✅ Correct** | `alter user jsmith set rsa_public_key='...'` on the Snowflake side. Then set **Private Key** and **Private Key Passphrase** on the dbt Credentials page. |
>
> > 💡 **Key rule**: Public key → Snowflake user. Private key + passphrase → dbt Credentials. Key pair is the default for new Snowflake credentials. dbt v2 wants PKCS#8 with AES-256. Rotating via the Admin API is an exam objective, but the docs I found don't describe the steps.

---

### Q18.
> **Subdomain 3.18 — Environment editable fields by platform**

A team uses Postgres. They want to change a connection value for one deployment environment, but the environment settings show no connection section. What do they do?

- A) Create a new Postgres connection for every environment.
- B) Use extended attributes on the environment's profile.
- C) It can't be done on Postgres.
- D) Set the value in the job's Target name field.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not needed. Values come from the project connection and extended attributes override them. |
> | **B) ✅ Correct** | The docs say the section doesn't appear for Postgres because all values are inferred from the project's connection. Use extended attributes to override them. The same goes for Redshift, BigQuery and Spark. |
> | **C) ❌ Incorrect** | Extended attributes exist for this. |
> | **D) ❌ Incorrect** | Target name is a string for macro logic. It doesn't change connection values. |
>
> > 💡 **Key rule**: Snowflake = Role, Database, Warehouse. Databricks = Catalog (optional). Postgres, Redshift, BigQuery, Spark = no connection fields, use extended attributes.

---

### Q19.
> **Subdomain 3.19 — Developer plan scheduling interval**

A team on the **Developer plan** wants to schedule a dbt job to run every 5 minutes to keep their data as fresh as possible. Will this work?

- A) No — the Developer plan has a minimum scheduling interval of **10 minutes**. A 5-minute schedule cannot be set.
- B) Yes — 5-minute intervals are supported on Developer plan but require cron syntax.
- C) Yes — there is no minimum scheduling interval documented for the Developer plan.
- D) No — the Developer plan does not support scheduled jobs at all; only manual triggers are available.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The **Developer plan** enforces a minimum scheduling interval of **10 minutes**. A 5-minute schedule cannot be configured on this plan. Teams that need sub-10-minute freshness must upgrade or use an alternative triggering mechanism via the API. Starter, Enterprise, and Enterprise+ do not have a documented minimum scheduling interval. |
> | **B) ❌ Incorrect** | Cron syntax does not bypass the 10-minute minimum on Developer plan. |
> | **C) ❌ Incorrect** | A minimum interval is documented for the Developer plan. |
> | **D) ❌ Incorrect** | Developer plan does support scheduled jobs — it just has a 10-minute minimum interval. |
>
> > 💡 **Key rule**: Developer plan = 10-minute minimum scheduling interval. Other plans have no documented minimum.

---

### Q20.
> **Subdomain 3.20 — Secrets in extended attributes**

A team needs a password inside an environment's extended attributes. What is the recommended way?

- A) Hardcode it. Extended attributes are encrypted and masked.
- B) Reference an environment-scoped env var.
- C) Reference a project-scoped env var with the `DBT_ENV_SECRET_` prefix: `password: '{{ env_var('DBT_ENV_SECRET_PASSWORD') }}'`.
- D) Reference any env var name, e.g. `SNOWFLAKE_PASSWORD`.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say extended attributes don't mask secret values. They recommend avoiding secrets in the text box and logs. |
> | **B) ❌ Incorrect** | Environment-scoped variables aren't available during connection tests, so they must be project-scoped. |
> | **C) ✅ Correct** | Wrap secrets in an env var. `DBT_ENV_SECRET_` values are scrubbed from logs and never shown in the UI or artifacts. Variables used in extended attributes must be project-scoped. |
> | **D) ❌ Incorrect** | Env var names must start with `DBT_`, `DBT_ENV_SECRET_` or `DBT_ENV_CUSTOM_ENV_`. |
>
> > 💡 **Key rule**: Secrets → `DBT_ENV_SECRET_` env var, project-scoped, referenced from extended attributes. Snowflake private keys can't come from an env var at all.

---

### Q21.
> **Subdomain 3.21 — Environment-level permissions**

Developers should be able to create and run jobs in Staging but not write to Production. What do admins set up?

- A) Environment-level permissions on the developers' group: write access for the Staging environment type, not Production.
- B) A separate dbt account for production.
- C) A read-only toggle in the Production environment's settings.
- D) A separate project for each environment.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Admins give a group write access by environment **type** (Account settings → Groups & Licenses). The docs suggest locking Production and allowing Development, Staging and General. |
> | **B) ❌ Incorrect** | Not needed. The docs do this inside one account and project. |
> | **C) ❌ Incorrect** | Access is set on the group, not on the environment. |
> | **D) ❌ Incorrect** | Not needed. The docs restrict Production within a single project. |
>
> > 💡 **Key rule**: Environment-level permissions are per group and per environment **type**, not per single environment. Supported permission sets: Database admin, Git admin, Team admin, Analyst, Developer. Nothing selected = read-only. Developer defaults to **All environments**.

---

*[End of Topic 3 — 21 questions]*

