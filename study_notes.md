# dbt Architect Certification — Study Notes

> Audience: Daily dbt platform user. Architect-level gotchas only.
> Format: Reference notes + Gotcha Q&A per topic. Study the **High-Yield** section at the bottom first if time is short.

**Where things are**

| Exam topic | Section here | Practice set |
|---|---|---|
| 1 Warehouse connections | Topic 1 | `q01` |
| 2 Git connections | Topic 2 | `q02` |
| 3 Environments | Topic 3, 3b (schemas) | `q03` |
| 4 Jobs | Topic 4 | `q04` |
| 5 Security and licenses | Topic 5 | `q06` |
| 6 Monitoring and alerting | Topic 6 | `q07` |
| 7 dbt Mesh | Topic 7 (includes model governance) | `q08`, `q12` (Topic 11) |
| 8 Catalog | Topic 8 | `q09` |
| Extra: Blue/green and `dbt clone` | inside Topic 4 | `q05` (Topic 4c) |
| Extra: dbt commands and node selection | inside Topic 4 | `q11` (Topic 10) |
| Extra: Hooks and operations | Topic 9 | `q10` (Topic 9) |

---

## TOPIC 1: Warehouse Connections

### Reference Notes

**Connections**
- Connections are **account-level** (Account settings → Connections). Reuse the same one across projects.
- A connection reaches a project **through an environment**. A project with 2 environments can use 1 or 2 connections (e.g. separate prod from non-prod).
- One environment = one connection. A single job can't write to two warehouses.
- Test: use **Test connection** in the setup flow. Most common Snowflake failure: `snowflakecomputing.com` left in the Account field.

**IP allowlisting**
- dbt connects from the IPs on the Regions & IP addresses page. Allow them in your firewall and database grants.
- The docs also say those IPs **can change occasionally** and recommend dbt platform **hostnames** (e.g. `abc123.us1.dbt.com`) as the stable reference. The docs don't reconcile the two. "What stays stable?" → hostnames.
- Multi-tenant: IPs / CIDR ranges listed per region. Single-tenant / Virtual Private: ask Support for your IPs, use your vanity URL.
- Find your IPs: Project Settings → Connection → Settings.
- Allowing the IPs only opens the warehouse connection. Using the dbt API needs `cloud.getdbt.com` allowed.

**Private connectivity (PrivateLink)**
- **Enterprise+ and Virtual Private** plans.
- dbt ↔ warehouse without crossing the public internet.
- dbt and the warehouse must be on the **same cloud** (AWS with AWS, etc.).
- Env vars aren't supported for private endpoint settings. Use **extended attributes**.
- With ingress PrivateLink or IP allowlisting, CI hooks may be unavailable and CI jobs can fail silently.

**OAuth overview**
- OAuth is for **development** (each developer signs in). Deployment jobs use key pair (Snowflake) or service JSON / Workload Identity Federation (BigQuery).
- Snowflake OAuth and BigQuery OAuth: **Enterprise / Enterprise+**.
- Support (dbt v2 table): Snowflake and BigQuery = warehouse OAuth ✅ + external OAuth ✅. Databricks = warehouse OAuth ✅, external ❌. Redshift = none. Service-to-service OAuth = ❌ everywhere.
- **Client ID + Secret** go on the connection: Account settings → Connections → the connection.
- Every developer must then authenticate in their own **Credentials** before using the IDE.

**Snowflake**
- Account: `db5261993` or `db5261993.east-us-2.azure`. ❌ `db5261993.eu-central-1.snowflakecomputing.com` (test fails).
- Role is mandatory. Database and Warehouse are set on the connection.
- Custom domain: extended attribute `host: https://custom_domain.com`. Can conflict with Snowflake OAuth over PrivateLink → use External OAuth.
- **Auth:**
  - Key pair = default for new credentials (dev + deploy).
  - New username/password credentials **can't be created**. Existing ones can't be saved until switched to key pair or OAuth.
  - Existing username/password + MFA: dev and deploy (`authenticator: username_password_mfa` in the dev environment).
  - Snowflake OAuth: dev only, Enterprise.
- **Key pair:** public key on the Snowflake user (`alter user x set rsa_public_key='...'`). Private key + passphrase in dbt Credentials, **with the BEGIN/END lines**. The private key can't come from an env var.
- dbt v2 (Fusion): PKCS#8 + AES-256. No 3DES, no headerless keys.
- **"Could not deserialize key data"** = bad paste (missing dashes or BEGIN/END lines). Check the key in a text editor.
- **"JWT token is invalid"** = no answer from Snowflake within 60 seconds, or wrong public key. dbt needs to retry; check the public key.
- Minimum grants: `USAGE` on warehouse, database, schema; `SELECT`; `CREATE TABLE`, `CREATE VIEW` on schema; `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`. Plus metadata access (`USAGE` on INFORMATION_SCHEMA, `DESCRIBE TABLE`, `SHOW OBJECTS`). `CREATE SCHEMA` / `CREATE DATABASE` only if dbt creates them.

**Snowflake OAuth setup**
1. Copy the **Redirect URI** from dbt (project → Development connection → OAuth method Snowflake SSO).
2. In Snowflake (ACCOUNTADMIN or a role with global `CREATE INTEGRATION`): `CREATE SECURITY INTEGRATION ... TYPE = OAUTH ... OAUTH_REDIRECT_URI = '<URI>'`. Add `OAUTH_USE_SECONDARY_ROLES = 'IMPLICIT'` if you use secondary roles.
3. Get the client ID and secret with `system$show_oauth_client_secrets('DBT_CLOUD')`.
4. dbt: Account settings → Connections → edit the connection → enter them → Save.
5. Users: Credentials → **Connect to Snowflake Account**.

**BigQuery**
- Dev: Service JSON or OAuth (Enterprise). Deployment: Service JSON or Workload Identity Federation (Enterprise, Entra ID is the only IdP).
- Keyfile: upload the JSON, or give it as a base64 string.
- Pick the **BigQuery** schema option for new connections. "BigQuery (Legacy)" is deprecated.
- **OAuth setup:**
  1. Google Cloud: APIs & Services → Credentials → Create OAuth client ID → Web application. Paste the **Redirect URI** copied from dbt (connection → Development OAuth section).
  2. Copy the client ID + secret into dbt: Account settings → Connections → the connection → **OAuth 2.0 Settings** (token URI default `https://oauth2.googleapis.com/token`).
  3. Users: Account settings → Credentials → project → Authentication Method = **Native OAuth** → **Connect to BigQuery**.
- `403 Account restricted`? A Google Workspace admin must mark the client ID **Trusted**.

**Databricks**
- Use **`dbt-databricks`**. Connecting via `dbt-spark` is deprecated.
- Required: **Server Hostname**, **HTTP Path**. Catalog is optional (Unity Catalog).
- Unity Catalog = dbt 1.1+. Python models = dbt 1.3+.
- Unity Catalog privileges: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `MODIFY` (+ `CREATE SCHEMA` if dbt creates schemas).
- Hive metastore: `USAGE`, `SELECT`, `CREATE`, `MODIFY`.

**Managed repository**
- A way to trial dbt without your own repo. You **can't use Git features like pull requests**. dbt Labs **recommends against** using it in production.
- You can **export** it any time: project settings → repo link → Deploy key → Download repository (needs write access to Git repositories).

### Gotcha Q&A

**Q: A new Snowflake connection test fails. The Account field is `db5261993.snowflakecomputing.com`. Why?**
A: The Account value still includes `snowflakecomputing.com`. Use `db5261993` or `db5261993.east-us-2.azure`.

**Q: You get `JWT token is invalid`. Why?**
A: Snowflake didn't answer within 60 seconds, or the public key was entered wrong. Retry and check the public key.

**Q: You get "Could not deserialize key data". Why?**
A: The private key was pasted wrong: missing dashes or BEGIN/END lines. Check it in a text editor.

**Q: Can you create new Snowflake credentials with username and password?**
A: No. Key pair is the default. Existing password credentials must switch to key pair or OAuth before they can be saved.

**Q: Can a production job use Snowflake OAuth?**
A: No. Snowflake OAuth is development only (Enterprise). Deployment uses key pair.

**Q: Where do the BigQuery OAuth Client ID and Secret go?**
A: Account settings → Connections → the connection → OAuth 2.0 Settings. Developers then connect under Credentials → Native OAuth.

**Q: A team allowlists dbt IPs and worries they'll change. What do the docs recommend?**
A: Use dbt platform hostnames as the stable reference. Single-tenant: ask Support for IPs.

**Q: Which plans get private connectivity (PrivateLink)?**
A: Enterprise+ and Virtual Private. dbt and the warehouse must be on the same cloud.

**Q: A Databricks project uses `dbt-spark`. What changes?**
A: Move to `dbt-databricks`. Unity Catalog needs dbt 1.1+, Python models 1.3+.

**Q: A team prototyped on a managed repo and is going to production. What now?**
A: Export it and move to your own Git host. dbt Labs recommends against managed repos in production, and you can't use pull requests.

**Q: How many connections can one project use?**
A: One per environment. A project with 2 environments can use 1 or 2 connections. A single job can't write to two warehouses.

---

## TOPIC 2: Git Connections

### Reference Notes

**Which provider gets which method**

| Provider | Native integration | Plan | Automated CI |
|---|---|---|---|
| GitHub | Yes (dbt GitHub App) | All plans | Yes |
| GitLab | Yes | All plans | Yes (but see GitLab Free below) |
| Azure DevOps | Yes | **Enterprise / Enterprise+ only** | Yes |
| Bitbucket, AWS CodeCommit | No | — | No — use git clone + Admin API |

- Azure DevOps on Starter/Developer: deploy key only. You can develop, but no automated CI.

**GitHub**
- The **GitHub org owner** installs the dbt GitHub App. That person also needs **Owner or Account Admin** in dbt.
- Native app lets you import repos in a few clicks, clone over **HTTPS** (not SSH), and trigger CI when a PR is opened.
- **Repo name is case-sensitive** and must match the URL exactly (`MyRepo`, not `myrepo`) — otherwise clone errors or job failures.
- Linking your personal GitHub profile: **required on Enterprise/Enterprise+** (the IDE checks each developer's read/write access). On Starter it's optional but recommended.
- GitHub Enterprise Cloud on a **`ghe.com`** domain: the shared dbt app can't reach it. Enterprise/Enterprise+ → register a **custom GitHub app** (private beta). Other plans → git URL.
- On-prem GitHub (GitHub Enterprise Server): same rule — custom GitHub app (private beta) on Enterprise/Enterprise+, git URL on other plans.
- **One GitHub app per dbt account**, not per project. Switching from the shared app to a custom app breaks every profile link — everyone has to relink.

**Git clone (deploy key)**
- Use it when the provider has no native integration (Bitbucket, AWS CodeCommit, Azure DevOps Server), or when you're on a plan that can't use the native one.
- The URL must be **SSH** (`git@github.com:org/repo.git`). dbt can't clone over HTTPS.
- **Each dbt project gets its own deploy key**, even if two projects use the same repo. The key needs **read and write** access.
- **No automated CI and no PR status updates.** For Bitbucket/CodeCommit you trigger CI with the **dbt Admin API** (Enterprise/Enterprise+ only). dbt will **not** auto-delete the temp CI schema for API-triggered runs, because that cleanup depends on Git provider webhooks (native integrations only).
- AWS CodeCommit extras: IAM user with `AWSCodeCommitPowerUser`, dbt Support finishes the setup, and the default branch is `master` — set it as the custom branch.

**GitLab**
- OAuth app uses the **`api` scope**
- Repos must belong to a **GitLab group** — dbt will not read repos tied to a personal user account
- **Maintainer role** required to set up the connection
- Enterprise: admin creates a group-owned OAuth app → adds Application ID + Secret in Account settings → Integrations
- Developer/Starter: users connect their own account via Personal profile → Linked accounts
- When you connect a repo, dbt sets up a **webhook** (triggers CI jobs) and a **project access token** (sends job status back to GitLab).
- **GitLab Free**: MRs trigger CI jobs, but job status is **NOT reported back** to GitLab. Native CI needs a paid or self-hosted GitLab that supports **webhooks and project access tokens**.
- CI doesn't trigger at all? Check the webhook in GitLab (Settings → Webhooks): enabled, correct URL and secret.
- **Self-hosted GitLab** can only be connected on **Enterprise** plans (the redirect URL can only be customized there).

**Azure DevOps**
- Native integration is **Enterprise/Enterprise+ only**
- Azure DevOps **Server (on-prem)**: no native integration. Use git URL import.
- Recommended auth: **Service Principal** (Service User is legacy)
- Needs three admin teams: dbt, Azure Entra ID, and Azure DevOps
- PR status stuck on "pending"? Check the branch policy setting **"Reset status whenever there are new changes"** (under Status checks → Reset conditions). It can stop dbt from updating the status.

### Gotcha Q&A

**Q: You set up GitHub native integration but CI jobs aren't triggering on PRs. What do you check?**
A: Make sure the dbt GitHub App was installed by a GitHub org owner, and that the CI job has **Triggered by pull requests** on (draft PRs also need **Run on draft pull requests**). Linking personal profiles is about IDE/CLI read/write access, not CI triggers.

**Q: Your org uses GitHub Enterprise Cloud on a `ghe.com` domain and has the Enterprise plan. The dbt GitHub App can't connect. What now?**
A: The shared dbt app can't reach `ghe.com`. Register a custom GitHub app (private beta, Enterprise/Enterprise+) and use the native integration.

**Q: CI runs work on GitHub but an Azure DevOps repo on a Starter plan doesn't trigger CI. Why?**
A: Azure DevOps native integration is Enterprise-only. On Starter you can only use a deploy key, which gives you no automated CI (you can still develop).

**Q: A team uses Bitbucket and wants CI on their PRs. How?**
A: Bitbucket has no native integration. Connect with git clone + deploy key, then trigger CI jobs through the dbt Admin API (Enterprise/Enterprise+ only).

**Q: A user created a GitLab repo under their personal account and tried to connect it to dbt. Why won't it work?**
A: dbt will not read repos tied to a user. The repo must belong to a GitLab **group**.

**Q: You're on GitLab Free. CI runs succeed in dbt but developers see no status on their MRs. Why?**
A: On GitLab Free, MRs trigger CI but dbt can't report the job status back. Use a paid or self-hosted GitLab account that supports webhooks and project access tokens.

---

## TOPIC 3: Environments ⭐ DEEP

### Reference Notes

**Environment types (per project)**

| Type | Count | Used for |
|---|---|---|
| Development | 1 | Studio IDE / CLI settings |
| Production | 1 | Project "source of truth". Needed for Catalog and cross-project refs |
| Staging | 1 | Pre-prod. Optional, but changes how cross-project refs resolve (see below) |
| General | Any number | Other deployment work (testing, experiments) |

- Deleting an environment **deletes its jobs**. Move them first. Can't be undone.
- Custom branch: **dev** env = branch devs create branches from and open PRs against. **Deploy** env = branch **cloned** when the job runs (no merge).

**Connections, profiles and credentials**
- Deployment environments get their connection + credentials from a **connection profile**. Profiles are created at the **project** level and apply to **deployment environments only** (not dev).
- To change it: edit the environment → swap icon → Assign profile → Save.
- ⚠ Older study material says "an environment's connection can't be changed, create a new one". The current docs don't say that.
- Connection section in environment settings:
  - Snowflake: Role, Database, Warehouse
  - Databricks: Catalog (optional)
  - Postgres, Redshift, BigQuery, Spark: section not shown → values come from the project connection → override with **extended attributes**

**Snowflake credentials**
- **Key pair is the default** for new credentials (dev and deploy). New password credentials can't be created. Existing ones must move to key pair or OAuth before they can be saved.
- Snowflake OAuth: development only, Enterprise.
- Public key goes on the **Snowflake user** (`alter user x set rsa_public_key='...'`). Private key + passphrase go in the dbt **Credentials** page, with the BEGIN/END lines.
- The private key **can't come from an env var**.
- dbt v2 (Fusion): PKCS#8 with AES-256. No 3DES, no headerless keys.
- ⚠ Rotating the key via the Admin API is an exam objective, but the docs describe no procedure. Read the Admin API v3 credentials endpoints.

**Service tokens (service accounts)**
- Belong to the **account**, not a user. For system-level integrations that don't run on behalf of one person.
- Enterprise/Enterprise+: any permission set. Developer/Starter: Semantic Layer set only.
- Created by an account admin. Shown once. 403 = IP allowlist problem.

**Access control by environment**
- Admins give a **group** write access by environment **type** (not a single environment): Account settings → Groups & Licenses.
- Only these permission sets support it: Database admin, Git admin, Team admin, Analyst, Developer. Nothing selected = read-only.
- Developer defaults to **All environments**. Check it.
- Typical setup: lock Production, allow Development, Staging, General.

**Environment variables**
- Order, highest first: **job override / personal (IDE) override** > **environment** > **project default** > default argument in `env_var()`.
- There is **no account-level** scope.
- Names must start with `DBT_`, `DBT_ENV_SECRET_` or `DBT_ENV_CUSTOM_ENV_`.
- `DBT_ENV_SECRET_` values are scrubbed from logs and never shown in the UI or artifacts.
- No project default and no job value → compile error "Env var required but not provided".
- Can't be used in the Snowflake OAuth account/host field. Use extended attributes there.

**Extended attributes**
- A `profiles.yml` snippet. Deployment: set on the connection profile. Dev: on the dev environment.
- **Top-level keys only.** To change a sub-key, give the whole top-level key as a JSON block (e.g. all of BigQuery `keyfile_json`).
- Overrides environment-level values and env vars. Adds the key if it's missing.
- They **don't mask secrets**. Use `password: '{{ env_var('DBT_ENV_SECRET_PASSWORD') }}'`.
- Env vars used here must be **project-scoped**. Environment-scoped ones aren't available in connection tests.
- Not supported for SSH tunneling.

**Release tracks** (dbt v1)

| Track | What it is | Plans |
|---|---|---|
| Latest | Continuous release. **Default** | All |
| Compatible | Monthly, aligned with open source dbt v1 | Starter and up |
| Extended | The previous month's Compatible | Enterprise, Enterprise+ |
| Fallback | The previous month's Extended. Emergency rollback | Enterprise+ |

- dbt v2 (Fusion): Nightly, **Stable (default, weekly)**, Extended (Enterprise+), Fallback (Enterprise+, set in Account settings only).
- Set per environment. Admins can set the account default for new projects.
- The docs state no "support window" for any track.

**Deferral**
- Studio IDE: toggle **Defer to staging/production**. Needs the environment marked as Production and a **successful job run first**.
- Uses **staging if it exists, otherwise production**. Only one environment per run.
- Staging exists but never had a deploy job run → IDE defer **doesn't work**.
- Ref resolution with `--defer`: your own dev relation first. If it doesn't exist, the deferral environment (staging if it exists, otherwise production). `--favor-state` skips the dev check.
- CLI: defer is on by default. `--no-defer` turns it off. `defer-env-id` picks another environment.
- Job setting "Compare changes against": No deferral (default) / Environment (recommended) / This Job. CI jobs default to Production.
- Environment deferral = state from the **latest successful run in that environment**, from any job that updates artifacts there.

**Cross-project refs and Staging**

| Downstream environment | Resolves to upstream |
|---|---|
| Production | Production |
| Staging | Staging if it exists, else Production |
| Development | Staging if it exists, else Production |

- Upstream Staging exists → dbt uses it **right away**, with **no fail-over to Production**, even with zero successful Staging runs. Downstream refs then fail.
- Safe order: create the environment without marking it Staging → define a job → run it successfully → mark it Staging.
- Upstream needs: `access: public` models, and a Production environment with a successful job (it produces the `manifest.json`).
- Staging + deferral (dbt 1.11+): unbuilt upstream models and UDFs in project B resolve to project B's staging, not production.

### Gotcha Q&A

**Q: You override one nested key in extended attributes and it doesn't apply. Why?**
A: Only top-level keys are accepted. Give the whole top-level key as a JSON block.

**Q: Which environment variable wins: project `analytics`, environment `analytics_staging`, job `analytics_ci`?**
A: `analytics_ci`. Job > environment > project. No account level.

**Q: A dev IDE job resolves a cross-project ref. The upstream project has no Staging. Where does it resolve?**
A: Upstream **Production**.

**Q: The upstream project has Staging, but it never had a successful run. Does it fall back to Production?**
A: No. It uses Staging and the ref fails.

**Q: You add a Staging environment to the upstream project and downstream dev jobs break. Fix?**
A: Staging is used immediately. Next time: create it without marking Staging, run a job successfully, then mark it Staging. Now: run a successful deploy job in it.

**Q: A CI job compares changes against Production. Which run does it use?**
A: The latest successful run in Production, from any job that updates artifacts there. It targets the environment, not a job ID.

**Q: What happens to jobs when you delete an environment?**
A: They're deleted too. Move them first.

**Q: A team needs a deployment environment to use different credentials. How?**
A: Assign a different connection profile in the environment settings.

**Q: Where do the Snowflake key pair keys go?**
A: Public key on the Snowflake user. Private key + passphrase in dbt Credentials. Not in an env var.

**Q: Where do you put a secret used in extended attributes?**
A: A project-scoped `DBT_ENV_SECRET_...` env var, referenced with `env_var()`. Extended attributes don't mask secrets.

**Q: Max stability on dbt v1, Enterprise plan. Which release track?**
A: Extended (the previous month's Compatible). Latest is the default.

**Q: Developers should run jobs in Staging but not write to Production. What do you set?**
A: Environment-level permissions on their group: write access for Staging, not Production.

---

## TOPIC 3b: Schema Generation & Custom Schema Precedence ⭐ HIGH-YIELD

### Reference Notes

**What schema does a model land in?** The `generate_schema_name` macro decides.

**Default macro:**
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

| Target schema | `schema` config | Result |
|---|---|---|
| `analytics_prod` | none | `analytics_prod` |
| `analytics_prod` | `marketing` | `analytics_prod_marketing` |
| `alice_dev` | `marketing` | `alice_dev_marketing` |
| `dbt_cloud_pr_123_456` | `marketing` | `dbt_cloud_pr_123_456_marketing` |

**The custom schema is appended to the target schema, it does not replace it.**

**Why:** if you drop `default_schema` from the macro, developers who use the same custom schema overwrite each other's models.

**The docs' production override** (env-aware):
- `target.name == 'prod'` → use the custom schema (target schema if none)
- Anything else (dev, CI) → **custom schema ignored**, target schema used

| Environment | Target schema | `schema` config | Result |
|---|---|---|---|
| prod | `analytics_prod` | `marketing` | `marketing` |
| dev | `alice_dev` | `marketing` | `alice_dev` |
| CI | `dbt_cloud_pr_123_456` | `marketing` | `dbt_cloud_pr_123_456` |

- dbt ships this as `generate_schema_name_for_env`. It's **off by default**. To turn it on:
```jinja
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ generate_schema_name_for_env(custom_schema_name, node) }}
{%- endmacro %}
```
- Put the override in `macros/generate_schema_name.sql`. dbt **ignores** `generate_schema_name` macros from installed packages.
- Set **Target name = `prod`** on the production job. Docs suggest `dev`, `ci`, `prod`.

**Target name**
- Job: Target Name field in job settings. IDE: Account settings → Credentials → target name.
- It's a string your macro reads. It is **not** the environment type.

**CI schemas**
- PR schema looks like `dbt_cloud_pr_<job_id>_<pr_id>` and is dropped when the PR merges or closes.
- If you override `generate_schema_name`, the result must **keep the `dbt_cloud_pr_` prefix**. ✅ `dbt_cloud_pr_123_456_marketing` ❌ `marketing`. Otherwise the temp schemas are **not dropped**.

### Gotcha Q&A

**Q: Dev target schema is `dbt_user_1`, model has `schema: 'core'`, default macro. Where does it land?**
A: `dbt_user_1_core`.

**Q: A team wants `schema: 'core'` to land in `core` in production. What do they do?**
A: Override `generate_schema_name` in `macros/`. When `target.name == 'prod'` return the custom schema. Set Target name = `prod` on the production job.

**Q: Someone makes the macro always return just the custom schema. What breaks in dev?**
A: Developers with the same `schema` config write to the same schema and overwrite each other.

**Q: PR schemas aren't dropped after merge. Why?**
A: A custom `generate_schema_name` doesn't keep the `dbt_cloud_pr_` prefix.

**Q: The production job has Target name `prod` and the macro returns the custom schema for `prod`. Model has `schema: core`. Where does it land?**
A: `core`.

**Q: Alice (`dbt_alice`) and Bob (`dbt_bob`) both use `schema: 'finance'`. Do they collide?**
A: No. `dbt_alice_finance` and `dbt_bob_finance`.

---

## TOPIC 4: Jobs & CI/CD ⭐ DEEP

### Reference Notes

**Job types**
- **Deploy job**: runs on a schedule, after another job, by API, or manually. Uses a **run slot**.
- **CI job**: runs when a PR is opened or gets a new commit. **No run slot**, never blocks production runs.
- **Merge job**: runs on merge. **Does use a run slot**. One run at a time, newest queued run wins.
- CI default command: `dbt build --select state:modified+`.

**Commands**
- Run in order. If a step fails, the next ones **don't run** and the job is **Error**.
- At least **one dbt command** is required. `dbt deps` is built in.
- `dbt lint` can't go in deploy jobs. CI has a linting toggle (SQLFluff on v1, `dbt lint` on v2). Linting: Starter, Enterprise, Enterprise+. Stop or continue on error.
- A selector that matches nothing doesn't fail the job.
- `dbt sl validate`: the docs list `dbt build --select state:modified+` first, then `dbt sl validate --select state:modified+`.
- **`dbt build` order = DAG order.** No fixed order by resource type.
  - Unit tests run **before** the model is built. Data tests run after.
  - A failing test on an upstream node makes downstream nodes **SKIP**. Set severity `warn` to avoid it. A failing model also skips its downstream models, unless the model sets `on_error: continue`.
  - `--full-refresh`: applies to every selected type that supports it. **Snapshots ignore it** (v2.0+).
  - `--empty`: refs and sources return zero rows. Use `.render()` to force a relation.

**Source freshness**
- **Checkbox**: runs `dbt source freshness` **first**. If it fails, later steps still run and the job can still succeed.
- **Command step**: if it fails, the steps after it **don't run**.
- Want stale data to block the build? Run it first as a step. Otherwise last, or in a separate job.
- `dbt build` does **not** run freshness.
- A job with only the checkbox needs a placeholder command like `dbt compile`.
- Check at least **2× as often** as your tightest SLA (1 hour SLA → every 30 min).
- Snowflake freshness uses `LAST_ALTERED`.

**Generating docs / Catalog**
- dbt v2 jobs: no docs command needed. Every run refreshes Catalog metadata.
- Catalog updates after each job run in a **production or staging** deployment environment.
- v1: **Generate docs on run** checkbox. Not applicable to dbt v2 jobs. When it runs relative to your commands isn't stated in the docs.
- Legacy docs site: Project → Edit → **Artifacts** → pick the job. Use **one** production job per project.

**Deferral (job setting "Compare changes against")**
- Deploy job default: **No deferral**. CI job default: **Production**.
- **Environment** (recommended): state from the **latest successful run** in that environment, from **any** job that updates artifacts there.
- **This Job** (self-deferral, older): that job's own last successful run.
- CI state comparison needs a deferred environment selected.
- ⚠ The docs don't say what happens on a first run with no prior manifest.

**Scheduling**
- **Intervals**: every N hours from midnight UTC, same gap each time. **Specific hours**: comma-separated UTC hours (whole hours only). **Cron**: exact times (`5 4 * * *` = 4:05 UTC; `L` and `MON#1` work).
- Everything is **UTC**. No daylight saving adjustment.
- Developer plan: minimum **10 minutes**. Starter and up: no limit.
- The same job runs **serially**. If runs take longer than the schedule, the scheduler keeps only the **newest** queued run and cancels older ones. It won't cancel API-triggered runs.
- All run slots busy → the run waits.

**Limits**
- Run slot counts aren't in the docs (see pricing page). Multi-tenant Enterprise: unlimited concurrency since July 2023. Starter and Developer: **one project each**.
- Memory: **600 MiB** per run, all accounts, not configurable. Over it → "memory limit error".
- Auto-deactivation: a deploy or CI job after **100 consecutive failures**. Reactivate by editing and saving the job, or **Run now**. Inactive account: warning at 90 days, jobs deactivated 7 days later.
- Threads default **4**. Don't override the dbt version.

**Job chaining ("Run when another job finishes")**
- Plans: **Starter and Enterprise-tier** (not Developer).
- Setup: job → Triggers → Run when another job finishes → pick the **project**, the upstream **job**, and **Completes on** (Success only, or all statuses).
- One upstream job can trigger several downstream jobs, including in other projects. You need permission on both.
- Cross-project chaining needs more than one project → **Enterprise-tier**.

**CI jobs**
- **Triggered by pull requests**: on by default. **Run on draft pull request**: opt-in.
- Same PR, new commit: the newest run starts and stale in-flight runs are **cancelled** (serial). Different PRs: **concurrent**. Concurrent CI and smart cancellation need **Starter+**, and aren't available for API-triggered CI on Starter.
- Temp schema `dbt_cloud_pr_<job_id>_<pr_id>`, dropped when the PR closes or merges. Not dropped if a `generate_schema_name` override loses the `dbt_cloud_pr_` prefix, or for API-triggered CI.
- **Run source freshness** option: runs freshness before the CI job.
- **Run timeout**: 3600 s by default when dbt compare is on.
- **Monorepo**: one PR triggers CI for **all** connected projects. Use a target branch per project (`main-project-a`).
- **Fork PR**: dbt can only check out commits from the original repo.
- Ingress PrivateLink or IP allowlisting: CI hooks **may be unavailable**, so CI can fail silently.
- Azure DevOps: no new run if the PR's latest commit already triggered one.

**Advanced CI (dbt compare)**
- **Enterprise / Enterprise+**, turned on by an admin. Platforms: BigQuery, Databricks, Postgres, Redshift, Snowflake.
- CI and production must be on the **same database host / connection**.
- Record-level compare needs a **primary key constraint or uniqueness test**, or you get "Primary key missing".
- `event_time` on the model: compares only the overlapping time range, so no false "deleted" or "new" rows.
- Results: **Compare tab** on the run + a **PR comment**.
- Cache: up to **100 rows per modified model**, encrypted, S3 / Azure Blob in your region, **30 days**.
- **Not dynamically masked.** Every account user can see the comparison results and cached rows. Restrict the CI environment's credentials, or use synthetic data.
- Limit what's compared: `--select state:modified --exclude fct_orders`.

---

### dbt Commands & Node Selection (practice set: Topic 10)

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
| `state:old` | A node with the same `unique_id` exists in the comparison manifest |
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
- By default dbt resolves `ref` against your **dev target**. The state manifest is used only if the node isn't selected **and** doesn't exist in your database
- `--favor-state` makes dbt prefer the state manifest (not for selected nodes)
- `--defer-state` lets deferral use a **different manifest** than `--state` (which still drives `state:modified`)
- **Ephemeral models are never deferred**

**Using `--state` and `--defer` together (standard CI pattern):**
```bash
dbt build --select state:modified+ --defer --state /path/to/prod/manifest
```
- Runs only modified models + their downstream descendants
- Upstream parents that aren't modified → resolved against production tables
- Saves significant warehouse compute in CI

**Critical state gotchas:**
- **Vars and env vars**: if a model uses `var()` or `env_var()`, dbt can't trace a value change into `state:modified`. It's only likely to be marked modified if the change alters the model's config
- **Manifest overwrite**: dbt overwrites `manifest.json` while parsing, so don't set `--state` and `--target-path` to the same path with `--defer` or `state:modified` (non-idempotent). Fix: move the manifest to its own folder, use a different `--target-path`, or pass `--no-write-json`
- **Seeds over 1 MiB**: dbt can't compare contents and warns. It only tracks the file path. Seeds under 1 MiB are tracked by file hash
- **Relationship tests with mixed parents**: with `--defer`, a `relationships` test between a modified and an unmodified model queries across two environments. Workaround: `dbt test -s "state:modified" --exclude "test_name:relationships"`
- **What `state:modified` ignores**: changes to `tags` and `meta`. A `description` change counts only with `persist_docs`
- **Code, not data**: it detects code, config and metadata changes, not data changes. Don't use it in a scheduled job that must build every run

**`dbt ls` Command**
- Lists project resources. Docs (dbt v2.0+): it reads your connection profile but doesn't connect to the database or run any queries
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

- Precedence: `--vars` on the command line beats `dbt_project.yml` (or `vars.yml`, v1.12+). The `var()` default argument is last
- Jinja isn't supported inside the `vars` config. Values are literal
- Missing variable with no default → compilation error
- `var()` / `env_var()` value changes aren't traced by `state:modified` (see state gotchas above)
- A `--vars` change forces a full re-parse (partial parsing)

**Indirect Selection (`--indirect-selection`)**
Controls which tests run when models (not tests) are selected:

| Mode | Behavior |
|---|---|
| `eager` (default) | Runs tests if ANY parent node is selected — may error if other parents unbuilt |
| `buildable` | Runs tests whose dependencies are either selected or ancestors of selected nodes |
| `cautious` | Runs tests ONLY if ALL parent nodes are selected |
| `empty` | Runs no tests at all, even tests attached directly to the selected node |

```bash
dbt test --select "stg_orders+" --indirect-selection cautious
```

**Other Useful Selection Methods**
```bash
--select result:error          # any resource that errored (needs a prior run, test, build or seed)
--select result:fail           # test nodes only. Tests have no downstream, so re-run models with 1+result:fail+
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

- `source_status:` documents only the value `fresher`.
- Required workflow:
  1. Run `dbt source freshness` previously and persist the resulting `sources.json` to a known path.
  2. Re-run `dbt source freshness` now (so dbt has a current snapshot to compare).
  3. Then `dbt build --select source_status:fresher+ --state path/to/previous/`.
- Without `--state`, dbt has nothing to diff against and the selector resolves to **zero nodes** — the run silently does nothing.
- If you misspell as `source:fresher+` (single word), dbt looks for a source literally **named** `fresher` — almost always matches nothing.
- Common use: source-driven incremental jobs that only build downstream when raw data has actually landed; cheaper than `state:modified+` when source updates are sparser than code changes.

**Other commands (from the docs)**
- **`dbt retry`**: re-runs the last invocation from the point of failure, using `run_results.json`. If the run failed before any node ran (for example a warehouse connection error), there's nothing to retry from: re-run the job. If the previous run succeeded, retry ends as "no operation". Supported: build, check, compile, clone, docs generate, seed, snapshot, test, run, run-operation.
- **`dbt compile`**: needs a warehouse connection (introspective queries). `dbt compile --inline "select * from {{ ref('raw_orders') }}"` compiles a snippet without a model file (dbt v1.5+). `dbt parse` validates the project **without** connecting to the warehouse, and its manifest has no compiled SQL.
- **Partial parsing**: on by default. For a full re-parse run with `--no-partial-parse` or set `PARTIAL_PARSE: false` (profiles.yml, env var or flag). dbt re-parses fully when `--vars`, `profiles.yml`, `dbt_project.yml`, packages, the dbt version or certain widely-used macros change. The cache is `target/partial_parse.msgpack` (`dbt clean` removes it). dbt v2 job runs no longer support the partial-parse flags.
- **Source freshness**: a source is checked if it has a `freshness` config with `warn_after` and/or `error_after` (each needs `count` + `period`). Neither set → no check. `freshness: null` turns it off for a table. `loaded_at_field` is **optional**: without it dbt uses warehouse metadata tables when possible. `loaded_at_query` (v1.10+) is an alternative, and setting both is a parse error. Stale = nonzero exit code. v1 writes `target/sources.json`. v2 uses `dbt freshness` and writes `freshness.json`, plus `sources.json` for compatibility.

### Gotcha Q&A

**Q: A CI job runs `dbt sl validate` before `dbt build` and fails. Why?**
A: The docs list `dbt build` first, then `dbt sl validate`.

**Q: Two PRs open at once. What does dbt do?**
A: Runs them **concurrently**, each in its own temp schema. No run slots used.

**Q: A developer pushes 3 commits to one PR. What happens?**
A: Runs for the same PR are serial. The newest commit runs and stale in-flight runs are cancelled.

**Q: Source freshness is a checkbox and fails. Does `dbt build` still run?**
A: Yes. The checkbox runs first and doesn't break later steps. As a command step, it would stop them.

**Q: A job has only the source freshness checkbox. It errors. Why?**
A: A job needs at least one command. Add a placeholder like `dbt compile`.

**Q: `dbt retry` does nothing after a warehouse connection error. Why?**
A: No nodes ran, so `run_results.json` has nothing to retry from. Re-run the job.

**Q: A job scheduled every 15 minutes takes 20. What happens?**
A: The queue grows. The scheduler keeps only the newest queued run and cancels older ones.

**Q: You need a job at exactly 4:05 UTC daily. Which schedule type?**
A: Cron (`5 4 * * *`). Specific hours only takes whole hours.

**Q: A team on the Developer plan wants a 5-minute schedule.**
A: Not possible. Developer plan minimum is 10 minutes.

**Q: Job B in project B should run after Job A in project A. Which plans?**
A: Chaining is Starter and up, but Starter and Developer have one project each. Cross-project needs Enterprise-tier.

**Q: Advanced CI shows lots of "deleted rows" though production didn't change. Why?**
A: No `event_time`. Without it, whole tables are compared and CI's smaller window looks like deletions.

**Q: Advanced CI says "Primary key missing". Why?**
A: Record-level compare needs a primary key constraint or a uniqueness test on the model.

**Q: Advanced CI can't compare. CI and prod are on different hosts.**
A: They must be on the same database host / connection.

**Q: Comparison results from 5 weeks ago are gone. Why?**
A: The cache expires after 30 days.

**Q: A viewer sees unmasked PII in the Compare tab. Why?**
A: Cached rows aren't dynamically masked, and every account user can see them. Restrict the CI environment's credentials or use synthetic data.

**Q: PR schemas aren't dropped after merge. Why?**
A: A `generate_schema_name` override lost the `dbt_cloud_pr_` prefix, or the CI was triggered through the API.

**Q: One PR triggers CI in projects that didn't change. Why?**
A: Monorepo: a PR triggers CI for every connected project. Use a target branch per project.

**Q: CI says "Failed to checkout to specified revision" on a fork PR.**
A: dbt can only check out commits from the original repo. Push the branch there.

**Q: A `dbt build` test on `stg_orders` fails. What about its downstream models?**
A: They are **skipped**. Set the test severity to `warn` to avoid it.

**Q: When do unit tests run in `dbt build`?**
A: Before the model is built.

**Q: `state:modified` selects nothing even though `--state` is set. Why?**
A: `--state` and `--target-path` point to the same folder, so `manifest.json` is overwritten. Use separate folders, or `--no-write-json`.

---

### Blue/Green Deployments and `dbt clone` (practice set: Topic 4c)

**What the official docs say**
- Blue/green shows up in the docs as a **use case for `dbt clone`**: "blue/green continuous deployment (on data warehouses that support zero-copy cloning tables)". The docs don't give a full blue/green procedure.
- The database-swap steps below are a **community pattern** (dbt Community Forum, Snowflake). They are not in the official docs.

**`dbt clone`**
- Clones selected nodes from the specified state into the target schema(s). It relies on `--defer`.
- Zero-copy platforms: **Snowflake, Databricks, BigQuery**, when the model exists as a table in the source environment. Otherwise dbt creates a simple **pointer view** (`select * from` the source object).
- `dbt clone --state path/to/artifacts` clones everything. `--select` clones a subset. `--threads` runs clone statements in parallel.
- Pre-existing relations are **skipped** by default. `--full-refresh` recreates them.
- Deferral: the **dbt platform CLI** adds `--defer` automatically. In the **Studio IDE** you turn on the "Defer to production" toggle first.
- Available in the Studio IDE and the dbt platform CLI. Needs dbt 1.6+.
- **Clone vs deferral:** clone needs compute and creates extra objects in your warehouse. Deferral is often cheaper and simpler.
- Documented uses:
  - blue/green continuous deployment
  - cloning current production into development schemas
  - handling incremental models in CI jobs
  - testing code changes on downstream dependencies in your BI tool

**Incremental models in CI (docs example)**
A modified incremental model has no table in the PR schema, so it builds in full. Clone production's copy first so it runs incrementally:
```bash
dbt clone --select state:modified+,config.materialized:incremental,state:old
dbt build --select state:modified+
```
`state:old` skips brand-new incremental models that don't exist in production. Only works on warehouses with zero-copy cloning, otherwise you get pointer views.

**Community blue/green pattern (Snowflake)**
- Two databases (for example `stage` and `prod`). Build and test in `stage`, then swap them so the tested data becomes `prod`.
- The swap is a macro you write, run with `dbt run-operation`. It's not a built-in command. On Snowflake: `alter database prod swap with stage`.
- Job steps: `dbt run` → `dbt test` → `dbt run-operation swap_database`. A failed step stops the job, so the swap never runs.
- The swap moves the **whole database**, so only swap after a full build.
- **Views with fully qualified names** break or go stale after a swap. The thread's fix is to override `ref` (and `source`) so compiled SQL drops the database name.
- BigQuery datasets can't be renamed, and the thread advises against schema swapping because it can break views and custom schemas.

### Gotcha Q&A

**Q: Is `swap_database` a built-in dbt command?**
A: No. It's a macro you write and run with `dbt run-operation`.

**Q: What does `dbt clone` do on Postgres or Redshift?**
A: Creates pointer views, because those platforms aren't in the zero-copy list (Snowflake, Databricks, BigQuery). The docs only say "otherwise a pointer view."

**Q: A `dbt clone` skips models already in the target schema.**
A: Default behavior. Use `--full-refresh` to recreate them.

**Q: You run `dbt clone` in the Studio IDE and nothing is deferred.**
A: Turn on the "Defer to production" toggle. The platform CLI includes `--defer` automatically.

**Q: BI team wants to test against production-like data before release. Clone or deferral?**
A: Clone: it creates real objects in the warehouse. Deferral is cheaper but only affects dbt's `ref` resolution.

**Q: Blue/green swap is run after a test failure. Does it happen?**
A: No. Job steps run in order and a failed step stops the job.

---

## TOPIC 5: Security & Licenses ⭐ DEEP

### Reference Notes

**Licenses (a license always overrides group permissions)**

| License | Plans | Inherits permission sets? | Notes |
|---|---|---|---|
| Developer | All | Yes | Full feature access (IDE, CLI, jobs). Can use service tokens |
| Analyst | Enterprise, Enterprise+ | Yes | Legacy, not for new purchase |
| IT | Starter, Enterprise, Enterprise+ | **No** | Fixed: Security Admin + Billing Admin + edit Connections. Manages users, groups, connections, licenses. No IDE, no jobs. Max **1 IT seat** per Starter or Enterprise-tier account, doesn't count toward seats. Can't be the default license |
| Read-Only | Starter, Enterprise, Enterprise+ | **No** | View-only on all dbt resources (artifacts, Catalog, deploy section) |

- **Rule:** Account Admin group + Read-Only license = read-only. Account Admin group + IT license = still just IT access.
- Enterprise: Read-Only users can be given the **Analyst read** permission set, and scoped to projects with granular permissions (a one-time, permanent switch).
- Service tokens: Developer / Analyst licenses only (not Read-Only, not IT). Personal access tokens: Developer, Read-Only, IT.
- Developer plan can't add users. Upgrade to Starter.

**Adding and removing users**
- Enterprise-tier: Account Settings → **Users** → **Invite Users**.
- Starter: raise the **developer billing seat count** (Account settings → Billing), then invite. There are two counts: user seats and billing seats.
- Remove: Account settings → Users → the user → **Edit → Delete → Confirm**. It's immediate. You can re-invite. A deleted Developer user frees a seat. Starter: lower the seat count on Billing.

**Groups and RBAC**
- Permissions are assigned **only to groups**, never to users. A group = permission sets + project scope + environment write access.
- User in several groups → the **most permissive** wins.
- Custom groups, SSO mappings and RBAC need **Enterprise / Enterprise+**. Starter and Developer: passwords with MFA only.

| Default group | Permissions | Notes |
|---|---|---|
| Owner | Account Admin. **Permissions can't be changed** | For people responsible for the whole account |
| Member | Broad. Restricts only billing and security features | New users are added automatically |
| Everyone | Yours to customize | New users are added automatically |

- New users go into **both Member and Everyone**. You can delete the default groups once you've created your own.
- You can't edit your own user.
- Environment-level permissions: see Topic 3.

**Permission sets**
- Account-level: Account Admin, Account Viewer, Billing Admin, Cost Insights Admin, Cost Insights Viewer, Manage marketplace apps (marketplace integrations only), Notification Manager (Slack / Teams / email notifications), Project Creator, Security Admin.
- Project-level: Admin, Analyst, Analyst read, Database Admin, Developer, Git Admin, Job Admin, Job Creator, Job Runner, Job Viewer, Metadata (Discovery API only), Semantic Layer, Stakeholder (= Read-Only), Team Admin, v2 Migration Admin.

| Task | Who |
|---|---|
| Create projects | Account Admin, **Project Creator**. Project Admin can't |
| Use the IDE | Account Admin, Project Creator, Admin, Analyst, Developer |
| Create / edit jobs and environments | Account Admin, Project Creator, Admin, Job Admin (Job Creator: jobs in assigned projects and environment types) |
| Run jobs | The above + Job Runner |
| Edit connections (account) | Account Admin, Project Creator (IT license can too) |
| Users, groups, licenses, SSO, IP restrictions | Security Admin (+ Account Admin) |
| Full audit log (incl. sensitive) | Account Admin, **Account Viewer** |
| Audit log without sensitive info | Stakeholder / Read-Only |
| Query the Semantic Layer | **Semantic Layer** set, with a service token |

Traps:
- **Admin ≠ Account Admin.** Admin can't create projects.
- **Security Admin**: no IDE, no jobs, no runs, no environments.
- **Database Admin**: no IDE. Write access to data platform configs, read-only environments.
- **Analyst** = run and analyze models in the IDE, can't create or edit anything outside it. **Developer** = build models and manage production behavior (not the same as the Developer license).
- **Billing Admin**: Billing section only. **Job Viewer**: job results and logs (+ Catalog).
- **Semantic Layer**: service tokens only. **v2 Migration Admin**: users only.

**Service tokens**
- Belong to the **account**, not a user. For system-level integrations.
- Create: Account settings → Service Tokens → Create. You need a **Developer license and account admin permissions**.
- Shown **once**. Rotate: create new → update integrations → delete old.
- One token can hold many permission sets, each for all projects or specific projects.
- **Permission sets by plan:** Enterprise = any. Legacy Team = Account Admin, Member, Job Admin, Read-Only, Metadata, Semantic Layer. Developer / Starter = **Semantic Layer only**.
- An Account Admin token has full read + write. Use with caution.
- Service tokens obey **IP restrictions**: a 403 "Access denied" = the caller's IP isn't allowlisted. Add the integration's CIDRs.
- Tokens created before July 18, 2023 still work. Rotate them if used at high frequency.

**Personal access tokens (PATs)**
- Inherit the creator's permissions. Account-specific: one PAT per account, even with the same email.
- Create: Account settings → API Tokens → Personal Tokens. Shown once. Rotate: create new, delete old.
- Use a PAT only where needed. For flows that need a service account, use a **service token**. A PAT can't create a service token (400).
- Old user API keys are deprecated and no longer work. Move to PATs.

**SSO (Enterprise / Enterprise+)**
- Setup: Account settings → **SSO & SCIM**. IdPs: Okta, Entra ID, Google Workspace, generic SAML 2.0. Flows: IdP-initiated, SP-initiated, **JIT** provisioning.
- Login slug: generated by dbt, read-only (recreating the config makes a new one). Users sign in at `login.dbt.com` or `https://YOUR_ACCESS_URL/enterprise-login/<slug>`.
- Once SSO is on, non-admin users must use SSO. **Admins keep password login** unless you turn off "Allow password logins for account administrators". Re-authentication every **24 hours**.

**Okta SAML setup**
- Okta: new app, Web, SAML 2.0. SSO URL `https://YOUR_AUTH0_URI/login/callback?connection=<slug>`. Audience URI `urn:auth0:<YOUR_AUTH0_ENTITYID>:<slug>`. Relay state `<slug>`. Name ID format Unspecified.
- Attributes: `email`, `first_name`, `last_name`. Group attribute `groups`, filter regex `.*` (or `Starts with DBT_CLOUD_`). **Okta returns only 100 groups per user.**
- Username: SSO only → `user.getInternalProperty("id")`. SSO + SCIM → **Email**.
- dbt: Account settings → SSO & SCIM → Get started / Edit → Log in with Okta → paste SSO URL, Issuer, **X.509 certificate** → Save.
- The certificate expiry is manual: an Okta admin must renew it and paste it into dbt, or access breaks.

**License mappings (SSO)**
- Account settings → **Groups & Licenses** → **License mappings**. Enter comma-separated **IdP group names** for **Read-Only** and **Developer**.
- Based on **IdP groups**, not dbt groups. Applied at sign-in, so changes take effect the next time the user signs in.
- In both mapped groups → **Developer** wins. In neither → the account's **default license**.
- Default license: Groups & Licenses → Default license type → Developer, Read-Only or Analyst. **IT can't be the default.**
- SSO group mapping: a dbt group is assigned if the user is in one of its mapped IdP groups, or if the group has **Assign by Default**.

**SCIM (Enterprise / Enterprise+)**
- Okta and Entra ID. Automates provisioning and de-provisioning, profile updates, groups and licenses.
- With SCIM on: SSO group mappings are off, users **aren't auto-added to default groups**, and manual updates (including inviting users) are off by default.
- Create an **Account Admin** group in the IdP with the **same name** as the dbt group.
- SCIM token: Account settings → SSO & SCIM → Enable SCIM → Create SCIM token. Shown **once**. Replace it in your IdP before deleting the old one.
- IP restrictions on? Allowlist Okta's IPs. Entra ID: keep "Ignore dbt license mapping" **off**.

**IP restrictions (Enterprise)**
- Account Settings → IP Restrictions. Rules are Allow or Deny, in CIDR. With only an allowlist, everything else is denied. Deny carves exceptions out of an allowed range.
- Applies to the UI, the API, PATs and **service tokens**. You can't save if your own IP is in a deny range.

### Gotcha Q&A

**Q: A user is in the Account Admin group but has a Read-Only license. What can they do?**
A: Read-only. The license wins.

**Q: You give an IT-licensed user the Account Admin group so they can manage projects. Can they?**
A: No. IT users don't inherit permission sets. IT access is fixed.

**Q: Who can create service tokens?**
A: Someone with a Developer license and account admin permissions. Read-Only and IT licenses can't use service tokens.

**Q: You lose a service token right after creating it. How do you recover it?**
A: You can't. Create a new one, update integrations, delete the old one.

**Q: A service token gets 403 on every call but is valid. Why?**
A: The caller's IP isn't on the account's IP allowlist.

**Q: Which token for a production pipeline?**
A: A service token with the minimum permission sets. PATs inherit one person's permissions and are for user-specific access.

**Q: Can one token have Job Admin on project A and Read-Only on project B?**
A: Yes, a service token can hold several permission sets, each scoped to all or specific projects.

**Q: What's the Semantic Layer permission set for?**
A: Querying the Semantic Layer with a service token.

**Q: Which license does an SSO user get if they're in IdP groups mapped to both Read-Only and Developer?**
A: Developer. With no match, the default license.

**Q: Where do you set up license mappings, and what goes in?**
A: Account settings → Groups & Licenses → License mappings. Comma-separated IdP group names for Read-Only and Developer.

**Q: SSO is on and the IdP is down. Can admins still get in?**
A: Yes, with a password, unless you turned off "Allow password logins for account administrators".

**Q: New contractors shouldn't see any projects. What do you change?**
A: New users join both Member and Everyone. Customize both groups' permissions.

**Q: A project Admin can't create a project. Why?**
A: Only Account Admin and Project Creator can.

**Q: A Security Admin can't open Jobs during an incident. Why?**
A: Security Admin has no access to jobs, runs, environments or the IDE. Use Job Admin or Job Runner.

**Q: Which set gives read-only access including the sensitive audit log?**
A: Account Viewer. Stakeholder and Read-Only exclude sensitive information.

---

## TOPIC 6: Monitoring & Alerting

### Reference Notes

**Job notifications** (profile icon → **Notification settings**)
- Channels: **email**, **Slack**, **Microsoft Teams**.
- Events: **Succeeds** (no warnings or errors), **Warns**, **Fails**, **Is canceled**.
  - Warns comes from warning-level lines in data tests or source freshness. A run can show Success in the UI and still trigger Warns.
- **Email**: you need to be a developer user, account admin, or have the **Notification Manager** permission set (Enterprise). Developers set up their own. Admins can send to another internal user, or to an **external email** (a Teams channel address, PagerDuty).
- **Slack**: an account admin links the workspace (Account settings → Integrations → OAuth). Only Account Admins can connect or disconnect it. **Public channels only.**
- **Teams**: an account admin links the Teams app.
- IT license users can **receive** job notifications but can't **configure** them.
- Runs cancelled by the inactivity cleanup (10 minutes) may not reach Slack. Use email or webhooks.
- The docs don't give a plan limit for these.

**Webhooks**
- Needs a **Starter or Enterprise-tier** plan, a multi-tenant or AWS single-tenant deployment, and a destination that accepts **Authorization headers** (Azure Logic Apps and Power Automate may not).
- Create: Account settings → **Webhooks** → Create webhook. Name, description, events, jobs (**empty = all jobs**), endpoint URL. Save → you get a secret token.
- Who can create: Enterprise-tier → Account Admin, Admin or Developer permission set (UI or service token). Starter → Developer license.
- **Events**
  - `job.run.started`: run started.
  - `job.run.completed`: run finished, **success or failure**. Fires once metadata and artifacts are ingested and available from the Admin and Discovery APIs.
  - `job.run.errored`: fires **immediately**. Artifacts may not be ingested yet.
  - Subscribe to both → **two notifications** when a job errors.
  - Need API data? Use `completed` and filter on `runStatus`.
- **Verify the sender**: the `Authorization` header holds a **SHA256 HMAC of the request body**, keyed with your secret token. Compute it on your server and compare. Docs strongly recommend it.
- **Delivery**: JSON payload. **10-second timeout.** dbt retries each event **5 times**. Delivery log kept **7 days** (Recent Deliveries).
- **Auto-archive**: after **1,000 consecutive failed deliveries or 7 consecutive days** of failures, whichever comes first.
  - Reactivate: change the endpoint URL (UI), or API `PUT` with `active: true`.
- Payload: `accountId`, `webhookId`, `eventId`, `timestamp`, `eventType`, `webhookName`, and `data` (`jobId`, `jobName`, `runId`, `environmentId`, `projectName`, `dbtVersion`, `runStatus`, `runStatusCode`, `runStatusMessage`, `runReason`, `runStartedAt`...). Examples: Running = 3, Success = 10, Errored = 20.
- API: `/api/v3/accounts/{id}/webhooks/subscriptions` (list, create), `.../subscription/{id}` (get, update, delete), `.../subscription/{id}/test`.

**Scheduling and limits** (details in Topic 4)
- Intervals run every N hours from midnight UTC with a constant gap. Cron for exact times. All UTC.
- If a job runs longer than its schedule, the scheduler keeps only the newest queued run.
- A deploy or CI job is deactivated after **100 consecutive failures**.
- Memory: **600 MiB** per run, all accounts. Default threads: **4**.

### Gotcha Q&A

**Q: Your handler calls the dbt API for artifacts on `job.run.errored` and finds none. Why?**
A: `errored` fires immediately, before artifacts are ingested. Use `completed` and filter on `runStatus`.

**Q: You subscribe a webhook to both `completed` and `errored`. A job fails. How many notifications?**
A: Two.

**Q: Your endpoint takes 25 seconds to respond. What happens?**
A: dbt's webhook timeout is 10 seconds, so dbt records a failed delivery. Respond right away and process asynchronously.

**Q: When does dbt archive a failing webhook?**
A: After 1,000 consecutive failed deliveries or 7 consecutive days of failures, whichever is first. Each event is retried 5 times.

**Q: How do you reactivate it?**
A: Change the endpoint URL in the UI, or `PUT` with `active: true` through the API.

**Q: How do you check a webhook really came from dbt?**
A: Compare the `Authorization` header with a SHA256 HMAC of the request body, keyed with your secret token.

**Q: How long can you review webhook deliveries?**
A: 7 days (Recent Deliveries).

**Q: Which events can job notifications use?**
A: Succeeds, warns, fails, is canceled.

**Q: Can Slack notifications go to a private channel?**
A: No, public channels only.

**Q: Who can create webhooks on Enterprise?**
A: Account Admin, Admin or Developer permission set. On Starter, a Developer license.

---

## TOPIC 7: dbt Mesh & Cross-Project References ⭐ DEEP

### Reference Notes

**Plans:** cross-project `ref()` and project dependencies = **Enterprise and Enterprise+**. Multi-project lineage in Catalog = Enterprise / Enterprise+.

**Setting up projects (upstream = producer, downstream = consumer)**
- **Upstream project needs:**
  - Models with `access: public` and at least one successful job run after you define `access`.
  - A **Production** environment with at least one successful deployment job (it produces `manifest.json`).
  - If it has a **Staging** environment: a successful deployment job there too.
  - Each project `name` must be unique in the account.
- **Downstream project:**
  1. `dependencies.yml` at the project root.
  2. List the upstream project under `projects:` with `name:` (**case-sensitive**, must match the upstream's `dbt_project.yml` `name`).
  3. Use a two-argument ref: `ref('jaffle_finance', 'monthly_revenue')`.
- Two-way dependencies are **stepwise**: A runs and produces public models → B adds A and runs → A adds B. dbt checks for **cycles across projects** and errors. Two-way is fine if there's no node-level cycle.
- You can **select** upstream models in a downstream job, but you **can't build** them. Upstream models are built by the upstream project's own jobs.
- Semantic Layer: cross-project refs only work in the legacy YAML spec.
- Sources can't be shared across projects. Use a **foundational project** that holds the source staging models and exposes them as public. No two sources in a mesh should point to the same relation.
- Run downstream jobs after upstream ones with **"Run when another job finishes"** (see Topic 4).

**How cross-project refs resolve** (via a metadata service, not installed code)

| Downstream environment | Resolves to upstream |
|---|---|
| Production | Production |
| Staging | Staging if it exists, else Production |
| Development | Staging if it exists, else Production |

- Upstream Staging is used as soon as it exists, with **no fail-over to Production**, even with zero successful Staging runs. Safe order: create it unmarked → run a job → mark it Staging (Topic 3).
- Staging is optional. Production is the required one.

**Packages vs project dependencies**
- Package: source code is installed and runs as part of your project.
- Project dependency: the metadata service resolves refs. Upstream models are **not** parsed or run in your project.

**Model access** (governance features apply to **models only**, not sources, seeds or snapshots)

| Access | Who can `ref` it |
|---|---|
| `private` | Same group |
| `protected` (default) | Same project, or an installed package |
| `public` | Any group, package or project |

- Docs recommend `private` for new models. Changing to `public`: rerun a production job to apply it.
- Set in YAML under `config:` (`access: public`).
- **Ephemeral models can't be `public`** (parse error).
- `access` does **not** grant warehouse `SELECT`. Use the `grants` config.
- Private violation: `DbtReferenceError` at parse time ("not allowed because the referenced node is private to the finance group").
- Package `restrict-access: True`: only `public` models can be referenced outside the package. Default is `False`.
- There's no per-project allowlist. `public` means any project.

**Groups**
- Defined under `groups:` with a `name` and an `owner` (**name or email**, one is required), plus optional `description`.
- Assign with the `group` config: project level (`+group`), YAML `config:`, or in the model file. Each node belongs to **one** group.
- Members can be models, tests, seeds, snapshots, analyses, metrics. Not sources or exposures.
- Platform user groups (RBAC) are separate. The docs don't link them.

**Model contracts**
```yaml
models:
  - name: dim_customers
    config:
      contract:
        enforced: true
    columns:
      - name: customer_id
        data_type: int
        constraints:
          - type: not_null
      - name: customer_name
        data_type: string
```
- Enforced → every column needs `name` and `data_type`. Column order isn't checked.
- A preflight check runs at build time. If the output doesn't match, **the model doesn't build**.
- **Breaking changes:** removing a column, changing a `data_type`, removing or modifying a constraint (v1.6+), removing a contracted model (v1.9+: error if versioned, warning if not).
- **Materializations:** table ✅. View: names and types only, no constraints. Incremental: only `on_schema_change: append_new_columns` or `fail`. ❌ Python models, materialized views, ephemeral, custom materializations, BigQuery recursive CTEs.
- Contracts check the output shape at build time. Data tests check content after the build.

| Constraint | Postgres | Snowflake / Redshift | BigQuery | Databricks |
|---|---|---|---|---|
| not_null | enforced | enforced | enforced | enforced |
| primary_key, foreign_key | enforced | defined only | defined only | defined only |
| unique | enforced | defined only | not supported | not supported |
| check | enforced | not supported (dbt skips it) | not supported | enforced |

**Model versions**
```yaml
models:
  - name: dim_customers
    latest_version: 2
    versions:
      - v: 2
        columns:
          - include: all
            exclude: [country_name]
      - v: 1
        defined_in: dim_customers
        deprecation_date: 2026-06-01
```
- `latest_version` defaults to the **numerically highest** version. Set it lower and higher versions are **prereleases**.
- Unpinned `ref('dim_customers')` → latest version (dbt warns if a prerelease exists). Pinned: `ref('dim_customers', v=1)`. Cross-project: `ref('project', 'model', v=1)`.
- File: `<model>_v<N>.sql` by default. Override with `defined_in`. Relation name defaults to `<model>_v<N>` (use `alias` to change it).
- `deprecation_date`: dbt notifies consumers when new versions appear or a version is slated for deprecation.
- Breaking change on a contracted public model → add a **new version**, bump `latest_version`, set `deprecation_date` on the old one, let consumers migrate, then remove it.

**Catalog and Mesh** (Enterprise / Enterprise+)
- Nodes for another project show a **project icon** next to the project name. Downstream projects show as separate project nodes with dashed lines.
- Only **directly referenced public models** from other projects appear. Indirect ones show only in the Studio IDE lineage.
- Upstream project's Relationships tab: counts every project that lists it in `dependencies.yml`, even without a `ref`.
- Account lineage → **List view** = table of projects and their public models.
- Details of a public model or a private one need permission on the project that defines it.

### Gotcha Q&A

**Q: An upstream project has no Staging environment. Where does a downstream dev job resolve refs?**
A: Upstream Production.

**Q: You add `access: public` but the downstream ref still fails. What else?**
A: `dependencies.yml` in the downstream project (exact project name), an Enterprise or Enterprise+ plan, and successful production runs in the upstream.

**Q: You set up a two-way dependency in one go and both fail. Why?**
A: It must be stepwise. A runs and produces public models → B adds A and runs → A adds B.

**Q: A downstream job selects an upstream public model. Does it build?**
A: No. You can select it but not build it. Build it with the upstream project's jobs.

**Q: How do you run a downstream job when the upstream job finishes?**
A: "Run when another job finishes" on the downstream job: pick the upstream project and job.

**Q: Can projects share a `sources:` block?**
A: No. Use a foundational project that exposes public staging models.

**Q: You set `access: public` on an ephemeral model.**
A: Parse error.

**Q: A contract only declares 3 of 15 columns.**
A: Every column needs `name` and `data_type` when the contract is enforced.

**Q: A contract on an incremental model uses `sync_all_columns`.**
A: Not allowed. Only `append_new_columns` or `fail`.

**Q: Can you use a `check` constraint on Snowflake?**
A: No. Snowflake doesn't support `check`, so dbt skips it. Postgres and Databricks enforce it.

**Q: You need to drop a column from a contracted public model.**
A: New version, bump `latest_version`, set `deprecation_date` on the old version, let consumers migrate.

**Q: `access: public` is set but the consumer gets "Insufficient privileges" from the warehouse.**
A: `access` is only a dbt rule. Grant warehouse access with the `grants` config.

**Q: An installed package's protected models can be referenced by the root project. How do you stop that?**
A: By default (`restrict-access: False`) a root project can ref a package's protected models. Set `restrict-access: True` in the package so only public ones are visible.

---

## TOPIC 8: dbt Catalog

### Reference Notes

**What it is and who gets it**
- Catalog = dynamic view of your project's resources, lineage and model consumption, showing the latest **production (or staging)** state. Plans: **Starter, Enterprise, Enterprise+**. Developer and read-only seats can browse it.
- dbt Docs is a different thing. dbt Docs v2 is an open-source static site you generate locally (`dbt docs generate`). It is **not available in the dbt platform**. Catalog is populated automatically when jobs run with dbt v2.

| Feature | Starter | Enterprise | Enterprise+ |
|---|:-:|:-:|:-:|
| Lineage, resource browsing, global navigation | ✅ | ✅ | ✅ |
| Data health signals | ✅ | ✅ | ✅ |
| Model performance, project recommendations | ❌ | ✅ | ✅ |
| Column-level lineage | ❌ | ✅ | ✅ |
| Multi-project lineage | ❌ | ✅ | ✅ |
| Model query history | ❌ | ✅ | ✅ |
| Downstream exposures, data health tile | ❌ | ✅ | ✅ |
| Cost Insights (separate feature) | ❌ | ✅ | ✅ |

**What updates Catalog**
- Prereqs: a **production or staging** deployment environment (set a single environment per project as production or staging) and at least one successful job run in it.
- Metadata refreshes after **each job run in the production or staging environment** (deploy and merge jobs).
- **CI jobs do NOT update Catalog.** They don't reflect production state.
- dbt v2 jobs refresh Catalog automatically on every run. No `dbt docs generate` step.
- Some metadata needs specific commands: test results need `dbt test` or `dbt build`, source freshness needs `dbt source freshness`.
- **Inactivity purge:** no job runs in the past **3 months** → all metadata for that environment is purged. Run a job at least every 3 months.
- A deleted model disappears after the next job run that no longer includes it.

**Data health signals** (all plans, Preview)
- Statuses: **Healthy, Caution, Degraded, Unknown** (Unknown = no job run has processed the resource).
- Shown for models, sources, exposures.
- Models:
  - **Degraded:** failed to build, failing tests, or an upstream source is stale (freshness errored or hasn't run in 30 days).
  - **Caution:** not built in 30 days, no tests, test warnings, source freshness warning, or missing description.
  - **Healthy:** built in the last 30 days, tests configured and passing, has a description, fresh sources.
- Sources: Degraded = freshness error. Caution = freshness warning, not configured, not run in 30 days, or no description.

**Lenses** (lineage graph, lower-right corner): map layers that tag nodes. **One lens at a time.**

| Lens | Shows |
|---|---|
| Resource type | models, tests, seeds, saved queries… |
| Materialization type | Table, View, Incremental, Ephemeral, Materialized View |
| Latest status | status of the resource's latest execution in this environment |
| Model layer | Marts: `fct_` / `dim_` prefix or `/marts/`. Intermediate: `int_` or `/int/`, `/intermediate/`. Staging: `stg_` or `/staging/` |
| Test status | latest test results. Several tests with different results → **worst case** |
| Consumption query history | query count over a period |

There is **no Cost lens**.

**Column-level lineage (CLL)**
- Plans: Enterprise / Enterprise+. Open the resource → **Columns** tab → column card.
- Works for **models, sources, snapshots**. Lineage comes from the SQL `select` statements.
- **Python models can't be parsed** → shows a Python error. Other errors: parsing (SQL too complex or ambiguous) and unknown (e.g. hardcoded table names instead of `ref`).
- Only `select` usage counts. Joins and filters aren't reflected.
- Refreshes after each run in production or staging.

**Model query history** (Enterprise / Enterprise+)
- Tracks **consumption queries**: `select` queries against a model in your warehouse query logs, aggregated daily. **Excludes** dbt builds and test runs.
- Warehouses: Snowflake (Enterprise edition or higher), BigQuery, Redshift, Databricks.
- Needs a **production** environment with a successful run, dbt admin permissions, and warehouse query-history permissions for the production deployment credentials (e.g. Snowflake: `GRANT DATABASE ROLE SNOWFLAKE.GOVERNANCE_VIEWER` by `ACCOUNTADMIN`).
- New PROD environments: enabled automatically. Existing PROD: Orchestration → Environments → PROD env → Settings → Edit → **Query History** → **Test Permissions** → **Enable query history** → Save. If it fails on persistent errors dbt disables it; re-run **Test Permissions** to re-enable.
- View it in: **Performance** → "Most consumed models" (up to 3 months), **Lenses → Consumption queries** (last 30 days), **Resources → Models** sorted by Consumption.
- It uses warehouse credits.

**Cost Insights** (Enterprise / Enterprise+)
- Needs a supported warehouse (Snowflake, BigQuery, Databricks, Redshift Preview), platform **metadata credentials** (test must pass), and at least one **production** job.
- **dbt State / state-aware orchestration is needed only for cost-reduction data**, not for cost data. The docs don't mention Fusion as a requirement.
- Cost formulas: Snowflake = credits × price per credit. BigQuery on-demand = data processed × price per TiB. BigQuery capacity = compute time × price per slot hour (cached queries = $0). Databricks = DBUs allocated by query runtime × cost per DBU.
- Calculated **once daily** (~17:00 UTC), completed days only. Estimates for optimization, **not billing reconciliation**.
- Viewed in: project dashboard, Catalog model page, job details page.

**Other Catalog features**
- **Model performance** (Enterprise / Enterprise+): most executed, longest-running, most failures. Lookback 1 week to 3 months (default two weeks).
- **External metadata ingestion** (Enterprise / Enterprise+, Preview): shows warehouse tables and views not defined in dbt. **Snowflake only** for now. Runs daily at 5 PM UTC, and each time you save credentials.
- **Multi-project lineage**: see Topic 7. Needs public models and project dependencies. Direct references only.

**Artifact files**
- `manifest.json`: project nodes, config and lineage.
- `catalog.json`: warehouse metadata about the tables and views your project builds (column names, types, stats).
- `sources.json`: source freshness results (legacy artifact).

**Artifacts setting (legacy)**
- Account settings → project → Edit → **Artifacts** picks the job for **legacy dbt Docs** and source freshness links.
- Catalog doesn't use it. It reads metadata from the Discovery API after each production/staging run.
- Docs say to associate **one** production job per project.

### Gotcha Q&A

**Q: A model built in your IDE dev schema isn't in Catalog. Why?**
A: Catalog shows production and staging deployment runs. Development builds don't appear.

**Q: CI jobs run fine but Catalog hasn't changed. Why?**
A: CI jobs don't update Catalog. Production or staging deployment jobs do.

**Q: A project's Catalog data disappeared after a quiet period.**
A: No job runs for 3 months purges the environment's metadata. Run a job at least every 3 months.

**Q: Column-level lineage is missing for a Python model.**
A: Python models can't be parsed. CLL works for SQL models, sources and snapshots.

**Q: Which plan do you need for column-level lineage, query history, multi-project lineage?**
A: Enterprise or Enterprise+. Not Starter.

**Q: A model shows Caution but all tests pass.**
A: Caution also comes from a missing description, no tests, or not built in 30 days.

**Q: Does query history count dbt's own runs?**
A: No. Only consumption `select` queries. dbt builds and tests are excluded.

**Q: Do you need Fusion for Cost Insights?**
A: The docs don't list Fusion as a requirement. State-aware orchestration or dbt State is only for cost-reduction data.

**Q: Can you combine two lenses on one graph?**
A: No. Switch between them.

---

## TOPIC 9: Hooks & Operations

### Reference Notes

**Hook types**

| Hook | Runs | Configured in |
|---|---|---|
| `pre-hook` | Before each model, seed or snapshot is built | `dbt_project.yml` (`+pre-hook`), `config()` block, YAML property file (`config:`) |
| `post-hook` | After each model, seed or snapshot is built | Same as above |
| `on-run-start` | At the start of a command | `dbt_project.yml` |
| `on-run-end` | At the end of a command | `dbt_project.yml` |

- `on-run-start` / `on-run-end` run for: `dbt build`, `compile`, `docs generate`, `run`, `seed`, `snapshot`, `test`. Once per command, not per model.
- Each hook takes one SQL string or a **list** of strings.
- Seeds and snapshots take hooks in `dbt_project.yml` or their YAML property file. A CSV seed has no `config()` block.
- Hooks can call macros: `"{{ some_macro() }}"`. If the macro uses execution-time values (model configs, `ref()`), wrap the call in an **extra set of curly braces**.

**Ordering and accumulation**
- Hooks from every scope are all applied. Model hooks don't replace project hooks.
- Order: (1) hooks from dependent **packages** run before the active package's hooks, (2) hooks in `dbt_project.yml` run before hooks in the model itself, (3) within one place, in the order defined.

**Transactions**
- On adapters that use transactions (the docs name **Postgres and Redshift**), pre- and post-hooks run **inside the same transaction** as the model build. A failing hook fails that transaction.
- To run a hook outside the transaction:
  - `before_begin("...")` / `after_commit("...")` helper macros, or
  - the dictionary form: `{sql: "...", transaction: false}`
- **Don't use this on Snowflake, BigQuery, Spark or Databricks.** dbt doesn't use transactions there.
- Typical reasons: `VACUUM` on Redshift (can't run in a transaction), or an audit record that should persist even if the build fails.

**Context variables**

| Variable | Where |
|---|---|
| `{{ this }}` | pre- and post-hooks: the current relation |
| `schemas` | `on-run-end` only: schemas dbt built models into |
| `database_schemas` | `on-run-end` only: `(database, schema)` pairs, for runs across several databases |
| `results` | `on-run-end` only: one Result object per resource that executed |

- Outside `on-run-end`, `schemas`, `database_schemas` and `results` are **none**. No error.
- Result fields used in the docs: `res.node.unique_id`, `res.status`, `res.message`. The docs example shows both a `success` and an `error` result in one `on-run-end` summary.

**Grants: use the `grants` config first**
- Docs: define grants as resource configs **whenever possible** (models, seeds, snapshots):
  ```yaml
  models:
    +grants:
      select: ['reporter', 'bi']
  ```
- dbt makes the grants **match exactly**: grantees not listed are revoked. No `grants` config on a node = dbt doesn't touch its grants.
- Child config replaces parent grantees per privilege. Use `+select` to **add** instead.
- Use a post-hook only when the config can't do it: objects other than tables and views, masking or row access policies, future grants, advanced permissions. Databricks `READ_METADATA` / `USAGE` need post-hooks.
- Spark / Delta Lake OSS doesn't support `grants`.

**Operations (`dbt run-operation`)**
- Runs a macro on demand. Not a resource in your project.
- Unlike hooks, the macro must **execute** its SQL with a `statement` block or `run_query()`. Otherwise dbt just returns the SQL as a string.
- Arguments are a **YAML string** mapped to the macro's keyword arguments:
  ```bash
  dbt run-operation grant_select --args '{role: reporter}'
  ```
- dbt v1.12+: `dbt run-operation --sql "..."` runs a SQL/Jinja string directly. Can't be combined with a macro name or `--args`.
- `run-operation` doesn't enforce model `access` or `group` rules. A macro can `ref()` a private model.
- Docs use cases: UDFs, Snowflake warehouse management, Redshift vacuum, creating shares or clones.

**Hooks vs operations**

| | Hooks | Operations |
|---|---|---|
| How they run | Automatically with a model, seed, snapshot or run | You invoke them (CLI or a job command step) |
| Executes SQL | The hook string is run as SQL | The macro must run it itself |
| Typical use | Per-resource or per-run automation | One-off admin tasks |

### Gotcha Q&A

**Q: A post-hook inserts an audit row on Redshift. The model fails. Is the row there?**
A: Not by default. The hook is in the model's transaction. Use `transaction: false` (or `after_commit`).

**Q: You add `transaction: false` to a Snowflake hook. Good idea?**
A: No. The docs say not to use it where dbt doesn't support transactions (Snowflake, BigQuery, Spark, Databricks).

**Q: 2 post-hooks in `dbt_project.yml`, 2 more in the model. How many run?**
A: All 4. Project hooks first, then the model's.

**Q: `{{ results }}` in a post-hook returns none. Why?**
A: It only exists in `on-run-end`. Elsewhere it's none, with no error.

**Q: Your `on-run-end` hook needs the schemas touched in a multi-database run.**
A: `database_schemas` gives `(database, schema)` pairs. `schemas` is just schema names.

**Q: Where do you set `on-run-end`?**
A: `dbt_project.yml`.

**Q: You need to grant SELECT on every model to a role. Hook or config?**
A: The `grants` config. Hooks only for what it can't do.

**Q: `dbt run-operation` on a macro that only returns a `DROP TABLE` string. Nothing happens.**
A: The macro must execute the SQL with `run_query()` or a `statement` block.

**Q: How do you pass arguments to `run-operation`?**
A: `--args` with a YAML string, e.g. `--args '{role: reporter}'`.

**Q: How do you call a macro from a hook?**
A: Put the call in Jinja braces in the hook string: `post_hook: "{{ my_macro(this) }}"`.

---

## High-Yield: Top 10 Exam Topics

> Study these first if time is short.

1. **Cross-project env resolution table** — dev and staging → upstream staging if it exists, else production; prod → prod
2. **Deferral options** — Environment (recommended) vs This Job (older self-deferral) vs No deferral; CI defaults to Production
3. **License always overrides group permissions** — know specific failure scenarios
4. **CI job behavior** — no run slots, temp schema lifecycle, smart cancellation for same PR
5. **Command ordering** — `dbt build` before `dbt sl validate`; checkbox vs step for source freshness
6. **Governance trifecta** — model access + contracts + versions and how they interact
7. **Service token gotchas** — one-time visibility, IP restrictions, rotation pattern
8. **Webhook reliability** — archived after 1,000 failures or 7 days; 7-day delivery log; `errored` vs `completed` timing
9. **Manifest state loss** — same `--state` and `--target-path` = non-idempotent deferral
10. **Plan gates** — cross-project refs, project dependencies and Advanced CI (Enterprise, Enterprise+); PrivateLink (Enterprise+)

---

## Plan Tier Quick Reference

| Feature | Developer | Starter | Enterprise | Enterprise+ |
|---|---|---|---|---|
| Job chaining | No | Yes | Yes | Yes |
| Cross-project refs | No | No | Yes | Yes |
| Project dependencies | No | No | Yes | Yes |
| Advanced CI (compare) | No | No | Yes | Yes |
| SSO / SCIM | No | No | Yes | Yes |
| Column-level lineage | No | No | Yes | Yes |
| Multi-project lineage | No | No | Yes | Yes |
| PrivateLink | No | No | No | Yes |
| Azure DevOps native | No | No | Yes | Yes |
| Scheduling min interval | 10 min | — | — | — |