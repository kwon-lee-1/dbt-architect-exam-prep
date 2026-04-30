# Topic 1: Warehouse Connections — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1.
> **Subdomain 1.1 — Snowflake account identifier format**

A developer sets up a new Snowflake connection in dbt Cloud. They enter `db5261993.snowflakecomputing.com` as the account identifier. The connection test passes in the UI, but all scheduled jobs fail silently with a connection error. What is the most likely cause?

- A) The Snowflake warehouse is suspended and needs to be resumed before dbt can connect.
- B) The account identifier uses the full domain URL instead of the locator format, causing a silent connection failure.
- C) The dbt Cloud IP addresses are not whitelisted in Snowflake's network policy.
- D) The user account does not have the required `USAGE` privilege on the warehouse.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A suspended warehouse causes query errors, not a connection-level silent failure. The test would have caught a warehouse issue. |
> | **B) ✅ Correct** | Snowflake requires the **locator format** (e.g., `db5261993.east-us-2.azure`), NOT the full `.snowflakecomputing.com` domain. Using the full URL causes a silent connection failure — the UI connection test may still pass but jobs fail. |
> | **C) ❌ Incorrect** | Missing IP whitelist would cause an explicit network-level rejection, not a silent failure tied to the identifier format. |
> | **D) ❌ Incorrect** | Missing privileges would cause permission errors on specific operations, not a connection-level failure. |
>
> > 💡 **Key rule**: Snowflake account ID = locator format only (`db5261993.east-us-2.azure`). Never use the full `.snowflakecomputing.com` URL.

---

### Q2.
> **Subdomain 1.2 — IP whitelisting**

Your organization adds a new cloud region to its dbt Cloud account. Immediately after, Snowflake's network policy begins blocking dbt connections. No firewall rules were changed. What is the root cause?

- A) The new region uses a different Snowflake driver that is incompatible with the existing network policy.
- B) Raw IP addresses were hardcoded in the Snowflake network policy instead of using dbt-provided hostnames.
- C) The dbt Cloud service account needs to be re-authenticated after a region change.
- D) PrivateLink was not configured for the new region.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud uses consistent drivers across regions. Driver incompatibility is not a firewall issue. |
> | **B) ✅ Correct** | dbt publishes **static hostnames** but the **underlying IPs are dynamic** (cloud infrastructure can reassign them). If you hardcode IPs, any infrastructure change — including adding a region — silently breaks the allowlist. Always use hostnames, not raw IPs. |
> | **C) ❌ Incorrect** | Service account credentials don't change when a region is added. |
> | **D) ❌ Incorrect** | PrivateLink is a separate network architecture choice. The scenario describes a firewall rule failure, not a missing PrivateLink setup. |
>
> > 💡 **Key rule**: Always use **hostnames** in firewall rules — never raw IPs. dbt's underlying IPs are dynamic.

---

### Q3.
> **Subdomain 1.3 — PrivateLink**

Which of the following accurately describes the requirements and behavior of dbt Cloud's PrivateLink feature? **Select TWO correct answers.**

- A) PrivateLink is available on all dbt Cloud plans including Starter.
- B) PrivateLink provides VPC-to-VPC connectivity with no public internet traversal.
- C) PrivateLink is region-specific — you must configure it separately for each region.
- D) PrivateLink automatically configures IP whitelisting in your warehouse once enabled.
- E) PrivateLink replaces the need for service accounts in production environments.

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | PrivateLink is **Enterprise-only** — not available on Starter or Developer plans. |
> | **B) ✅ Correct** | PrivateLink creates a VPC-to-VPC connection that routes entirely within the cloud provider's private network, bypassing the public internet. |
> | **C) ✅ Correct** | PrivateLink is **region-specific** — each region requires its own configuration. A multi-region setup needs separate PrivateLink configurations per region. |
> | **D) ❌ Incorrect** | PrivateLink and IP whitelisting are separate mechanisms. PrivateLink doesn't auto-configure warehouse firewall rules. |
> | **E) ❌ Incorrect** | PrivateLink is a network topology feature, completely unrelated to authentication methods like service accounts. |
>
> > 💡 **Key rule**: PrivateLink = Enterprise-only, VPC-to-VPC, region-specific. Also note: CI hooks are NOT available with PrivateLink.

---

### Q4. ⭐
> **Subdomain 1.4 — Snowflake Fusion key pair authentication**

A team configures key pair authentication for a Snowflake connection using the dbt Fusion engine. The connection test fails with the error "Could not deserialize key data." What is the most likely cause?

- A) Key pair authentication is not supported by the Fusion engine — only username/password is allowed.
- B) The private key was generated in 3DES format instead of PKCS#8 AES-256 format.
- C) The public key was not uploaded to Snowflake before testing the connection.
- D) The key pair passphrase contains special characters that dbt cannot parse.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Fusion engine does support key pair authentication — it specifically requires it. |
> | **B) ✅ Correct** | Fusion requires **PKCS#8 AES-256** format. Legacy **3DES** format keys (and headerless keys) are rejected with exactly this error message: "Could not deserialize key data." |
> | **C) ❌ Incorrect** | Not uploading the public key to Snowflake would cause an authentication rejection from Snowflake — a different error, not a deserialization error on dbt's side. |
> | **D) ❌ Incorrect** | The passphrase is a separate field and would produce a passphrase-related error, not a key deserialization error. |
>
> > 💡 **Key rule**: Fusion key pair = **PKCS#8 AES-256 only**. 3DES format → "Could not deserialize key data."

---

### Q5.
> **Subdomain 1.5 — Connections are account-level**

An organization has three dbt Cloud projects: `sales`, `marketing`, and `finance`. They want `sales` and `marketing` to use the same Snowflake account but with different warehouse names. Which of the following is true?

- A) Each project must have its own dedicated connection — connections cannot be shared across projects.
- B) A single connection can be shared across multiple projects; environment-level settings control warehouse overrides.
- C) The connection must be duplicated per project, but the credentials can be the same.
- D) Connections are project-level, so `sales` and `marketing` will automatically use different connections.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is the opposite of how dbt Cloud works. Connections are account-level and are explicitly designed to be shared. |
> | **B) ✅ Correct** | Connections are **account-level** — shared across multiple projects. Different projects (or different environments within a project) can override warehouse-level settings at the environment level without needing separate connections. |
> | **C) ❌ Incorrect** | There is no need to duplicate connections. The same connection object is referenced by multiple projects. |
> | **D) ❌ Incorrect** | Connections are account-level, not project-level. Multiple projects can and do share the same connection. |
>
> > 💡 **Key rule**: Connections are **account-level** (not project-level) — shared across projects. Each environment references exactly one connection.

---

### Q6.
> **Subdomain 1.6 — BigQuery OAuth limitations**

A team on a Starter plan wants to configure OAuth authentication for their BigQuery connection so developers can use their personal Google accounts in the dbt Cloud IDE. Will this work?

- A) Yes — BigQuery OAuth is available on all plans including Starter.
- B) No — BigQuery OAuth requires Enterprise tier and is unavailable on Starter.
- C) Yes — OAuth works for IDE use on Starter but not for production jobs.
- D) No — BigQuery does not support OAuth; only service account JSON files are supported.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | BigQuery OAuth in dbt Cloud is plan-gated — it is not available on Starter. |
> | **B) ✅ Correct** | BigQuery OAuth (Client ID + Secret) is available for **development environments on Enterprise tier only**. Starter plan teams must use service account JSON or key-based auth. |
> | **C) ❌ Incorrect** | There is no Starter-with-IDE-only exception. The restriction is plan-level regardless of environment type. |
> | **D) ❌ Incorrect** | BigQuery does support OAuth in dbt Cloud — it's just gated to Enterprise plans. |
>
> > 💡 **Key rule**: BigQuery OAuth = Enterprise tier only. After org setup, users link via **Profile Settings**.

---

### Q7.
> **Subdomain 1.7 — Lineage graph: logical vs physical**

A dbt Cloud project uses a Snowflake connection for the development environment and a different Snowflake connection for production. A data engineer expects to see two separate warehouse nodes in the lineage graph in dbt Catalog showing the physical data flow. What will they actually see?

- A) Two separate warehouse nodes labeled with their respective connection names.
- B) A single logical DAG based on `ref()` and `source()` calls, with no distinction between physical warehouses.
- C) The lineage graph only shows the production connection since Catalog reflects production only.
- D) An error — dbt Catalog does not support projects with multiple connections.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The lineage graph has no concept of connections or physical warehouses — it is purely logical. |
> | **B) ✅ Correct** | The lineage graph in dbt Catalog is **logical** — it shows model dependencies based on `ref()` and `source()` calls in the DAG, not physical warehouse topology. It does not distinguish which connection ran a model or show cross-warehouse data movement. |
> | **C) ❌ Incorrect** | While Catalog reflects production by default, the lineage graph's logical nature is a separate concept from which environment it reflects. |
> | **D) ❌ Incorrect** | Multiple connections per project are fully supported. Catalog handles them without error. |
>
> > 💡 **Key rule**: Lineage graph = **logical** (based on `ref()`/`source()`), not physical. Never shows warehouse topology.

---

### Q8.
> **Subdomain 1.8 — Managed repositories**

An architect is reviewing a team's setup. They find that a dbt Cloud project in active production use is configured with a managed (dbt-hosted) repository instead of a self-hosted Git repository. Which of the following is the primary concern?

- A) Managed repositories cannot store dbt models larger than 100MB.
- B) Managed repositories do not support pull requests, branching, or standard Git workflows — they are not suitable for production.
- C) Managed repositories are only available on Enterprise plans.
- D) Managed repositories cannot be connected to CI jobs.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | File size limits are not a documented concern with managed repositories. |
> | **B) ✅ Correct** | Managed (dbt-hosted) repositories are intended for **trial/POC only**. They have no Git workflows, no pull requests, no branching, and no version history. dbt Labs explicitly advises against using them in production. |
> | **C) ❌ Incorrect** | Managed repositories are available on all plans — they're the default option for new accounts getting started. |
> | **D) ❌ Incorrect** | CI jobs are not the primary concern — the bigger issues are the lack of code review workflows, branching, and version history. |
>
> > 💡 **Key rule**: Managed repos = POC/trial only. No PRs, no branching. Migrate to self-hosted before production.

---

### Q9.
> **Subdomain 1.9 — Snowflake MFA authentication**

A company wants to enforce multi-factor authentication (MFA) for all dbt Cloud connections to Snowflake, including production jobs. Is this possible?

- A) Yes — MFA can be enforced for both development and production environments.
- B) No — MFA is supported for development environments only; production environments must use service accounts or key pair authentication.
- C) Yes — MFA is available for production environments when combined with PrivateLink.
- D) No — dbt Cloud does not support MFA for any Snowflake connection type.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | MFA is explicitly limited to development environments. Production jobs cannot interactively prompt for a second factor. |
> | **B) ✅ Correct** | Snowflake MFA is supported for **development environments only** in dbt Cloud. Production pipelines run unattended and cannot complete an interactive MFA challenge. Production should use service accounts or key pair authentication instead. |
> | **C) ❌ Incorrect** | PrivateLink affects network routing, not authentication method limitations. |
> | **D) ❌ Incorrect** | MFA is supported in dbt Cloud for development use — just not for production. |
>
> > 💡 **Key rule**: Snowflake MFA = **dev environments only**. Production = service account or key pair.

---

### Q10.
> **Subdomain 1.10 — Databricks connector**

A data platform team has been running dbt models on Databricks using the `dbt-spark` connector for 18 months. They're upgrading to use Unity Catalog and Python models. What changes must they make? **Select TWO correct answers.**

- A) Migrate from `dbt-spark` to `dbt-databricks` — `dbt-spark` is deprecated.
- B) Upgrade to dbt version 1.1+ for Unity Catalog support.
- C) Upgrade to dbt version 1.3+ for Python model support.
- D) Upgrade to dbt version 2.0+ for Python model support.
- E) Unity Catalog requires a Databricks Premium or Enterprise workspace tier.

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `dbt-spark` is **deprecated**. All Databricks projects must migrate to `dbt-databricks`. This is required regardless of Unity Catalog usage. |
> | **B) ❌ Incorrect** | Unity Catalog requires **dbt 1.1+** — this is correct for Unity Catalog but the question asks about *both* Python models and Unity Catalog. B is partially true but C supersedes it as the higher version requirement. |
> | **C) ✅ Correct** | Python models on Databricks require **dbt 1.3+**. Since this team needs both Unity Catalog (1.1+) and Python models (1.3+), they must be on at least 1.3. |
> | **D) ❌ Incorrect** | Python models require dbt 1.3+, not 2.0+. |
> | **E) ❌ Incorrect** | Unity Catalog workspace tier requirements are a Databricks-side concern, not a dbt-side version constraint. |
>
> > 💡 **Key rule**: Databricks: `dbt-spark` → deprecated. Unity Catalog = dbt 1.1+. Python models = dbt 1.3+.

---

---

### Q11.
> **Subdomain 1.11 — Password rotation and OAuth advantage**

A team uses username/password authentication for their Snowflake dbt Cloud connection. A security policy rotation forces all Snowflake passwords to be changed immediately. What is the impact on dbt, and what authentication method would have avoided it?

- A) No impact — dbt caches credentials and continues running until the next job restart.
- B) All dbt jobs immediately fail with authentication errors; the connection credential must be updated in Account Settings. OAuth would have avoided this.
- C) Only CI jobs fail; deploy jobs use a separate service account that is unaffected.
- D) Jobs fail only after the session expires; rotating to key pair authentication would have avoided it.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt does not cache credentials between job runs. Each connection attempt uses the stored credential, so a rotated password causes immediate failures. |
> | **B) ✅ Correct** | Username/password auth stores the password in the dbt Cloud connection. When the Snowflake password changes, dbt jobs fail immediately — the admin must update the credential in Account Settings → Connections. With **OAuth**, credential revocation and rotation happen at the warehouse side; dbt uses OAuth tokens refreshed against the warehouse, so no dbt config change is required. |
> | **C) ❌ Incorrect** | CI and deploy jobs share the same connection credentials. Both are affected equally by a password rotation. |
> | **D) ❌ Incorrect** | There is no credential caching — failures are immediate, not session-expiry-delayed. Key pair authentication would also require a credential update on rotation; OAuth is the method that eliminates this manual step. |
>
> > 💡 **Key rule**: Username/password rotation = manual update required in dbt. OAuth = revocation is warehouse-side; no dbt config change needed.

---

### Q12.
> **Subdomain 1.12 — Developer OAuth vs service token auth**

A developer configures BigQuery OAuth so they can use their personal Google account in the dbt Cloud IDE. They then try to configure a CI service token to also use the same OAuth credentials for automated jobs. What is the correct understanding of how OAuth works in dbt Cloud?

- A) OAuth can be shared between human users and service tokens by linking the OAuth app in Account Settings once.
- B) OAuth in dbt Cloud is user-level — each developer links their personal account via Profile Settings. Service tokens cannot use OAuth; they authenticate at the connection level using service account credentials.
- C) Service tokens use OAuth automatically once the organization-level OAuth app is configured.
- D) OAuth is available for all authentication scenarios in dbt Cloud, but requires Enterprise tier for service tokens.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | OAuth credentials are not shareable between users and service tokens. OAuth in dbt Cloud is strictly user-level. |
> | **B) ✅ Correct** | dbt Cloud OAuth is a **user-level** feature. Each developer links their personal warehouse account via **Profile Settings → Linked Accounts**. Service tokens are account-level automation credentials — they authenticate at the **connection level** using service account JSON, key pair, or username/password. Service tokens cannot use OAuth. |
> | **C) ❌ Incorrect** | Configuring the OAuth app at the org level enables it for human users only. Service tokens are not affected by this setup. |
> | **D) ❌ Incorrect** | OAuth for service tokens is not a supported feature on any tier. The restriction is architectural, not plan-based. |
>
> > 💡 **Key rule**: OAuth in dbt = user-level (Profile Settings). Service tokens = connection-level (service account / key pair). These are separate systems.

---

### Q13.
> **Subdomain 1.13 — Snowflake custom domain**

A company uses a custom vanity domain (`analytics.company.com`) for their Snowflake account instead of the standard locator URL. A developer configures the dbt Cloud connection using `analytics.company.com` in the Account field. The connection test fails. What is the correct way to configure this?

- A) Use the full URL `https://analytics.company.com` in the Account field.
- B) Contact Snowflake support to get the locator-format account ID that maps to the custom domain.
- C) Enter the locator-format account ID in the Account field and add `host: https://analytics.company.com` as an extended attribute on the environment.
- D) Custom domains are not supported in dbt Cloud Snowflake connections — the locator format must always be used directly.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Account field expects a locator-format ID, not a full HTTPS URL — this will cause a parsing error or silent failure. |
> | **B) ❌ Incorrect** | While the locator ID exists, Snowflake custom domains can be configured in dbt without needing to abandon the custom domain. |
> | **C) ✅ Correct** | For Snowflake custom domains, the **Account field** must still contain the locator-format account ID. The custom domain is specified separately using the extended attribute `host: https://your_custom_domain.com` on the environment. Both pieces are needed. |
> | **D) ❌ Incorrect** | Custom domains are supported — they require the `host` extended attribute alongside the locator-format account ID. |
>
> > 💡 **Key rule**: Snowflake custom domain = locator ID in Account field + `host: https://custom_domain.com` in extended attributes.

---

### Q14.
> **Subdomain 1.14 — Snowflake minimum permissions**

A new Snowflake service account is created for dbt Cloud. An admin grants only `USAGE` on the warehouse, database, and schema, plus `SELECT` on all tables. After connecting successfully, the dbt jobs fail when trying to materialize models. What is the most likely missing permission?

- A) `MONITOR` on the warehouse — required to track query execution.
- B) `CREATE TABLE` and `CREATE VIEW` on the schema — required for dbt to materialize models.
- C) `SYSADMIN` role — required for dbt to manage schemas.
- D) `OWNERSHIP` on the target schema — required for model creation.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `MONITOR` on the warehouse is not in the documented minimum permission set for dbt. |
> | **B) ✅ Correct** | `SELECT` alone is insufficient. dbt materializes models by creating or replacing tables and views. The minimum permissions include `USAGE` on warehouse/database/schema **plus** `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, and `DROP` on the schema. Without `CREATE TABLE` and `CREATE VIEW`, model materialization fails. |
> | **C) ❌ Incorrect** | `SYSADMIN` is far more permissive than needed and is not a documented requirement. A purpose-built role with specific grants is the best practice. |
> | **D) ❌ Incorrect** | `OWNERSHIP` is also overly permissive. dbt only needs specific DML/DDL grants, not ownership. |
>
> > 💡 **Key rule**: Snowflake minimum = `USAGE` (warehouse/DB/schema) + `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`.

---

### Q15.
> **Subdomain 1.15 — BigQuery OAuth setup flow**

An Enterprise-tier team successfully configures BigQuery OAuth at the organization level in dbt Cloud Account Settings. A developer on the team opens the dbt Cloud IDE but gets an authentication error even though the org-level OAuth app is configured. What step is the developer missing?

- A) The developer must request an IT admin to link their account — individual users cannot complete this step themselves.
- B) The developer must link their personal BigQuery account via **Profile Settings → Linked Accounts** in dbt Cloud.
- C) The developer must log out and back in so dbt Cloud re-reads the org-level OAuth configuration.
- D) The developer must be assigned the Database Admin permission set before OAuth becomes active for their profile.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Individual developers complete this step themselves in their own profile — it is not an admin-delegated action. |
> | **B) ✅ Correct** | Org-level OAuth setup is only step one. Each developer must independently link their personal BigQuery Google account by navigating to **Profile Settings → Linked Accounts** in dbt Cloud. Until they do, the IDE falls back to the connection-level service account credentials, or fails if none are configured. |
> | **C) ❌ Incorrect** | Logging out does not trigger the personal OAuth linking flow. The developer must explicitly navigate to Profile Settings. |
> | **D) ❌ Incorrect** | OAuth personal linking is not gated on any specific permission set — any developer with IDE access can complete this step. |
>
> > 💡 **Key rule**: BigQuery OAuth = two steps: (1) admin sets up org OAuth app; (2) each developer links personal account via Profile Settings → Linked Accounts.

---

### Q16.
> **Subdomain 1.16 — Databricks Unity Catalog naming and permissions**

A team migrates their Databricks dbt project to Unity Catalog. After enabling the Catalog field in their dbt Cloud environment and running their models, they notice model references in SQL use two-part names (`schema.model`) instead of three-part names. They also get `USE CATALOG` permission errors. What explains both issues?

- A) Three-part naming requires dbt 1.6+ — the team is on an older version.
- B) Unity Catalog three-part naming (`catalog.schema.model`) is only enabled automatically when `dbt-databricks` is used. The `USE CATALOG` error occurs because the service account lacks `USE CATALOG` and `USE SCHEMA` privileges.
- C) The Catalog field in the environment must be set to the catalog name; three-part naming then becomes automatic, and `USE CATALOG` is granted by the `SYSADMIN` role automatically.
- D) Three-part naming must be enabled manually in `dbt_project.yml` using the `quoting` config block.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Unity Catalog support was added in dbt 1.1+ — version is not the root cause here. |
> | **B) ✅ Correct** | With `dbt-databricks` and a Catalog field set in the environment, Unity Catalog **three-part naming** (`catalog.schema.model`) is enabled automatically. The `USE CATALOG` error confirms the service account is missing required Unity Catalog permissions: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW`, and `MODIFY` must all be granted explicitly. |
> | **C) ❌ Incorrect** | `SYSADMIN` does not auto-grant Unity Catalog permissions — these must be explicitly granted via `GRANT` statements in Databricks. |
> | **D) ❌ Incorrect** | Three-part naming is controlled by the Catalog field in the environment, not `dbt_project.yml` quoting config. |
>
> > 💡 **Key rule**: Databricks Unity Catalog = three-part naming auto-enabled when Catalog field is set. Required permissions: `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `MODIFY`.

---

### Q17.
> **Subdomain 1.17 — Databricks required connection fields**

An architect is documenting the minimum required fields for a Databricks connection in dbt Cloud. Which two fields are always required regardless of whether Unity Catalog is used?

- A) Server Hostname and Catalog
- B) Server Hostname and HTTP Path
- C) HTTP Path and Token
- D) Catalog and Token

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Catalog is **optional** — it is only needed when using Unity Catalog. It is not a required field. |
> | **B) ✅ Correct** | **Server Hostname** (the Databricks workspace URL) and **HTTP Path** (the SQL warehouse or cluster endpoint) are always required for any Databricks connection. The Token (personal access token or service principal credential) is also required for authentication, but Catalog is optional and only used for Unity Catalog. |
> | **C) ❌ Incorrect** | HTTP Path + Token alone are insufficient — Server Hostname is also required and is one of the two most fundamental fields. |
> | **D) ❌ Incorrect** | Catalog is optional, and Token alone without Server Hostname and HTTP Path is not sufficient to establish a connection. |
>
> > 💡 **Key rule**: Databricks required fields = **Server Hostname** + **HTTP Path**. Catalog is optional (Unity Catalog only). Token is required for auth.

---

### Q18.
> **Subdomain 1.18 — Platform-specific editable environment fields**

A team uses Redshift as their data warehouse. An architect wants to use the environment UI to override the schema that a production deployment job writes to, separate from the connection-level schema. They navigate to the environment settings but find no editable schema field. What is the correct approach?

- A) The schema field is hidden by default — enable "Advanced mode" in the environment settings to reveal it.
- B) Redshift environment settings have no editable connection fields in the UI; schema overrides must be done via extended attributes on the environment.
- C) Redshift schema overrides must be set at the job level using environment variables, not at the environment level.
- D) Redshift connections require the schema to be defined at the connection level — it cannot be overridden per environment.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no "Advanced mode" toggle that reveals hidden Redshift environment fields. |
> | **B) ✅ Correct** | For **Postgres, Redshift, BigQuery, and Spark**, the environment UI has **no editable connection fields** — all settings are inferred from the project connection. To override values like schema, use **extended attributes** (a YAML snippet in the environment settings that overrides `profiles.yml` top-level keys). Snowflake is the exception — it exposes Role, Database, and Warehouse as editable fields directly in the environment UI. |
> | **C) ❌ Incorrect** | While job-level environment variables can influence schema naming via custom macros, the canonical override mechanism at the environment level is extended attributes. |
> | **D) ❌ Incorrect** | Redshift schemas can be overridden per environment — just not via a UI field. Extended attributes are the mechanism. |
>
> > 💡 **Key rule**: Snowflake = editable Role/Database/Warehouse in environment UI. Postgres/Redshift/BigQuery/Spark = no UI fields; use extended attributes.

---

### Q19.
> **Subdomain 1.19 — Single-warehouse constraint per job**

An architect proposes a dbt Cloud architecture where a single production job writes transformed models to both a Snowflake data warehouse and a Redshift warehouse simultaneously, using two separate connections defined in the same project. Is this possible?

- A) Yes — dbt Cloud supports multi-warehouse jobs by specifying multiple target profiles in the job configuration.
- B) Yes — but only on Enterprise+ plan where multiple connections per job are supported.
- C) No — each environment references exactly one connection, and a single job cannot write to two warehouses simultaneously.
- D) No — but the same job can write to two schemas within the same warehouse using the `schema` config on individual models.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not support specifying multiple target profiles for a single job. Each job runs against one environment, which has one connection. |
> | **B) ❌ Incorrect** | Multi-warehouse jobs are not a feature on any dbt Cloud plan. |
> | **C) ✅ Correct** | A dbt Cloud environment references **exactly one connection**, and a job runs in exactly one environment. Therefore, a single job cannot write to two different warehouses simultaneously. Different environments (e.g., dev on Snowflake, prod on Redshift) can use different connections, but each environment is single-warehouse. Splitting writes across warehouses requires separate projects and separate jobs. |
> | **D) ❌ Incorrect** | While models can write to different schemas within one warehouse, this answer sidesteps the actual question about cross-warehouse writes, which remain unsupported. |
>
> > 💡 **Key rule**: One environment = one connection = one warehouse. A single job cannot write to two warehouses simultaneously.

---

### Q20.
> **Subdomain 1.20 — Managed repository migration**

A startup used a dbt-managed (dbt-hosted) repository to prototype their first dbt project over three months. The project is now ready for production. An architect reviews the setup and insists they must migrate before going live. Which of the following is NOT a valid reason to migrate away from a managed repository?

- A) Managed repositories do not support pull requests or code review workflows.
- B) Managed repositories cannot be connected to external CI/CD systems.
- C) Managed repositories do not support branching or Git version history.
- D) Managed repositories cannot be exported to a self-hosted Git provider.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Not the answer** | This IS a valid reason — managed repos have no PR or code review workflow, making them unsuitable for production team collaboration. (A valid reason to migrate.) |
> | **B) ❌ Not the answer** | This IS a valid reason — without a real Git provider, external CI/CD integration is not possible. (A valid reason to migrate.) |
> | **C) ❌ Not the answer** | This IS a valid reason — managed repos have no branching, no version history, and no Git workflow capabilities. (A valid reason to migrate.) |
> | **D) ✅ Correct (NOT a valid reason)** | Managed repositories **can** be exported to a self-hosted Git provider at any time. This is explicitly supported. So "cannot be exported" is false — it is NOT a valid reason to urgently migrate. The urgency comes from the lack of PR workflows, branching, and version history, not from being trapped. |
>
> > 💡 **Key rule**: Managed repos = no PRs, no branching, no version history — not for production. BUT they CAN be exported to self-hosted at any time.

---

*[End of Topic 1 — 20 questions]*

