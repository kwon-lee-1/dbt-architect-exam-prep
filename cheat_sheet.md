# dbt Architect Exam — Cheat Sheet

> One page per topic. Bold = high-yield. Read top-to-bottom the morning of the exam.

---

## T1: Warehouse Connections

- Connections are **account-level** (shared across projects), not project-level
- Each environment = **exactly one connection** — a job cannot write to two warehouses
- Different envs in the same project CAN use different connections/warehouse types
- IPs are listed per region (Project Settings → Connection → Settings) but can change occasionally — docs recommend dbt **hostnames** as the stable reference. Single-tenant: ask Support
- PrivateLink = **Enterprise+ / Virtual Private**, no public internet, dbt and warehouse on the **same cloud**
- OAuth = **development only**, per developer, Enterprise. Client ID/Secret go on the connection (Account settings → Connections)

| Platform | Critical Gotcha |
|---|---|
| Snowflake | Account ID = **locator format** (`db5261993.east-us-2.azure`), NOT the `.snowflakecomputing.com` URL |
| Snowflake | Key pair = default for new creds (dev + deploy). **New username/password creds not allowed**. Snowflake OAuth = dev only, Enterprise |
| Snowflake | dbt v2 key = **PKCS#8 AES-256**, no 3DES/headerless. "Could not deserialize key data" = bad paste (missing dashes / BEGIN-END lines) |
| BigQuery | OAuth = dev + **Enterprise only**. ID/Secret: Connections → OAuth 2.0 Settings. Users: Credentials → Native OAuth. Deploy = Service JSON or WIF |
| Databricks | `dbt-spark` is **deprecated** — use `dbt-databricks`; Unity Catalog = dbt 1.1+; Python models = dbt 1.3+ |
| Managed repo | Trial only; no pull requests; dbt Labs recommends against production; export any time |

---

## T2: Git Connections

| Provider | Key Facts |
|---|---|
| GitHub (native) | Requires GitHub org owner + dbt Account Admin/Owner to install |
| Azure DevOps | **Enterprise/Enterprise+ only** — Starter/Developer = deploy keys only (no auto CI) |
| GitLab | OAuth needs **`api` scope**; repos must be in a **GitLab group** (personal repos won't work); **Maintainer role** required |
| GitLab Free | CI triggers but **status NOT posted back** to MRs — no green/red check |
| BitBucket / CodeCommit | No native integration — git clone + Admin API (Enterprise/Enterprise+) to trigger CI; temp schema is **not** auto-deleted |
| Azure DevOps Server (on-prem) | No native integration on any plan |
| GitHub on-prem or `ghe.com` | Shared dbt app can't reach it. Enterprise/Enterprise+: custom GitHub app (**private beta**). Other plans: git URL |

- Repo name must match the GitHub URL **exactly, including case** — mismatch = clone errors or job failures
- Enterprise/Enterprise+: each developer must link their GitHub profile (the IDE checks read/write access). Starter: optional but recommended

---

## T3: Environments

**Environment UI — key fields:**

| Field | Gotcha |
|---|---|
| Environment type | Greyed out if that type already exists for the project |
| Production environment toggle | One per project — controls Catalog source of truth + cross-project ref resolution |
| dbt version / release track | v1: Latest (default) / Compatible / Extended / Fallback. v2: Nightly / Stable (default) / Extended / Fallback |
| Custom branch | Deploy env = branch cloned at runtime; Dev env = branch devs fork from |
| Extended attributes | Top-level YAML keys only — to change a sub-key give the whole top-level key as JSON. Don't mask secrets → project-scoped `DBT_ENV_SECRET_` env vars |
| Snowflake: Role, Database, Warehouse | Editable in UI |
| Databricks: Catalog | Optional field for Unity Catalog |
| Postgres / Redshift / BigQuery / Spark | No editable fields — inferred from connection; use extended attributes |

**Counts per project (memorize):**

| Type | Count | Purpose |
|---|---|---|
| Development | Exactly 1 | IDE/CLI; controls branch developers fork from |
| Production | Exactly 1 | Catalog source of truth; cross-project ref resolution |
| Staging | Exactly 1 | Pre-prod; optional. Once it exists, dev/staging cross-project refs resolve to it |
| General | Unlimited | Experimental/non-critical jobs |

**Critical rules:**
- **Profiles**: deployment envs get connection + credentials from a project-level profile (not dev). Swap it in environment settings. Older material says the connection is immutable; current docs don't say that
- **Deferral** uses the latest **successful** run in the deferred environment. Needs at least one successful run. IDE defer fails if Staging exists but never ran
- **Staging env gotcha**: once created and linked, dbt **always** uses staging for dev resolution — even with zero successful staging runs. No fallback to prod. Safe order: create it unmarked → run a job → mark it Staging.
- Extended attributes: top-level keys only — give the whole top-level key as JSON to change a sub-key
- Env var precedence: **job (or personal IDE) > environment > project default**. No account level. Names start with `DBT_`; `DBT_ENV_SECRET_` is scrubbed from logs

**Release tracks:**
- v1: **Latest** (continuous, default) → **Compatible** (monthly, Starter+) → **Extended** (previous month's Compatible, Enterprise / Enterprise+) → **Fallback** (Enterprise+)
- v2: **Nightly**, **Stable** (default, weekly), **Extended**, **Fallback**

---

## T3b: Schema Generation & Custom Schema Precedence ⭐

**The answer**: Dev schema = `dbt_user_1`, model has `config: { schema: 'core' }` → model lands in **`dbt_user_1_core`**

Default rule: `<target.schema>_<custom_schema>` — custom schema APPENDS, does NOT replace.

**Default `generate_schema_name` logic:**
```
no custom schema → target.schema only
custom schema    → target.schema + "_" + custom_schema
```

**Result table:**

| scenario | result |
|---|---|
| dev `dbt_user_1`, no schema config | `dbt_user_1` |
| dev `dbt_user_1`, `schema: core` | **`dbt_user_1_core`** |
| prod `analytics`, `schema: core` (default) | `analytics_core` |
| prod `analytics`, `schema: core` (with override macro) | `core` |

**Why it appends**: prevents developer collisions — if all devs with `schema: core` wrote to the same `core` schema they'd overwrite each other.

**Override pattern from the docs** (prod = custom schema; dev/CI ignore it and use the target schema). Built in as `generate_schema_name_for_env`, off by default:
```jinja
{%- if target.name == 'prod' and custom_schema_name is not none -%}
    {{ custom_schema_name | trim }}
{%- else -%}
    {{ default_schema }}
{%- endif -%}
```
Place in `macros/generate_schema_name.sql`. Macros in installed packages are ignored.

**`target.name`**: set via the job's Target Name field (IDE: Account settings → Credentials). Set `prod` on the production job. It's a string your macro reads, not the environment type.

**Gotchas:**
- **Custom macro + CI**: the result must keep the `dbt_cloud_pr_` prefix (✅ `dbt_cloud_pr_123_456_marketing`, ❌ `marketing`) or temp schemas aren't dropped
- **Always preserve `target.schema` prefix in dev** — dropping it causes multi-developer collisions
- Override in `macros/` only — never edit dbt core files

---

## T4: Jobs & CI/CD

**Deploy job UI — key fields:**

| Section | Field | Gotcha |
|---|---|---|
| Job Settings | Environment | Defaults to the environment you created the job from |
| Execution | Commands | Sequential; one failure stops all subsequent steps |
| Execution | Generate docs (checkbox) | v1 only — not for dbt v2 jobs (Catalog refreshes automatically). Timing vs commands isn't in the docs |
| Execution | Run source freshness (checkbox) | Runs **first**; a failure doesn't break later steps |
| Triggers | Schedule type | Intervals (every N h from midnight UTC) / Specific hours (whole hours) / Cron (exact times) — all UTC |
| Triggers | Run when another job finishes | Starter and Enterprise-tier; project + job + Completes on (Success only, or all statuses). Cross-project needs Enterprise-tier |
| Advanced | Compare changes against | Default **No deferral**. Options: Environment (recommended) / This Job (older self-deferral) |
| Advanced | Threads | Default 4 |
| Advanced | dbt version override | Not recommended |
| Advanced | Target name | For custom macro schema logic |

**CI job UI — key fields (differences from deploy job):**

| Section | Field | Default | Gotcha |
|---|---|---|---|
| Git Trigger | Triggered by pull requests | **ON** | Main trigger |
| Git Trigger | Run on draft PRs | OFF | Opt-in |
| Execution | Commands | `dbt build --select state:modified+` | Editable |
| Execution | Linting (SQLFluff) | OFF | Starter+; sub-option: stop or continue on error |
| Execution | dbt compare | OFF | **Enterprise / Enterprise+**; needs a PK constraint or uniqueness test |
| Execution | Run timeout | 3600s (1hr) | Only active when dbt compare enabled |

**Job types:**
- Deploy jobs: consume run slots, materialize prod data
- Merge jobs: also consume run slots (one run at a time, newest wins)
- CI jobs: **no run slots**, temp schema `dbt_cloud_pr_<job_id>_<pr_id>`, schema deleted on PR close/merge

**Concurrency:**
- Same PR → CI runs **serially** (stale in-flight runs are cancelled)
- Different PRs → CI runs **concurrently**
- Concurrent CI + smart cancellation need Starter+ (not for API-triggered CI on Starter)

**Command ordering:**
- `dbt build` goes **before** `dbt sl validate` (the order in the docs' CI setup)
- `dbt source freshness` as **checkbox** → runs first, failure is **isolated** (job can still succeed)
- `dbt source freshness` as **command step** → failure **blocks** all subsequent steps
- dbt v2 jobs: no docs command needed — every run refreshes Catalog. Production/staging job runs update Catalog
- `dbt build` failure on upstream test → downstream models enter **SKIP** (not error)
- Unit tests run **before** model materialization

**`dbt retry`:**
- Re-runs from failure point using `run_results.json`
- **No-op** if job failed before any nodes executed (infra failure, connection error) — must rerun fully

**Scheduling:**
- All times in **UTC only**
- Intervals run every N hours from midnight UTC — use **cron** for exact times (`5 4 * * *`)
- Job duration > interval → scheduler cancels queued runs, keeps newest
- Auto-deactivation after **100 consecutive failures** (deploy and CI jobs)

**Run slots:**
- Slot counts: pricing page. Multi-tenant Enterprise: unlimited concurrency. Starter/Developer: one project each
- Memory limit: **600 MiB** per run, all plans
- CI jobs bypass the slot system; merge jobs use slots

**CI edge cases:**

| Scenario | Behavior |
|---|---|
| Monorepo | Single PR triggers CI for ALL connected dbt projects |
| Fork PR | dbt cannot check out fork commits — fails; push to origin |
| Ingress PrivateLink / IP allowlisting + CI | CI hooks **may be unavailable** — can fail silently |
| Azure DevOps reused branch | CI won't trigger if the PR's latest commit already triggered a run (e.g. branch reused after an abandoned PR) |
| GitLab Free | CI triggers but no status posted back to MR |

**Deferral types:**

| Type | Use when | Breaks when |
|---|---|---|
| Environment deferral | Standard CI (CI default = Production) | No successful run in that environment yet |
| Self-deferral (This Job) | Older option: that job's own last successful run | Docs don't say what a first run does |
| No deferral | State unreliable | — (always full rebuild, expensive) |

**Advanced CI (Enterprise) — Compare Changes:**
- **Requirements**: Enterprise / Enterprise+; same database host for CI + prod; model needs PK constraint or uniqueness test
- **How it works**: CI builds modified models in temp schema → compares row-by-row against prod → posts summary comment to PR + Compare tab in dbt Cloud
- **`event_time`**: without it, full tables compared → CI's smaller date window looks like deleted rows → false positives every run. With it: only overlapping time range compared.
- **CI result cache**: up to **100 rows/model**, stored encrypted (S3 or Azure Blob), expires after **30 days** — inaccessible after that
- **Not dynamically masked** — all account users can see results and cached rows; restrict the CI environment's credentials or use synthetic data
- **Smart cancellation**: same PR new commit → stale in-flight runs auto-cancelled; different PRs run concurrently (Starter+)
- **SQL linting** (SQLFluff): Starter+; stop or continue on linting error

**Job chaining:** Starter and Enterprise-tier (not Developer). Cross-project chaining needs more than one project → Enterprise-tier.

**Setup steps (per dbt docs):**
1. **Deploy → Jobs** → select/create the **downstream** job → **Triggers** section
2. Enable **Run when another job finishes**
3. **Specify the parent project** (same or different project)
4. **Specify the upstream deploy job**
5. **Completes on** → choose run status(es) that enqueue the downstream job (Success only, or all statuses)
6. Save

**Gotchas:**
- Run details page shows a link back to the upstream job that triggered the run
- Need permissions on **both** projects to configure the trigger
- One upstream job can trigger several downstream jobs, including in other projects

---

## T4b: Advanced Commands & Node Selection

**Graph operators:**

| Syntax | Meaning |
|---|---|
| `+model` | All upstream ancestors |
| `model+` | All downstream descendants |
| `+model+` | Ancestors + model + descendants |
| `2+model` / `model+1` | Bounded depth (N levels) |
| `@model` | Full closure — model + descendants + all ancestors of those descendants |
| `path/.*` | Wildcard for all models in a path |

**Set operations:**
- Space = union (OR): `tag:daily tag:nightly`
- Comma (no space) = intersection (AND): `marts,tag:daily`
- `--exclude` = difference: `--select "marts.*" --exclude big_model+`

**State selectors (require `--state path/to/manifest`):**

| Selector | Selects |
|---|---|
| `state:new` | No matching `unique_id` in prior manifest — brand new |
| `state:modified` | New + any changed nodes |
| `state:old` | Same `unique_id` exists in the prior manifest |
| `state:modified.body` | SQL/seed content changed |
| `state:modified.configs` | Config changed (not relation names) |
| `state:modified.relation` | database/schema/alias changed |
| `state:modified.macros` | Upstream macro changed (transitive) |
| `state:modified.contract` | Contract column/type changed |

**`--defer` + `--state` together (standard CI pattern):**
```bash
dbt build --select state:modified+ --defer --state /path/to/prod/manifest
```
- Runs modified models + their downstream nodes
- Unselected upstream parents resolved against **production tables** (not rebuilt)
- Default: your dev target wins if the relation exists. The state manifest only fills gaps. `--favor-state` prefers state, `--defer-state` = separate manifest for deferral
- Ephemeral models are never deferred

**State gotchas:**
- `var()` / `env_var()` value changes aren't traced by **`state:modified`** — a model is likely flagged only if its config changes
- `--state` and `--target-path` pointing to the same dir → dbt overwrites the manifest before comparison → wrong state. Use separate dirs.
- Seeds >1 MiB: only tracked on path changes, not content
- `tags` / `meta` changes don't trigger `state:modified`. It sees code/config, not data
- Relationship tests with `--defer`: can query across two environments → false failures

**`dbt ls`** — lists resources, no connection to the database (dbt v2.0+):
```bash
dbt ls --select state:modified                        # preview CI scope
dbt ls --select config.materialized:incremental       # all incrementals
dbt ls --select tag:nightly --resource-type test      # tests by tag
dbt ls --select "+my_model" --output path             # file paths of ancestors
```
`--output`: `name` \| `path` \| `json` \| `selector`

**`--vars`:**
```bash
dbt run --vars '{"event_type": "signup", "region": "us"}'
```
- Overrides `dbt_project.yml` vars at runtime
- `--vars` beats `dbt_project.yml`; `var()` default is last. No Jinja inside `vars`
- Missing var (no default) → compile error
- `var()` / `env_var()` value changes aren't traced by `state:modified`

**Other useful selectors:**
```bash
--select result:error          # any resource that errored
--select result:fail           # tests only (use 1+result:fail+ to re-run their models)
--select source:snowplow+      # source + all downstream (NAME-based)
--select source_status:fresher+  # sources with NEW data since last freshness + downstream (STATE-based; requires --state)
--select exposure:my_dashboard+  # exposure + upstream deps
--select test_name:unique      # specific named test
--select package:dbt_utils     # models from a package
```

**`source:` vs `source_status:` (common trap):**

| Selector | Method | What `<value>` means | Needs `--state`? |
|---|---|---|---|
| `source:<name>+` | Name lookup | Source's declared name | No |
| `source_status:fresher+` | Freshness state diff | Only valid value: `fresher` (newer `max_loaded_at` vs prior `sources.json`) | **Yes** |

- `source_status:` documents only `fresher`.
- Workflow: prior `dbt source freshness` writes `sources.json` → `dbt source freshness` again now → `dbt build --select source_status:fresher+ --state path/to/previous/`.
- Without `--state`, selector resolves to **zero nodes** — silent no-op.
- `source:fresher+` (no underscore) is a **name lookup** — dbt searches for a source literally named `fresher` and almost always finds nothing.
- Use case: source-driven jobs that only build downstream when raw data actually arrives.

**`--indirect-selection`** (controls which tests run when models are selected):
- `eager` (default): tests run if ANY parent selected — may error if other parents unbuilt
- `cautious`: tests run only if ALL parents selected
- `buildable`: tests run if dependencies are selected or their ancestors
- `empty`: no tests at all

**Other commands:**
- `dbt build`: DAG order. Unit tests → model → data tests. Upstream test/model failure **skips** downstream
- `dbt retry`: resumes from the failure using `run_results.json`. Nothing ran (e.g. connection error) → nothing to retry. Previous run succeeded → no operation
- `dbt compile` needs a warehouse connection. `--inline` compiles a snippet. `dbt parse` doesn't connect
- Partial parsing: `--no-partial-parse` or `PARTIAL_PARSE: false`. `--vars`, profiles, project file, package or dbt version changes force a full re-parse
- Source freshness: needs a `freshness` config (`warn_after` / `error_after`). `loaded_at_field` is **optional** (warehouse metadata used otherwise)

---

## T4c: Blue/Green Deployments and `dbt clone`

**Official docs:** blue/green is only listed as a **use case of `dbt clone`** (on warehouses with zero-copy cloning). The swap steps are a **community pattern**, not official.

**`dbt clone`:**
- Clones selected nodes from the specified state into the target schema(s)
- Zero-copy on **Snowflake, Databricks, BigQuery** (if the model is a table). Otherwise a **pointer view**
- Skips pre-existing relations. `--full-refresh` recreates them
- Relies on `--defer`: platform CLI adds it automatically, Studio IDE needs the "Defer to production" toggle
- Needs dbt 1.6+. Clone needs compute and extra objects, deferral is often cheaper
- Uses: blue/green, prod → dev schemas, incrementals in CI, testing downstream in your BI tool

**Community blue/green (Snowflake):**
1. `dbt run` (build in the stage database)
2. `dbt test`
3. `dbt run-operation swap_database` (custom macro, `alter database prod swap with stage`)
- Failed step stops the job, so no swap
- Swaps the whole database → only after a full build
- Views with fully qualified names go stale → override `ref` / `source` to drop the database name

---

## T5: Security & Licenses

**License always overrides group permissions:**

| License | Inherits permission sets? | Fixed access |
|---|---|---|
| Developer | ✅ Yes | Full feature access |
| Analyst | ✅ Yes | Enterprise / Enterprise+; legacy |
| IT | ❌ **No** | Security Admin + Billing Admin + edit Connections only |
| Read-Only | ❌ **No** | View artifacts + deploy section only |

**IT/Read-Only trap**: assigning these users to any group has zero effect on their access.

**Permission sets — quick lookup:**

| Need to... | Role |
|---|---|
| Create projects | Account Admin or **Project Creator** only |
| Access IDE | Account Admin, Project Creator, Admin, Developer, Analyst |
| Create/edit jobs | Account Admin, Admin, **Job Admin** |
| Trigger jobs | + Job Runner |
| Manage SSO/users | **Security Admin** (has zero data access) |
| Edit connections | Account Admin, Project Creator (IT license too) |
| Query Semantic Layer (API) | **Semantic Layer** service token only |
| Full audit log (sensitive) | Account Admin, **Account Viewer** |

**Common traps:**
- **Admin ≠ Account Admin**: project Admin cannot create new projects
- **Security Admin**: no IDE, no jobs, no data access — admin only
- **Database Admin**: no IDE — configs only
- **Stakeholder vs Account Viewer**: Stakeholder / Read-Only = audit log without sensitive info; Account Viewer = full audit log
- **Most permissive group wins** when user is in multiple groups

**Default groups:**

| Group | Auto-add new users? | Mutable? |
|---|---|---|
| Owner | No | ❌ Immutable |
| Member | **Yes** | Yes |
| Everyone | **Yes** | Yes |

New users are added to **both Member AND Everyone**.

**Service tokens:**
- Value shown **once only** — unrecoverable after close
- Rotation: create new → update integrations → delete old
- IP restrictions apply to service tokens; 403 = IP not allowlisted
- Created via Account Settings → Service Tokens: needs a **Developer license + account admin permissions** (Read-Only and IT licenses can't use them)
- One token can carry **multiple permission sets**, each scoped to all projects or specific projects
- Pre-July 18, 2023 tokens: rotate to new format for performance

**PAT vs Service Token:**

| | PAT | Service Token |
|---|---|---|
| Identity | Tied to a user | Account-level, no user |
| Permissions | **Inherited** from user (license + groups); not configurable | **Explicitly assigned** permission sets |
| Multi-permission-set | No | **Yes** |
| Project scoping | User's projects | Per permission set: all / specific |
| Multi-account user (same email) | **Separate PAT per account** | N/A |
| Created by | Developer, Read-Only or IT license user | Developer license + account admin permissions |
| Recommended for | dbt CLI, dev scripts, user-context endpoints | Production CI/CD, Terraform, partner integrations |

**Service token permission sets by tier:**
- **Enterprise/Enterprise+**: any permission set
- **Legacy Team**: Account Admin, Member, Job Admin, Read-Only, Metadata, Semantic Layer
- **Developer/Starter**: **Semantic Layer only**

**PAT vs Service Token — exam traps:**
- Production automation → **service token** with minimal permission sets (a PAT inherits one person's permissions)
- "Where do PAT permissions come from?" → user's license + groups; **not configurable on the token**
- "Which can be scoped per-project?" → service token only
- A PAT can't create a service token (400)
- Same user, two dbt accounts → **two separate PATs** required
- **Semantic Layer Only** permission = service-token-exclusive (cannot assign to user)
- **v2 Migration Admin** permission = user-only (cannot assign to service token)

**SSO (Enterprise / Enterprise+):**
- JIT provisioning on first login; re-auth every **24 hours**
- **SCIM**: Okta and Entra ID. Provisions/de-provisions users and groups from the IdP; SSO group mappings are off while SCIM is on
- **License mappings**: Groups & Licenses → IdP group names for Read-Only / Developer; applied at sign-in; in both → Developer; in neither → default license (IT can't be default)
- Admins keep password access even with SSO enforced

**SSO setup steps — Okta SAML (per dbt docs):**

*Okta side:*
1. Okta Admin → **create app** → Web platform, **SAML 2.0** sign-on
2. App name: `dbt`
3. **SAML Settings** (uses your dbt **login URL slug**, e.g. `dbt-labs-afk123`):
   - SSO URL: `https://YOUR_AUTH0_URI/login/callback?connection=<slug>`
   - Audience URI: `urn:auth0:<YOUR_AUTH0_ENTITYID>:<slug>`
   - Relay State: `<slug>`
   - Name ID format: Unspecified
   - **Application username**: `user.getInternalProperty("id")` for SSO-only; **Email** if SCIM is in scope
4. **Attribute Statements**: `email` → `user.email`, `first_name` → `user.firstName`, `last_name` → `user.lastName`
5. **Group Attribute Statements**: name `groups`, filter `Matches regex` → `.*` (Okta caps at **100 groups/user** — restrict if needed)
6. Finish → "internal app" → **View Setup Instructions** → copy SSO URL, Issuer, X.509 Certificate

*dbt Cloud side:*
1. **Account settings → SSO & SCIM → Get started / Edit**
2. Fill: Log in with `Okta` | IdP SSO URL | IdP Issuer | X.509 Certificate
3. Save

*End-user login URL:* `https://YOUR_ACCESS_URL/enterprise-login/<slug>`

**SSO gotchas:**
- **X.509 cert expiry is manual** — Okta admin must regenerate before expiry; expired cert breaks SSO entirely
- **SCIM-vs-SSO username conflict** — SCIM requires Email format; pick upfront (changing later is disruptive)
- SSO group mapping and license mapping use the **IdP group names** you enter in dbt — they must match your IdP
- Admins keep password fallback by default — recovery path if IdP breaks
- Other IdPs (Entra ID, Google Workspace, generic SAML 2.0) follow the same flow with different IdP-side UIs

**RBAC rules:**
- Permissions at **group level only** — no individual assignments
- New users join **Member and Everyone** — customize both to limit default access
- With SCIM on, users aren't auto-added to default groups

---

## T6: Monitoring & Alerting

**Job notifications** (profile → Notification settings):
- Channels: email, Slack (**public channels only**), Teams
- Events: **succeeds / warns / fails / is canceled**. Warns = warning-level lines from data tests or source freshness
- Email: developer user, account admin or Notification Manager. IT license can receive but **not configure**

**Webhooks:**
- Plans: **Starter or Enterprise-tier**; destination must accept an `Authorization` header
- Events: `job.run.started` | `job.run.completed` | `job.run.errored`
- `errored` fires **immediately** — artifacts may not be ingested yet. `completed` fires **after** ingestion (success or failure) — use it for API queries
- Subscribe to both → **two notifications** on an error
- Verify: `Authorization` = SHA256 HMAC of the body, keyed with the secret
- **10-second timeout**; each event retried **5 times**; delivery log **7 days**
- **Archived** after **1,000 consecutive failures or 7 days** of failures. Reactivate: change the endpoint URL (UI) or `PUT active: true` (API)
- Create: Enterprise-tier = Account Admin, Admin or Developer permission set; Starter = Developer license

---

## T7: dbt Mesh

**Plans:** cross-project `ref()` and project dependencies = **Enterprise and Enterprise+**.

**Cross-project env resolution (MEMORIZE):**

| Downstream env | Resolves to upstream |
|---|---|
| Development | Staging if it exists, else Production |
| Staging | Staging if it exists, else Production |
| Production | Production |

- Upstream Staging is used **immediately** once it exists — no fail-over to Production. Create it unmarked → run a job → mark it Staging. Staging is optional.

**Setup:**
- Upstream: `access: public` + a successful run after; a Production env with a successful deploy job (makes `manifest.json`); a successful job in Staging if it exists
- Downstream: `dependencies.yml` → `projects: - name:` (**case-sensitive**) → `ref('project','model')`
- Two-way = **stepwise** (A runs → B adds A and runs → A adds B). Node-level cycles = error
- You can **select** upstream models downstream but **can't build** them — build them with the upstream's jobs
- Run downstream after upstream: **"Run when another job finishes"** (Enterprise-tier for 2 projects)
- Sources aren't shared across projects → foundational project with public staging models

**Model access:**
- `private` — same group · `protected` — same project or installed package (**default**) · `public` — any group, package or project
- Ephemeral models **cannot** be `public` (parse error)
- `access` does **not** grant warehouse SELECT — use `grants`
- Private violation = `DbtReferenceError` at parse time
- Package `restrict-access: True` → only `public` models visible outside the package
- Governance features apply to **models only**

**Groups:** `groups:` with `name` + `owner` (name **or** email) · `group` config · one group per node · members: models, tests, seeds, snapshots, analyses, metrics (not sources/exposures)

**Contracts:**
- `enforced: true` → every column needs `name` + `data_type`; order isn't checked; mismatch = model doesn't build
- Breaking: remove column, change `data_type`, remove/modify constraint, remove contracted model (v1.9+: error if versioned, warning if not)
- Table ✅ · view (names/types only) · incremental only `append_new_columns` or `fail` · ❌ Python, materialized view, ephemeral, custom, BigQuery recursive CTE

| Constraint | Postgres | Snowflake / Redshift | BigQuery | Databricks |
|---|---|---|---|---|
| not_null | ✅ | ✅ | ✅ | ✅ |
| primary_key / foreign_key | ✅ | ⚠️ defined | ⚠️ defined | ⚠️ defined |
| unique | ✅ | ⚠️ defined | ❌ | ❌ |
| check | ✅ | ❌ (skipped) | ❌ | ✅ |

**Model versions:**
- `latest_version` defaults to the **highest** number; set lower → higher versions are prereleases
- Unpinned `ref('model')` → latest · pinned `ref('model', v=1)` · cross-project `ref('project','model', v=1)`
- Default file `model_v2.sql`; `defined_in` overrides. `deprecation_date` → dbt notifies consumers

**Catalog + Mesh (Enterprise/Enterprise+):** project icon on other-project nodes · only **directly referenced public models** shown (indirect only in Studio IDE lineage) · Account lineage → List view

---

## T8: dbt Catalog

- Plans: **Starter, Enterprise, Enterprise+**. Column-level lineage, multi-project lineage, query history, model performance, Cost Insights = **Enterprise / Enterprise+** (not Starter). Health signals = all plans.
- Updated after each job run in a **production or staging** environment. Dev builds don't show up.
- **CI jobs do NOT update Catalog**
- dbt v2 jobs refresh Catalog automatically (no `dbt docs generate`). Tests need `dbt test`/`build`, freshness needs `dbt source freshness`
- Inactivity purge: **no job runs in 3 months** → environment metadata purged
- Artifacts setting (Account settings → project → Edit → Artifacts) = legacy dbt Docs / freshness. One production job per project. Catalog doesn't use it
- Column-level lineage: **SQL models only** (also sources, snapshots). Python models can't be parsed. Columns tab
- Health signals: Healthy / Caution / Degraded / Unknown. Degraded = failed build, failing tests, stale source. Caution = warnings, no tests, no description, not built in 30 days

**Artifact files:** `manifest.json` = project nodes and lineage · `catalog.json` = warehouse metadata (columns, types, stats) · `sources.json` = source freshness results (legacy)

**Lenses** (one at a time, no combined view, **no Cost lens**): Resource type · Materialization type · Latest status · Model layer · Test status (worst case) · Consumption query history

**Model Query History (Enterprise / Enterprise+):**
- Tracks consumption `select` queries — **excludes** dbt builds and test runs
- On by default for new PROD environments. Existing: Orchestration → Environments → PROD → Settings → Edit → Query History → Test Permissions → Enable → Save
- Needs warehouse query-history permissions (Snowflake, BigQuery, Redshift, Databricks)
- View in: Performance → Most consumed models · Lenses → Consumption queries · Resources → Models sorted by Consumption
- Use for: optimization prioritization, deprecation impact

**Cost Insights (Enterprise / Enterprise+):** needs metadata credentials + a production job. State-aware orchestration / dbt State only for cost-reduction data. Calculated once daily. Estimates, not billing.

**External metadata ingestion (Enterprise / Enterprise+, Preview):** non-dbt warehouse tables/views. Snowflake only.

---

## Plan Tier Quick Reference

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|---|---|---|---|
| Job chaining | ❌ | ✅ | ✅ | ✅ |
| Cross-project refs | ❌ | ❌ | ✅ | ✅ |
| Project dependencies (Mesh) | ❌ | ❌ | ✅ | ✅ |
| Advanced CI (compare) | ❌ | ❌ | ✅ | ✅ |
| SSO / SCIM | ❌ | ❌ | ✅ | ✅ |
| Column-level lineage | ❌ | ❌ | ✅ | ✅ |
| Multi-project lineage | ❌ | ❌ | ✅ | ✅ |
| PrivateLink | ❌ | ❌ | ❌ | ✅ |
| Azure DevOps native | ❌ | ❌ | ✅ | ✅ |
| BigQuery OAuth | ❌ | ❌ | ✅ | ✅ |
| Run slots | 1 | 1 | Higher | Higher |
| Scheduling min interval | 10 min | — | — | — |

---

## T9: Hooks & Operations

**Hook types:**

| Hook | Runs | Configured In |
|---|---|---|
| `pre-hook` / `post-hook` | Before / after each model, seed, snapshot | `dbt_project.yml`, `config()` block, YAML |
| `on-run-start` / `on-run-end` | Start / end of a command (build, compile, docs generate, run, seed, snapshot, test) | `dbt_project.yml` |

**Transactions:**
- On Postgres / Redshift, hooks run **inside** the model's transaction by default
- Outside it: `{sql: "...", transaction: false}` or `before_begin()` / `after_commit()`
- **Don't use on Snowflake, BigQuery, Spark, Databricks** (no transactions)

**Order:** all hooks accumulate (model doesn't override project). Package hooks → `dbt_project.yml` → model; within one place, definition order

**Context variables:** `{{ this }}` in pre/post-hooks. `schemas`, `database_schemas`, `results` = **`on-run-end` ONLY** (none elsewhere, no error)

**Grants:** use the **`grants` config** first (grantees match exactly, unlisted are revoked). Post-hook only for what it can't do (masking/row access policies, future grants, non-table objects, Databricks `READ_METADATA`/`USAGE`)

**Operations (`dbt run-operation`):**
- Macro run on demand. Must run its SQL with `run_query()` or a `statement` block, otherwise dbt just returns a string
- `dbt run-operation <macro> --args '{key: value}'` (YAML string)
- dbt v1.12+: `--sql "..."` runs SQL directly
- Doesn't enforce model `access` / `group`
- Can be a job command step

**Key gotchas:**
- Redshift `VACUUM` can't run in a transaction → `transaction: false`
- `{{ results }}` in a post-hook = none, silently
- Seeds have no `config()` block → hooks in `dbt_project.yml` or YAML
- Call a macro from a hook: `"{{ my_macro(this) }}"`

---

## Must-Know Gotchas (All Topics)

1. **IT/Read-Only licenses ignore groups** — assigning to Admin group does nothing
2. **Env var precedence** — job (or personal IDE) > environment > project default. No account level
3. **Staging env + Mesh** — once created, always used; adding staging with no successful runs breaks dev resolution
4. **`dbt retry` on infra failure** = no-op (no nodes in `run_results.json`)
5. **Checkbox failures are isolated** — source freshness / docs generate checkbox won't fail the overall job
6. **GitLab: personal repos won't work** — must be a GitLab Group repo
7. **Webhook archived after 1,000 consecutive failures or 7 days** — change the endpoint URL to reactivate
8. **`job.run.errored` fires before artifacts** — use `job.run.completed` if you need artifact data
9. **Snowflake account ID = locator format** — not the `.snowflakecomputing.com` domain
10. **Deferral needs a successful run** — state comes from the latest successful run in the deferred environment
11. **Most permissive group wins** — a low-access group can be overridden by any other group
12. **`dbt build` upstream test fail → downstream = SKIP** (not error)
13. **Unit tests run before materialization** — fail early, cheaper
14. **Interval schedules run every N hours from midnight UTC** — use cron for exact clock times
15. **CI jobs don't update Catalog** — only job runs in a production or staging environment do
16. **Ephemeral models cannot be `access: public`** — parsing error
17. **Contracts: must declare ALL columns** — partial contracts not supported
18. **`check` constraints: Postgres + Databricks only** — Snowflake/BigQuery don't support them
19. **Project names in `dependencies.yml` are case-sensitive**
20. **Governance groups ≠ RBAC user groups** — completely separate systems
21. **`access: public` is all-or-nothing** — no per-project allowlist; cannot scope a public model to a specific downstream project
22. **`source:fresher+` ≠ `source_status:fresher+`** — `source:` is name-based (looks for a source literally named "fresher"); `source_status:fresher+` is the freshness-state selector and **requires `--state`** to compare prior `sources.json`
23. **Project dependencies need Enterprise or Enterprise+** — upstream needs a public model, a successful Production deploy job (and Staging job if it exists).
24. **You can select upstream Mesh models downstream but can't build them** — use "Run when another job finishes" to run downstream after upstream (Enterprise-tier for 2 projects).
25. **Production automation → service token.** A PAT inherits the creator's permissions and can't create a service token.