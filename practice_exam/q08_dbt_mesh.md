# Topic 7: dbt Mesh & Cross-Project References — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 23 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 7.1 — Cross-project environment resolution**

A dbt Mesh has two projects: `platform` (producer) and `marketing` (consumer). The `platform` project has both a Staging environment and a Production environment. A developer's IDE job in `marketing` references a public model from `platform`. Which environment does `marketing`'s development job resolve the cross-project ref against?

- A) Production — development jobs always use production data for stability.
- B) The job fails — cross-project refs cannot be resolved from the IDE.
- C) Development — cross-project refs always resolve against the producer's Development environment.
- D) Staging — development jobs in a consumer project resolve against the producer's Staging environment when one exists.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Development jobs do NOT resolve to Production by default when a Staging environment exists. |
> | **B) ❌ Incorrect** | Cross-project refs from the IDE are supported on Enterprise and Enterprise+. |
> | **C) ❌ Incorrect** | The docs resolve downstream Development refs to the upstream's Staging (if it exists) or Production. |
> | **D) ✅ Correct** | The cross-project env resolution table (memorize this): Development → **Staging (if exists), else Production**. Since `platform` has a Staging environment, the `marketing` developer's IDE job resolves refs there. |
>
> > 💡 **Key rule**: Dev → Staging (if exists), else Production. Staging → Staging if it exists, else Production. Production → Production.

---

### Q2. ⭐
> **Subdomain 7.2 — Setting up additional dbt projects stepwise**

An architect is setting up a bidirectional dependency between ProjectA and ProjectB in dbt Mesh simultaneously — adding both `dependencies.yml` entries at the same time and running both projects at once. Both fail to resolve cross-project refs. What went wrong?

- A) Bidirectional dependencies are not supported in dbt Mesh — only one-directional.
- B) Cross-project dependencies must be set up **stepwise**: the producer runs first to generate its manifest, then the consumer adds the dependency and runs. Setting both up simultaneously creates a bootstrap failure.
- C) The project names in `dependencies.yml` use mismatched casing.
- D) Both projects need to be on the same dbt version for cross-project refs to work.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Bidirectional dependencies between projects can be set up — but must be done stepwise, not simultaneously. |
> | **B) ✅ Correct** | The docs say to set up dependent projects stepwise: each project must run and produce public models before the original producer can depend on the original consumer (A runs → B adds A and runs → A adds B). |
> | **C) ❌ Incorrect** | Case sensitivity in `dependencies.yml` is a real gotcha, but the scenario specifically describes a simultaneous setup failure — that's a stepwise issue, not a naming issue. |
> | **D) ❌ Incorrect** | There is no requirement for matching dbt versions across Mesh projects. |
>
> > 💡 **Key rule**: Mesh setup = **stepwise**. Producer runs first → consumer adds dependency → consumer runs. Never simultaneous.

---

### Q3. ⭐
> **Subdomain 7.3 — Ephemeral models cannot be public**

A data engineer sets `access: public` on an ephemeral model to share it across projects. What happens?

- A) dbt throws a **parsing error** — ephemeral models cannot have `access: public`.
- B) The model is automatically converted to a view to support public access.
- C) The model becomes public and is available for cross-project refs.
- D) The model compiles but fails at runtime with an access violation.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say models with `materialized: ephemeral` cannot be `public`, and setting it causes a parse error. |
> | **B) ❌ Incorrect** | dbt does not auto-convert materialization types based on access levels. |
> | **C) ❌ Incorrect** | Not allowed. dbt raises a parse error. |
> | **D) ❌ Incorrect** | The error occurs at **parse time**, not runtime. |
>
> > 💡 **Key rule**: Ephemeral + `access: public` = **parsing error**. Ephemeral can only be `protected` or `private`.

---

### Q4. ⭐
> **Subdomain 7.4 — Model contracts must declare all columns**

A team adds `contract: enforced: true` to a model but only declares 3 of the model's 15 columns in the YAML. What happens?

- A) The contract compiles successfully; undeclared columns get default type validation.
- B) The contract enforces the 3 declared columns and auto-discovers the remaining 12 from the database.
- C) dbt raises a compilation error — contracts require ALL columns to be declared when `enforced: true`.
- D) The contract validates only the 3 declared columns and ignores the rest.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There are no default type validations for undeclared columns. The compilation fails. |
> | **B) ❌ Incorrect** | dbt does not auto-discover or infer contract columns — all must be explicitly declared. |
> | **C) ✅ Correct** | When `contract: enforced: true`, **ALL columns must be declared** in the model's YAML. Partial declarations cause a compilation error. This is by design — a contract guarantees the complete schema, not just selected columns. |
> | **D) ❌ Incorrect** | Partial contracts are not supported — you cannot selectively enforce some columns. |
>
> > 💡 **Key rule**: Contracts = **ALL columns must be declared**. Partial contracts not supported → compilation error.

---

### Q5. ⭐
> **Subdomain 7.5 — check constraint platform support**

A team uses Snowflake as their warehouse and adds a `check` constraint to a model contract expecting it to enforce data validation at the database level. Will this work?

- A) Yes — Snowflake enforces `check` constraints defined in dbt contracts.
- B) No — `check` constraints are not supported in dbt contracts on any platform.
- C) Yes — but only when using the Fusion engine with PKCS#8 key pair authentication.
- D) No — Snowflake does not support `check` constraints in dbt contracts. Only Postgres and Databricks enforce them.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Snowflake doesn't support the `check` syntax. dbt skips the `check` config. |
> | **B) ❌ Incorrect** | `check` constraints ARE supported — just not on all platforms. Postgres and Databricks enforce them. |
> | **C) ❌ Incorrect** | The Fusion engine is related to performance and key pair auth — it doesn't change constraint enforcement capabilities. |
> | **D) ✅ Correct** | `check` constraints are enforced on **Postgres** and **Databricks**. Snowflake doesn't support `check` (dbt skips it), and neither does BigQuery. |
>
> > 💡 **Key rule**: `check` constraints = **Postgres + Databricks only**. Snowflake and BigQuery do NOT support them.

---

### Q6. ⭐
> **Subdomain 7.6 — Requirements for cross-project refs**

A team on dbt Cloud Enterprise has set `access: public` on a model in ProjectA and wants ProjectB to reference it. They add the `ref()` call in ProjectB but get a resolution error. What else is required? **Select TWO correct answers.**

- A) Add a `public_models:` block to ProjectA's `dbt_project.yml`.
- B) Ensure the project name in `dependencies.yml` matches the name in `dbt_project.yml` exactly (case-sensitive).
- C) Configure a shared service token that both projects use for model resolution.
- D) Upgrade to Enterprise+ plan — cross-project refs require Enterprise+, not Enterprise.
- E) Add ProjectA to ProjectB's `dependencies.yml` under the `projects:` key.

> [!success]- Answer & Explanations
> **✅ Correct: B, E**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `public_models:` block in `dbt_project.yml` — public access is declared on individual models via `access: public`. |
> | **B) ✅ Correct** | The project name in `dependencies.yml` is **case-sensitive** and must exactly match the `name:` field in ProjectA's `dbt_project.yml`. The docs say it must match exactly. |
> | **C) ❌ Incorrect** | Cross-project ref resolution uses the dbt Metadata Service — it doesn't require a shared service token between projects. |
> | **D) ❌ Incorrect** | Cross-project refs require **Enterprise or Enterprise+** — both tiers support it. Enterprise alone is sufficient. |
> | **E) ✅ Correct** | The consuming project (ProjectB) must list the producer project (ProjectA) in its `dependencies.yml` under the `projects:` key. Without this, dbt doesn't know to resolve refs against ProjectA's metadata. |
>
> > 💡 **Key rule**: Cross-project ref = `access: public` + Enterprise or Enterprise+ + **`dependencies.yml`** with the exact case-sensitive project name + successful production runs upstream.

---

### Q7.
> **Subdomain 7.7 — Model versioning and deprecation**

A public contracted model `dim_customers` is at `latest_version: 2`. Several downstream teams are still pinned to `v=1`. The platform team wants to retire v1. What is the correct approach?

- A) Set `access: private` on v1 to prevent new consumers from using it while allowing existing ones to continue.
- B) Set a `deprecation_date` on v1 — dbt notifies consumers that v1 is slated for deprecation, giving them time to migrate.
- C) Delete the `dim_customers_v1.sql` file directly — downstream consumers will auto-upgrade to v2.
- D) Change `latest_version` to `1` so all unpinned consumers revert to v1 while the team coordinates.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Changing access to `private` would break cross-project consumers referencing v1 immediately — not a graceful migration. |
> | **B) ✅ Correct** | The docs say dbt notifies consumers of a versioned model when new versions become available or when versions are slated for deprecation. The graceful flow: create v2 → bump `latest_version` → set `deprecation_date` on v1 → let consumers migrate → remove v1 after the date. |
> | **C) ❌ Incorrect** | Deleting `v1.sql` immediately breaks all downstream consumers pinned on v1 — no migration window. |
> | **D) ❌ Incorrect** | Changing `latest_version` back to 1 doesn't help — consumers pinned to v1 are already on v1. Unpinned consumers would move to v1, which may be outdated for them. |
>
> > 💡 **Key rule**: Retiring a model version = set `deprecation_date` → consumers are notified. Never modify contracted public models in place.

---

### Q8.
> **Subdomain 7.8 — Governance groups vs RBAC groups**

A model is assigned to the `finance` governance group with `access: private`. A user in the RBAC "Finance Team" user group tries to reference this model from another model in a different governance group. Does their RBAC group membership grant them access?

- A) Yes — but only if the admin explicitly links the RBAC group to the governance group in Account Settings.
- B) No — private model access requires the user to have a Developer license.
- C) No — governance groups and RBAC user groups are completely orthogonal concepts. RBAC user group membership does not grant governance group model access.
- D) Yes — being in the "Finance Team" RBAC group implies membership in the `finance` governance group.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not documented. |
> | **B) ❌ Incorrect** | License type is about UI feature access, not model governance group access. |
> | **C) ✅ Correct** | A model's `group` is set in project code, and `access: private` means only resources in that group can reference it. Platform user groups are a separate access-control feature, and the docs don't link the two. |
> | **D) ❌ Incorrect** | Not documented. |
>
> > 💡 **Key rule**: Model groups (code) ≠ platform user groups (access control). A model's `group` decides who can `ref()` it when it's private.

---

### Q9.
> **Subdomain 7.9 — Multiple projects sharing sources**

A dbt Mesh has three projects, each needing access to the same raw data sources (e.g., `raw.orders`, `raw.customers`). Can they all define `sources:` for these tables independently?

- A) They shouldn't. The docs advise that no two sources in a mesh point to the same relation. Use a foundational project that exposes public staging models.
- B) Yes — each project can define its own `sources:` for the same raw tables with no conflicts.
- C) No — sources can only be defined in one project. Other projects must import the source definitions via packages.
- D) Sources are defined at the account level in dbt Cloud and shared automatically across all projects.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say sharing sources across projects isn't currently possible. The workaround is a foundational project that holds the source staging models and exposes them as public models. They also advise that no two sources in a mesh point to the same relation. |
> | **B) ❌ Incorrect** | The docs advise against two sources in a mesh pointing to the same relation. |
> | **C) ❌ Incorrect** | Not what the docs say. |
> | **D) ❌ Incorrect** | Sources are not account-level constructs — they're defined within projects. |
>
> > 💡 **Key rule**: Don't share `sources:` across Mesh projects. Use a **foundational project** with public staging models instead.

---

### Q10.
> **Subdomain 7.10 — Recognizing Mesh in lineage graph**

An architect is reviewing the dbt Catalog lineage graph for a project. Which of the following visual indicators confirm the project is part of a dbt Mesh? **Select TWO correct answers.**

- A) The Catalog shows a "Cost Insights" tab for each project.
- B) The graph shows distinct project boundary nodes — upstream projects appear as labeled groupings separate from the local project's DAG.
- C) Lineage edges cross project boundaries with the upstream model labeled by its source project name.
- D) All models display their `access` level (private/protected/public) next to their name.
- E) Models are displayed with their schema and database names visible.

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not a Mesh indicator. |
> | **B) ✅ Correct** | In Catalog, nodes for another project show a project icon next to the project name, and downstream projects appear as separate project nodes connected by dashed lines. |
> | **C) ✅ Correct** | Public models from other projects appear in the lineage, and selecting one shows which project produces it. |
> | **D) ❌ Incorrect** | Not a documented Mesh indicator. |
> | **E) ❌ Incorrect** | Schema and database names may be visible in any project setup — this is not a Mesh-specific indicator. |
>
> > 💡 **Key rule**: Mesh in Catalog = project nodes (project icon) + public models from other projects. Only **directly referenced** public models appear. Account lineage → List view lists projects and public models.

---

### Q11. ⭐
> **Subdomain 7.11 — Incremental model + contract: on_schema_change**

A contracted incremental model on Snowflake uses `on_schema_change: sync_all_columns`. The team runs a refresh and gets a compilation error. What is the issue?

- A) Contracted models cannot be incremental — they must be table or view materializations.
- B) Contracts on incremental models only support `on_schema_change: append_new_columns` or `fail` — `sync_all_columns` is not supported.
- C) `sync_all_columns` is not a valid `on_schema_change` value — the correct value is `sync_columns`.
- D) `sync_all_columns` requires the Fusion engine to work with contracts.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Contracted models can be incremental — they just have restricted schema change options. |
> | **B) ✅ Correct** | The docs say incremental models with an enforced contract are supported only with `on_schema_change: append_new_columns` or `fail`. |
> | **C) ❌ Incorrect** | `sync_all_columns` is a valid `on_schema_change` value in general — it's just incompatible with contracts. |
> | **D) ❌ Incorrect** | The Fusion engine doesn't change the schema change handling for contracted incrementals. |
>
> > 💡 **Key rule**: Incremental + contract = only `append_new_columns` or `fail`. `sync_all_columns` not supported with contracts.

---

### Q12.
> **Subdomain 7.12 — Unpinned ref resolves to latest_version**

A model in a consumer project references an upstream versioned model with an unpinned `ref('dim_customers')` call. The producer project has `latest_version: 2` with v1 and v2 both defined. Which version does the consumer reference?

- A) The call is ambiguous and raises a compile error — all versioned model refs must be pinned.
- B) v1 — unpinned refs always resolve to the lowest version for stability.
- C) The version used depends on which environment the job runs in.
- D) v2 — unpinned refs always resolve to `latest_version`.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Unpinned refs are valid and resolve to `latest_version`. Only when you need a specific older version do you need to pin (e.g., `ref('dim_customers', v=1)`). |
> | **B) ❌ Incorrect** | Unpinned refs resolve to the *latest* version, not the lowest. |
> | **C) ❌ Incorrect** | `latest_version` is a project-level definition — it doesn't vary by environment. |
> | **D) ✅ Correct** | An unpinned `ref('dim_customers')` **always resolves to `latest_version`**. Since `latest_version: 2`, the consumer gets v2. To pin to an older version: `ref('dim_customers', v=1)`. Cross-project: `ref('producer_project', 'dim_customers', v=1)`. |
>
> > 💡 **Key rule**: Unpinned `ref('model')` → resolves to **`latest_version`**. Pin with `v=1` to use older versions.

---

---

### Q13.
> **Subdomain 7.13 — Python models and contracts**

A team wants to apply a dbt contract to a Python model to enforce column types across cross-project consumers. They add `contract: enforced: true` and declare all columns in the YAML. The contract is ignored and no validation occurs. Why?

- A) Python models support contracts but require the `--enforce-contracts` flag at runtime.
- B) Contracts on Python models require dbt 1.5+ — the team is likely on an older version.
- C) Python model contracts require BigQuery or Databricks — they are not supported on Snowflake.
- D) dbt contracts only work on **SQL materializations** — Python models cannot have contracts enforced.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no `--enforce-contracts` runtime flag. Contracts are a compile-time feature, and Python models are simply not supported. |
> | **B) ❌ Incorrect** | Version is not the limitation. Python model contracts are architecturally unsupported regardless of dbt version. |
> | **C) ❌ Incorrect** | The limitation is not platform-specific — Python model contracts are unsupported on all platforms. |
> | **D) ✅ Correct** | The docs list Python models as not supported for contracts (along with ephemeral, materialized views and custom materializations). |
>
> > 💡 **Key rule**: Contracts = **SQL models only**. Python models cannot have contracts. Reimplement as SQL if governance is required.

---

### Q14.
> **Subdomain 7.14 — state:modified.contract selector**

A platform team wants to detect when any model's contract has changed — specifically, when column names or data types in a contracted model's YAML definition have been modified. Which state selector should they use in their CI job?

- A) `state:modified.relation` — detects schema changes
- B) `state:modified.configs` — detects all configuration changes
- C) `state:modified.contract` — specifically detects contract changes (column names or types)
- D) `state:modified.body` — detects SQL content changes

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `state:modified.relation` detects changes to database, schema, or alias — not contract definitions. |
> | **B) ❌ Incorrect** | `state:modified.configs` detects configuration changes but **excludes** database/schema/alias changes. It also does not specifically target contract column/type changes. |
> | **C) ✅ Correct** | **`state:modified.contract`** is the precise selector for detecting when a model's **contract has changed** — specifically column names or data types in the contract definition. This is essential in a dbt Mesh: if a contracted public model's column types change, downstream consumers need to know. Using this selector in CI ensures contract changes are always caught and validated. |
> | **D) ❌ Incorrect** | `state:modified.body` detects changes to the model's SQL or seed file content — not YAML contract definitions. |
>
> > 💡 **Key rule**: `state:modified.contract` = detects contract changes (column names/types). Use in CI for contracted public models.

---

### Q15.
> **Subdomain 7.15 — Cross-project ref syntax**

A developer in the `marketing` project wants to reference a public model named `monthly_revenue` from the `jaffle_finance` project. They also need to pin to version 1 of the model. Which `ref()` calls are correct? **Select TWO correct answers.**

- A) `{{ ref('jaffle_finance', 'monthly_revenue', v=1) }}`
- B) `{{ ref('jaffle_finance', 'monthly_revenue') }}`
- C) `{{ source('jaffle_finance', 'monthly_revenue') }}`
- D) `{{ ref('monthly_revenue') }}`
- E) `{{ ref('jaffle_finance.monthly_revenue') }}`

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Three-argument `ref('project', 'model', v=N)`** is the cross-project ref with version pinning: `{{ ref('jaffle_finance', 'monthly_revenue', v=1) }}`. This pins to version 1 specifically. |
> | **B) ✅ Correct** | **Two-argument `ref('project', 'model')`** is the correct cross-project ref syntax: `{{ ref('jaffle_finance', 'monthly_revenue') }}`. This references the latest version of `monthly_revenue` in the `jaffle_finance` project. |
> | **C) ❌ Incorrect** | `source()` is for raw source tables, not dbt models in other projects. Cross-project model references use `ref()`. |
> | **D) ❌ Incorrect** | Single-argument `ref('monthly_revenue')` only searches within the current project — it will fail or reference a wrong model if the source model is in another project. |
> | **E) ❌ Incorrect** | Dot notation `'jaffle_finance.monthly_revenue'` is not valid `ref()` syntax. The project and model name are separate arguments. |
>
> > 💡 **Key rule**: Cross-project ref = `ref('project_name', 'model_name')`. With version pin = `ref('project_name', 'model_name', v=1)`.

---

### Q16.
> **Subdomain 7.16 — dependencies.yml case sensitivity**

A team's consumer project has the following `dependencies.yml`:
```yaml
projects:
  - name: jaffle_Finance
```
The upstream project's `dbt_project.yml` has `name: jaffle_finance` (all lowercase). Cross-project refs fail. What is the cause?

- A) The upstream project must also list the consumer project in its `dependencies.yml` for bidirectional resolution.
- B) Project names in `dependencies.yml` must match the upstream project's `dbt_project.yml` name **exactly** — including case. `jaffle_Finance` ≠ `jaffle_finance`.
- C) `dependencies.yml` only accepts lowercase project names — uppercase letters are not permitted.
- D) The `dependencies.yml` file must be placed in the `models/` directory, not the project root.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Bidirectional dependencies require careful stepwise setup, but the issue here is simply a case mismatch in the project name. |
> | **B) ✅ Correct** | Project names in `dependencies.yml` are **case-sensitive** and must exactly match the `name:` field in the upstream project's `dbt_project.yml`. `jaffle_Finance` does not match `jaffle_finance`. The docs say the name must match exactly, e.g. `jaffle_marketing`, not `JAFFLE_MARKETING`. |
> | **C) ❌ Incorrect** | Project names can technically be mixed case in `dbt_project.yml`. The constraint is matching exactly, not forcing lowercase. |
> | **D) ❌ Incorrect** | `dependencies.yml` belongs in the project root, not in `models/`. This is correct placement. |
>
> > 💡 **Key rule**: `dependencies.yml` project names are **case-sensitive** — must exactly match `dbt_project.yml` `name:` field.

---

### Q17.
> **Subdomain 7.17 — Protected vs private access**

A team has a model assigned `access: protected` (the default). A developer in a different governance group within the same project tries to reference it. Another developer in an installed package also tries to reference it. Which of these succeed?

- A) The same-project developer succeeds; the package developer also succeeds. `protected` = same project or installed package.
- B) Neither — `protected` is equivalent to `private` and restricts access to the same group only.
- C) The same-project developer succeeds; the package developer fails. `protected` = same project only.
- D) Both succeed — `protected` allows access from any project or package.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **`protected` (default)** allows references from: (1) any model within the **same project** regardless of governance group, AND (2) models in **installed packages**. A developer in a different group within the same project can reference it; a developer in an installed package can also reference it. Only **cross-project refs from other dbt projects** (not packages) are blocked. `private` would restrict to same governance group only. |
> | **B) ❌ Incorrect** | `protected` is less restrictive than `private`. `private` restricts to the same governance group only. |
> | **C) ❌ Incorrect** | Installed packages CAN reference `protected` models — this is one of the two allowed access scenarios. |
> | **D) ❌ Incorrect** | `public` allows any project or package. `protected` is more restrictive than `public`. |
>
> > 💡 **Key rule**: `private` = same group only. `protected` = same project + installed packages. `public` = any project.

---

### Q18.
> **Subdomain 7.18 — --favor-state flag**

A developer runs `dbt build --select state:modified+ --defer --state ./prod` in their local environment. Some modified models exist in their local dev schema, but dbt resolves their upstream parent models against local dev relations instead of production. They want dbt to prefer the production state even when a local dev relation exists. What flag achieves this?

- A) Add `target: prod` to `profiles.yml` to force resolution against production.
- B) `--prefer-prod` — forces all upstream resolution to production.
- C) `--no-defer` combined with `--state` achieves the same effect.
- D) `--favor-state` — flips defer resolution to prefer the state manifest (production) over local dev relations.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Changing `profiles.yml` target changes where the job writes, not how `--defer` resolves upstream parents. |
> | **B) ❌ Incorrect** | `--prefer-prod` is not a valid dbt flag. |
> | **C) ❌ Incorrect** | `--no-defer` disables deferral entirely — it would force all upstream nodes to be built rather than resolved. |
> | **D) ✅ Correct** | By default dbt resolves `ref` against your dev target, and `--defer` only fills in unselected upstream nodes that don't exist there (using the state manifest). **`--favor-state`** flips this priority: it prefers the **state manifest** (production) for resolution even when a local dev relation exists. Use `--favor-state` when you want to test against production-state data, not your potentially-stale local dev state. |
>
> > 💡 **Key rule**: Default `--defer` = your dev relations first, then the state manifest. `--favor-state` = flips priority to prefer state manifest (prod) over local dev relations.

---

### Q19.
> **Subdomain 7.19 — Breaking contract changes**

A platform team has a public contracted model `dim_customers` that downstream projects depend on. Which of the following changes to the contract definition are considered **breaking changes** that require creating a new model version? **Select TWO correct answers.**

- A) Updating a column's description in the YAML
- B) Removing an existing column from the contract definition
- C) Changing a column's data type from `string` to `int`
- D) Adding a new column to the contract definition
- E) Adding a new tag to the model's config block

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Description changes are non-breaking — they have no effect on data or schema. |
> | **B) ✅ Correct** | **Removing an existing column** is a **breaking change** — any downstream consumer referencing that column will fail. This is exactly what contracts protect against: removing a column from a contracted public model without creating a new version is a contract violation. |
> | **C) ✅ Correct** | **Changing a column's data type** is a **breaking change** — downstream models may fail due to type incompatibility. Both removing columns and changing types are the primary breaking change scenarios contracts enforce. |
> | **D) ❌ Incorrect** | Adding a new column is **non-breaking** — downstream consumers that don't use the new column are unaffected. |
> | **E) ❌ Incorrect** | Tag additions are non-breaking configuration changes — they don't affect the model's schema or data. |
>
> > 💡 **Key rule**: Contract breaking changes = **removing columns** + **changing data types** + modifying constraints. Never modify in-place — create a new version.

---

### Q20.
> **Subdomain 7.20 — Public model without contract**

A platform team publishes a model as `access: public` without adding a contract (`enforced: false`). Three months later, they rename a column in the model SQL and the YAML. Downstream consumer projects do not immediately break. When do they break?

- A) Immediately — dbt Mesh validates public model schemas in real-time via the metadata service.
- B) Never — without a contract, downstream projects are not coupled to column definitions.
- C) When the downstream project next **parses and runs** against the updated schema — the breaking change is undetected until runtime.
- D) Within 24 hours — the metadata service refreshes public model schemas on a daily cycle.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The metadata service does not perform real-time schema validation. Downstream projects only encounter the change when they actually run. |
> | **B) ❌ Incorrect** | Downstream projects are still coupled at runtime — if they reference a column by name that no longer exists, the query will fail. The contract merely moves this detection earlier (to compile time). |
> | **C) ✅ Correct** | Without a contract, breaking changes (like renaming a column) are **undetected until the downstream project next parses and runs** against the new schema. The downstream team gets no warning — their pipeline silently succeeds on old data until the next run hits the missing column and fails. This is the core reason contracts on public models are critical: they surface breaking changes at compile time, not at runtime. |
> | **D) ❌ Incorrect** | Not documented. |
>
> > 💡 **Key rule**: No contract on public model = breaking changes detected only at downstream **runtime**. Contracts surface them at compile time. Always add contracts to public models.

---

### Q21. ⭐
> **Subdomain 7.21 — Per-project access scoping**

A platform team owns the `core` project, which contains a sensitive model `customer_pii` they want to expose to **only** the `compliance` consumer project — no other downstream project should be able to reference it. They set `access: public` on the model and add `compliance` to its `dependencies.yml`. A few weeks later, the `marketing` project also adds `core` as a dependency and successfully references `customer_pii`. The platform team is surprised. What is the correct understanding?

- A) The `marketing` project bypassed dbt's access controls — this is a known bug that requires escalating to dbt Labs Support.
- B) `access: public` exposes a model to **any** downstream project that adds the producer as a dependency. dbt Mesh has **no per-project allowlist** for public models. To restrict the model, keep it `private` to a governance group and consume it via a shared package or foundational-project pattern.
- C) The platform team made a configuration mistake — `access: public` accepts an `allowed_projects:` list that they forgot to populate.
- D) Adding `restrict-access: True` to the `core` project's `dbt_project.yml` would have limited the public model to the first project listed in `dependencies.yml`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is the **documented behavior**, not a bug. `public` means public. |
> | **B) ✅ Correct** | `access: public` is **all-or-nothing** — once a model is public, *any* downstream project that adds the producer as a dependency can `ref()` it. dbt Mesh has no per-project allowlist mechanism. The closest workarounds: (1) keep the model `private` to a governance group and have only the intended consumer use it via a shared package, or (2) use a foundational-project pattern that exposes only what's intended for broad consumption. Sensitive models should generally not be `public` at all. |
> | **C) ❌ Incorrect** | There is **no `allowed_projects:` field** on `access: public`. The access modifier is a three-level scope (`private`/`protected`/`public`), not a recipient list. |
> | **D) ❌ Incorrect** | `restrict-access: True` is a **package-level** flag that blocks consumers from referencing `protected` models in an installed package. It is still binary (block all consumers vs. allow all) — not a per-project allowlist, and it does not affect `public` models at all. |
>
> > 💡 **Key rule**: `access: public` = any downstream project can ref it. **No per-project allowlist exists.** Use `private` + shared package, or a foundational-project pattern, for selective exposure.

---

### Q22. ⭐
> **Subdomain 7.22 — Building upstream models from a downstream job**

A downstream project lists an upstream project in `dependencies.yml`. A job in the downstream project selects one of the upstream's public models. What happens?

- A) dbt builds the upstream model in the downstream environment.
- B) The downstream job can select it but can't build it. Upstream models are built by the upstream project's own jobs.
- C) It builds only with `--full-refresh`.
- D) It builds only with `--defer`.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say that with project dependencies you can select upstream models but can't actually build them. |
> | **B) ✅ Correct** | Upstream models aren't parsed or run in the downstream project. The metadata service resolves the ref. |
> | **C) ❌ Incorrect** | A flag doesn't change this. |
> | **D) ❌ Incorrect** | `--defer` doesn't change this either. |
>
> > 💡 **Key rule**: With project dependencies you can select upstream models but can't build them. Build them with the upstream project's own jobs.

---

### Q23. ⭐
> **Subdomain 7.23 — Orchestrating across projects**

A platform team wants the `analytics` project's job to run automatically after the `core` project's deployment job finishes. What do they configure?

- A) `dbt build --select package:core+` in the analytics job.
- B) A `source_status:fresher+` selector in the analytics job.
- C) "Run when another job finishes" on the analytics job, selecting the `core` project and its job.
- D) A copy of the core job inside the analytics project.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A selector can select upstream models in the downstream project but can't build them. |
> | **B) ❌ Incorrect** | A selector doesn't trigger another project's job. |
> | **C) ✅ Correct** | In the job's Triggers, enable Run when another job finishes, pick the project, the upstream job, and the **Completes on** status. It needs a Starter or Enterprise-tier plan, and two projects means an Enterprise-tier plan. |
> | **D) ❌ Incorrect** | Not needed. |
>
> > 💡 **Key rule**: Cross-project orchestration = "Run when another job finishes" (project + job + Completes on). Selectors don't build or trigger upstream projects.

---

*[End of Topic 7 — 23 questions]*

