# dbt Architect Exam — Cheat Sheet

> One page per topic. Bold = high-yield. Read top-to-bottom the morning of the exam.

---

## T1: Warehouse Connections

- Connections are **account-level** (shared across projects), not project-level
- Each environment = **exactly one connection** — a job cannot write to two warehouses
- Different envs in the same project CAN use different connections/warehouse types
- Lineage graph is **logical** (based on `ref()`/`source()`), not physical — doesn't show warehouse topology
- Use **hostnames** not raw IPs in firewall rules — dbt IPs are dynamic
- PrivateLink = VPC-to-VPC, no public internet; Enterprise only, region-specific

| Platform | Critical Gotcha |
|---|---|
| Snowflake | Account ID = **locator format** (`db5261993.east-us-2.azure`), NOT the `.snowflakecomputing.com` URL |
| Snowflake | Fusion key pair = **PKCS#8 AES-256** only — 3DES rejected with "Could not deserialize key data" |
| Snowflake | MFA = dev environments only |
| BigQuery | OAuth = dev + **Enterprise tier only**; users link accounts via Profile Settings |
| Databricks | `dbt-spark` is **deprecated** — use `dbt-databricks`; Unity Catalog = dbt 1.1+; Python models = dbt 1.3+ |
| Managed repo | POC/trial only — **not production**; no PRs, no branching |

---

## T2: Git Connections

| Provider | Key Facts |
|---|---|
| GitHub (native) | Requires GitHub org owner + dbt Account Admin/Owner to install |
| Azure DevOps | **Enterprise/Enterprise+ only** — Starter/Developer = deploy keys only (no auto CI) |
| GitLab | OAuth needs **`api` scope**; repos must be in a **GitLab group** (personal repos won't work); **Maintainer role** required |
| GitLab Free | CI triggers but **status NOT posted back** to MRs — no green/red check |
| BitBucket / CodeCommit | No native integration — git clone + API to trigger CI |
| Azure DevOps Server (on-prem) | No native integration on any plan |

- Repo name is **case-sensitive** in dbt UI — mismatch = silent clone failure
- Each developer must link their personal profile separately even after org-level setup

---

## T3: Environments

**Environment UI — key fields:**

| Field | Gotcha |
|---|---|
| Environment type | Greyed out if that type already exists for the project |
| Production environment toggle | One per project — controls Catalog source of truth + cross-project ref resolution |
| dbt version / release track | Latest / Compatible / Extended |
| Custom branch | Deploy env = branch cloned at runtime; Dev env = branch devs fork from |
| Extended attributes | Top-level YAML keys only — partial nested overrides silently ignored |
| Snowflake: Role, Database, Warehouse | Editable in UI |
| Databricks: Catalog | Optional field for Unity Catalog |
| Postgres / Redshift / BigQuery / Spark | No editable fields — inferred from connection; use extended attributes |

**Counts per project (memorize):**

| Type | Count | Purpose |
|---|---|---|
| Development | Exactly 1 | IDE/CLI; controls branch developers fork from |
| Production | Exactly 1 | Catalog source of truth; cross-project ref resolution |
| Staging | Exactly 1 | Pre-prod; architecturally mandatory in dbt Mesh |
| General | Unlimited | Experimental/non-critical jobs |

**Critical rules:**
- **Connection immutability**: once assigned to an env, connection **cannot be changed** — create a new env instead
- **Deferral breaks** if the referenced environment's last run failed — no valid manifest
- **Staging env gotcha**: once created and linked, dbt **always** uses staging for dev resolution — even with zero successful staging runs. No fallback to prod.
- Extended attributes: top-level keys only — partial nested overrides are **silently ignored**
- Environment variable precedence: **job > env > project > account**

**Release tracks:**
- **Latest** — always newest, auto-upgraded
- **Compatible** — lags slightly, most teams use this
- **Extended** — slowest to upgrade, strictest change management

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

**Override pattern** (prod = clean schema name):
```jinja
{%- if target.name == 'prod' -%}
    {{ custom_schema_name | trim }}
{%- else -%}
    {{ default_schema }}_{{ custom_schema_name | trim }}
{%- endif -%}
```
Place in `macros/generate_schema_name.sql`.

**`target.name`**: set via Advanced Settings → "Target name" on a job; IDE defaults to `dev`. This is the signal your macro reads to distinguish environments.

**Gotchas:**
- **Custom macro + CI**: if your macro returns a non-standard name, dbt can't identify the `dbt_cloud_pr_<job_id>_<pr_id>` temp schema to auto-delete it on PR merge → orphaned schemas
- **Always preserve `target.schema` prefix in dev** — dropping it causes multi-developer collisions
- Override in `macros/` only — never edit dbt core files

---

## T4: Jobs & CI/CD

**Deploy job UI — key fields:**

| Section | Field | Gotcha |
|---|---|---|
| Job Settings | Environment | **Cannot be changed after creation** |
| Execution | Commands | Sequential; one failure stops all subsequent steps |
| Execution | Generate docs (checkbox) | Runs **after** all commands; failure **isolated** |
| Execution | Run source freshness (checkbox) | Runs **before** all commands; failure **isolated** |
| Triggers | Schedule type | Intervals / Specific hours / Cron (all UTC) |
| Triggers | Run when another job finishes | Starter+ only; select project + job + completion status |
| Advanced | Compare changes against | No deferral / Environment (prod) / This Job (self) |
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
| Execution | dbt compare | OFF | **Enterprise+ only**; needs PK constraints or uniqueness tests |
| Execution | Run timeout | 3600s (1hr) | Only active when dbt compare enabled |

**Job types:**
- Deploy jobs: consume run slots, materialize prod data
- CI jobs: **no run slots**, temp schema `dbt_cloud_pr_<job_id>_<pr_id>`, schema deleted on PR close/merge

**Concurrency:**
- Same PR → CI runs **serially** (smart cancels stale builds)
- Different PRs → CI runs **concurrently**

**Command ordering:**
- `dbt build` **must precede** `dbt sl validate`
- `dbt source freshness` as **checkbox** → runs first, failure is **isolated** (job can still succeed)
- `dbt source freshness` as **command step** → failure **blocks** all subsequent steps
- `dbt docs generate` as **checkbox** → runs last, failure is **isolated**
- `dbt build` failure on upstream test → downstream models enter **SKIP** (not error)
- Unit tests run **before** model materialization

**`dbt retry`:**
- Re-runs from failure point using `run_results.json`
- **No-op** if job failed before any nodes executed (infra failure, connection error) — must rerun fully

**Scheduling:**
- All times in **UTC only**
- Interval mode drifts — use **cron** for clock-aligned schedules
- Job duration > interval → scheduler cancels queued runs, keeps newest
- Auto-deactivation after **100 consecutive failures** [Beta]

**Run slots:**
- Developer/Starter: **1 slot** (serial only)
- Enterprise+: higher (contract-dependent)
- Memory limit: **600 MiB** per pod, all plans
- CI jobs bypass the slot system

**CI edge cases:**

| Scenario | Behavior |
|---|---|
| Monorepo | Single PR triggers CI for ALL connected dbt projects |
| Fork PR | dbt cannot check out fork commits — fails; push to origin |
| PrivateLink + CI | CI hooks **not available** — fails silently |
| Azure DevOps reused branch | CI won't trigger on new PR with same old branch name |
| GitLab Free | CI triggers but no status posted back to MR |

**Deferral types:**

| Type | Use when | Breaks when |
|---|---|---|
| Prod deferral | Standard CI | Prod hasn't run successfully recently |
| Self-deferral | Cost opt in chained jobs | First-ever run (no prior manifest) |
| No deferral | State unreliable | — (always full rebuild, expensive) |

**Advanced CI (Enterprise) — Compare Changes:**
- **Requirements**: Enterprise+; same database host for CI + prod; model needs PK constraint or uniqueness test
- **How it works**: CI builds modified models in temp schema → compares row-by-row against prod → posts summary comment to PR + Compare tab in dbt Cloud
- **`event_time`**: without it, full tables compared → CI's smaller date window looks like deleted rows → false positives every run. With it: only overlapping time range compared.
- **CI result cache**: up to **100 rows/model**, stored encrypted (S3 or Azure Blob), expires after **30 days** — inaccessible after that
- **Dynamic data masking does NOT apply** to cached rows — all job users see unmasked data; exclude PII models with `--exclude tag:pii`
- **Smart cancellation**: same PR new commit → stale queued runs auto-cancelled; different PRs run concurrently
- **SQL linting** (SQLFluff): Starter+; stop or continue on linting error

**Job chaining:** Starter+ (not Developer); can chain across projects. Cross-project Mesh chaining is gated by Enterprise+ via Mesh itself.

**Setup steps (per dbt docs):**
1. **Deploy → Jobs** → select/create the **downstream** job → **Triggers** section
2. Enable **Run when another job finishes**
3. **Specify the parent project** (same or different project)
4. **Specify the upstream deploy job**
5. **Completes on** → choose run status(es) that enqueue the downstream job (Success / Success+Warning / etc.)
6. Save

**Gotchas:**
- Run details page shows a link back to the upstream job that triggered the run
- Need permissions on **both** projects to configure the trigger
- This is the **only** way to do upstream→downstream Mesh orchestration — no selector does it

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
| `state:old` | Exists in prior manifest, unchanged |
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
- Resolution order: dev relations → staging → production; `--favor-state` flips to state-first

**State gotchas:**
- `--vars` changes are **invisible to `state:modified`** — changing only a var value doesn't mark models modified
- `--state` and `--target-path` pointing to the same dir → dbt overwrites the manifest before comparison → wrong state. Use separate dirs.
- Seeds >1 MiB: only tracked on path changes, not content
- Relationship tests with `--defer`: can query across two environments → false failures

**`dbt ls`** — lists resources, no warehouse connection needed:
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
- Works in `.sql` and `.yml`; NOT in `profiles.yml` or `packages.yml`
- Missing var (no default) → compile error
- **Does not affect `state:modified` detection**

**Other useful selectors:**
```bash
--select result:error          # errored nodes from last run
--select result:fail           # failed tests from last run
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

- `source_status:` accepts **only** `fresher` — no other values.
- Workflow: prior `dbt source freshness` writes `sources.json` → `dbt source freshness` again now → `dbt build --select source_status:fresher+ --state path/to/previous/`.
- Without `--state`, selector resolves to **zero nodes** — silent no-op.
- `source:fresher+` (no underscore) is a **name lookup** — dbt searches for a source literally named `fresher` and almost always finds nothing.
- Use case: source-driven jobs that only build downstream when raw data actually arrives.

**`--indirect-selection`** (controls which tests run when models are selected):
- `eager` (default): tests run if ANY parent selected — may error if other parents unbuilt
- `cautious`: tests run only if ALL parents selected
- `buildable`: tests run if dependencies are selected or their ancestors
- `empty`: no indirect tests

---

## T4c: Blue/Green Deployments

**What it is:** Build everything in staging (green), atomically swap to production (blue) only after tests pass. Zero downtime, instant rollback.

**Flow:**
1. Run all models against green (staging) — blue untouched
2. Run all tests against green — fail = abort, blue stays live
3. `dbt run-operation swap_database` — atomic swap, green becomes production
4. Old blue preserved as rollback point; becomes new staging next deploy

**`dbt clone`:**
- Creates zero-copy clones of production models in a target schema
- Auto-includes `--defer`; falls back to pointer views on unsupported platforms
- Default skips existing relations — use `--full-refresh` to recreate
- Use clone (not deferral) when BI tools need to query realistic data before cutover

**Platform support:**

| Platform | Blue/Green viable? |
|---|---|
| Snowflake | ✅ `CLONE` + `SWAP WITH` |
| Databricks | ✅ shallow clone + schema swap |
| BigQuery | ✅ with dataset workarounds |
| Redshift | ❌ no rename/swap support — not viable |
| Postgres | ❌ sequential DDL only |

**Critical gotchas:**
- **Views with hardcoded DB names break after swap** — override `ref()` and `source()` to exclude database qualifier: `builtins.ref(model).include(database=false)`
- **Snapshots break** — `dbt_valid_to` continuity disrupted by swap; store snapshots in a separate non-swapped database
- **Incremental models get stale baseline** — demoted blue's incremental table is the new staging baseline; run `--full-refresh` on incrementals post-swap
- **Only swap on full runs** — never swap after a partial `--select` run; green will be incomplete
- **Failure is safe** — if run or tests fail, swap never executes; blue unchanged

---

## T5: Security & Licenses

**License always overrides group permissions:**

| License | Inherits permission sets? | Fixed access |
|---|---|---|
| Developer | ✅ Yes | Full feature access |
| Analyst | ✅ Yes | Enterprise only; legacy |
| IT | ❌ **No** | Security Admin + Billing Admin + edit Connections only |
| Read-Only | ❌ **No** | View artifacts + deploy section only |

**IT/Read-Only trap**: assigning these users to any group has zero effect on their access.

**Permission sets — quick lookup:**

| Need to... | Role |
|---|---|
| Create projects | Account Admin or **Project Creator** only |
| Access IDE | Admin, Developer, Analyst |
| Create/edit jobs | Account Admin, Admin, **Job Admin** |
| Trigger jobs | + Job Runner |
| Manage SSO/users | **Security Admin** (has zero data access) |
| Manage connections | Account Admin, Security Admin, Database Admin |
| Query Semantic Layer (API) | **Semantic Layer** service token only |
| Full audit log (sensitive) | Account Admin, **Viewer** (account-level) |

**Common traps:**
- **Admin ≠ Account Admin**: project Admin cannot create new projects
- **Security Admin**: no IDE, no jobs, no data access — admin only
- **Database Admin**: no IDE — configs only
- **Stakeholder vs Viewer**: Stakeholder = project-level, no sensitive audit; Viewer = account-level, full audit
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
- Created via Account Settings → Service Tokens (**Account Admin only**)
- One token can carry **multiple permission sets**, each scoped to all projects or specific projects
- Pre-July 18, 2023 tokens: rotate to new format for performance

**PAT vs Service Token:**

| | PAT | Service Token |
|---|---|---|
| Identity | Tied to a user | Account-level, no user |
| Permissions | **Inherited** from user (license + groups); not configurable | **Explicitly assigned** permission sets |
| Multi-permission-set | No | **Yes** |
| Project scoping | User's projects | Per permission set: all / specific |
| User deactivated | **Token dies** | Persists |
| Multi-account user (same email) | **Separate PAT per account** | N/A |
| License consumption | Yes (user's seat) | No |
| Audit attribution | The user | The token |
| Created by | The user themselves | Account Admin |
| Recommended for | dbt CLI, dev scripts, user-context endpoints | Production CI/CD, Terraform, partner integrations |

**Service token permission sets by tier:**
- **Enterprise/Enterprise+**: any permission set
- **Legacy Team**: Account Admin, Member, Job Admin, Read-Only, Metadata, Semantic Layer
- **Developer/Starter**: **Semantic Layer only**

**PAT vs Service Token — exam traps:**
- "Production job fails after employee X leaves" → PAT was the auth; replace with service token
- "Where do PAT permissions come from?" → user's license + groups; **not configurable on the token**
- "Which can be scoped per-project?" → service token only
- Endpoints that need user context (e.g., updating a specific user's credentials) → **PAT only** (service tokens have no user identity)
- Same user, two dbt accounts → **two separate PATs** required
- **Semantic Layer Only** permission = service-token-exclusive (cannot assign to user)
- **Fusion Admin** permission = user-only (cannot assign to service token)

**SSO (Enterprise only):**
- JIT provisioning on first login; re-auth every **24 hours**
- **SCIM**: Okta and Entra ID only; syncs on login (not real-time)
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
1. **Account Settings → Enterprise → Single Sign On → Edit**
2. Fill: Log in with `Okta` | IdP SSO URL | IdP Issuer | X.509 Certificate
3. Save

*End-user login URL:* `https://YOUR_ACCESS_URL/enterprise-login/<slug>`

**SSO gotchas:**
- **X.509 cert expiry is manual** — Okta admin must regenerate before expiry; expired cert breaks SSO entirely
- **SCIM-vs-SSO username conflict** — SCIM requires Email format; pick upfront (changing later is disruptive)
- **IdP group names = dbt group names** (case-sensitive) — most common cause of "groups don't apply" tickets
- Admins keep password fallback by default — recovery path if IdP breaks
- Other IdPs (Entra ID, Google Workspace, generic SAML 2.0) follow the same flow with different IdP-side UIs

**RBAC rules:**
- Permissions at **group level only** — no individual assignments
- IdP group names must match dbt group names **exactly** (case-sensitive)
- Disable "Add all new users by default" on Everyone for proper isolation

---

## T6: Monitoring & Alerting

**Webhooks:**
- Events: `job.run.started` \| `job.run.completed` \| `job.run.errored`
- `errored` fires **before** artifact ingestion — don't query API for artifacts on this event
- `completed` fires **after** artifact ingestion — safe for API queries
- **5 consecutive failures = silent auto-disable** (no alert sent)
- 10-second response window; must return 2xx
- 30-day delivery history

---

## T7: dbt Mesh

**Cross-project env resolution (MEMORIZE):**

| Consuming env type | Resolves to producer's... |
|---|---|
| Development | Staging (if exists), else Production |
| Staging | Staging |
| Production | Production |

**Model access levels:**
- `private` — same group only
- `protected` — same project/package (default)
- `public` — any project; cross-project ref requires **Enterprise+**
- Ephemeral models **cannot** be `public` — parsing error
- **No per-project allowlist** — `public` cannot be scoped to one specific downstream project. Workaround: keep it `private` to a group and consume via shared package / foundational project pattern. `restrict-access: True` on a package only blocks consumers from referencing `protected` models in that package — still binary, not per-project

**Contracts:**
- `enforced: true` required (opt-in); must declare **ALL columns**
- Breaking changes: removing columns, changing types, modifying constraints
- Incremental + contract: only `append_new_columns` or `fail` — not `sync_all_columns`

**Constraint enforcement:**

| Constraint | Postgres | Snowflake | BigQuery | Databricks |
|---|---|---|---|---|
| not_null | ✅ | ✅ | ✅ | ✅ |
| primary_key | ✅ | ⚠️ defined | ⚠️ defined | ⚠️ defined |
| foreign_key | ✅ | ⚠️ defined | ⚠️ defined | ⚠️ defined |
| unique | ✅ | ⚠️ defined | ❌ | ⚠️ defined |
| check | ✅ | ❌ | ❌ | ✅ |

**Model versions:**
- Unpinned `ref('model')` → `latest_version`
- Pinned: `ref('model', v=1)` \| cross-project: `ref('project', 'model', v=1)`
- `deprecation_date` triggers warning to pinned consumers
- Default file: `model_v2.sql`; use `defined_in` to override filename

**Model groups:**
- Governance groups ≠ RBAC user groups — completely orthogonal
- Each model belongs to exactly **one** group
- Private model outside its group = hard error at parse time

**`dependencies.yml`:**
```yaml
projects:
  - name: jaffle_finance   # case-sensitive — must match dbt_project.yml exactly
```

**Mesh setup rules:**
- Stepwise: producer runs first → consumer adds dependency → run; not simultaneous
- Cannot share `sources:` across projects — use foundational project with public staging models
- `dbt build --select` does NOT trigger upstream project builds across boundaries

**`package:upstream_project` selector (Mesh):**

Once an upstream project is in `dependencies.yml`, the downstream manifest treats it like an installed package — same namespace as `package:dbt_utils`.

```bash
# In downstream project after adding upstream to dependencies.yml:
dbt ls    --select package:upstream            # list upstream public models in manifest
dbt build --select package:upstream+           # build everything downstream of upstream
dbt build --select state:modified+ --exclude package:upstream   # CI: skip upstream nodes
dbt ls    --select +package:upstream           # what of MINE depends on upstream
```

- Project name is **case-sensitive** — must match upstream's `dbt_project.yml` `name:` exactly.
- Hub packages + Mesh upstream projects share the namespace — `--exclude package:a package:b` (space = union).

**Selector vs orchestration — critical distinction:**

| Goal | Mechanism |
|---|---|
| Reference upstream public models, treat as immutable | `--exclude package:upstream` (refs resolve against upstream's prod via metadata service) |
| Trigger downstream build when upstream finishes | **"Run when another job finishes"** chaining in dbt Cloud (Starter+; cross-project Mesh chaining gated by Enterprise+ via Mesh) — NOT a selector |
| Cross-project upstream-then-downstream in one CLI call | **Not possible** — needs job chaining or external orchestrator |

`state:modified` is **project-local** — does NOT detect upstream changes (column renames, contract updates). Upstream's own CI must run `state:modified.contract`. `source_status:fresher+` does NOT flag upstream public models (consumed via `ref()`, not `source()`).

**Recognizing Mesh in lineage graph:**
- Project boundary nodes (labeled groupings, not flat model nodes)
- Cross-project edges labeled with source project name
- Public model badges on shared models
- "Find public models" view in Catalog only appears with Mesh configured

---

## T8: dbt Catalog

- Reflects **production environment** only by default
- **CI jobs do NOT update Catalog** — only deployment jobs (scheduled/manual) in prod or staging do
- Inactivity purge: no successful run in **3+ months** → environment auto-removed from Catalog
- One job per project for artifact generation — multiple jobs = conflicting/overwritten artifacts
- Column-level lineage: **Enterprise+ only; SQL models only** — Python models not supported

**`dbt docs generate` artifacts:**

| File | Contents |
|---|---|
| `manifest.json` | Model metadata, lineage graph, node definitions |
| `catalog.json` | Column names/types from database introspection |
| `sources.json` | Source definitions and freshness results |

**Model Query History:**
- **Plan: Enterprise+** — not available on Starter
- **What it tracks**: SELECT queries by downstream users/tools — **excludes** dbt builds and test runs
- **How to enable**: Orchestration → Environments → Production env → Settings → Query History → "Test Permissions" → enable → Save
- **Where to view** (4 places):
  1. Project details → "Most consumed models" (performance chart)
  2. Lineage graph → **Lenses** overlay (query volume) — Lenses are single-attribute; switch between materialization / test status / query volume / cost on the same DAG (no combined view)
  3. Resources list → sort by consumption column
  4. Individual model page in Catalog
- **Use for**: optimization prioritization, deprecation impact assessment

**Cost Insights:** Fusion + state-aware orchestration required; up to **24-hour** refresh lag.

---

## Plan Tier Quick Reference

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|---|---|---|---|
| Job chaining | ❌ | ✅ | ✅ | ✅ |
| Cross-project refs | ❌ | ❌ | ✅ | ✅ |
| Project dependencies (Mesh) | ❌ | ❌ | ❌ | ✅ |
| Advanced CI (compare) | ❌ | ❌ | ✅ | ✅ |
| SSO / SCIM | ❌ | ❌ | ✅ | ✅ |
| Column-level lineage | ❌ | ❌ | ❌ | ✅ |
| Multi-project lineage | ❌ | ❌ | ❌ | ✅ |
| PrivateLink | ❌ | ❌ | ✅ | ✅ |
| Azure DevOps native | ❌ | ❌ | ✅ | ✅ |
| BigQuery OAuth | ❌ | ❌ | ✅ | ✅ |
| Run slots | 1 | 1 | Higher | Higher |
| Scheduling min interval | 10 min | — | — | — |

---

## T9: Hooks & Operations

**Hook types:**

| Hook | Scope | Configured In | Fires |
|---|---|---|---|
| `pre-hook` | Model, Seed, Snapshot | `dbt_project.yml`, `config()` block, YAML | Per resource |
| `post-hook` | Model, Seed, Snapshot | `dbt_project.yml`, `config()` block, YAML | Per resource |
| `on-run-start` | **Project only** | `dbt_project.yml` only | Once per command |
| `on-run-end` | **Project only** | `dbt_project.yml` only | Once per command |

**Transaction behavior (critical):**
- post-hook runs **inside** the model transaction by default
- **Model fails → post-hook does NOT run** (transaction rolled back first)
- **post-hook fails → model creation rolls back** too
- Escape the transaction: `post_hook: {sql: "...", transaction: false}`

**Execution order — multiple scopes:**
- All hooks accumulate — model-level does NOT override project-level
- Order: package → `dbt_project.yml` → `config()` block; within scope: definition order

**Context variables:**

| Variable | Where Available |
|---|---|
| `{{ this }}` | `pre-hook`, `post-hook` |
| `{{ results }}` | **`on-run-end` ONLY** — None everywhere else |
| `{{ schemas }}` | `on-run-end` ONLY |

- `on-run-end` fires even on partial run failure — `results` shows all statuses
- Seeds: hooks via `dbt_project.yml` or YAML only (no `config()` block in CSV files)

**Operations (`dbt run-operation`):**
- Runs a macro directly — **no model materialization**, not part of DAG
- Syntax: `dbt run-operation <macro> --args '{key: value}'`
- Can be a job command step in dbt Cloud
- Use for: ad-hoc grants, backfills, one-time maintenance

**Hooks vs. Operations:**

| | Hooks | Operations |
|---|---|---|
| Invocation | Automatic | Manual |
| DAG | Yes | No |
| Best for | Routine automated tasks | Ad-hoc tasks |

**Key gotchas:**
- `VACUUM` on Redshift cannot run inside a transaction → use `transaction: false`
- `{{ results }}` in a post-hook = `None` (silent, no error)
- GRANT post-hooks are the standard Snowflake permission pattern
- post-hook skipped ≠ on-run-end skipped — on-run-end always fires

---

## Must-Know Gotchas (All Topics)

1. **IT/Read-Only licenses ignore groups** — assigning to Admin group does nothing
2. **Connection immutability** — can't change a connection on an existing environment
3. **Staging env + Mesh** — once created, always used; adding staging with no successful runs breaks dev resolution
4. **`dbt retry` on infra failure** = no-op (no nodes in `run_results.json`)
5. **Checkbox failures are isolated** — source freshness / docs generate checkbox won't fail the overall job
6. **GitLab: personal repos won't work** — must be a GitLab Group repo
7. **Webhook: 5 failures = silent auto-disable** — monitor proactively
8. **`job.run.errored` fires before artifacts** — use `job.run.completed` if you need artifact data
9. **Snowflake account ID = locator format** — not the `.snowflakecomputing.com` domain
10. **Deferral requires a successful manifest** — failed last run = no valid manifest = full rebuild
11. **Most permissive group wins** — a low-access group can be overridden by any other group
12. **`dbt build` upstream test fail → downstream = SKIP** (not error)
13. **Unit tests run before materialization** — fail early, cheaper
14. **Interval scheduling drifts** — use cron for fixed clock alignment
15. **CI jobs don't update Catalog** — only scheduled deployment jobs do
16. **Ephemeral models cannot be `access: public`** — parsing error
17. **Contracts: must declare ALL columns** — partial contracts not supported
18. **`check` constraints: Postgres + Databricks only** — Snowflake/BigQuery don't support them
19. **Project names in `dependencies.yml` are case-sensitive**
20. **Governance groups ≠ RBAC user groups** — completely separate systems
21. **`access: public` is all-or-nothing** — no per-project allowlist; cannot scope a public model to a specific downstream project
22. **`source:fresher+` ≠ `source_status:fresher+`** — `source:` is name-based (looks for a source literally named "fresher"); `source_status:fresher+` is the freshness-state selector and **requires `--state`** to compare prior `sources.json`
23. **Mesh upstream projects = `package:` selector** — case-sensitive match to `dbt_project.yml` name; same namespace as Hub packages
24. **`--select package:upstream+` does NOT trigger upstream builds** — only filters the downstream invocation; cross-project orchestration uses **"Run when another job finishes"** chaining (Starter+ for the feature itself; Enterprise+ in practice for cross-project Mesh), not selectors
25. **PAT dies with the user** — never authenticate production with a PAT; use a service token. PATs inherit permissions from the user (not configurable on the token); service tokens have explicit, project-scoped permission sets.