# dbt Architect Certification — Study Notes

> Audience: Daily dbt Cloud user. No basics — architect-level gotchas only.
> Format: Reference notes + Q&A self-test per topic.
> Exam in ~2 weeks. Prioritize the **High-Yield** section at the bottom.

---

## TOPIC 1: Warehouse Connections

### Reference Notes

- Connections are **account-level**, not project-level — shared across multiple projects
- Each environment references **exactly one connection** — a single job cannot write to two warehouses simultaneously
- Dev env and prod env within the same project CAN reference different connections (even different warehouse types), but each environment is single-warehouse
- The lineage graph in Catalog is **logical** (based on `ref()`/`source()` calls), not physical — it does not show warehouse topology or distinguish which connection ran a model
- **OAuth (warehouse-native)**: Credential revocation at warehouse immediately takes effect in dbt; preferred over username/password for compliance
- **IP whitelisting**: dbt publishes static hostnames but underlying IPs are dynamic (cloud infra); always use **hostnames** not raw IPs in firewall rules — or use PrivateLink
- **PrivateLink**: VPC-to-VPC, no public internet traversal; Enterprise only, region-specific
- BigQuery and Snowflake support External OAuth (Okta/Entra ID) for Semantic Layer queries
- Connection testing available in UI before creating jobs — test before scheduling

**Platform-Specific Connection Details**

**Snowflake**
- Account identifier: **locator format only** (e.g. `db5261993.east-us-2.azure`) — NOT the full domain URL (`db5261993.snowflakecomputing.com`) → silent connection failure
- MFA auth: **development environments only**; Snowflake is phasing out single-factor auth (Nov 2025)
- Key pair auth for **Fusion engine**: must be **PKCS#8 AES-256** format — 3DES or headerless keys rejected with "Could not deserialize key data"
- Custom domain: use extended attribute `host: https://custom_domain.com` (not the account locator)
- JWT token error = no Snowflake response within 60 seconds; add retry logic
- Minimum permissions required: `USAGE` on warehouse/database/schema; `SELECT`, `CREATE TABLE/VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`

**BigQuery**
- OAuth (Client ID + Secret): development environments + **Enterprise tier only**
- After org-level OAuth setup, end users link personal BigQuery accounts via Profile Settings
- Redirect URI pattern: `https://YOUR_ACCESS_URL/complete/bigquery`

**Databricks**
- `dbt-spark` connector is **deprecated** — must use `dbt-databricks`
- Unity Catalog requires **dbt 1.1+**; Python models require **dbt 1.3+**
- Three-part naming enabled by Unity Catalog: `catalog.schema.model`
- Required fields: Server Hostname, HTTP Path; Catalog (optional, for Unity Catalog)
- Unity Catalog permissions: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `MODIFY`

**Managed Repositories**
- dbt-hosted repo for trial/POC only — no Git workflows, no PRs, no branching
- **NOT recommended for production** (dbt Labs explicitly advises against this)
- Can be exported to a self-hosted repository at any time

### Gotcha Q&A

**Q: A new region was added to your dbt Cloud account and your Snowflake firewall suddenly blocks connections. What went wrong?**
A: IP addresses were hardcoded in the firewall rule instead of using dbt-provided hostnames. dbt's underlying IPs are dynamic; hostnames are stable.

**Q: You rotate a Snowflake user's password. dbt jobs fail immediately. Why, and what's the fix?**
A: The connection uses username/password auth. Update the credential in Account Settings → Connections. OAuth avoids this — revocation is warehouse-side and requires no dbt config changes.

**Q: A developer connects via OAuth but a service token cannot. Why?**
A: OAuth in dbt is user-level (personal credentials in Profile Settings). Service tokens use service account or key-based auth at the connection level, not OAuth.

**Q: You set up Snowflake key pair auth for the Fusion engine but get "Could not deserialize key data." Why?**
A: Fusion requires PKCS#8 AES-256 format. The key was likely generated in legacy 3DES format or is missing the BEGIN/END headers. Regenerate in the correct format.

**Q: A Databricks project was built using dbt-spark. Should anything change?**
A: Yes — dbt-spark is deprecated. Migrate to dbt-databricks. Also verify dbt version: Unity Catalog requires 1.1+, Python models require 1.3+.

**Q: You used a managed repository to prototype a project. The team is ready for production. What must change?**
A: Export the managed repo and migrate to a self-hosted Git repository. Managed repos have no PR workflows, branching, or version history — they're not suitable for production.

**Q: How many warehouse connections can a single dbt project use? Can different environments use different warehouse types?**
A: A dbt project uses **one connection per environment**. Dev and prod environments within the same project CAN point to different connections (e.g., one Snowflake connection for dev, a different Snowflake connection for prod), but each environment uses exactly one connection at a time. You cannot run a single job that writes to two different warehouses simultaneously. However, you can have environments in the same project pointing to entirely different warehouse types (Snowflake dev, Databricks prod) — though this is unusual and each environment's connection type is immutable after creation.

**Q: A project uses one Snowflake connection for dev and a different Snowflake connection for prod. Can both be viewed in the same lineage graph in dbt Catalog?**
A: Yes — the lineage graph in dbt Catalog/Explorer is **logical**, not physical. It shows model dependencies based on `ref()` and `source()` calls in the project DAG, not the physical warehouse topology. The graph reflects a single project's model relationships regardless of which connections the environments use. Cross-project lineage (Enterprise+) extends this across projects via the metadata service. The lineage graph does NOT show cross-warehouse data movement or distinguish which physical warehouse a model ran on.

---

## TOPIC 2: Git Connections

### Reference Notes

- **Native GitHub App** (recommended): Requires GitHub org owner AND dbt Account Admin/Owner to install; enables CI triggers and PR status checks
- **Git URL / deploy key method**: Required for on-prem GitHub, GitHub Enterprise on non-`ghe.com` domains; CI features limited
- **Azure DevOps**: Native integration is Enterprise-only; Starter/Developer must use deploy keys (no auto CI triggers)
- **Repository name is case-sensitive** in dbt UI — mismatch causes silent clone failures
- Each developer must authenticate their personal GitHub profile separately even after org-level setup
- BitBucket/AWS CodeCommit: No native integration → Git clone method + dbt Admin API to manually trigger CI

**GitLab Specifics**
- OAuth app requires **`api` scope** (not just `read_api`)
- Repos must belong to a **GitLab group** — personal user account repos do NOT work
- **Maintainer role** required to set up the connection
- Enterprise: admin creates group-owned OAuth app → adds Application ID + Secret to Account Settings → Integrations
- Developer/Starter: users connect personal accounts via Profile → Linked Accounts
- **GitLab Free Plan**: CI jobs trigger but **status is NOT posted back** to Merge Requests — no green/red check in the GitLab UI

**Azure DevOps Specifics**
- **Enterprise/Enterprise+ only** for native integration — Starter/Developer cannot use it at all
- Azure DevOps **Server (on-premise)**: no native integration — must use git URL import regardless of plan
- Recommended auth method: **Service Principal** (Service User is legacy)
- Requires coordination across three admin teams: dbt admins + Azure Entra ID admins + Azure DevOps admins

### Gotcha Q&A

**Q: You set up GitHub native integration but CI jobs aren't triggering on PRs. What's the likely cause?**
A: Either the dbt GitHub App wasn't installed by the org owner, or developers haven't authenticated their personal GitHub profiles. Both are required independently.

**Q: CI runs work on GitHub but an Azure DevOps repo on a Starter plan doesn't trigger CI. Why?**
A: Azure DevOps native integration is Enterprise-only. On Starter, only deploy keys are available — which don't support automatic CI triggers.

**Q: A GitLab user set up a repo under their personal account and connected it to dbt. CI triggers fire but nothing runs. Why?**
A: GitLab repos must belong to a GitLab **group**, not a personal user account. Repos in personal accounts are not supported for the native integration.

**Q: You're on GitLab Free Plan. CI runs succeed in dbt but developers see no status checks on their MRs. Why?**
A: GitLab Free Plan does not allow dbt to post CI status back to Merge Requests. Upgrade to GitLab Pro or switch to GitHub/Azure DevOps for status feedback.

---

## TOPIC 3: Environments ⭐ DEEP

### Reference Notes

**Environment Types — Counts Per Project**

| Type | Count | Purpose |
|---|---|---|
| Development | Exactly 1 | Drives IDE/CLI; sets branch devs fork from |
| Production | Exactly 1 | Source of truth for Catalog and cross-project ref resolution |
| Staging | Exactly 1 | Pre-prod validation; critical safety layer for dbt Mesh |
| General | Unlimited | Non-critical or experimental jobs |

**Custom Branches**
- Dev environment: controls which branch developers branch **from** in the IDE
- Deployment environments: controls which branch is **cloned** during job execution — NOT merged
- A custom branch on a deploy environment does not auto-merge from main

**Environment Variables — Scoping**
- Precedence (most specific wins): job-level > environment-level > project-level > account-level
- **Extended attributes** (YAML snippets for `profiles.yml`): only top-level keys are accepted
- Nested overrides require providing the **entire parent key as a JSON block** — partial nested overrides are silently ignored

**Service Accounts**
- Use when no human identity should own a connection (prod pipelines, CI)
- Key pair authentication must be rotated via the **dbt Admin API** — no UI path

**Key Pair Authentication Rotation (via API)**
- Flow: generate new key pair → POST new public key to API → verify → invalidate old key

**Deferral**
- "Deferral environment" provides its latest successful manifest to jobs that reference it
- If the deferred environment's last run **failed**, deferral breaks — architect must plan a fallback

**Connection Immutability**
- Once a connection is assigned to an environment, it **cannot be changed** after the fact
- To switch warehouse types: create a NEW environment → migrate jobs → delete old environment
- There is no "edit connection" option on an existing environment

**Default Schema/Dataset per Platform**

| Platform | Configurable Fields | Override Method |
|---|---|---|
| Snowflake | Role, Database, Warehouse | Editable in environment UI |
| Postgres / Redshift | Inferred from project connection | Extended attributes |
| BigQuery / Spark | Inferred from project connection | Extended attributes |
| Databricks | Catalog field (Unity Catalog) | Environment UI |

- Best practice: wrap secrets in **environment variables** rather than hardcoding values in extended attributes

**dbt Version Release Tracks (Environment-level)**
- **Latest**: Always the most recent dbt version; auto-upgraded immediately
- **Compatible**: Lags behind Latest for stability; recommended for most teams
- **Extended**: Longest support window; slowest to upgrade; for risk-averse teams

**Staging Environment — Mesh-Specific Benefits**
- If **Project B** also has a Staging environment, deferral within Project B resolves refs to unbuilt upstream models AND UDFs against that staging environment — not production
- This preserves clear environment separation without requiring separate projects per team
- Staging has its own independent view in Catalog (not just a production snapshot)

### Gotcha Q&A

**Q: You configure an extended attribute to override only a nested key in `profiles.yml`. The override doesn't apply. Why?**
A: Extended attributes accept top-level keys only. To override a nested value, provide the entire parent block as a JSON object — partial nested overrides are silently ignored.

**Q: A CI job's deferral is configured against Production, but the last production run failed 3 days ago. The CI job builds the entire DAG instead of just modified models. Why?**
A: Deferral requires a **successful** manifest from the reference environment. With no recent successful run, there's no valid manifest — falls back to full DAG build.

**Q: You delete a deployment environment. What happens to jobs configured in that environment?**
A: Jobs are deleted with the environment unless transferred first. Always transfer jobs before deleting an environment.

**Q: A job uses `--state` for deferral but the manifest keeps getting overwritten before comparison. What causes this?**
A: `--state` and `--target-path` point to the same directory. dbt overwrites `manifest.json` during parse before comparison. Fix: use separate directories, or pass `--no-write-json`.

**Q: A dev IDE job resolves cross-project refs. The upstream project has NO staging environment configured. Where does it resolve?**
A: To the upstream project's **Production** environment. When no staging environment exists, dev cross-project ref resolution falls back to Production. This is the **only** scenario where Production is used as the resolution target for a dev IDE job.

**Q: A dev IDE job resolves cross-project refs. The upstream project has a Staging environment configured, but it has never had a successful job run. Where does it resolve — and does it fall back to Production?**
A: dbt routes to **Staging — not Production**. Once a staging environment exists and is linked to the metadata service, dbt always routes to it regardless of whether any runs have succeeded. Because no successful run has populated the staging metadata, the cross-project ref resolution **fails** outright — it does not silently fall back to Production. Critical gotcha: adding a staging environment with no successful runs immediately breaks downstream dev IDE jobs. **Fix**: run at least one successful deployment job in Staging immediately after creating it.

**Q: A developer's IDE job references an upstream model in Project B. Project B has a staging environment. The specific upstream model hasn't been built in staging yet. Does dbt fall back to Production for that model?**
A: No. dbt routes to **Staging** for all cross-project ref resolution once a staging environment exists. Whether resolution succeeds depends on whether staging has a successful run with metadata. Fallback to Production only occurs when the staging environment **type doesn't exist at all** — not when a specific model is absent from it.

**Q: You add a Staging environment to an upstream project in your Mesh. Developer jobs immediately start failing to resolve cross-project refs. Why?**
A: Once a staging environment is created and linked to the metadata service, dbt **immediately** routes all dev cross-project ref resolution to it — with no fallback to Production, even though no jobs have run yet. The staging environment has no metadata, so resolution fails. This is not a gradual transition. **Fix**: run at least one successful deployment job in the new staging environment before relying on downstream dev IDE jobs.

**Q: A team wants to switch their production environment from Redshift to Snowflake. How do you do this?**
A: You cannot change the connection on an existing environment. Create a new environment pointing to the Snowflake connection, migrate all jobs to it, then delete the old Redshift environment.

**Q: What's the difference between the Compatible and Extended release tracks?**
A: Compatible lags slightly behind Latest for stability — good for most teams. Extended has the longest support window and upgrades last — for teams with strict change management. Never use Latest in production if you need predictable versioning.

---

### Environment UI — All Configurable Fields

**Core fields (all environment types):**

| Field | Notes |
|---|---|
| Environment name | Required |
| Environment type | Deployment / Development; greyed out if that type already exists for the project |
| **Production environment** toggle | One per project; makes this env the Catalog source of truth and cross-project ref resolver |
| dbt version / release track | Latest / Compatible / Extended |
| Custom branch | Controls which branch is cloned at job runtime (deploy envs) or forked from (dev env) |
| Extended attributes | YAML snippet overriding `profiles.yml`; top-level keys only |

**Connection-specific editable fields:**

| Platform | Editable in environment UI |
|---|---|
| Snowflake | Role, Database, Warehouse |
| Databricks | Catalog (optional, for Unity Catalog) |
| Postgres / Redshift | Nothing — inferred from project connection; use extended attributes to override |
| BigQuery / Spark | Nothing — inferred from project connection; use extended attributes to override |

**Deployment credentials (per platform):**

| Platform | Credential fields |
|---|---|
| Snowflake | Auth method (Username+Password or Key Pair), Username, Password or Private Key + optional passphrase, Schema |
| Postgres / Redshift | Username, Password, Schema |
| BigQuery | Dataset |
| Databricks / Spark | Token, Schema |

**Gotcha**: Wrap credential values in environment variables — avoid hardcoding secrets in the credentials form, as values may appear in logs.

---

## TOPIC 3b: Schema Generation & Custom Schema Precedence ⭐ HIGH-YIELD

### Reference Notes

**The Core Question: What schema does a model land in?**

dbt determines the final schema name using a Jinja macro called `generate_schema_name`. This macro lives in the dbt core library but can be overridden in your project's `macros/` directory.

**Default `generate_schema_name` macro:**
```jinja
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

**Result table — default behavior:**

| Setup | Resulting schema |
|---|---|
| Dev target schema = `dbt_user_1`, no `schema` config | `dbt_user_1` |
| Dev target schema = `dbt_user_1`, model config `schema: core` | **`dbt_user_1_core`** |
| Prod target schema = `analytics`, model config `schema: core` | `analytics_core` |
| Prod target schema = `analytics`, no `schema` config | `analytics` |

**The custom schema does NOT replace the target schema — it appends to it.**

---

**Why the default appends (not replaces):**
If the default returned just the custom schema in dev, every developer with `schema: core` would write to the same shared `core` schema — developers would overwrite each other's data. Appending the personal target schema prefix (`dbt_user_1_`) ensures isolation in development.

---

**The Architect Override Pattern (prod uses clean schema name):**

Most production teams want models with `schema: core` to land in `core`, not `analytics_core`. The standard override pattern:

```jinja
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {%- if target.name == 'prod' -%}
            {{ custom_schema_name | trim }}
        {%- else -%}
            {{ default_schema }}_{{ custom_schema_name | trim }}
        {%- endif -%}
    {%- endif -%}
{%- endmacro %}
```

- **Dev** (`target.name = dev`): `dbt_user_1_core` — isolated per developer
- **Prod** (`target.name = prod`): `core` — clean schema name

Place this in `macros/generate_schema_name.sql` — dbt auto-detects it.

---

**`target.name` — the environment signal:**
- Set via the dbt Cloud job's **Advanced Settings → Target name** field
- dbt Cloud IDE defaults to `target.name = dev` unless overridden
- Deployment jobs can be given `target.name = prod` to trigger production schema logic
- `target.name` is distinct from environment type — it's a string you control; your macro decides how to use it

---

**Key rules:**
- **Default formula**: `target.schema` + `_` + `custom_schema`
- **Override location**: `macros/` directory — any file name; dbt detects by macro name
- **Always preserve `target.schema` prefix in dev** — dropping it causes developer collisions
- **CI temp schema is exempt**: CI jobs write to `dbt_cloud_pr_<job_id>_<pr_id>` — the CI schema is NOT passed through `generate_schema_name` for the temp schema itself

---

**CI + Custom Schema Conflict:**
- If a custom `generate_schema_name` macro returns a name that doesn't match the expected `dbt_cloud_pr_<job_id>_<pr_id>` pattern, dbt cannot identify the temp schema to delete it on PR close/merge — the PR schema orphans in the warehouse.
- Fix: ensure custom macro logic does not interfere with CI temp schema naming, or use the `node.config.schema` guard in the macro.

---

### Gotcha Q&A

**Q: Dev schema is `dbt_user_1`. A model has `config: { schema: 'core' }`. You run it in the dbt Cloud IDE. What schema does the model land in?**
A: `dbt_user_1_core`. The default `generate_schema_name` macro prepends the target schema. The custom schema does NOT replace the target schema — it appends to it with an underscore.

**Q: In production, a team wants models with `schema: 'core'` to land in the `core` schema, not `analytics_core`. What do they need to do?**
A: Override `generate_schema_name` in `macros/` with logic that checks `target.name == 'prod'` and returns only the custom schema name in that case. Leave the default prefix behavior for all other target names.

**Q: A developer overrides `generate_schema_name` to always return just the custom schema name. What goes wrong in development?**
A: All developers whose models have `schema: 'core'` now share the same `core` schema — they overwrite each other's model data. Always preserve `target.schema` as a prefix in non-production targets.

**Q: You set `schema: 'core'` on a CI job. After the PR merges, the PR schema isn't cleaned up. What's the likely cause?**
A: A custom `generate_schema_name` macro is overriding the expected PR schema naming. dbt can only auto-delete the temp schema if its name matches `dbt_cloud_pr_<job_id>_<pr_id>`. A macro that outputs a different name breaks auto-cleanup.

**Q: A job's Advanced Settings has `target name` set to `prod`. The team's custom macro returns just the custom schema when `target.name == 'prod'`. A model with `schema: core` runs. Where does it land?**
A: In the `core` schema — the "Target name" override feeds directly into `target.name` within the macro.

**Q: Two developers both have models with `config: { schema: 'finance' }`. Developer A's target schema is `dbt_alice`, Developer B's is `dbt_bob`. Do they collide?**
A: No — default behavior produces `dbt_alice_finance` and `dbt_bob_finance` respectively. The personal target schema prefix ensures isolation.

---

## TOPIC 4: Jobs & CI/CD ⭐ DEEP

### Reference Notes

**Job Types**
- **Deploy jobs**: scheduled or event-triggered; consume run slots; materialize prod data
- **CI jobs**: PR-triggered; **do NOT consume run slots**; use temp schema `dbt_cloud_pr_<job_id>_<pr_id>`; schema auto-deleted on PR close/merge (unless a custom schema macro overrides default naming)
- Same PR → CI runs **serially** with smart cancellation of stale builds
- Different PRs → CI runs **concurrently**

**Command Ordering Rules**
- Commands run sequentially; failure at step N skips all subsequent steps
- `dbt build` **must** run before `dbt sl validate` — models must exist in CI schema first
- `dbt source freshness` as a **checkbox**: runs **first**; if it fails, the job can still succeed if all subsequent steps succeed
- `dbt source freshness` as a **command step**: failure blocks all subsequent steps
- `dbt docs generate` as a **checkbox**: runs **after** all listed commands; if it fails, the job can still succeed if all subsequent steps succeed
- Key nuance: checkbox failures are **isolated** — they don't propagate to the overall job status as long as the steps after them pass

**Deferral Types**

| Type | Use Case | Risk |
|---|---|---|
| Defer to Production | Standard CI: validate PR against prod state | Breaks if prod job hasn't run successfully recently |
| Self-deferral | Cost optimization in chained jobs | Requires a prior successful run of the same job |
| No deferral | When state is unreliable | Full DAG builds — expensive |

**Self-Deferral**
- Job defers to its own previous successful run (not another environment)
- Ideal when job_A triggers job_B and job_B only needs to rebuild what changed since last run
- First-ever run has no prior manifest → falls back to full DAG build

**Advanced CI — Full Detail (Enterprise only)**

*Requirements:*
- Plan: **Enterprise or Enterprise+** — not available on Starter/Developer
- Must be explicitly enabled in account settings by a dbt admin
- CI and production models must live on the **same database host/connection** — different hosts = compare fails completely
- Model must have a **primary key constraint or uniqueness test** — without it you get "Primary key missing" error, no row-level diff
- Supported platforms: BigQuery, Databricks, Postgres, Redshift, Snowflake only

*How Compare Changes works end-to-end:*
1. PR opens or receives a new commit → CI job triggers
2. dbt builds modified models in the temp CI schema, defers unmodified upstream to production
3. dbt compares the CI output against the production version of the same model, row by row
4. Results appear in two places: the **Compare tab** in the dbt Cloud job run details, and an **automated comment posted to the PR** in the git provider
5. PR comment summarises: added rows, removed rows, modified rows, column-level changes, primary key analysis

*`event_time` — why it matters:*
- Without `event_time`: full tables compared → CI runs typically cover a smaller date window than production → rows outside that window appear as "deleted" → **false positives on every run**
- With `event_time`: dbt filters both CI and production tables to the **overlapping time range** before comparing → accurate diff, no spurious deletions

*CI result cache:*
- Up to **100 rows per modified model** cached for preview
- Stored **encrypted** in region-specific S3 or Azure Blob Storage (in your account's region)
- Retained for **30 days** — after that, comparison results are inaccessible and show an expiration message
- Cache is reused when you revisit the Compare tab — avoids re-querying the warehouse on each view
- **Dynamic data masking does NOT apply** to cached samples — all users with job access see the same unmasked cached rows regardless of warehouse masking policies

*Other Advanced CI features:*
- **SQL linting** (SQLFluff): available Starter+; sub-options: stop on error vs continue on error
- **Smart cancellation**: same PR, new commit → stale queued CI runs are automatically cancelled; only the latest commit's run proceeds
- **Concurrent CI**: different PRs run concurrently (each gets its own temp schema); same PR runs serially
- **Custom commands**: can add commands to the CI job to exclude large models from comparison (e.g. `--exclude tag:large`) or limit scope to reduce cost

**Job Chaining**
- Available: Starter, Enterprise, Enterprise+ — **NOT Developer**
- Can chain jobs across projects (cross-project Mesh chaining still gated by Enterprise+ for Mesh itself)
- Configure which statuses trigger downstream (success only, or success+failure)

**Setup steps (per dbt docs):**
1. Navigate to **Deploy → Jobs** → select or create the **downstream** job → **Triggers** section.
2. Enable **Run when another job finishes**.
3. **Specify the parent project** — same project for intra-project chaining, or a different project for cross-project Mesh orchestration.
4. **Specify the upstream deploy job** to listen to.
5. Under **Completes on**, choose the run status(es) that should enqueue the downstream job (e.g., Success only, or Success + Warning).
6. Save the job.

**Verification & gotchas:**
- When chained, the run details page shows a link back to the upstream job that triggered the run — useful for debugging missed triggers.
- You must have proper permissions on **both** the upstream project/job and the downstream project/job to configure the trigger.
- Chaining is the canonical Mesh upstream→downstream orchestration mechanism — there is no CLI selector that builds two projects in one invocation.
- A chained job runs at most once per upstream completion event. Rapid back-to-back upstream runs do not coalesce — each completion enqueues a separate downstream run.

**Scheduling**
- All scheduling in **UTC only** — no timezone conversion
- If job duration exceeds scheduling frequency: scheduler cancels queued runs, keeps only newest → queue bloat prevention
- Developer plan: 10-minute minimum scheduling interval

**Run Slots**
- CI jobs bypass the slot system entirely
- Deploy jobs consume slots; over-provisioning without planning causes queue buildup

**`dbt build` Execution Order**
1. Seeds
2. Models + Snapshots (concurrent)
3. Tests (after upstream resources complete)
4. UDFs (v1.11+ / Fusion engine only)

- Failing test on an upstream model → all downstream models enter **SKIP** status (not error — skip)
- Workaround: set test severity to `warn` instead of `error` to prevent downstream blocking
- Unit tests run **before** model materialization — cheaper to fail early

**`dbt build` Key Flags**
- `--empty`: schema-only dry run; limits refs/sources to zero rows; macros using `.render()` required to avoid errors
- `--full-refresh`: applies uniformly to all resource types in the run
- `--select model_a`: runs AND tests `model_a` plus dependent tests (indirect selection)

**Source Freshness — Extra Gotchas**
- Run freshness checks at minimum **2x the frequency** of your lowest SLA (e.g., 1-hour SLA → check every 30 min)
- If a job contains **only** a `dbt source freshness` checkbox with no other steps, add a placeholder command (e.g., `dbt compile`) — a job with nothing to execute will error
- Snowflake freshness uses `LAST_ALTERED` column, which has known edge-case limitations

**CI Edge Cases**

| Scenario | Behavior | Fix |
|---|---|---|
| **Monorepo** (multiple dbt projects in one repo) | Single PR triggers CI jobs for ALL connected projects | Use project-specific target branches: `main-project-a`, `main-project-b` |
| **Fork PR** | dbt cannot check out fork commits | Contributors must push to origin repo, not a fork |
| **PrivateLink + CI** | CI hooks are NOT available with Virtual Private dbt | Check PrivateLink security settings; jobs fail silently |
| **Azure DevOps** reused branch | CI won't trigger on new PR with same branch name used in abandoned PR, or same commit | Use new branch names and new commits |
| **GitLab Free Plan** | CI triggers but status not posted back to MR | Upgrade to Pro, or switch to GitHub/Azure DevOps |
| **Stale manifest** | Multiple jobs updating artifacts → unpredictable CI state | Run `dbt parse --no-partial-parse` after merges; designate single job for artifacts |

**`dbt retry` Command**
- Re-executes last invocation from the failure point, using `run_results.json`
- Supported commands: `build`, `compile`, `clone`, `docs generate`, `seed`, `snapshot`, `test`, `run`, `run-operation`
- **Critical limitation**: If the job fails before ANY nodes execute (warehouse connection error, permission error) → retry is a **no-op** — nothing in `run_results.json` to resume from
- In that case: must trigger a full job rerun manually
- **Rule**: `dbt retry` = recoverable SQL/model errors only. NOT for infrastructure failures.

**Run Slots & Concurrency**
- **Developer / Starter**: **1 run slot** — serial execution only; cannot run two jobs simultaneously
- **Enterprise / Enterprise+**: Higher allocation (exact number varies by contract)
- Memory limit: **600 MiB** per run pod — all plans, not configurable; exceeded by loading data into macros
- Job auto-deactivation [Beta]: scheduled jobs stop auto-enqueueing after **100 consecutive failures**

**Scheduling Drift**
- "Every 2 hours" mode = elapsed time after first run, NOT fixed clock intervals
- Job starts 3:05am → next runs at 5:05am, 7:05am (NOT 4:00am, 6:00am)
- For precise clock-aligned scheduling: **use cron syntax** instead of interval mode

**CI Job Notifications**
- CI results appear as **native Git platform status checks** only (GitHub PR check, GitLab MR status, Azure DevOps PR status)
- No email/Slack notification documented for CI jobs specifically
- Advanced CI Compare Changes: posts a detailed **PR comment** with row/column diffs

**Optional Settings — Gotcha Flags**
- `dbt version override`: NOT recommended — breaks run reproducibility
- Thread count default: 4; too high causes warehouse contention
- Target name override: useful for environment-specific schema naming in custom macros

---

### Deploy Job UI — All Configurable Fields

**Job Settings section:**

| Field | Required? | Notes |
|---|---|---|
| Job name | ✅ | e.g. "Daily build" |
| Description | No | Documents what the job consumes/produces |
| Environment | ✅ | Defaults to env where job was created; **cannot be changed after creation** |

**Execution Settings section:**

| Field | Required? | Notes |
|---|---|---|
| Commands | ✅ | Sequential; default `dbt build`; failure at step N skips all subsequent steps |
| Generate docs on run | No (checkbox) | Runs **after** all commands; failure is **isolated** (won't fail the job) |
| Run source freshness | No (checkbox) | Runs **before** all commands; failure is **isolated** (won't fail the job) |

**Triggers section:**

| Field | Notes |
|---|---|
| Run on schedule toggle | Enables scheduled execution |
| Schedule type | Three options: **Intervals** (every N hours), **Specific hours** (comma-separated UTC hours), **Cron** (full cron expression) |
| Days of week | Multi-select; available with Intervals or Specific hours modes |
| Run when another job finishes toggle | Enables job chaining; Starter+ only (not Developer) |
| Upstream project + job + status | Dropdowns to select which job and on what completion status (success / failure / both) triggers this job |

**Advanced Settings section:**

| Field | Default | Notes |
|---|---|---|
| Environment variables | Empty | Key-value overrides; job-level wins over env/project/account |
| Target name | — | Override for custom macro schema logic |
| Run timeout (minutes) | None | Cancels job if exceeded |
| Compare changes against | No deferral | Options: **No deferral**, **Environment** (prod deferral), **This Job** (self-deferral) |
| dbt version | Inherits from env | Override not recommended |
| Threads | 4 | Increase cautiously — too high causes warehouse contention |

---

### CI Job UI — All Configurable Fields

**Job Settings section:** same as deploy job (name, description, environment).

**Git Trigger section:**

| Field | Default | Notes |
|---|---|---|
| Triggered by pull requests toggle | **ON** | Main trigger for CI jobs |
| Run on draft pull requests toggle | OFF | Opt-in; triggers on draft PR creation and updates |

**Execution Settings section:**

| Field | Default | Notes |
|---|---|---|
| Commands | `dbt build --select state:modified+` | Runs modified models + downstream; editable |
| Linting (SQLFluff) toggle | OFF | Starter+ only; sub-options: **Stop on error** vs **Continue on error** |
| dbt compare toggle | OFF | **Enterprise+ only**; compares PR data vs production row-level; requires PK constraints or uniqueness tests |
| Compare changes against (deferral) | Production environment | Dropdown; environment to defer unmodified nodes to |
| Run timeout (seconds) | 3600 (1 hour) | Only active when dbt compare is enabled |

**Advanced Settings section:** same fields as deploy job (env vars, target name, dbt version, threads).

**Additional checkboxes on CI jobs:**

| Field | Default | Notes |
|---|---|---|
| Generate docs on run | OFF | Not typical for CI; documents PR state |
| Run source freshness | OFF | Runs freshness check as part of CI |

---

### Advanced dbt Commands & Node Selection

**Graph Operators — Traversal Syntax**

| Operator | Meaning | Example |
|---|---|---|
| `+model` | Model + ALL upstream ancestors | `+orders` |
| `model+` | Model + ALL downstream descendants | `orders+` |
| `+model+` | Model + all ancestors + all descendants | `+orders+` |
| `n+model` | Model + ancestors up to N levels | `2+orders` |
| `model+n` | Model + descendants up to N levels | `orders+1` |
| `@model` | Model + descendants + all ancestors of those descendants | `@orders` |
| `path.*` | Wildcard — all models in a path | `models/marts/*` |

- `@model` is the "full closure" operator — ensures everything needed to build the model AND its downstream tests exists; common in CI

**Set Operations**

| Operation | Syntax | Logic |
|---|---|---|
| Union (OR) | Space between selectors | `tag:daily tag:nightly` |
| Intersection (AND) | Comma, no space | `marts,tag:daily` |
| Exclusion | `--exclude` flag | `--select "marts.*" --exclude stg_orders+` |

```bash
# Run all mart models tagged daily, excluding one heavy model and its children
dbt run --select "marts,tag:daily" --exclude "marts.big_model+"
```

**State Selection Methods**

| Selector | What it selects |
|---|---|
| `state:new` | Nodes with no matching `unique_id` in comparison manifest — brand new resources |
| `state:modified` | All new nodes + any nodes that changed vs comparison manifest |
| `state:old` | Nodes in the comparison manifest that are unchanged |
| `state:unmodified` | Existing nodes with no changes |
| `state:modified.body` | Changes to model SQL or seed file content |
| `state:modified.configs` | Config changes (excludes database/schema/alias) |
| `state:modified.relation` | Changes to database/schema/alias only |
| `state:modified.macros` | Changes to any upstream macro (transitive — macro deps of macro deps included) |
| `state:modified.contract` | Contract changes (column names or types) |
| `state:modified.persisted_descriptions` | Description changes when `persist_docs` is enabled |

**`--state` flag** — provides the path to a prior `manifest.json` for comparison:
```bash
dbt run --select state:modified --state path/to/prod/artifacts
```

**`--defer` flag** — for unselected upstream nodes, resolves their refs against a prior environment's relations instead of building them:
```bash
dbt run --select state:modified+ --defer --state path/to/prod/artifacts
```
- Resolution priority with `--defer`: dev relations first → staging → production
- `--favor-state` flag flips this: uses state manifest metadata first regardless of dev relations

**Using `--state` and `--defer` together (standard CI pattern):**
```bash
dbt build --select state:modified+ --defer --state /path/to/prod/manifest
```
- Runs only modified models + their downstream descendants
- Upstream parents that aren't modified → resolved against production tables
- Saves significant warehouse compute in CI

**Critical state gotchas:**
- **Variables don't trigger `state:modified`**: if only `var()` values change between runs, dbt cannot detect the diff — affected models won't appear as modified
- **Manifest overwrite**: dbt writes a new `manifest.json` during parse before state comparison — if `--state` points to the same `--target-path`, state comparison gets the freshly-written manifest, not the prior one. Fix: use a separate directory for comparison artifacts
- **Seeds >1 MiB**: only tracked on file path changes, not content changes
- **Relationship tests with mixed parents**: when using `--defer`, a relationship test between a modified model (in CI schema) and an unmodified model (in prod) can cause false failures — it queries across two environments simultaneously

**`dbt ls` Command**
- Lists project resources without connecting to the warehouse or executing anything
- Alias: `dbt list`
- Supports full node selection syntax (`--select`, `--exclude`, all graph operators)

```bash
dbt ls --select state:modified           # list what would run in CI
dbt ls --select config.materialized:incremental   # list all incremental models
dbt ls --select tag:nightly --resource-type test   # list tests tagged nightly
dbt ls --select "marts,tag:daily" --output json    # JSON output with intersection
dbt ls --select "+my_model" --output path          # show file paths of ancestors
dbt ls --resource-type source                      # list all sources
```

`--output` options: `name` (default), `path`, `json`, `selector`
`--output-keys` (JSON only): specify which node properties to include, e.g. `"name resource_type description"`

**`--vars` Flag**
- Pass variable values at runtime, overriding `dbt_project.yml` definitions
- Syntax: YAML or JSON dict format

```bash
dbt run --vars '{"event_type": "signup", "region": "us"}'
dbt run --vars '{event_type: signup}'              # YAML dict — quotes optional
```

In models:
```sql
select * from events where event_type = '{{ var("event_type") }}'
-- With default fallback:
select * from events where event_type = '{{ var("event_type", "activation") }}'
```

- Works in `.sql` and `.yml` files during Jinja compilation
- Does **NOT** work in `profiles.yml` or `packages.yml`
- Missing required variable (no default) → compilation failure with a clear error
- **Critical**: `--vars` changes are **invisible to `state:modified`** — changing only a var value won't mark dependent models as modified

**Indirect Selection (`--indirect-selection`)**
Controls which tests run when models (not tests) are selected:

| Mode | Behavior |
|---|---|
| `eager` (default) | Runs tests if ANY parent node is selected — may error if other parents unbuilt |
| `buildable` | Runs tests whose dependencies are either selected or ancestors of selected nodes |
| `cautious` | Runs tests ONLY if ALL parent nodes are selected |
| `empty` | Runs no indirect tests at all |

```bash
dbt test --select "stg_orders+" --indirect-selection cautious
```

**Other Useful Selection Methods**
```bash
--select result:error          # nodes that errored in last run (works with run_results.json)
--select result:fail           # tests that failed in last run
--select source:snowplow+      # source and all downstream models (NAME-based)
--select source_status:fresher+  # sources with new data since last freshness run + downstream (STATE-based)
--select tag:nightly           # tag-based selection
--select config.materialized:incremental  # config value matching
--select path:models/marts     # file path selection
--select package:dbt_utils     # models from a specific package
--select test_name:unique      # specific named test
--select exposure:my_exposure+ # exposure and its upstream dependencies
```

**`source:` vs `source_status:` — common trap**

These are **two different selector methods**. They look similar but resolve completely differently:

| Selector | Method | Selects... | Requires `--state`? |
|---|---|---|---|
| `source:<name>+` | Name-based | The source literally named `<name>` plus its descendants | No |
| `source_status:fresher+` | State-aware | Sources whose freshness state diffed as `fresher` (newer `max_loaded_at`) vs the prior `sources.json`, plus their descendants | **Yes** |

- `source_status:` only accepts the value `fresher` — it is the **only** valid value of this method.
- Required workflow:
  1. Run `dbt source freshness` previously and persist the resulting `sources.json` to a known path.
  2. Re-run `dbt source freshness` now (so dbt has a current snapshot to compare).
  3. Then `dbt build --select source_status:fresher+ --state path/to/previous/`.
- Without `--state`, dbt has nothing to diff against and the selector resolves to **zero nodes** — the run silently does nothing.
- If you misspell as `source:fresher+` (single word), dbt looks for a source literally **named** `fresher` — almost always matches nothing.
- Common use: source-driven incremental jobs that only build downstream when raw data has actually landed; cheaper than `state:modified+` when source updates are sparser than code changes.

### Gotcha Q&A

**Q: A CI job runs `dbt sl validate --select state:modified+` before `dbt build`. Semantic validation fails. Why?**
A: Models must be materialized in the CI schema before semantic layer validation. `dbt build` must always precede `dbt sl validate`.

**Q: You configure self-deferral on a new CI job. The first run builds the full DAG instead of only modified models. Why?**
A: Self-deferral needs a previous successful run of the same job to produce a manifest. On the first run, no prior manifest exists.

**Q: Two PRs open simultaneously. What does dbt do?**
A: Runs them **concurrently** — each gets its own temp schema, no slot consumption.

**Q: A developer pushes 3 commits to a PR in rapid succession. How many CI runs execute?**
A: Ideally 1. dbt smart-cancels stale queued builds for the same PR, running only the latest.

**Q: The PR temp schema isn't cleaned up after the PR merges. What's the likely cause?**
A: A custom schema macro overrides default naming — dbt can't identify the PR schema to delete it.

**Q: Advanced CI reports "rows deleted" on every run even though production data hasn't changed. What's misconfigured?**
A: `event_time` is not configured. Without it, full tables are compared — CI runs covering smaller date windows appear to have deleted rows.

**Q: Advanced CI's Compare Changes feature is enabled but no row-level diff appears — just a "Primary key missing" error. Why?**
A: The model has no primary key constraint or uniqueness test. Advanced CI requires one of these to perform record-level comparison. Add a `not_null` + `unique` test on the PK column, or a primary key constraint in the model contract.

**Q: A developer views the Advanced CI Compare tab and sees unmasked PII in the cached rows, even though warehouse dynamic data masking is configured. Why?**
A: Dynamic data masking does not apply to Advanced CI cached samples. The cache stores raw rows at query time, and all users with job access see the same unmasked data. Sensitive models should be excluded from Advanced CI comparisons using `--exclude tag:pii` or similar.

**Q: Advanced CI is configured but Compare Changes fails because CI and production are on different database hosts. How do you fix this?**
A: CI and production environments must point to the same database host/connection for Advanced CI to work. Reconfigure either the CI or production environment to use the same connection.

**Q: Advanced CI comparison results from 5 weeks ago are no longer viewable. Why?**
A: The CI result cache expires after 30 days. Historical comparison data is permanently inaccessible after that window — it's not retrievable.

**Q: A scheduled job runs every 15 minutes but each run takes 20 minutes. What happens?**
A: The scheduler cancels queued runs and keeps only the most recent. Effective interval becomes ~20 minutes. Prevents queue buildup.

**Q: You want to chain Job B (in Project B) to run after Job A (in Project A). What's the minimum plan required?**
A: Starter plan or higher. Developer plan does not support job chaining.

**Q: A `dbt build` run has a failing test on `stg_orders`. Which resources are affected?**
A: All models downstream of `stg_orders` enter **SKIP** status — not error. They don't run at all. Fix: set the test severity to `warn` if downstream models should still build.

**Q: Unit tests are expensive to run. When does `dbt build` execute them relative to model materialization?**
A: Unit tests run **before** model materialization — if a unit test fails, the model never materializes. This is cheaper than failing after a full table build.

**Q: A job has only `dbt source freshness` as a checkbox and no other steps. It errors on creation. Why?**
A: A job needs at least one executable command step. Add a placeholder like `dbt compile` alongside the checkbox.

**Q: You use a macro with `this` in a `dbt build --empty` run and it fails. Why?**
A: `--empty` limits refs/sources to zero rows but macros must use `.render()` to handle the empty context correctly. Without `.render()`, the macro errors.

**Q: A CI job fails with "cannot check out commit." The contributor submitted a fork PR. What's the issue?**
A: dbt cannot check out commits from fork repositories. The contributor must push to the origin repo directly. Fork-based PRs are not supported for CI.

**Q: You enable PrivateLink for security. CI jobs stop running and there are no error messages. What happened?**
A: CI hooks are not available with Virtual Private dbt (PrivateLink). The jobs fail silently. Check the PrivateLink security configuration or move CI to a non-PrivateLink connection.

**Q: A `dbt retry` command runs but nothing executes. The prior failure was a warehouse connection timeout before any models ran. Why?**
A: `dbt retry` reads `run_results.json` to find the failure point. If no nodes executed before the failure, the file has no nodes to resume from — retry is a no-op. Trigger a full job rerun instead.

**Q: You have a Starter plan. Two jobs are scheduled to run at the same time. What happens?**
A: Starter has 1 run slot. The second job queues and waits for the first to complete — they cannot run concurrently.

**Q: A job is scheduled "every 30 minutes" but runs are drifting to irregular times. Why?**
A: Interval scheduling maintains elapsed time after the first run, not fixed clock alignment. For fixed clock times, switch to cron syntax (e.g. `*/30 * * * *`).

---

### Blue/Green Deployments ⭐ DEEP

**What it solves:**
Standard deployments risk downtime and data inconsistency — if a job fails mid-run, live queries may hit partially-built tables. Blue/green eliminates this by building everything in a staging environment and atomically swapping to production only after tests pass.

**Core mechanism:**
1. **Blue** = current production; **Green** = staging (being built)
2. Run all dbt models targeting the green environment — production untouched
3. Run all tests against green — if any fail, abort; blue remains live
4. Execute an atomic **swap operation** — blue and green swap metadata pointers in a single operation
5. Green is now production (blue); old blue becomes the new staging for next deployment
6. Old blue data is preserved as an instant rollback point

**`dbt clone` command:**
- Copies selected nodes from a source state to a target schema using zero-copy cloning where available
- Automatically includes `--defer`, so unselected upstream nodes resolve against the source state
- Falls back to pointer views (`SELECT * FROM source`) on platforms that don't support native cloning
- Default behaviour: skips pre-existing relations — use `--full-refresh` to recreate them
- **Use clone when**: downstream tools (BI, apps) need to query realistic production-scale data before cutover
- **Use deferral when**: testing only dbt logic in CI and cost matters — cheaper than clone

```bash
dbt clone --state path/to/prod/artifacts             # clone all production models
dbt clone --select "tag:finance" --state path/       # clone a subset
dbt clone --state path/ --full-refresh               # recreate pre-existing clones
dbt run-operation swap_database                      # atomic swap (custom macro)
```

**Platform support:**

| Platform | Zero-copy clone | Atomic swap | Blue/Green viable? |
|---|---|---|---|
| Snowflake | ✅ (`CLONE`) | ✅ (`SWAP WITH`) | ✅ Fully supported |
| Databricks | ✅ (shallow clone) | ✅ | ✅ Fully supported |
| BigQuery | ✅ (table clone) | ⚠️ Dataset swap workaround | ✅ With workarounds |
| Redshift | ❌ | ❌ No rename support | ⚠️ Not viable without downtime |
| Postgres | ❌ | ❌ | ⚠️ Sequential DDL only |

**Blue/green vs standard deployment:**

| | Blue/Green | Standard |
|---|---|---|
| Downtime risk | Zero (atomic swap) | High (mid-run failure hits live queries) |
| Rollback | Instant (swap back) | Manual recovery |
| Storage | 2× (blue + green) | 1× |
| Complexity | High (macros, ref overrides) | Low |
| Incremental model risk | Yes — stale baseline after swap | No |
| Snapshot compatibility | Breaks continuity | Native |

**Critical failure modes and gotchas:**

**Views with hardcoded database names break after swap:**
```jinja
{# REQUIRED: override ref() to exclude database from compiled SQL #}
{% macro ref(model_name) %}
  {% do return(builtins.ref(model_name).include(database=false)) %}
{% endmacro %}

{# Same override needed for source() #}
{% macro source(source_name, table_name) %}
  {% do return(builtins.source(source_name, table_name).include(database=false)) %}
{% endmacro %}
```
Without this, views reference the hardcoded old database name and point to stale data after the swap.

**Snapshots break after a database swap:**
- `dbt_valid_to` tracking is disrupted when the snapshot table's database is swapped
- **Fix**: store snapshots in a dedicated, non-swapped database; use a custom `ref_snapshot()` macro that always routes to that database

**Incremental models risk stale baseline:**
- After swap, the demoted blue becomes the new staging — its incremental table is the last pre-swap state
- Next deployment builds incrementally on top of potentially stale data
- **Fix**: run `dbt run --full-refresh --select <incremental_models>` after each swap, or track high-water marks in a separate non-swapped table

**Only swap on full runs:**
- Never trigger `swap_database` on a partial run (e.g. `--select state:modified`) — green will be incomplete
- Partial CI jobs should deploy directly without swapping

**Failure is safe:**
- If `dbt run` or `dbt test` fails → swap never executes → blue production unchanged
- If the swap itself fails → most platforms leave both databases untouched; retry the swap

**Recommended job sequence:**
```bash
dbt run                    # build all models in green
dbt test                   # validate; abort on any failure
dbt run-operation swap_database   # atomic swap; only if tests pass
```

### Gotcha Q&A

**Q: After a blue/green swap, views in downstream BI tools are returning stale data. Why?**
A: Views were compiled with hardcoded database names. After the swap, the database name they reference now points to the old (demoted) blue database. Fix: override `ref()` and `source()` macros to exclude the database qualifier from compiled SQL so views resolve against whichever database is currently aliased as production.

**Q: Snapshot history has gaps after a blue/green deployment. What went wrong?**
A: Snapshot tables were included in the database swap. The `dbt_valid_to` continuity tracking breaks when the snapshot table's physical database changes. Snapshots must live in a dedicated, non-swapped database.

**Q: An incremental model has missing rows after several blue/green deployments. Why?**
A: After each swap, the demoted blue becomes the new staging baseline. The incremental model's next run adds only rows newer than the stale demoted state — rows processed in the previous deployment may not be in the new staging baseline. Use `--full-refresh` on incremental models post-swap or maintain a separate high-water mark table.

**Q: You want to validate a blue/green deployment against your BI tool before cutover. Should you use `dbt clone` or deferral?**
A: `dbt clone`. Deferral is invisible to external tools — BI tools query the actual warehouse tables. `dbt clone` creates real relations in the staging schema that BI tools can connect to. Use deferral for pure dbt logic testing in CI where cost matters.

**Q: Your team uses Redshift. A colleague proposes implementing blue/green deployments. What's the problem?**
A: Redshift does not support database/schema renaming or atomic swaps. Blue/green is not viable on Redshift without brief downtime from sequential DDL operations. Snowflake, Databricks, and BigQuery are the viable platforms.

**Q: A `dbt clone` run skips models that already exist in the target schema. Why?**
A: By default, `dbt clone` skips pre-existing relations. Use `--full-refresh` to force recreation of existing clones.

---

## TOPIC 5: Security & Licenses ⭐ DEEP

### Reference Notes

**License Types — Always Override Group Permissions**

| License | Plans | Inherits Permission Sets? | Notes |
|---|---|---|---|
| Developer | All | Yes — any permission set | Full feature access |
| Analyst | Enterprise, Enterprise+ only | Yes — any permission set | Legacy; not available for new purchase |
| IT | Starter, Enterprise, Enterprise+ | **No** — fixed access regardless of group | Security Admin + Billing Admin + edit Connections; can manage users, groups, connections, licenses |
| Read-Only | Starter, Enterprise, Enterprise+ | **No** — fixed access regardless of group | View artifacts and deploy section (jobs, runs, schedules) only |

**Critical Rule**: License type **always overrides** group permission sets. Admin group + Read-Only license = read-only.

**IT and Read-Only — The Group Assignment Trap**
- IT and Read-Only users do **not** inherit rights from any permission sets — group assignment is irrelevant for them
- Every IT user has **identical** access across the account regardless of which group(s) they belong to
- Every Read-Only user has **identical** access across the account regardless of which group(s) they belong to
- Assigning an IT or Read-Only user to a high-permission group has **zero effect** on their access

---

### Permission Sets Reference (Enterprise)

**Mental Model — Account-Level Roles (7)**

| Role | One-liner | Key "cannot do" |
|---|---|---|
| Account Admin | Everything, no restrictions | N/A — full access |
| Project Creator | Create & configure projects | Cannot manage billing, SSO, or IP restrictions |
| Security Admin | Users, groups, licenses, SSO, IP restrictions | No IDE, no jobs, no runs, no environments |
| Billing Admin | Billing section only + read public models | Almost everything else |
| Cost Insights Admin | Configure cost metadata credentials + view cost data | No IDE, no job execution |
| Cost Insights Viewer | Read-only cost and savings data | Cannot configure anything |
| Viewer | Read-only everything + full audit log (incl. sensitive) | No IDE access |

**Mental Model — Project-Level Roles (14)**

| Role | One-liner | Key "cannot do" |
|---|---|---|
| Admin | Full project control (not account-wide) | Cannot **create new projects** |
| Developer | Write code in IDE + personal credentials | Cannot create/edit jobs or environments |
| Analyst | IDE access + view jobs/runs/environments | Cannot create jobs, edit environments |
| Job Admin | Create/edit jobs, runs, env vars + data warehouse config | No IDE access |
| Job Runner | Execute jobs only | No IDE, no job creation, no other access |
| Job Viewer | Read-only job results, status, logs | Cannot execute or modify anything |
| Database Admin | Data platform configs + env vars + Semantic Layer config | No IDE access |
| Git Admin | Git integrations + env vars + project settings | No IDE access |
| Team Admin | Manage project(s) for a team + limited account read | More limited than Admin |
| Stakeholder | Read-only projects, envs, jobs, runs + limited audit log | No IDE; audit log excludes sensitive info |
| Read-Only | Identical to Stakeholder | Same as Stakeholder |
| Metadata | Discovery API read-only access only | No execution, no modification |
| Semantic Layer | Query Semantic Layer only | Service token exclusive — cannot assign to users |
| Fusion Admin | Fusion upgrade workflow only | Cannot assign to service tokens |

---

**Who Can Do X — Quick Lookup**

| Task | Roles that can do it |
|---|---|
| **Create new projects** | Account Admin, Project Creator only |
| **Access the IDE** | Account Admin, Admin, Developer, Analyst |
| **Create/edit jobs** | Account Admin, Admin, Job Admin |
| **Execute (trigger) jobs** | Account Admin, Admin, Job Admin, Job Runner |
| **Configure SSO / auth providers** | Account Admin, Security Admin |
| **Manage users, groups, licenses** | Account Admin, Security Admin |
| **Manage connections** | Account Admin (write); Security Admin (write); Database Admin (project write) |
| **Configure Semantic Layer** | Account Admin, Admin, Database Admin, Job Admin (read), Semantic Layer token (query only) |
| **View full audit log (incl. sensitive)** | Account Admin, Viewer (account-level) |
| **View audit log (excl. sensitive)** | Stakeholder / Read-Only |
| **Create webhooks** | Account Admin, Developer (project-level write) |
| **Manage service tokens** | Account Admin (write); Security Admin (read only) |
| **Query Semantic Layer via API** | Semantic Layer (service token only) |
| **Access Discovery API (metadata)** | Metadata, most project roles (read) |

---

**Permission Set Gotchas**
- **Admin ≠ Account Admin**: Project-level Admin has full project control but **cannot create projects** — only Account Admin and Project Creator can
- **Security Admin has zero data access**: No IDE, no jobs, no runs — purely administrative
- **Database Admin has no IDE**: Common trap — Database Admin manages platform configs but cannot write dbt code
- **Git Admin has no IDE**: Manages repositories and git integrations only
- **Job Runner is minimal**: Can only execute existing jobs and read their status — no creation, no other access
- **Stakeholder vs Viewer**: Stakeholder (project-level) = limited audit log, no sensitive info; Viewer (account-level) = full audit log including sensitive
- **Stakeholder = Read-Only**: These are two names for the identical permission set
- **Semantic Layer**: Service token only — cannot be granted to human users
- **Fusion Admin**: User-only — cannot be assigned to service tokens
- **Project Creator + account settings**: Can create projects and manage limited account settings but cannot touch SSO, billing, or IP restrictions

**Permission Set Hierarchy**
- Account-level: Account Admin > Security Admin > Project Creator > Billing Admin > Cost Insights Admin > Viewer
- Project-level: Admin > Job Admin > Developer ≈ Analyst > Database Admin > Git Admin > Job Runner > Job Viewer > Metadata
- When a user is in multiple groups: **most permissive wins** (not most restrictive)

**Service Tokens**
- Account-level, not tied to individuals
- **Token value shown ONCE** — save immediately; unrecoverable after dialog close
- Rotation pattern: create new → update integrations → delete old (no in-place rotation)
- Subject to IP restriction allowlists; a `403` on API calls = IP not allowlisted (not a bad token)
- Pre-July 18, 2023 tokens: recommend rotation to new format for performance and latency improvements
- Created at: **Account Settings → Service Tokens → + New Token**. Creation requires Account Admin permission (regardless of the creator's license).
- A single service token can carry **multiple permission sets**, and each permission set can be scoped to **all projects** or to **specific projects**.

**Personal Access Tokens (PATs) vs Service Tokens**

PATs and service tokens are both authentication tokens for the dbt Cloud APIs, but they are architecturally different.

| Dimension | Personal Access Token (PAT) | Service Token |
|---|---|---|
| Identity | Tied to a specific user | Account-level — no user identity |
| Permissions source | **Inherited** from the creating user's license + group memberships — not configurable on the token | **Explicitly assigned** permission sets at creation time |
| Multiple permission sets per token? | No — whatever the user has | **Yes** — one token can carry many permission sets |
| Project scoping | Whatever projects the user can access | Per permission set: **"all projects"** or **"specific projects"** |
| Tier requirement | User must hold a Developer / Read-only / IT license | Available on all tiers, but the *available permission sets* differ by tier (see below) |
| Created at | Account Settings → API Tokens → **Personal tokens** (the user creates their own) | Account Settings → **Service Tokens** (Account Admin only) |
| License consumption | Consumes the user's seat | No seat consumed |
| Audit trail | Actions logged as the user | Actions logged as the token (no human attribution) |
| Lifecycle if user is deactivated | **PAT dies with the user** — deactivating/removing the user revokes all their PATs | Persists independently of any user |
| Multi-account user with same email | **Separate PAT per dbt account** | N/A (token belongs to one account) |
| IP allowlist | Subject to IP restrictions; 403 = IP not allowlisted | Same |
| Visibility on creation | Shown **once**, unrecoverable after dialog close | Same |
| Rotation | Create new → swap → delete old | Create new → swap → delete old |
| Recommended use | dbt CLI, dev/staging scripts, endpoints requiring user context (e.g., creating/updating user credentials) | CI/CD, production Terraform, partner integrations (Semantic Layer, Hightouch, Datafold), all service-to-service automation |

**Service-token permission sets by plan tier (per dbt docs):**

| Plan | Permission sets available to service tokens |
|---|---|
| Enterprise / Enterprise+ | Any permission set: Account Admin, Account Viewer, Admin, Analyst, Billing Admin, Database Admin, Developer, Git Admin, Job Admin, Job Runner, Job Viewer, Manage Marketplace Apps, Metadata Only, Read-only, Semantic Layer Only, Security Admin, Stakeholder, Team Admin |
| Legacy Team | Account Admin, Member, Job Admin, Read-Only, Metadata, Semantic Layer |
| Developer / Starter | **Semantic Layer permissions only** |

PATs have no equivalent table — they are simply whatever the user has. You **cannot** narrow a PAT below the user's own permissions; to restrict a PAT, you must restrict the user.

**Architect-level uniqueness — PATs:**
- Permission inheritance is implicit — there is no permission picker on the token itself.
- A user with access to two dbt accounts (same email) needs **two separate PATs**, one per account.
- PAT dies with the user — this is the canonical "production job fails after employee X leaves" trap.
- PATs are required for the small set of API endpoints that need user context (e.g., creating or updating a specific user's credentials) — service tokens cannot perform those because they have no user identity.
- Deprecated **user API keys** (the predecessor of PATs) no longer work — migration is mandatory.

**Architect-level uniqueness — service tokens:**
- One token, many permission sets, each with its own project scope. This is how you build a least-privilege automation token (e.g., `Job Runner` on Project A + `Read-Only` on Project B).
- An **Account Admin** service token has full read+write across the entire account — dbt's docs flag this with a caution warning. Use sparingly and rotate aggressively.
- The **Semantic Layer Only** permission set is service-token-exclusive — it cannot be assigned to a user. Conversely, **Fusion Admin** is user-only and cannot be assigned to a service token.
- Service tokens persist independently of users — deactivating any individual leaves the token untouched.

**When PAT vs service token (per dbt docs):**
- Use a **service token** for: production CI/CD, dbt Cloud API automation, Semantic Layer integrations, Hightouch / Datafold / Census / Terraform / partner apps, anything that should outlive any individual.
- Use a **PAT** for: local dbt CLI operations, dev/staging scripts, ad-hoc API calls, and endpoints that require user context.

### Token Gotcha Q&A

**Q: A production CI job that worked for months suddenly returns 401. The employee who set it up just left the company. What happened, and what's the fix?**
A: The job was authenticated with the employee's **PAT**, which was revoked when the user was deactivated. **Fix**: replace it with a **service token** scoped to the minimum permission set needed (typically Job Admin + Read-Only on the relevant projects). PATs should never authenticate production automation.

**Q: Where do you configure permissions for a personal access token?**
A: **You don't.** PATs inherit the user's license + group memberships. To narrow a PAT's effective permissions, you must change the user's groups or license — which also affects the human. This is the architectural reason to prefer service tokens for any non-trivial scope: service tokens have explicit, narrowable permission sets independent of any user.

**Q: A user has access to two dbt Cloud accounts using the same email address. Is one PAT sufficient for both?**
A: No. PATs are **account-specific** — a separate PAT must be created per account, even when the user's email is the same.

**Q: Which token type can be assigned multiple permission sets, each scoped to a different project?**
A: **Service tokens only.** A single service token can carry, e.g., `Job Admin` on Project A + `Read-Only` on Project B. PATs have no per-project scoping mechanism — they always operate at the user's full permission level.

**Q: A Developer-licensed user attempts to create a service token from Account Settings → Service Tokens but doesn't see the option. Why?**
A: Service token creation requires **Account Admin** permission. The user's license type doesn't matter — the action is gated by permission set, not license. Either grant the user Account Admin (likely overkill) or have an Account Admin create the token on their behalf.

**Q: A team built a service token in 2022 that's still working but their docs recommend rotating it. Why?**
A: Service tokens issued **before July 18, 2023** use an older format. dbt recommends rotating high-frequency tokens to the new format for performance and latency improvements. They still work, but the new-format tokens are more efficient.

**Q: An admin needs an integration that creates and updates a user's profile credentials. They configure it with an Account Admin service token but the API rejects the request. Why?**
A: Endpoints that operate **on a specific user's account** require user-context authentication — i.e., a **PAT** for that user. Service tokens have no user identity and cannot satisfy these endpoints. This is one of the few cases where PATs are required.

**SSO (Enterprise only)**
- Mandatory for all non-admin users when enabled
- **JIT provisioning**: account auto-created on first SSO login
- Re-authentication every **24 hours**
- **SCIM** (Okta and Microsoft Entra ID only): automates user + group provisioning/deprovisioning from IdP
- Admins retain password access by default even with SSO enforced (can be explicitly restricted)

**SSO setup with Okta — full step-by-step (per dbt docs)**

Tier requirement: Enterprise / Enterprise+. Requires Okta admin and dbt Account Admin (or Security Admin) access.

*Okta side:*
1. In the **Okta Admin dashboard**, create a new app:
   - Platform: **Web**
   - Sign-on method: **SAML 2.0**
2. **General Settings**: App name `dbt`, logo optional.
3. **SAML Settings** — uses your dbt **login URL slug** (auto-generated, alphanumeric+dashes, e.g. `dbt-labs-afk123`):
   - **Single Sign On URL**: `https://YOUR_AUTH0_URI/login/callback?connection=<login-slug>`
   - **Audience URI (SP Entity ID)**: `urn:auth0:<YOUR_AUTH0_ENTITYID>:<login-slug>`
   - **Relay State**: `<login-slug>`
   - **Name ID format**: Unspecified
   - **Application username**: Custom → `user.getInternalProperty("id")` for SSO-only setups; **switch to Email** if you intend to enable SCIM (SCIM requires email-format usernames)
   - **Update username on**: Create and update
4. **Attribute Statements** (user attributes):
   - `email` / Unspecified / `user.email`
   - `first_name` / Unspecified / `user.firstName`
   - `last_name` / Unspecified / `user.lastName`
5. **Group Attribute Statements**:
   - Name: `groups`, Format: Unspecified, Filter: `Matches regex` → `.*`
   - Use a more restrictive filter (e.g. `Starts with: DBT_CLOUD_`) if your org has many groups — **Okta only returns 100 groups per user**
6. Finish: select "I'm an Okta customer adding an internal app" → "This is an internal app".
7. Click **View Setup Instructions** — copy: Identity Provider SSO URL, Identity Provider Issuer, X.509 Certificate.

*dbt Cloud side:*
1. Navigate to **Account Settings → Enterprise → Single Sign On** → **Edit**.
2. Fill in:
   - **Log in with**: Okta
   - **Identity Provider SSO URL**: from Okta
   - **Identity Provider Issuer**: from Okta
   - **X.509 Certificate**: from Okta
3. **Save**.

*Login URL for end users:* `https://YOUR_ACCESS_URL/enterprise-login/<login-slug>` (region-specific access URL + the slug used in Okta).

*Supported flows:* IdP-initiated SSO, SP-initiated SSO, Just-in-Time provisioning.

*Architect-level gotchas:*
- **Cert expiry is manual** — Okta admin must regenerate the X.509 cert before expiry; there's no auto-renewal. An expired cert breaks SSO entirely.
- **SCIM-vs-SSO username conflict**: SSO-only setups can use `user.getInternalProperty("id")` for username, but SCIM requires Email format. Pick the right value upfront if SCIM is in scope — switching later is disruptive.
- **IdP group names ↔ dbt group names must match exactly (case-sensitive)** — the most common cause of "SSO works but groups don't apply" tickets.
- **Admins keep password fallback** by default even when SSO is enforced (so a broken IdP doesn't lock everyone out). This can be explicitly restricted, but doing so removes the recovery path.
- **Other IdPs**: same flow, different setup pages — Microsoft Entra ID (formerly Azure AD), Google Workspace, and a generic SAML 2.0 guide. The dbt-side fields are the same; only the Okta-specific UI changes.

**RBAC Design**
- Permissions assigned at **group level only** — no individual permission assignments
- Most permissive group wins when user is in multiple groups
- License type caps effective permissions regardless of group (but only applies to Developer and Analyst — IT and Read-Only ignore groups entirely)

**Default Groups — Behavior Details**

| Group | Permissions | Mutable? | New users auto-added? |
|---|---|---|---|
| Owner | Full account admin (Account Admin) | **No — immutable** | No |
| Member | Broad access; restricts only billing/security features | Yes | **Yes** |
| Everyone | Customizable to org needs | Yes | **Yes** |

- New users are added to **both Member AND Everyone** by default — not just one
- Owner group permissions **cannot be changed** — immutable by design
- To restrict default new-user access: customize Member and Everyone permissions, or disable auto-add

**Adding/Removing Users — Plan Differences**
- Enterprise: one place (Account Settings → Users)
- Starter: two places — Account Settings seat count AND billing seat count separately

**Environment-Level Permissions**
- Cannot restrict access to a **specific** environment — only to environment **types** (Production, Staging, etc.)
- Cannot restrict to specific resources (e.g., jobs only within one environment)
- Write access to environments grants: create/edit/delete runs and jobs — but **NOT** environment creation or deletion
- Typical persona → environment access mapping:
  - Standard Developer: Dev + General
  - QA/Testing: Dev + Staging + General
  - Production Deployer: all environments
  - Data Analyst: read-only all

**RBAC Design — Additional Rules**
- IdP group names must match dbt group names **exactly** (case-sensitive) for SSO/SCIM sync to work
- Group membership syncs only **on user login** — not in real-time
- Disable **"Add all new users by default"** on the Everyone group for proper RBAC isolation
- Best practice: **1:1 IdP-to-dbt group mapping** for predictable sync behavior
- A group can grant environment write access (job/run ops) even if the permission set is read-only — these are independent controls

**IP Restrictions**
- Allowlist CIDR ranges for account access
- Service tokens respect IP restrictions
- Supplementary blocklist: deny specific IPs within an allowlisted CIDR

**Password Requirements** (when not using SSO)
- Minimum 9 characters; must include uppercase, lowercase, numeral, and special character

### Gotcha Q&A

**Q: A user is in an Admin group but can't edit anything. What's wrong?**
A: Their license type is Read-Only or IT. Licenses always override group permissions.

**Q: You lose a service token immediately after creating it. How do you recover it?**
A: You can't. Delete it, create a new one, update all integrations.

**Q: SSO is enforced. An admin gets locked out of the IdP. How do they access dbt?**
A: Admins retain password login by default even when SSO is enforced (unless explicitly restricted).

**Q: A service token API call returns 403. Credentials are valid. What's the most likely cause?**
A: The calling IP is not on the account's IP allowlist. Service tokens honor IP restrictions just like human logins.

**Q: You need read-only Catalog access for a contractor, scoped to one project. What's the right setup?**
A: Read-Only license + Viewer permission set scoped to that specific project.

**Q: Your team uses SCIM from Okta. A user is removed from the Okta group. What happens in dbt?**
A: SCIM automatically deprovisions them — their dbt account is deactivated.

**Q: Most permissive group wins — give a scenario where this creates an unintended security issue.**
A: A user is in both the "Everyone" group (Viewer) and "Data Team" group (Developer). They get Developer access account-wide — any guest added to "Everyone" inherits this if they're also a Data Team member, or vice versa if "Everyone" is accidentally elevated.

**Q: You configure SCIM with Okta but group assignments in dbt aren't reflecting the IdP groups. What's wrong?**
A: IdP group names must match dbt group names **exactly** (case-sensitive). Also, syncs only happen on user login — changes don't propagate until the user next authenticates.

**Q: A developer has read-only permissions but can still create and trigger job runs in the production environment. How?**
A: Environment write access (job/run operations) and permission set read-only are independent controls. A group can grant write access to environment types without granting model/project write permissions. Review the group's environment access settings.

**Q: You want new contractors to join the org but not automatically get access to any projects. What setting do you change?**
A: Disable **"Add all new users by default"** on the Everyone group. Without this, every new user is auto-added to Everyone and inherits its permissions.

**Q: A project-level Admin user tries to create a new dbt project but the option is greyed out. Why?**
A: Project-level Admin cannot create new projects — only **Account Admin** and **Project Creator** (account-level) can. Admin gives full control within existing projects only.

**Q: You assign Security Admin to a user so they can also run jobs during an incident. They still can't trigger jobs. Why?**
A: Security Admin has zero access to jobs, runs, or environments. It's purely for user/group/SSO/IP management. Assign Job Admin or Job Runner instead.

**Q: A Database Admin user wants to write a quick fix in the IDE. Can they?**
A: No. Database Admin manages data platform configs and Semantic Layer settings but has no IDE access. IDE requires Developer, Analyst, or Admin role.

**Q: What's the difference between Stakeholder and Viewer?**
A: Stakeholder is **project-level** — read-only for that project, audit log excludes sensitive info. Viewer is **account-level** — read-only across everything, audit log includes sensitive info.

**Q: You need a service token that can only query the Semantic Layer. Which permission set?**
A: Semantic Layer — it's the only permission set that's service-token exclusive and scoped purely to Semantic Layer queries.

**Q: You assign the Analyst role. What can that user do that a Developer cannot?**
A: Both have IDE access, but Analyst explicitly can run jobs in read-only mode. Developer has personal credential management. In practice they're similar — Analyst is designed for data consumers who occasionally need to run queries, not for model builders.

**Q: You assign an IT-licensed user to the Account Admin group so they can manage projects. They still can't create projects. Why?**
A: IT-licensed users do not inherit rights from any permission sets — group assignment has no effect. IT access is fixed: Security Admin + Billing Admin + edit Connections. To create projects, the user needs a Developer license.

**Q: A Read-Only user is added to the Developer group for a specific project. Can they now edit models in the IDE?**
A: No. Read-Only users do not inherit from permission sets regardless of group. Their access is identical to every other Read-Only user — view artifacts and the deploy section only.

**Q: A job has `dbt source freshness` as a checkbox and `dbt build` as a step. The freshness check fails (sources are stale). Does `dbt build` still run?**
A: Yes. The source freshness checkbox failure is isolated — `dbt build` still runs. If you need stale sources to block the build, add `dbt source freshness` as a **command step** instead of a checkbox.

**Q: `dbt docs generate` is configured as a checkbox. The docs generation fails. Does the job fail?**
A: Not necessarily — the job can still succeed if all steps after the docs generate step succeed. Checkbox step failures are isolated from the overall job outcome.

---

## TOPIC 6: Monitoring & Alerting

### Reference Notes

**Email Notifications**
- Configured per job; triggered on success/failure; simplest option; no plan restrictions

**Webhooks**
- Three event types:
  - `job.run.started` — fires at job start
  - `job.run.completed` — fires after completion AND artifact ingestion (delayed but data is ready)
  - `job.run.errored` — fires immediately on error (fastest, but API artifacts may not be available yet)
- **5-retry auto-disable**: After 5 consecutive delivery failures, webhook silently deactivates — no alert sent
- 10-second response window; must return 2xx; timeout = failure
- SHA256 payload signature in Authorization header for validation
- 30-day delivery history per webhook

### Gotcha Q&A

**Q: A webhook fires on `job.run.errored` and your handler queries the dbt API for run artifacts. The artifacts aren't there. Why?**
A: `job.run.errored` fires before artifact ingestion. Use `job.run.completed` when you need artifacts available at handler time.

**Q: A critical webhook hasn't fired for 3 days and no alert was sent. What happened?**
A: 5 consecutive delivery failures silently auto-disabled the webhook. Monitor webhook status proactively — dbt does not notify you when a webhook is disabled.

---

## TOPIC 7: dbt Mesh & Cross-Project References ⭐ DEEP

### Reference Notes

**Environment Resolution for Cross-Project Refs — MEMORIZE THIS**

| Consuming job's environment type | Resolves to producer's... |
|---|---|
| Development | Staging (if exists), else Production |
| Staging | Staging |
| Production | Production |

- Automatic — no explicit configuration required
- If the upstream project has **no Staging environment**, development jobs fall back to Production (data risk in production!)
- This is why Staging environments are architecturally mandatory in a Mesh deployment

**Project Dependencies vs Packages**

| | Packages | Project Dependencies |
|---|---|---|
| Plan required | Any | Enterprise+ |
| What's shared | Full source code | Public models via metadata service |
| Governance | Harder | Clean — narrower scope |
| Recommended for Mesh | No | Yes |

**Model Access Levels**
- `private`: same group only; not referenceable outside
- `protected` (default): same project or installed package
- `public`: any group, package, or project; cross-project refs require Enterprise+

**Model Contracts — Full YAML**
```yaml
models:
  - name: dim_customers
    config:
      contract:
        enforced: true       # opt-in; must be explicit
    columns:
      - name: customer_id
        data_type: int
        constraints:
          - type: not_null
      - name: customer_name
        data_type: string    # must declare ALL columns — partial not allowed
```

**Constraint Enforcement by Platform**

| Constraint | Postgres | Snowflake | BigQuery | Redshift | Databricks |
|---|---|---|---|---|---|
| not_null | ✅ enforced | ✅ enforced | ✅ enforced | ✅ enforced | ✅ enforced |
| primary_key | ✅ enforced | ⚠️ defined only | ⚠️ defined only | ⚠️ defined only | ⚠️ defined only |
| foreign_key | ✅ enforced | ⚠️ defined only | ⚠️ defined only | ⚠️ defined only | ⚠️ defined only |
| unique | ✅ enforced | ⚠️ defined only | ❌ unsupported | ⚠️ defined only | ⚠️ defined only |
| check | ✅ enforced | ❌ unsupported | ❌ unsupported | ❌ unsupported | ✅ enforced |

- Only **Postgres** enforces `primary_key`, `foreign_key`, `unique`; only **Postgres and Databricks** enforce `check`
- Incremental + contract: only `on_schema_change: append_new_columns` or `fail` — `sync_all_columns` not supported
- **BigQuery recursive CTEs** cannot use contracts
- **Ephemeral models** cannot have `access: public` (parsing error); can be `protected` or `private`
- Contracts enforce: removing columns, changing types, modifying constraints are all breaking changes

**Model Versions — Full YAML**
```yaml
models:
  - name: dim_customers
    latest_version: 2
    versions:
      - v: 2                         # default file: dim_customers_v2.sql
        columns:
          - include: all
            exclude: [country_name]
      - v: 1
        defined_in: dim_customers    # overrides file name → maps to dim_customers.sql
        config:
          alias: dim_customers       # overrides the database relation name
        deprecation_date: 2026-06-01
```
- Default file naming: `<model_name>_v<N>.sql`; use `defined_in` to override
- `deprecation_date`: triggers warning for consumers still pinned on that version
- Unpinned `ref('dim_customers')` → always resolves to `latest_version`
- Pinned: `ref('dim_customers', v=1)` or cross-project: `ref('project', 'dim_customers', v=1)`
- Never mutate a contracted public model in place — always create a new version

**Model Groups — YAML Syntax**
```yaml
# groups.yml (define the group)
groups:
  - name: finance
    owner:
      email: finance@company.com   # required: name OR email
    description: "Finance team data assets"

# models/schema.yml (assign model to group)
models:
  - name: revenue
    config:
      group: finance
      access: private    # only finance group members can ref this

# OR bulk assign in dbt_project.yml
models:
  marts:
    finance:
      +group: finance
```
- **Governance groups ≠ RBAC user groups** — completely orthogonal concepts:
  - Model groups = data ownership/team boundary
  - User groups = access permissions/who can do what
- Each model belongs to exactly **one** group
- Private model referenced outside its group → error: "is not allowed because the referenced node is private to [group]"

**`dependencies.yml` and Cross-Project Ref Syntax**
```yaml
# dependencies.yml (in consumer project root)
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
projects:
  - name: jaffle_finance   # CASE SENSITIVE — must match dbt_project.yml exactly
```
```sql
-- Cross-project ref
select * from {{ ref('jaffle_finance', 'monthly_revenue') }}
-- Pinned version
select * from {{ ref('jaffle_finance', 'dim_customers', v=1) }}
```

**Architect Rules**
- Node-level cyclic dependencies: NOT allowed
- Bidirectional project dependencies must be set up **stepwise**: producer runs first → consumer adds dependency and runs → producer optionally adds reverse dependency
- Multiple projects cannot share `sources:` directly — use a foundational project with public staging models
- `dbt build --select` does NOT trigger upstream project runs across project boundaries
- Public models visible org-wide in Catalog; protected/private require project access
- **Indirect dependency visibility**: Explorer/Catalog shows only DIRECTLY referenced public models; Studio IDE lineage shows full indirect upstream tree
- **Case sensitivity**: project names in `dependencies.yml` must exactly match `dbt_project.yml` — mismatches cause silent resolution failures

**Selecting and Orchestrating Across Mesh Projects**

Once an upstream project is added to a downstream project's `dependencies.yml`, dbt loads it into the downstream manifest under the **same namespace as installed dbt Hub packages**. This means the standard `package:` selector method works on Mesh upstream projects:

```bash
# In the DOWNSTREAM project, after adding `jaffle_finance` to dependencies.yml:
dbt ls    --select package:jaffle_finance         # list upstream public models pulled into manifest
dbt build --select package:jaffle_finance+        # build everything downstream of any upstream model
dbt build --select state:modified+ --exclude package:jaffle_finance  # CI: skip upstream nodes
dbt build --exclude package:jaffle_finance package:dbt_utils         # exclude all third-party + Mesh
dbt run   --select +package:jaffle_finance                            # local nodes that flow FROM upstream
```

- The package name is the upstream project's `name:` field in `dbt_project.yml` — **case-sensitive** match (same rule as `dependencies.yml`).
- Hub packages and Mesh upstream projects share the namespace — `--exclude package:jaffle_finance package:dbt_utils` (space = union) excludes both.
- Exclusion is evaluated **after** selection, so an upstream model picked up via `state:modified+` is still removed by `--exclude package:upstream`.

**Critical limitation: `--select` does NOT trigger an upstream build**

The `package:upstream_project` selector only **scopes the current invocation's manifest** — it filters which nodes are referenced/built **inside the downstream job**. dbt **never** crosses the project boundary to invoke a build in the upstream project. Cross-project orchestration is a job-level concern, not a selector concern:

| Goal | Mechanism |
|---|---|
| Build only my downstream code, treating upstream models as already-built | `--select state:modified+ --exclude package:upstream` (resolution against upstream's prod via metadata service) |
| Trigger a downstream build whenever upstream finishes | **dbt Cloud "Run when another job finishes"** chaining (Starter+ in general; cross-project Mesh chaining still requires Enterprise+ because of Mesh itself) — set in downstream Job → Triggers → Run when another job finishes → select parent project + upstream job + completion statuses |
| Coordinate upstream-then-downstream within one orchestrator | External orchestrator (Airflow / Prefect / dbt Cloud APIs) — there is no single dbt CLI invocation that builds both |
| Audit "what of mine depends on upstream" | `dbt ls --select +package:upstream` |
| Know which upstream public models the downstream actually consumes | `dbt ls --select package:upstream` |

**Common orchestration trap — `state:modified` is project-local**

`state:modified` compares the **current downstream manifest** against the **prior downstream manifest**. It does **not** detect upstream-side changes:

- An upstream column rename, contract update, or version bump does NOT show up as `state:modified` in the downstream project.
- The downstream only learns about upstream changes when (a) the metadata service refreshes the upstream's published manifest and (b) the downstream re-resolves refs at parse time.
- To catch upstream contract changes that affect downstream models, the **upstream's** CI must use `state:modified.contract` and produce artifacts the downstream defers against.
- `source_status:fresher+` does **not** flag upstream public models — those are consumed via `ref()`, not `source()`. Use chained jobs ("Run after job") to trigger downstream when upstream rebuilds, not freshness selectors.

**Common patterns**

```bash
# Downstream Slim CI — build only my changed nodes, treat upstream as immutable, defer to prod
dbt build \
  --select state:modified+ \
  --exclude package:jaffle_finance \
  --defer --state ./prod-artifacts

# Downstream impact analysis — what of MY code depends on the upstream?
dbt ls --select +package:jaffle_finance --resource-type model

# Smoke test only the bridge layer between upstream and downstream
dbt build --select package:jaffle_finance+1   # 1-hop downstream of any upstream model
```

**How to Recognize dbt Mesh in the Lineage Graph (Explorer/Catalog)**
- **Project boundary nodes**: Upstream projects appear as distinct labeled project nodes — not just individual models. You see a project-level grouping separate from your own project's DAG.
- **Cross-project edges**: Lineage edges cross project boundaries; the upstream model is labeled with its source project name (e.g., `jaffle_finance.monthly_revenue`)
- **Public model badges**: Models shared via cross-project refs show their `public` access designation in the graph — private/protected models from other projects are NOT visible
- **Multi-project DAG view**: Explorer shows a multi-namespace graph spanning >1 project; a single-project setup only ever shows one project's models
- **"Find public models" in Catalog**: dbt Catalog has a dedicated view listing public models from all projects — only present when Mesh is configured
- **Contrast with single-project**: In a non-Mesh setup, all lineage is within one project namespace; no project boundary nodes appear, no cross-project edges exist

### Gotcha Q&A

**Q: How can you tell from the lineage graph in dbt Explorer/Catalog that a project is part of a dbt Mesh?**
A: Three visual indicators: (1) **project boundary nodes** — upstream projects appear as distinct labeled project groupings, not just flat model nodes; (2) **cross-project edges** — lineage edges cross project namespaces with the upstream model labeled by its source project; (3) **public model badges** — models shared via cross-project ref show their `public` access designation. In a single-project setup, none of these appear — all nodes belong to one namespace.

**Q: An upstream project has only a Production environment. A developer's IDE job can't resolve a cross-project ref. Why?**
A: Development jobs resolve to the upstream's Staging environment first. If none exists, they fall back to Production — but dev credentials may not have Production access. Fix: add a Staging environment to the upstream project.

**Q: You set `access: public` on a model but a downstream team in another project still can't ref it. What's missing?**
A: Two things required: **Enterprise+ plan** AND `project_dependencies` configured in the downstream project's `dependencies.yml`. `access: public` alone is insufficient.

**Q: A contract-enforced public model needs to remove a column. How do you handle this without breaking downstream consumers?**
A: Create a new version (`_v2`), bump `latest_version`, set a `deprecation_date` on v1, notify consumers to migrate. Never modify a contracted public model's structure directly.

**Q: Can you enforce a model contract on a Python model?**
A: No. Contracts only work on SQL materializations. The logic must be reimplemented as a SQL model if governance is required.

**Q: Your Mesh has ProjectA and ProjectB both depending on ProjectC. ProjectA needs a model from ProjectB. How should this be structured?**
A: Route the shared model through ProjectC (the foundational project) — ProjectB exposes it as public there. Avoid lateral A↔B dependencies, which risk circular references.

**Q: An upstream public model's column type changes without a contract. When does the downstream project break?**
A: Silently — the downstream project breaks only when it next parses and runs against the new schema. This is why contracts on public models are critical: without one, breaking changes are undetected until runtime.

**Q: You want to use `check` constraints on a Snowflake model's contract. Will it work?**
A: No. Snowflake does not support `check` constraints in dbt contracts. Only `not_null` is enforced on Snowflake; `primary_key` and `foreign_key` are documented but not enforced.

**Q: You add `access: public` to an ephemeral model. What happens?**
A: dbt throws a parsing error. Ephemeral models cannot be public. They can be `protected` or `private` only.

**Q: You set up a bidirectional dependency between ProjectA and ProjectB simultaneously. Both fail to resolve. Why?**
A: Cross-project dependencies must be set up stepwise. The producer must run first to generate its manifest, then the consumer adds the dependency and runs. Setting both up at the same time creates a bootstrap chicken-and-egg problem.

**Q: A governance group named `finance` exists in dbt. A user in the "Finance" RBAC user group tries to reference a private model in the `finance` governance group. Can they?**
A: Not automatically — governance groups and RBAC user groups are completely separate concepts. Model group membership governs which models can reference private assets. User group membership governs UI/job access permissions. They don't interact.

---

## TOPIC 8: dbt Catalog

### Reference Notes

- **Catalog vs dbt Docs**: Docs = static site, all plans; Catalog = dynamic real-time metadata, Starter+
- Catalog reflects **production environment** only by default — dev/staging models don't appear
- Cross-project lineage: Enterprise+; shows multi-project DAG including public model references
- Column-level lineage: Enterprise+ only; **SQL models only** — Python models not supported
- **Data health signals**: Healthy / Caution / Degraded — driven by test results and source freshness
- **Lenses**: DAG overlays for materialization type, test status, query volume, cost — **one attribute at a time**; switch lenses on the same lineage graph to read the intersection visually (no combined-overlay view)
- **Model query history**: consumption tracking — use for optimization prioritization and deprecation impact assessment
- Non-dbt warehouse assets can be ingested for complete lineage

**Model Query History — Full Detail**
- **Plan required**: Enterprise or higher — not available on Starter
- **What it tracks**: SELECT queries against a model by downstream users/tools; **excludes** dbt model builds and test executions — consumption only
- **How to enable**: Orchestration → Environments → select Production environment → Settings → scroll to Query History → click "Test Permissions" → check "Enable query history" → Save
- **Four places to view it**:
  1. **Performance charts** — "Most consumed models" under Project details
  2. **Lineage graph** — apply the **Lenses** overlay for query volume
  3. **Models list** — Resources section; sort by consumption column
  4. **Catalog overview** — consumption query count directly on model page
- **Use cases**: identify high-traffic models (prioritize optimization), assess downstream impact before deprecating a model, inform infrastructure spending decisions
- Permissions gate visibility: public models org-wide, protected/private require project access

**CI Jobs Do NOT Update Catalog**
- Only **deployment jobs** (scheduled or manual) in production or staging environments update Catalog metadata
- CI jobs are explicitly excluded — they don't reflect production state
- Common trap: relying on CI runs to keep Catalog fresh; it won't work

**Catalog Inactivity Purge**
- Environments with **no successful job run in 3+ months** are automatically purged from Catalog
- Must run at least one successful deployment job every 3 months to remain visible

**Production Job Designation (How to Configure)**
- Path: Account Settings (click account name in left sidebar) → select project → **Edit** → **Artifacts** section
- Select which job(s) generate documentation and source freshness artifacts
- Only **one job per project** should be designated — multiple jobs cause conflicting artifact states

**`dbt docs generate` — What It Creates**

| File | Contents |
|---|---|
| `manifest.json` | Model metadata, lineage graph, run results, node definitions |
| `catalog.json` | Column-level information introspected from the database |
| `sources.json` | Source definitions and freshness check results |

**Cost Insights (Enterprise+ / Fusion)**
- Requires: Fusion engine enabled + state-aware orchestration enabled
- Refresh lag: up to **24 hours** — not for real-time billing reconciliation
- Cost formulas: Snowflake = credits × price per credit; BigQuery = TiB processed × price (cached queries = $0); Databricks = proportional DBU allocation based on query runtime

### Gotcha Q&A

**Q: A model exists in dev but doesn't appear in Catalog. Why?**
A: Catalog reflects production only. Dev and staging models are not surfaced until they're in a production job run.

**Q: Column-level lineage is missing for a high-value Python model. Why?**
A: Column-level lineage only works for SQL models. Python model internals are opaque to dbt's lineage parser.

**Q: CI jobs are running successfully but the Catalog hasn't updated in days. Why?**
A: CI jobs do not update Catalog metadata. Only production or staging deployment jobs do. Ensure a scheduled deployment job with `dbt docs generate` is running.

**Q: A project disappears from Catalog after a quiet period. What happened?**
A: Environments with no successful job run in 3+ months are automatically purged. Schedule a lightweight job (even just `dbt compile`) to run at least quarterly.

**Q: You designate two jobs to generate artifacts for the same project. What's the risk?**
A: The jobs will overwrite each other's artifacts, causing inconsistent Catalog state. Only one job per project should be designated for artifact generation.

**Q: What does `catalog.json` contain that `manifest.json` doesn't?**
A: `catalog.json` contains column-level information introspected directly from the database (column names, types, row counts). `manifest.json` contains node definitions, lineage, and model metadata from the dbt project itself.

---

## TOPIC 9: Hooks & Operations

### Reference Notes

**Hook Types — Scope & Configuration**

| Hook | Scope | Where Configured | Runs Per |
|---|---|---|---|
| `pre-hook` | Model, Seed, Snapshot | `dbt_project.yml`, `config()` block, YAML property file | Each resource |
| `post-hook` | Model, Seed, Snapshot | `dbt_project.yml`, `config()` block, YAML property file | Each resource |
| `on-run-start` | Project only | `dbt_project.yml` only | Each dbt command |
| `on-run-end` | Project only | `dbt_project.yml` only | Each dbt command |

- `on-run-start` / `on-run-end` fire once per dbt command (`dbt run`, `dbt build`, `dbt test`, `dbt seed`, `dbt snapshot`, `dbt compile`, `dbt docs generate`) — not per model
- `on-run-start` / `on-run-end` **cannot** be set in model config blocks or YAML property files — `dbt_project.yml` only
- Seeds support hooks via `dbt_project.yml` or YAML property files only — no in-file `config()` block (seeds are CSV files)

**Transaction Behavior — CRITICAL**

- By default, `pre-hook` and `post-hook` run **inside** the same transaction as the model build
- If model creation **fails**: post-hook **does not run** (transaction is rolled back before post-hook executes)
- If a post-hook **fails**: the whole transaction rolls back — including the model creation
- To run a hook **outside** the transaction (so it persists even on model failure), use dictionary syntax:

```yaml
post_hook:
  - sql: "INSERT INTO audit_log VALUES ({{ this }}, current_timestamp)"
    transaction: false
```

**Execution Order — Multiple Hooks**

When hooks are defined at multiple scopes, all execute — they **do not override each other**:
1. Package-level hooks run first
2. `dbt_project.yml` project-level hooks
3. Model `config()` block / YAML property file hooks
4. Within the same scope: hooks execute in definition order (top to bottom)

If 3 post-hooks are in `dbt_project.yml` and 2 in a model's `config()` block, all 5 execute.

**Context Variables Available in Hooks**

| Variable | Available In | Description |
|---|---|---|
| `{{ this }}` | `pre-hook`, `post-hook` | Relation object for the current model (database.schema.identifier) |
| `{{ model }}` | `pre-hook`, `post-hook` | The full dbt graph node for the current model |
| `{{ results }}` | `on-run-end` ONLY | List of result objects for every resource that ran |
| `{{ schemas }}` | `on-run-end` ONLY | List of schemas written to during the run |
| `{{ database_schemas }}` | `on-run-end` ONLY | List of (database, schema) tuples |

- Using `{{ results }}` in a `pre-hook` or `post-hook` returns `None` — **silent failure**, no error
- Each object in `results` has: `res.node.unique_id`, `res.status` (success/error/skipped), `res.message`

**`on-run-end` behavior on partial failure:**
- If the run partially fails (some models succeed, some fail), `on-run-end` **still executes**
- `results` will contain result objects for all resources including failures — use `res.status` to filter

**Calling Macros from Hooks**

Hooks can call macros. If the macro uses runtime context (e.g., `this`, model configs), wrap the call with an extra Jinja layer:

```yaml
post_hook: "{{ my_grant_macro(this, 'reporter') }}"
```

**Common Use Cases**

| Use Case | Hook Type | Notes |
|---|---|---|
| GRANT permissions post-build | `post-hook` | Standard Snowflake pattern |
| Audit logging on every model | `post-hook` with `transaction: false` | Must be outside transaction to persist |
| Warehouse resume before run | `on-run-start` | Project-level, fires once |
| VACUUM / ANALYZE | `post-hook` with `transaction: false` | Redshift — must be outside transaction |
| Temp table cleanup | `post-hook` | Cleanup after model completes |
| Notify on run completion | `on-run-end` | Use `results` to report pass/fail counts |

---

### Operations (`dbt run-operation`)

- Executes a **macro directly** as a standalone command — no model materialization
- Does NOT become part of the DAG; not tied to any resource lifecycle
- Manual invocation only — not automatic like hooks
- Can be used as a command step in a dbt Cloud job (alongside `dbt run`, `dbt build`, etc.)

**Syntax:**
```bash
dbt run-operation <macro_name> --args '{key: value, key2: value2}'
```
Arguments are passed as a YAML dictionary and mapped to macro keyword arguments.

**Example macro definition:**
```sql
{% macro grant_select(role) %}
  GRANT SELECT ON ALL TABLES IN SCHEMA {{ target.schema }} TO ROLE {{ role }};
{% endmacro %}
```
```bash
dbt run-operation grant_select --args '{role: analyst}'
```

- The macro must use `run_query()` or a statement block to actually execute SQL — operations do not auto-execute SQL from a return value
- Transaction behavior is controlled within the macro logic itself

**Hooks vs. Operations — Decision Table**

| | Hooks | Operations |
|---|---|---|
| Invocation | Automatic at lifecycle points | Manual (`dbt run-operation`) |
| Part of DAG | Yes | No |
| Runs per | Resource or command | Once per explicit call |
| Best for | Routine automated tasks (grants, audit) | Ad-hoc tasks (backfills, one-time grants) |
| Fails if model fails | post-hook skipped; on-run-end still fires | N/A |

---

### Gotcha Q&A

**Q: A post-hook inserts an audit log row. The model fails mid-execution. Does the audit row get inserted?**
A: No. By default, post-hooks run inside the model's transaction. If the model fails, the transaction rolls back and the post-hook never executes. Fix: add `transaction: false` to the hook definition so it runs outside the transaction.

**Q: A team defines 2 post-hooks in `dbt_project.yml` and 2 more in a model's `config()` block. How many post-hooks execute?**
A: All 4. Hooks at different scopes accumulate — model-level hooks do not override project-level hooks. Execution order: project-level hooks first, then model-level hooks.

**Q: You use `{{ results }}` in a `post-hook` to log model outcomes. It always returns None. Why?**
A: `{{ results }}` is only available in `on-run-end` hooks. It returns None in `pre-hook` and `post-hook` — silently, with no error.

**Q: Your `on-run-end` hook sends a Slack notification. Three models in the run fail. Does the hook still fire?**
A: Yes. `on-run-end` executes after the run completes regardless of partial failures. The `results` variable will contain entries for all resources including failed ones — filter on `res.status == 'error'` to report failures.

**Q: You need to run a VACUUM command after each model build on Redshift. Using a standard post-hook, it fails. Why?**
A: `VACUUM` on Redshift cannot run inside a transaction. The post-hook runs inside the model's transaction by default. Fix: use `transaction: false` in the hook definition.

**Q: When is `dbt run-operation` the right choice over a post-hook?**
A: When the task is ad-hoc (one-time grant, backfill, maintenance) and not tied to a specific model's lifecycle. Use hooks for automated tasks that should run every time a model or run executes. Operations are also preferable when you need to run the same macro across multiple models from a single command step.

**Q: A seed file has a post-hook to grant SELECT after each seed load. Where must this be configured?**
A: In `dbt_project.yml` or a YAML property file — seeds do not support in-file `config()` blocks (they are CSV files, not SQL files).

---

## High-Yield: Top 10 Exam Topics

> Study these first if time is short.

1. **Cross-project env resolution table** — dev→staging/prod, staging→staging, prod→prod
2. **Deferral type trade-offs** — self-deferral vs prod deferral vs none; what breaks each
3. **License always overrides group permissions** — know specific failure scenarios
4. **CI job behavior** — no run slots, temp schema lifecycle, smart cancellation for same PR
5. **Command ordering** — `dbt build` before `dbt sl validate`; checkbox vs step for source freshness
6. **Governance trifecta** — model access + contracts + versions and how they interact
7. **Service token gotchas** — one-time visibility, IP restrictions, rotation pattern
8. **Webhook reliability** — 5-failure silent auto-disable; `errored` vs `completed` timing
9. **Manifest state loss** — same `--state` and `--target-path` = non-idempotent deferral
10. **Enterprise+ feature gate** — cross-project refs, project dependencies, column lineage, Advanced CI

---

## Plan Tier Quick Reference

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|---|---|---|---|
| Job chaining | No | Yes | Yes | Yes |
| Cross-project refs | No | No | Yes | Yes |
| Project dependencies | No | No | No | Yes |
| Advanced CI (compare) | No | No | Yes | Yes |
| SSO / SCIM | No | No | Yes | Yes |
| Column-level lineage | No | No | No | Yes |
| Multi-project lineage | No | No | No | Yes |
| PrivateLink | No | No | Yes | Yes |
| Azure DevOps native | No | No | Yes | Yes |
| Scheduling min interval | 10 min | — | — | — |