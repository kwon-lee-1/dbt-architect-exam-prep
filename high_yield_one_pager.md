# dbt Architect — High-Yield One-Pager

> Read top-to-bottom morning of exam. **Bold = trap-grade**. Pair with `cheat_sheet.md`.

---

## Plan Tier Matrix (memorize this column)

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|:-:|:-:|:-:|:-:|
| Job chaining | ❌ | ✅ | ✅ | ✅ |
| Cross-project ref (Mesh) | ❌ | ❌ | ✅ | ✅ |
| `dependencies.yml` projects | ❌ | ❌ | ✅ | ✅ |
| Advanced CI / dbt compare | ❌ | ❌ | ✅ | ✅ |
| SSO / SCIM | ❌ | ❌ | ✅ | ✅ |
| Column-level lineage | ❌ | ❌ | ✅ | ✅ |
| Multi-project lineage | ❌ | ❌ | ✅ | ✅ |
| PrivateLink | ❌ | ❌ | ❌ | ✅ |
| Azure DevOps native | ❌ | ❌ | ✅ | ✅ |
| BigQuery OAuth | ❌ | ❌ | ✅ | ✅ |
| Model Query History | ❌ | ❌ | ✅ | ✅ |
| Run slots | 1 | 1 | many | many |
| Minimum schedule interval | 10 minutes | — | — | — |

Memory limit: **600 MiB per pod, all plans.** CI jobs bypass run slots entirely.

---

## License → Group Rules (T5)

| License | Inherits group permissions? | Has IDE? |
|---|:-:|:-:|
| Developer | ✅ | ✅ |
| Analyst | ✅ (Enterprise / Enterprise+) | ✅ |
| **IT** | ❌ fixed: Security Admin + Billing Admin + Connections | ❌ |
| **Read-Only** | ❌ fixed: view artifacts + deploy section | ❌ |

- Assigning IT or Read-Only license to ANY group has **no effect**.
- Multiple groups → **most permissive group wins**.
- New users are auto-added to **both Member AND Everyone** groups.
- Owner group permissions **can't be changed**.
- Project Admin **cannot** create projects (only Account Admin or Project Creator can).
- Security Admin = **zero data access** (users, SSO, IP allowlists only).
- Database Admin = **no IDE access**.
- SCIM (Okta and Entra ID) provisions and de-provisions users and groups from the IdP. License mappings and SSO group mappings apply at sign-in.
- SSO re-authentication required every **24 hours**; admins keep password fallback even with SSO enforced.
- License mappings: Groups & Licenses → **IdP group names** for Read-Only / Developer. In both → Developer. In neither → default license (IT can't be default).
- Service token: shown only once on creation; **403 Forbidden = IP allowlist failure**; rotate by create-new → swap integrations → delete-old. Created with a **Developer license + account admin permissions**. One token can carry **multiple permission sets**, each scoped to all projects or specific projects. Pre-July 18, 2023 tokens should be rotated to the new format.

**PAT vs Service Token (exam-critical):**

| | PAT | Service Token |
|---|---|---|
| Identity | User-tied | Account-level |
| Permissions | **Inherited** from user (license + groups) — not configurable | Explicitly assigned permission sets |
| Multi-permission-set per token | No | **Yes** |
| Project scoping | User's projects | Per-permission-set: all or specific |
| Same user, 2 dbt accounts | **Separate PAT per account** | N/A |
| Use for | dbt CLI, user-specific access | Production CI/CD, Terraform, Semantic Layer, partner integrations |

**Service-token permission sets by tier:** Enterprise/Enterprise+ = any; Legacy Team = limited list; **Developer/Starter = Semantic Layer only**.

**Top traps:** Production automation → service token. PAT permissions are inherited (not set on the token). A PAT can't create a service token. Semantic Layer = service-token-only; v2 Migration Admin = user-only.

**SSO Okta SAML setup — quick map:**
- *Okta:* create app (Web, SAML 2.0) → SAML Settings: SSO URL `https://YOUR_AUTH0_URI/login/callback?connection=<slug>`, Audience `urn:auth0:<entity>:<slug>`, Relay State `<slug>`, Name ID Unspecified, App username `user.getInternalProperty("id")` (or **Email** if SCIM in scope) → Attribute Statements (`email`, `first_name`, `last_name`) → Group Attr `groups` regex `.*` (Okta caps at **100 groups/user**) → finish → **View Setup Instructions** (copy SSO URL, Issuer, X.509 cert).
- *dbt Cloud:* Account settings → SSO & SCIM → Get started / Edit → paste SSO URL, Issuer, X.509 cert → Save.
- *Login URL:* `https://YOUR_ACCESS_URL/enterprise-login/<slug>`.
- *Cert expiry is manual* — Okta admin must regenerate before expiry; expired cert breaks SSO entirely.

---

## Permission Sets (T5b)

| Role | Scope | Has IDE? | Key trap |
|---|---|:-:|---|
| Account Admin | Account | ✅ | The only role with full account-wide access |
| Project Creator | Account | ✅ | Creates and configures projects; write access to IDE, jobs, environments, connections. **Not** SSO / billing / IP |
| Security Admin | Account | ❌ | Users / groups / SSO / IP only — **zero data access** |
| Billing Admin | Account | ❌ | Billing section only (can read public models) |
| Account Viewer | Account | ❌ | Read-only **incl. full audit log w/ sensitive info** |
| Cost Insights Admin / Viewer | Account | ❌ | Cost data only |
| Admin | Project | ✅ | Full project control but **cannot create projects** |
| Developer | Project | ✅ | Builds models, manages production behavior (≠ Developer license) |
| Analyst | Project | ✅ | Run and analyze models in the IDE; can't create or edit outside it |
| Job Admin | Project | ❌ | Create/edit/run jobs + warehouse configs — **no IDE** |
| Job Runner | Project | ❌ | Execute existing jobs only — minimal role |
| Job Viewer | Project | ❌ | Read-only job results, status, logs |
| Database Admin | Project | ❌ | Platform configs + Semantic Layer — **no IDE** |
| Git Admin | Project | ❌ | Git integrations + env vars — **no IDE** |
| Stakeholder ≡ Read-Only | Project | ❌ | Read-only; audit log **excludes sensitive info** |
| Metadata | Project | ❌ | Discovery API read-only |
| Semantic Layer | — | ❌ | Query API only — **service token exclusive** (not assignable to users) |
| v2 Migration Admin | — | ❌ | dbt v2 upgrade workflows — **user-only** (not assignable to service tokens) |

**Who can do X — quick lookup:**

| Task | Roles |
|---|---|
| Create projects | Account Admin, Project Creator (only) |
| Access IDE | Account Admin, Project Creator, Admin, Developer, Analyst |
| Create / edit jobs | Account Admin, Project Creator, Admin, Job Admin |
| Trigger jobs | above + Job Runner |
| Manage SSO / users / licenses | Account Admin, Security Admin |
| Edit connections | Account Admin, Project Creator (IT license too) |
| Configure Semantic Layer | Account Admin, Admin, Database Admin |
| Query Semantic Layer via API | **Semantic Layer service token only** |
| Full audit log (incl. sensitive) | Account Admin, Account Viewer |
| Limited audit log (no sensitive) | Stakeholder / Read-Only |
| Manage service tokens | Account Admin (write); Security Admin (read only) |
| Create webhooks | Enterprise-tier: Account Admin, Admin or Developer permission set. Starter: Developer license |

- **Admin ≠ Account Admin** — project Admin **cannot create projects** (only Account Admin or Project Creator can).
- **Security Admin = zero data access** — no IDE, no jobs, no environments, purely administrative.
- **Database Admin = no IDE** — manages platform configs but cannot write dbt code.
- **Git Admin = no IDE** — manages repositories and integrations only.
- **Stakeholder ≡ Read-Only** — identical permission set under two names; both **exclude sensitive audit info**. For the full audit log, use **Account Viewer**.
- **Semantic Layer = service-token-only**; **v2 Migration Admin = user-only** — the two are non-interchangeable.
- License caps effective permissions even if the user's group is more permissive — e.g., Admin group + Read-Only license = Read-Only.

---

## Schema Generation (T3b — guaranteed question)

Default formula: `<target.schema>_<custom_schema>`. The custom schema **APPENDS, it never replaces**.

| Setup | Result |
|---|---|
| Development `dbt_user_1`, no schema config | `dbt_user_1` |
| Development `dbt_user_1`, `schema: core` | **`dbt_user_1_core`** |
| Production `analytics`, `schema: core`, default macro | `analytics_core` |
| Production `analytics`, `schema: core`, override macro | `core` |

Docs override checks `target.name` (set `prod` on the production job): prod uses the custom schema; dev/CI ignore it and use the target schema. Built in as `generate_schema_name_for_env`, off by default:
```jinja
{%- if target.name == 'prod' and custom_schema_name is not none -%}{{ custom_schema_name | trim }}
{%- else -%}{{ default_schema }}{%- endif -%}
```
- **Never strip the `target.schema` prefix in development** → causes multi-developer collisions.
- A custom macro that drops the `dbt_cloud_pr_` prefix → **orphaned CI schemas** (temp schemas aren't dropped). ✅ `dbt_cloud_pr_123_456_marketing` ❌ `marketing`.

---

## Environments (T3)

- **Counts per project**: Development = 1, Production = 1, Staging = 1, General = unlimited.
- **Profiles**: deployment environments get connection + credentials from a project-level profile (not dev); swap it in environment settings. Older material says the connection is immutable; current docs don't say that.
- **Staging trap**: once created, Staging is **instantly used** for development cross-project resolution; there is **no fallback to Production**, even with zero successful Staging runs. Safe order: create it unmarked → run a job → mark it Staging.
- **Extended attributes**: top-level YAML keys only; to change a sub-key give the whole top-level key as JSON. They don't mask secrets → project-scoped `DBT_ENV_SECRET_` env vars.
- **Environment variable precedence**: job (or personal IDE) > environment > project default. **No account level.**
- Snowflake environment fields editable in UI: Role, Database, Warehouse. Postgres / Redshift / BigQuery / Spark: no editable fields, use extended attributes.
- **Deferral** uses the latest **successful** run in the deferred environment (needs at least one). IDE defer fails if Staging exists but never ran.
- Release tracks (v1): **Latest** (default), **Compatible** (monthly, Starter+), **Extended** (previous month's Compatible, Enterprise / Enterprise+), **Fallback** (Enterprise+). v2: Nightly, **Stable** (default), Extended, Fallback.
- Deleting an environment also deletes **all of its jobs** — transfer jobs first.

**Cross-project ref resolution (MEMORIZE):**

| Consuming environment | Resolves to producer's |
|---|---|
| Development | Staging if it exists, otherwise **Production** |
| Staging | Staging if it exists, otherwise Production |
| Production | Production |

---

## Warehouse Connections (T1)

- Connections are **account-level**; one per environment; one warehouse per job.
- IPs are listed per region but can change occasionally — docs recommend dbt **hostnames** as the stable reference. Single-tenant: ask Support.
- PrivateLink: **Enterprise+ / Virtual Private**, same cloud on both sides. With ingress PrivateLink or IP allowlisting, CI hooks may be unavailable → silent CI failure.
- OAuth = **development only**, per developer. Client ID/Secret go on the connection (Account settings → Connections).

| Platform | Trap |
|---|---|
| Snowflake | Account ID = **locator format** (`db5261993.east-us-2.azure`), NOT the `.snowflakecomputing.com` URL |
| Snowflake | Key pair = default for new creds (dev + deploy); **new username/password creds not allowed**; Snowflake OAuth = dev only, Enterprise |
| Snowflake (dbt v2) | Key = **PKCS#8 AES-256**, no 3DES/headerless. "Could not deserialize key data" = bad paste (missing dashes / BEGIN-END lines) |
| Snowflake custom domain | Locator in Account field + `host:` in extended attributes |
| BigQuery OAuth | Dev only + **Enterprise**; ID/Secret on the connection (OAuth 2.0 Settings); each developer: Credentials → Native OAuth. Deploy = Service JSON or WIF |
| Databricks | `dbt-spark` is deprecated → use `dbt-databricks`; Unity Catalog requires dbt 1.1+; Python models require dbt 1.3+ |
| Databricks | Server Hostname + HTTP Path always required; Catalog field optional (Unity Catalog only) |
| Managed repository | Trial only — no pull requests; dbt Labs recommends against production; export any time |

Snowflake minimum grants: `USAGE` on warehouse, database, schema + `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP` on schema.

---

## Git Connections (T2)

| Provider | Rules |
|---|---|
| GitHub native | Requires GitHub **organization owner** + dbt Account Admin to install; Enterprise/Enterprise+: each developer must link their profile (IDE checks read/write access); Starter: optional |
| GitHub on-prem or `ghe.com` | Shared dbt app can't reach it. Enterprise/Enterprise+: custom GitHub app (**private beta**). Other plans: git URL / deploy key |
| Azure DevOps | **Enterprise / Enterprise+ only** for native integration with auto-CI; Starter/Developer = deploy key, no automated CI |
| Azure DevOps Server (on-premises) | **No native integration on any plan** |
| Azure DevOps | Service Principal preferred over Service User; a new pull request whose latest commit already triggered a run (e.g. **reused branch**) will not trigger CI |
| GitLab | OAuth app uses the **`api`** scope; dbt sets up a webhook (triggers CI) + project access token (reports status) |
| GitLab | Repositories must be in a **GitLab group** (personal repositories are unsupported); **Maintainer** role required |
| GitLab Free | CI runs but **no merge request status is posted back** |
| BitBucket / AWS CodeCommit | No native integration — use git URL + Admin API (Enterprise/Enterprise+); temp schema is **not** auto-deleted |
| All providers | Repository name must match the URL **exactly, including case** — mismatch causes clone errors or job failures |
| All providers | **Fork pull requests are not supported** — contributors must push to the origin repository |
| Deploy keys | Need **read and write** access; no automated CI, no PR status updates |

---

## Jobs and CI/CD (T4)

**Deploy job:**
- Environment defaults to the one you created the job from.
- Commands run sequentially; one failure stops all subsequent steps.
- **Source freshness as a CHECKBOX** = runs first, failure isolated. **As a command step** = blocks the chain on failure.
- **Generate docs checkbox**: v1 only (not for dbt v2 jobs; Catalog refreshes automatically). Production and staging job runs update Catalog.
- Compare changes against: No deferral (default) / Environment (recommended) / This Job (older self-deferral).
- Threads default to 4. Target name is set here and drives custom macro logic.

**Job chaining setup ("Run when another job finishes"):**
- Tier: **Starter and Enterprise-tier** (not Developer). Cross-project chaining needs more than one project → Enterprise-tier.
- Path: Deploy → Jobs → **downstream** job → **Triggers** → enable **Run when another job finishes** → pick **parent project** + **upstream job** + **Completes on** (Success only, or all statuses) → Save.
- Run details page on a triggered run shows a link back to the upstream job that fired it.
- One upstream job can trigger several downstream jobs, including in other projects.

**CI job:**
- Default command: `dbt build --select state:modified+`. Triggered-by-pull-request is ON. Run on draft pull requests is OFF.
- Linting (SQLFluff): Starter+. Choice between stop or continue on lint error.
- **Advanced CI / dbt compare**: Enterprise / Enterprise+; requires the **same database host as production** + a primary-key constraint or uniqueness test on the model.
- Compare run timeout: 3600 seconds (1 hour) — only active when compare is enabled.
- Cached comparison rows: **100 rows per model, 30-day expiry, encrypted** (S3 or Azure Blob). **Not dynamically masked** — all account users can see cached rows → restrict the CI environment's credentials or use synthetic data.
- Without `event_time` set on a model, dbt compare uses CI's narrower date window and reports false "deleted rows" every run.
- Same pull request → CI runs **serially with smart cancellation** of stale builds. Different pull requests → CI runs **concurrently**.
- **Monorepo**: a single pull request triggers CI for **all connected projects** (no file-path filtering).
- CI temporary schema: `dbt_cloud_pr_<job_id>_<pr_id>` — dropped on pull request close or merge (not for API-triggered CI, or if a schema override loses the `dbt_cloud_pr_` prefix).
- CI jobs **bypass run slots**. Catalog updates come from production and staging deployment job runs.

**Command rules:**
- `dbt build` goes before `dbt sl validate` (the order in the docs' CI setup).
- An upstream test failure in `dbt build` → downstream models receive **SKIP** status (not error). Use `severity: warn` to prevent blocking.
- Unit tests run **before** model materialization (fail early, cheaper).
- `dbt retry` is a **no-op** if no nodes ran (infrastructure failure with no entries in `run_results.json`).

**Scheduling:**
- All times are **UTC**. Intervals run every N hours from midnight UTC → use **cron** for exact times.
- If a run takes longer than the interval, the scheduler keeps the newest queued run and cancels the rest.
- **100 consecutive failures → automatic job deactivation** (deploy and CI jobs).

**Deferral types:**

| Type | When to use | Breaks when |
|---|---|---|
| Environment deferral | Standard CI (CI default = Production) | No successful run in that environment yet |
| Self-deferral (This Job) | Older option: that job's own last successful run | Docs don't say what a first run does |
| No deferral | When state is unreliable | Always full rebuild (expensive) |

`--state` and `--target-path` **must point to different directories** — pointing to the same directory causes dbt to overwrite the manifest before comparison, giving non-idempotent state comparison.

---

## Node Selection (T4b)

| Operator | Meaning |
|---|---|
| `+model` / `model+` / `+model+` | upstream / downstream / both |
| `2+model` / `model+1` | bounded depth (N levels) |
| `@model` | full closure: model + descendants + ancestors of those descendants |
| space | union (OR) |
| comma | intersection (AND) |
| `--exclude` | difference |

State selectors (require `--state path/to/manifest`): `new`, `modified`, `old`, `modified.body`, `modified.configs`, `modified.relation`, `modified.macros`, `modified.contract`.

- **`var()` / `env_var()` value changes aren't traced by `state:modified`** — a model is likely flagged only if its config changes.
- Seeds larger than 1 MiB are tracked by **path only**, content edits are invisible.
- Indirect selection modes: `eager` (default — any parent selected triggers the test) | `cautious` (all parents must be selected) | `buildable` | `empty`.
- `--favor-state`: flips dev-relation-first lookup → state-manifest-first lookup.
- `result:error` (run errors) versus `result:fail` (test assertion failures).
- **`source:` vs `source_status:` trap**: `source:<name>+` is **name-based** (looks for a source literally called `<name>`); `source_status:fresher+` is **state-based** — selects sources with newer `max_loaded_at` than the prior `sources.json` plus downstream. `source_status:` documents only `fresher`. **Requires `--state path/to/previous/`** — without it, resolves to zero nodes (silent no-op). `source:fresher+` (single word) is a name lookup that almost never matches anything.
- `dbt ls` doesn't connect to the database (dbt v2.0+). `dbt compile` does. `dbt parse` doesn't.
- `dbt retry` resumes from the failure via `run_results.json`. Nothing ran → nothing to retry. Previous run succeeded → no operation.
- `dbt build`: DAG order, unit tests → model → data tests. Upstream failure **skips** downstream.
- Source freshness needs a `freshness` config. `loaded_at_field` is **optional**.
- `state:modified` ignores `tags` / `meta` changes and sees code, not data. Ephemeral models are never deferred.

Standard slim CI command: `dbt build --select state:modified+ --defer --state /path/to/prod/manifest`.

---

## Blue/Green Deployments (T4c)

- Official docs: blue/green is a **use case of `dbt clone`** (zero-copy warehouses). The swap steps are a **community pattern**.
- `dbt clone`: zero-copy on **Snowflake, Databricks, BigQuery**, otherwise **pointer views**. Skips existing relations unless `--full-refresh`. Platform CLI adds `--defer` automatically, Studio IDE needs the "Defer to production" toggle. dbt 1.6+.
- Clone vs deferral: clone needs compute and extra objects, deferral is often cheaper. Clone when a BI tool needs real objects.
- Community pattern: `dbt run` → `dbt test` → `dbt run-operation swap_database` (a custom macro). A failed step stops the job. Swap only after a full build. Override `ref` / `source` so views don't keep a stale database name.

---

## Monitoring and Alerting (T6)

Job notifications (profile → Notification settings): email, Slack (**public channels only**), Teams. Events: **succeeds / warns / fails / is canceled**. IT license users can receive but not configure.

Webhook events:
- `job.run.started`
- `job.run.completed` — success or failure; fires **after** artifacts are ingested (safe to query the API)
- `job.run.errored` — fires **immediately**; artifacts may not be ingested yet. Subscribe to both → two notifications on an error.

- Plans: **Starter or Enterprise-tier**. Verify with the `Authorization` header (SHA256 HMAC of the body, keyed with the secret).
- **10-second timeout**. Each event retried **5 times**. Delivery log kept **7 days**.
- **Archived after 1,000 consecutive failures or 7 consecutive days** of failures. Reactivate by changing the endpoint URL (UI) or `PUT` with `active: true` (API).
- Run pod memory ceiling: **600 MiB**. Default thread count: 4.

---

## dbt Mesh (T7)

- **Plans:** cross-project `ref()` and project dependencies = **Enterprise and Enterprise+**.
- **Setup is stepwise**: A runs and produces public models → B adds A and runs → A adds B. dbt errors on node-level cycles.
- Upstream needs `access: public` + a successful run after, and a Production env with a successful deploy job (plus Staging, if it exists).
- `dependencies.yml` project name must **case-sensitively match** the upstream's `dbt_project.yml` `name:`.
- Cross-project ref: `ref('project','model')` or `ref('project','model', v=1)`. Unpinned → `latest_version`.
- You can **select** upstream models downstream but **can't build** them. Use **"Run when another job finishes"** to trigger downstream after upstream.
- Resolution: Production → Production. Staging and Development → upstream Staging if it exists, else Production (no fail-over once Staging exists).

**Access levels:**
- `private` — same group. `protected` — same project plus installed packages (**default**). `public` — any group, package or project.
- **Ephemeral models cannot be public** → parse error. A private-ref violation is a `DbtReferenceError` at **parse time**.
- `access` does **not** grant warehouse SELECT — use `grants`. No per-project allowlist for `public`.
- Package `restrict-access: True` → only `public` models can be referenced outside the package.

**Contracts:**
- `enforced: true` → **every column** needs `name` + `data_type`. Mismatch → the model doesn't build.
- Incremental + contract: only `append_new_columns` or `fail`. Python models, materialized views, ephemeral, custom materializations: no contracts.
- Breaking changes: remove a column, change a type, remove/modify a constraint. Ship a **new version**, set `deprecation_date`, let consumers migrate.
- `latest_version` defaults to the highest version. Lower it → newer versions are **prereleases**.

| | Postgres | Snowflake / Redshift | BigQuery | Databricks |
|---|:-:|:-:|:-:|:-:|
| not_null | ✅ | ✅ | ✅ | ✅ |
| primary_key / foreign_key | ✅ | ⚠ defined only | ⚠ defined only | ⚠ defined only |
| unique | ✅ | ⚠ defined only | ❌ | ❌ |
| check | ✅ | ❌ (skipped) | ❌ | ✅ |

**Governance groups:**
- One group per node. `owner` needs a name **or** an email. Members: models, tests, seeds, snapshots, analyses, metrics.
- Model groups are code. The docs don't link them to platform user groups.
- Sources can't be shared across projects → a foundational project with public staging models.

---

## Catalog (T8)

- Plans: Starter, Enterprise, Enterprise+. Column-level lineage, multi-project lineage, query history, Cost Insights = **Enterprise / Enterprise+**.
- Updated by job runs in **production or staging** environments. Dev builds don't appear.
- **CI jobs NEVER update the Catalog**. dbt v2 jobs refresh it automatically (no `dbt docs generate`).
- **No job runs in 3 months → environment metadata purged**.
- Column-level lineage: **SQL models only** (Python models can't be parsed).
- Health signals: Healthy / Caution / Degraded / Unknown (all plans).
- Artifacts setting (Account settings → project → Edit → Artifacts) is for legacy dbt Docs. One production job per project.
- `manifest.json` = project nodes and lineage; `catalog.json` = warehouse metadata (columns, types, stats); `sources.json` = source freshness results.
- **Lenses** (DAG overlays): **single attribute at a time** — you switch between lenses; they cannot be combined on one view. Available lenses:
  - **Resource type** — organizes resources by type (models, tests, seeds, saved query, etc.); uses the `resource_type` selector
  - **Materialization type** — strategy for building dbt models in the platform (table, view, incremental, ephemeral, materialized)
  - **Latest status** — status from the resource's latest execution in the current environment (useful for diagnosing failed DAG regions)
  - **Model layer** — modeling layer per best-practices guide. Detection rules:
    - **Marts** — model prefixed `fct_` or `dim_`, or living in `/marts/`
    - **Intermediate** — model prefixed `int_`, or living in `/int/` or `/intermediate/`
    - **Staging** — model prefixed `stg_`, or living in `/staging/`
  - **Test status** — status from the latest test execution against the resource. If a model has multiple tests with different results, the lens reflects the **worst-case** status.
  - **Consumption query history** — number of queries against the resource over a given time period
- **Model Query History** (Enterprise / Enterprise+): tracks **consumer SELECT queries**, excludes dbt builds and test runs. On by default for new PROD environments. Existing: Production environment → Settings → Edit → Query History → Test Permissions → Enable → Save. View in: Performance → Most consumed models, lineage Lenses, Resources list.
- Cost Insights (Enterprise / Enterprise+): needs metadata credentials + a production job. State-aware orchestration only for cost-reduction data. Calculated once daily.

---

## Hooks and Operations (T9)

| Hook | Where defined | Runs |
|---|---|---|
| pre-hook / post-hook | `dbt_project.yml`, `config()` block, YAML | Per model, seed, snapshot |
| on-run-start / on-run-end | `dbt_project.yml` | Once per command (build, compile, docs generate, run, seed, snapshot, test) |

- On Postgres / Redshift, hooks run **inside the model transaction** by default. Escape with `{sql: "...", transaction: false}` or `before_begin()` / `after_commit()`. **Not on Snowflake, BigQuery, Spark, Databricks.**
- **Redshift `VACUUM`** can't run inside a transaction → `transaction: false`.
- All hook scopes **accumulate**. Order: package → `dbt_project.yml` → model; within one place, definition order.
- `{{ this }}` works in pre/post-hooks. `schemas`, `database_schemas`, `results` = **`on-run-end` ONLY** (none elsewhere).
- Grants: use the **`grants` config**. Hooks only for what it can't do.
- Seeds: hooks via `dbt_project.yml` or YAML (no in-file `config()` block).
- `run-operation`: macro must call `run_query()` or a `statement` block to execute SQL. Args are a YAML string via `--args`. `--sql` needs dbt v1.12+.

---

## Trap List

1. IT and Read-Only licenses **ignore group assignments**.
2. Env var precedence: job (or personal IDE) > environment > project default. **No account level.**
3. Adding a Staging environment routes development resolution **immediately**, with no fallback.
4. `dbt retry` after an infrastructure failure is a **no-op**.
5. Source-freshness and docs-generate as **checkboxes** have isolated failures; as **command steps** they block the chain.
6. GitLab **personal repositories are unsupported**; you need a GitLab group, Maintainer role, and `api` OAuth scope.
7. Webhooks are **archived after 1,000 consecutive failures or 7 days** of failures (each event is retried 5 times).
8. `job.run.errored` fires **before** artifact ingestion.
9. Snowflake account ID is the **locator format**, not the URL.
10. Deferral uses the latest **successful** run in the deferred environment.
11. **Most permissive group wins** for users in multiple groups.
12. An upstream test failure in `dbt build` causes downstream models to receive **SKIP**, not error.
13. Unit tests run **before** materialization.
14. Interval schedules run every N hours from midnight UTC — use cron for exact times.
15. Catalog updates after production and staging job runs. CI jobs never update it.
16. Ephemeral models cannot have `access: public`.
17. Contracts must declare **all columns**; incremental plus contract is restricted to `append_new_columns` or `fail`.
18. The `check` constraint is enforced only on **Postgres and Databricks**.
19. The project name in `dependencies.yml` is **case-sensitive**.
20. `--state` and `--target-path` **must point to different directories** or the manifest is overwritten.
21. A custom schema macro that drops the `dbt_cloud_pr_` prefix produces **orphaned CI schemas**.
22. **PrivateLink with CI hooks results in silent failure**.
23. **Fork pull requests cannot run CI** — contributors must push to origin.
24. Advanced CI cache: 100 rows per model, 30-day retention, **no data masking** → all account users can see it; restrict the CI credentials or use synthetic data.
25. Without `event_time`, dbt compare reports false deleted rows on every CI run.
26. Blue/green is only a `dbt clone` use case in the docs. `swap_database` is a **custom macro**, not a built-in command. Only swap after a full build.
27. **`var()` / `env_var()` value changes aren't traced by `state:modified`** (likely flagged only if the model's config changes); seeds over 1 MiB are tracked by path only.
28. The pod memory ceiling is **600 MiB on every plan**.
29. **100 consecutive failures auto-deactivates a deploy or CI job.**
30. Lenses are **single-attribute** — you cannot combine query volume with materialization on one DAG view.
31. **`access: public` has no per-project allowlist** — once public, *any* downstream project can ref it. There is no syntax to scope a public model to one specific consumer project.
32. **`source:fresher+` ≠ `source_status:fresher+`** — the first is a name lookup (matches nothing unless a source is literally named `fresher`); the second is the state-aware freshness selector and **requires `--state`** with a prior `sources.json` to diff against.
33. **You can select upstream Mesh models downstream but can't build them** — use the upstream project's jobs, plus "Run when another job finishes" to trigger downstream after upstream.
34. **Production CI/CD → service token** (account-level, explicit permission sets). A PAT inherits the creator's permissions and is account-specific. Service tokens need a Developer license + account admin permissions.
