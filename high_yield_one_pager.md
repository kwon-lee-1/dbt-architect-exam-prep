# dbt Architect — High-Yield One-Pager

> Read top-to-bottom morning of exam. **Bold = trap-grade**. Pair with `cheat_sheet.md`.

---

## Plan Tier Matrix (memorize this column)

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|:-:|:-:|:-:|:-:|
| Job chaining | ❌ | ✅ | ✅ | ✅ |
| Cross-project ref (Mesh) | ❌ | ❌ | ✅ | ✅ |
| `dependencies.yml` projects | ❌ | ❌ | ❌ | ✅ |
| Advanced CI / dbt compare | ❌ | ❌ | ✅ | ✅ |
| SSO / SCIM | ❌ | ❌ | ✅ | ✅ |
| Column-level lineage | ❌ | ❌ | ❌ | ✅ |
| Multi-project lineage | ❌ | ❌ | ❌ | ✅ |
| PrivateLink | ❌ | ❌ | ✅ | ✅ |
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
| Analyst | ✅ (Enterprise only) | ✅ |
| **IT** | ❌ fixed: Security Admin + Billing Admin + Connections | ❌ |
| **Read-Only** | ❌ fixed: view artifacts + deploy section | ❌ |

- Assigning IT or Read-Only license to ANY group has **no effect**.
- Multiple groups → **most permissive group wins**.
- New users are auto-added to **both Member AND Everyone** groups.
- Owner group is **immutable**.
- Project Admin **cannot** create projects (only Account Admin or Project Creator can).
- Security Admin = **zero data access** (users, SSO, IP allowlists only).
- Database Admin = **no IDE access**.
- SCIM (Okta and Entra ID only) syncs **on login, not real-time** — manually deactivate users in dbt Cloud for instant offboarding.
- SSO re-authentication required every **24 hours**; admins keep password fallback even with SSO enforced.
- Identity Provider group names ↔ dbt group names must be **case-sensitive exact matches**.
- Service token: shown only once on creation; **403 Forbidden = IP allowlist failure**; rotate by create-new → swap integrations → delete-old. Created by **Account Admin only**. One token can carry **multiple permission sets**, each scoped to all projects or specific projects. Pre-July 18, 2023 tokens should be rotated to the new format.

**PAT vs Service Token (exam-critical):**

| | PAT | Service Token |
|---|---|---|
| Identity | User-tied | Account-level |
| Permissions | **Inherited** from user (license + groups) — not configurable | Explicitly assigned permission sets |
| Multi-permission-set per token | No | **Yes** |
| Project scoping | User's projects | Per-permission-set: all or specific |
| User deactivated | **Token dies** | Persists |
| Same user, 2 dbt accounts | **Separate PAT per account** | N/A |
| Required for | dbt CLI, user-context endpoints (e.g., updating a specific user's credentials) | Production CI/CD, Terraform, Semantic Layer, partner integrations |

**Service-token permission sets by tier:** Enterprise/Enterprise+ = any; Legacy Team = limited list; **Developer/Starter = Semantic Layer only**.

**Top traps:** PAT in production breaks when employee leaves → use service token. PAT permissions cannot be narrowed on the token (only via user). Semantic Layer Only = service-token-exclusive; Fusion Admin = user-only.

**SSO Okta SAML setup — quick map:**
- *Okta:* create app (Web, SAML 2.0) → SAML Settings: SSO URL `https://YOUR_AUTH0_URI/login/callback?connection=<slug>`, Audience `urn:auth0:<entity>:<slug>`, Relay State `<slug>`, Name ID Unspecified, App username `user.getInternalProperty("id")` (or **Email** if SCIM in scope) → Attribute Statements (`email`, `first_name`, `last_name`) → Group Attr `groups` regex `.*` (Okta caps at **100 groups/user**) → finish → **View Setup Instructions** (copy SSO URL, Issuer, X.509 cert).
- *dbt Cloud:* Account Settings → Enterprise → Single Sign On → Edit → paste SSO URL, Issuer, X.509 cert → Save.
- *Login URL:* `https://YOUR_ACCESS_URL/enterprise-login/<slug>`.
- *Cert expiry is manual* — Okta admin must regenerate before expiry; expired cert breaks SSO entirely.

---

## Permission Sets (T5b)

| Role | Scope | Has IDE? | Key trap |
|---|---|:-:|---|
| Account Admin | Account | ✅ | The only role with full account-wide access |
| Project Creator | Account | ❌ | Can create projects; **cannot** touch SSO / billing / IP allowlists |
| Security Admin | Account | ❌ | Users / groups / SSO / IP only — **zero data access** |
| Billing Admin | Account | ❌ | Billing section only (can read public models) |
| Viewer | Account | ❌ | Read-only **incl. full audit log w/ sensitive info** |
| Cost Insights Admin / Viewer | Account | ❌ | Cost data only |
| Admin | Project | ✅ | Full project control but **cannot create projects** |
| Developer | Project | ✅ | IDE + personal creds; **cannot create/edit jobs or environments** |
| Analyst | Project | ✅ | IDE + view jobs (Enterprise only); cannot create jobs |
| Job Admin | Project | ❌ | Create/edit/run jobs + warehouse configs — **no IDE** |
| Job Runner | Project | ❌ | Execute existing jobs only — minimal role |
| Job Viewer | Project | ❌ | Read-only job results, status, logs |
| Database Admin | Project | ❌ | Platform configs + Semantic Layer — **no IDE** |
| Git Admin | Project | ❌ | Git integrations + env vars — **no IDE** |
| Stakeholder ≡ Read-Only | Project | ❌ | Read-only; audit log **excludes sensitive info** |
| Metadata | Project | ❌ | Discovery API read-only |
| Semantic Layer | — | ❌ | Query API only — **service token exclusive** (not assignable to users) |
| Fusion Admin | — | ❌ | Fusion upgrades — **user-only** (not assignable to service tokens) |

**Who can do X — quick lookup:**

| Task | Roles |
|---|---|
| Create projects | Account Admin, Project Creator (only) |
| Access IDE | Account Admin, Admin, Developer, Analyst |
| Create / edit jobs | Account Admin, Admin, Job Admin |
| Trigger jobs | above + Job Runner |
| Manage SSO / users / licenses | Account Admin, Security Admin |
| Manage connections | Account Admin, Security Admin (write); Database Admin (project write) |
| Configure Semantic Layer | Account Admin, Admin, Database Admin |
| Query Semantic Layer via API | **Semantic Layer service token only** |
| Full audit log (incl. sensitive) | Account Admin, Viewer (account-level) |
| Limited audit log (no sensitive) | Stakeholder / Read-Only |
| Manage service tokens | Account Admin (write); Security Admin (read only) |
| Create webhooks | Account Admin, Developer (project-level write) |

- **Admin ≠ Account Admin** — project Admin **cannot create projects** (only Account Admin or Project Creator can).
- **Security Admin = zero data access** — no IDE, no jobs, no environments, purely administrative.
- **Database Admin = no IDE** — manages platform configs but cannot write dbt code.
- **Git Admin = no IDE** — manages repositories and integrations only.
- **Stakeholder ≡ Read-Only** — identical permission set under two names; both **exclude sensitive audit info**. For the full audit log, use the account-level **Viewer**.
- **Semantic Layer = service-token-only**; **Fusion Admin = user-only** — the two are non-interchangeable.
- Account hierarchy: Account Admin > Security Admin > Project Creator > Billing Admin > Cost Insights Admin > Viewer.
- Project hierarchy: Admin > Job Admin > Developer ≈ Analyst > Database Admin > Git Admin > Job Runner > Job Viewer > Metadata.
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

Override macro must check `target.name` (set on the job under Advanced Settings → Target name; the IDE defaults to `dev`):
```jinja
{%- if target.name == 'prod' -%}{{ custom_schema_name | trim }}
{%- else -%}{{ default_schema }}_{{ custom_schema_name | trim }}{%- endif -%}
```
- **Never strip the `target.schema` prefix in development** → causes multi-developer collisions.
- A custom macro that mangles the `dbt_cloud_pr_<job_id>_<pr_id>` pattern → **orphaned CI schemas** (dbt Cloud cannot identify them for cleanup on PR merge).

---

## Environments (T3)

- **Counts per project**: Development = 1, Production = 1, Staging = 1, General = unlimited.
- **Connection is IMMUTABLE** once assigned to an environment — create a new environment and migrate jobs.
- **Staging trap**: once created, Staging is **instantly used** for development cross-project resolution; there is **no fallback to Production**, even with zero successful Staging runs.
- **Extended attributes**: top-level YAML keys only; partial nested overrides are **silently ignored** (must provide the full parent block).
- **Environment variable precedence**: job > environment > project > account.
- Snowflake environment fields editable in UI: Role, Database, Warehouse. Postgres / Redshift / BigQuery / Spark: no editable fields, use extended attributes.
- **Deferral breaks** if the referenced environment's last run failed (no valid manifest).
- Release tracks: **Latest** (always newest), **Compatible** (slight lag, most teams), **Extended** (slowest, longest support, strictest change management).
- Deleting an environment also deletes **all of its jobs** — transfer jobs first.

**Cross-project ref resolution (MEMORIZE):**

| Consuming environment | Resolves to producer's |
|---|---|
| Development | Staging if it exists, otherwise **Production** |
| Staging | Staging |
| Production | Production |

---

## Warehouse Connections (T1)

- Connections are **account-level**; one per environment; one warehouse per job.
- The lineage graph is **logical** (based on `ref()` and `source()`), never physical warehouse topology.
- Use **hostnames** in firewall rules — dbt IP addresses are dynamic.
- PrivateLink: VPC-to-VPC, Enterprise+ only, region-specific. **CI hooks are unavailable on PrivateLink** → silent CI failure.

| Platform | Trap |
|---|---|
| Snowflake | Account ID = **locator format** (`db5261993.east-us-2.azure`), NOT the `.snowflakecomputing.com` URL |
| Snowflake (Fusion engine) | Key pair must be **PKCS#8 AES-256**; 3DES rejected with "Could not deserialize key data" |
| Snowflake | Multi-Factor Authentication = development environments only |
| Snowflake custom domain | Locator in Account field + `host:` in extended attributes |
| BigQuery OAuth | Development environments only + **Enterprise+ tier**; admin sets up the OAuth app, each developer links via Profile Settings → Linked Accounts |
| Databricks | `dbt-spark` is deprecated → use `dbt-databricks`; Unity Catalog requires dbt 1.1+; Python models require dbt 1.3+ |
| Databricks | Server Hostname + HTTP Path always required; Catalog field optional (Unity Catalog only) |
| Managed repository | Proof-of-concept only — no pull requests, no branches, **never use in production** |

Snowflake minimum grants: `USAGE` on warehouse, database, schema + `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP` on schema.

---

## Git Connections (T2)

| Provider | Rules |
|---|---|
| GitHub native | Requires GitHub **organization owner** + dbt Account Admin to install; each developer must re-link their personal profile |
| GitHub Enterprise (custom domain ≠ `ghe.com`) | Deploy key only |
| Azure DevOps | **Enterprise / Enterprise+ only** for native integration with auto-CI; Starter = deploy key + manual API trigger |
| Azure DevOps Server (on-premises) | **No native integration on any plan** |
| Azure DevOps | Service Principal preferred over Service User; a new pull request on a **reused branch name** will not trigger CI |
| GitLab | OAuth scope must be **`api`** for write-back; `read_api` only = CI runs but no status posted |
| GitLab | Repositories must be in a **GitLab group** (personal repositories are unsupported); **Maintainer** role required |
| GitLab Free | CI runs but **no merge request status is posted back** |
| BitBucket / AWS CodeCommit | No native integration — use git URL + Admin API |
| All providers | Repository name is **case-sensitive** — mismatch causes silent clone failure |
| All providers | **Fork pull requests are not supported** — contributors must push to the origin repository |
| Deploy keys | Read-only; do not support automatic pull-request CI triggers |

---

## Jobs and CI/CD (T4)

**Deploy job:**
- Environment is **immutable after creation**.
- Commands run sequentially; one failure stops all subsequent steps.
- **Source freshness as a CHECKBOX** = runs first, failure isolated. **As a command step** = blocks the chain on failure.
- **Generate docs as a CHECKBOX** = runs last, failure isolated.
- Compare changes options: No deferral / Production / This Job (self-deferral).
- Threads default to 4. Target name is set here and drives custom macro logic.

**Job chaining setup ("Run when another job finishes"):**
- Tier: **Starter+** (not Developer). Cross-project Mesh chaining gated by Enterprise+ via Mesh.
- Path: Deploy → Jobs → **downstream** job → **Triggers** → enable **Run when another job finishes** → pick **parent project** + **upstream job** + **Completes on** statuses (Success / Success+Warning / etc.) → Save.
- Run details page on a triggered run shows a link back to the upstream job that fired it.
- This is the **only** Mesh upstream→downstream orchestration mechanism — no CLI selector crosses project boundaries.

**CI job:**
- Default command: `dbt build --select state:modified+`. Triggered-by-pull-request is ON. Run on draft pull requests is OFF.
- Linting (SQLFluff): Starter+. Choice between stop or continue on lint error.
- **Advanced CI / dbt compare**: Enterprise+ tier; requires the **same database host as production** + a primary-key constraint or uniqueness test on the model.
- Compare run timeout: 3600 seconds (1 hour) — only active when compare is enabled.
- Cached comparison rows: **100 rows per model, 30-day expiry, encrypted** (S3 or Azure Blob). **Dynamic data masking does NOT apply to cached rows** → exclude PII models with `--exclude tag:pii`.
- Without `event_time` set on a model, dbt compare uses CI's narrower date window and reports false "deleted rows" every run.
- Same pull request → CI runs **serially with smart cancellation** of stale builds. Different pull requests → CI runs **concurrently**.
- **Monorepo**: a single pull request triggers CI for **all connected projects** (no file-path filtering).
- CI temporary schema: `dbt_cloud_pr_<job_id>_<pr_id>` — auto-deleted on pull request close or merge.
- CI jobs **bypass run slots** and **do NOT update the Catalog**.

**Command rules:**
- `dbt build` must precede `dbt sl validate` (models must exist before semantic-layer validation).
- An upstream test failure in `dbt build` → downstream models receive **SKIP** status (not error). Use `severity: warn` to prevent blocking.
- Unit tests run **before** model materialization (fail early, cheaper).
- `dbt retry` is a **no-op** if no nodes ran (infrastructure failure with no entries in `run_results.json`).

**Scheduling:**
- All times are **UTC**. Interval scheduling drifts (counts elapsed time from run start) → use **cron** for clock-aligned schedules.
- If a run takes longer than the interval, the scheduler keeps the newest queued run and cancels the rest.
- **100 consecutive failures → automatic job deactivation** (Beta).

**Deferral types:**

| Type | When to use | Breaks when |
|---|---|---|
| Production deferral | Standard CI | Production's last run failed |
| Self-deferral | Cost optimization in chained jobs | First-ever run (no prior manifest) |
| No deferral | When state is unreliable | Always full rebuild (expensive) |

`--state` and `--target-path` **must point to different directories** — pointing to the same directory causes dbt to overwrite the manifest before comparison, resulting in a full build every time.

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

- **`--vars` changes are INVISIBLE to `state:modified`** — only committed content changes mark a model as modified.
- Seeds larger than 1 MiB are tracked by **path only**, content edits are invisible.
- Indirect selection modes: `eager` (default — any parent selected triggers the test) | `cautious` (all parents must be selected) | `buildable` | `empty`.
- `--favor-state`: flips dev-relation-first lookup → state-manifest-first lookup.
- `result:error` (run errors) versus `result:fail` (test assertion failures).
- **`source:` vs `source_status:` trap**: `source:<name>+` is **name-based** (looks for a source literally called `<name>`); `source_status:fresher+` is **state-based** — selects sources with newer `max_loaded_at` than the prior `sources.json` plus downstream. `source_status:` only accepts the value `fresher`. **Requires `--state path/to/previous/`** — without it, resolves to zero nodes (silent no-op). `source:fresher+` (single word) is a name lookup that almost never matches anything.
- `dbt ls` requires **no warehouse connection** (lightest command).

Standard slim CI command: `dbt build --select state:modified+ --defer --state /path/to/prod/manifest`.

---

## Blue/Green Deployments (T4c)

Build green → test green → `dbt run-operation swap_database` → the old blue becomes the next staging environment. If the run or tests fail, the swap never executes and blue stays live.

| Platform | Viable? |
|---|:-:|
| Snowflake (`CLONE` + `SWAP WITH`) | ✅ |
| Databricks (shallow clone) | ✅ |
| BigQuery (dataset workaround) | ✅ |
| **Redshift** | ❌ no rename or swap support |
| **Postgres** | ❌ sequential DDL only |

- **Views with hardcoded database names break post-swap** — override `ref()` and `source()` to drop the database qualifier.
- **Snapshots break** — `dbt_valid_to` continuity is disrupted by the swap; store snapshots in a dedicated, non-swapped database.
- **Incremental models** post-swap have a stale baseline; run `--full-refresh` after swap.
- **Never swap after a partial `--select` run** — green will be incomplete.
- `dbt clone`: zero-copy where supported, pointer views elsewhere; auto-includes `--defer`; skips existing relations unless `--full-refresh` is passed. Use this (rather than deferral) when business-intelligence tools need to query realistic data before cutover.

---

## Monitoring and Alerting (T6)

Webhook events:
- `job.run.started`
- `job.run.completed` — fires **after** artifact ingestion (safe to query the API for artifacts)
- `job.run.errored` — fires **before** artifact ingestion (do not query the API for artifacts)

- **5 consecutive delivery failures = silent automatic disable** (no notification sent).
- Webhook receivers must return a 2xx response within **10 seconds**. 30 days of delivery history is retained.
- Run pod memory ceiling: **600 MiB**. Default thread count: 4.

---

## dbt Mesh (T7)

- **Setup is stepwise**: producer project runs first → consumer adds dependency → consumer runs. Never simultaneous.
- `dependencies.yml` project name must **case-sensitively match** the producer's `dbt_project.yml` `name:` value.
- Cross-project ref syntax: `ref('project','model')` or `ref('project','model', v=1)`. An unpinned ref resolves to `latest_version`.

**Access levels:**
- `private` — same governance group only.
- `protected` — same project plus installed packages (this is the default).
- `public` — any project (cross-project refs require Enterprise+ tier).
- **Ephemeral models cannot be public** → parsing error.
- A private-ref violation is caught at **parse time** as `DbtReferenceError`.
- **No per-project allowlist exists.** `public` = any downstream project; you cannot scope a public model to *one specific* consumer project. Closest workarounds: keep it `private` to a group consumed via a shared package, or use a foundational project pattern. `restrict-access: True` on a package only blocks `protected` refs from consumers — it is not a per-project allowlist either.

**Contracts:**
- `enforced: true` requires that **ALL columns are declared** (a partial contract is a compile error).
- Incremental + contract: only `on_schema_change: append_new_columns` or `fail` allowed (NOT `sync_all_columns`).
- Python models cannot have contracts.
- For breaking changes, never modify in place: ship a new version → set `deprecation_date` on the old version → wait for consumers to migrate → delete.
- `latest_version` is implicit and equals the highest version. Setting it lower makes newer versions act as **prereleases** (shipped but not the default).

**Constraint enforcement:**

| | Postgres | Snowflake | BigQuery | Databricks |
|---|:-:|:-:|:-:|:-:|
| not_null | ✅ | ✅ | ✅ | ✅ |
| primary_key | ✅ | ⚠ defined only | ⚠ defined only | ⚠ defined only |
| unique | ✅ | ⚠ defined only | ❌ | ⚠ defined only |
| check | ✅ | ❌ | ❌ | ✅ |

**Governance groups:**
- Each model belongs to **exactly one** group (precedence: in-file `config()` > `schema.yml` > project-level).
- The owner property accepts a name OR an email (either is sufficient).
- Governance groups are **orthogonal** to RBAC user groups — completely separate systems that may share names by coincidence.
- A package's `restrict-access: True` flag blocks consumers from referencing `protected` models in that package.
- You cannot share `sources:` across projects → use a foundational project that exposes public staging models instead.

**Selecting / orchestrating across projects:**
- An upstream Mesh project added to `dependencies.yml` lives in the **same namespace as Hub packages** → use `package:upstream_name+` (case-sensitive). `dbt ls --select package:upstream` lists pulled-in public models; `--select state:modified+ --exclude package:upstream` is the standard downstream Slim CI pattern.
- **`--select` never triggers an upstream build.** It only filters the current invocation. Cross-project upstream-then-downstream orchestration uses **"Run when another job finishes" chaining** (Starter+ for the feature; Enterprise+ in practice for cross-project Mesh) in the downstream job's Triggers settings — not a CLI flag.
- `state:modified` is **project-local** — does not see upstream column renames or contract updates. The upstream's own CI must run `state:modified.contract`.
- `source_status:fresher+` does **not** flag upstream public models (consumed via `ref()`, not `source()`). Use job chaining to trigger downstream when upstream rebuilds.

---

## Catalog (T8)

- Reflects the **production environment** by default; staging deployment jobs also update the Catalog.
- **CI jobs NEVER update the Catalog**. Only deployment jobs running `dbt docs generate` do.
- One artifact-generating job per project (multiple jobs cause overwrites).
- **3+ months without a successful run → environment auto-purged** from the Catalog.
- Column-level lineage: **Enterprise+ tier and SQL models only** (Python models not supported).
- `manifest.json` = project metadata and lineage graph; `catalog.json` = warehouse-introspected column types and row counts; `sources.json` = source definitions and freshness results.
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
- **Model Query History** (Enterprise+): tracks **consumer SELECT queries**, excludes dbt builds and test runs. Enable: Production environment → Settings → Query History → Test Permissions → Save. View in: project details chart, lineage Lenses, resources list, individual model page.
- Cost Insights: requires Fusion engine plus state-aware orchestration; up to **24-hour refresh lag**.

---

## Hooks and Operations (T9)

| Hook | Where defined | Fires |
|---|---|---|
| pre-hook / post-hook | `dbt_project.yml`, `config()` block, YAML | Per resource (model, seed, snapshot) |
| on-run-start / on-run-end | `dbt_project.yml` **only** | Once per command invocation |

- post-hook runs **inside the model transaction** by default → if the model fails, the hook is skipped; if the hook fails, the model creation is rolled back. Escape with `{sql: "...", transaction: false}`.
- **Redshift `VACUUM`** must use `transaction: false` (cannot run inside a transaction).
- All hook scopes **accumulate** (they never override). Order: package → `dbt_project.yml` → `config()` block.
- `{{ this }}` is available in pre-hooks and post-hooks. `{{ results }}` and `{{ schemas }}` are available in **`on-run-end` ONLY** (silently `None` everywhere else).
- `on-run-end` always fires, even on partial run failures.
- Seeds: hooks via `dbt_project.yml` or YAML property files (no in-file `config()` block, since seeds are CSV).
- `run-operation` is **not part of the DAG**; the macro must call `run_query()` or `{% call statement() %}` to actually execute SQL.
- Hooks vs operations: hooks are automatic and DAG-bound; operations are manual and ad-hoc.

---

## Top-30 Trap List

1. IT and Read-Only licenses **ignore group assignments**.
2. The connection on an existing environment is **immutable**.
3. Adding a Staging environment routes development resolution **immediately**, with no fallback.
4. `dbt retry` after an infrastructure failure is a **no-op**.
5. Source-freshness and docs-generate as **checkboxes** have isolated failures; as **command steps** they block the chain.
6. GitLab **personal repositories are unsupported**; you need a GitLab group, Maintainer role, and `api` OAuth scope.
7. Webhooks **silently auto-disable after 5 consecutive failures**.
8. `job.run.errored` fires **before** artifact ingestion.
9. Snowflake account ID is the **locator format**, not the URL.
10. Deferral requires a successful prior manifest.
11. **Most permissive group wins** for users in multiple groups.
12. An upstream test failure in `dbt build` causes downstream models to receive **SKIP**, not error.
13. Unit tests run **before** materialization.
14. Interval scheduling **drifts** — use cron for fixed times.
15. CI jobs **do not update the Catalog**.
16. Ephemeral models cannot have `access: public`.
17. Contracts must declare **all columns**; incremental plus contract is restricted to `append_new_columns` or `fail`.
18. The `check` constraint is enforced only on **Postgres and Databricks**.
19. The project name in `dependencies.yml` is **case-sensitive**.
20. `--state` and `--target-path` **must point to different directories** or the manifest is overwritten.
21. A custom schema macro that mangles the `dbt_cloud_pr_<job_id>_<pr_id>` pattern produces **orphaned CI schemas**.
22. **PrivateLink with CI hooks results in silent failure**.
23. **Fork pull requests cannot run CI** — contributors must push to origin.
24. Advanced CI cache: 100 rows per model, 30-day retention, **no data masking** → exclude PII models with `--exclude tag:pii`.
25. Without `event_time`, dbt compare reports false deleted rows on every CI run.
26. Blue/green: **never swap after a partial run**; views with hardcoded database names break; snapshots break; incrementals require `--full-refresh` afterward.
27. **`--vars` changes are invisible to `state:modified`**; seeds larger than 1 MiB are tracked by path only.
28. The pod memory ceiling is **600 MiB on every plan**.
29. **100 consecutive failures auto-deactivates a scheduled job** (Beta).
30. Lenses are **single-attribute** — you cannot combine query volume with materialization on one DAG view.
31. **`access: public` has no per-project allowlist** — once public, *any* downstream project can ref it. There is no syntax to scope a public model to one specific consumer project.
32. **`source:fresher+` ≠ `source_status:fresher+`** — the first is a name lookup (matches nothing unless a source is literally named `fresher`); the second is the state-aware freshness selector and **requires `--state`** with a prior `sources.json` to diff against.
33. **Mesh upstream projects use the `package:` selector** — case-sensitive match to `dbt_project.yml` `name:`; **selectors NEVER trigger upstream builds**, only filter the current invocation. Cross-project orchestration = **"Run when another job finishes" chaining** (Starter+ feature; Enterprise+ in practice for cross-project Mesh), not `--select`.
34. **PAT dies with the user; service token persists** — production CI/CD must use service tokens. PAT permissions are *inherited* from the user (not configurable on the token); service tokens have *explicit*, per-project permission sets. Same user across 2 dbt accounts = 2 separate PATs.
