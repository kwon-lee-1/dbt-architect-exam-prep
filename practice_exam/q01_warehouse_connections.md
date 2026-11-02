# Topic 1: Warehouse Connections — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1.
> **Subdomain 1.1 — Snowflake account identifier format**

A developer sets up a new Snowflake connection in dbt Cloud. They enter `db5261993.snowflakecomputing.com` as the account identifier. The connection test fails. What is the most likely cause?

- A) The user account does not have the required `USAGE` privilege on the warehouse.
- B) The dbt Cloud IP addresses are not whitelisted in Snowflake's network policy.
- C) The Account value still includes the `snowflakecomputing.com` domain.
- D) The Snowflake warehouse is suspended and needs to be resumed before dbt can connect.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Missing privileges would cause permission errors on specific operations, not a connection-level failure. |
> | **B) ❌ Incorrect** | A blocked IP is a different problem. The docs name the Account value as the most common cause. |
> | **C) ✅ Correct** | Use `db5261993` or `db5261993.east-us-2.azure`, not the full `.snowflakecomputing.com` domain. The docs say the most common cause of a failed connection test is an Account value that still includes `snowflakecomputing.com`. |
> | **D) ❌ Incorrect** | A suspended warehouse is not what the docs name as the most common cause. |
>
> > 💡 **Key rule**: Snowflake account ID = locator format only (`db5261993.east-us-2.azure`). Never use the full `.snowflakecomputing.com` URL.

---

### Q2.
> **Subdomain 1.2 — IP allowlisting**

A team allowlists dbt IP addresses in their warehouse firewall. The docs warn that those IPs can change occasionally. What do the docs recommend as the stable reference?

- A) dbt platform hostnames (for example `abc123.us1.dbt.com`).
- B) Allowlist the cloud provider's entire IP range.
- C) Re-check the IP list every quarter.
- D) Switch to PrivateLink on the Starter plan.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say to use dbt platform hostnames, which stay consistent even if the underlying IPs change. |
> | **B) ❌ Incorrect** | Not a documented recommendation. |
> | **C) ❌ Incorrect** | Not a documented recommendation. |
> | **D) ❌ Incorrect** | Private connectivity is for Enterprise+ and Virtual Private plans, not Starter. |
>
> > 💡 **Key rule**: Multi-tenant IPs are listed per region (Project Settings → Connection → Settings). They can change occasionally, so use hostnames as the stable reference. Single-tenant: ask Support for your IPs.

---

### Q3.
> **Subdomain 1.3 — PrivateLink**

Which statements about dbt's private connectivity (PrivateLink) are correct? **Select TWO correct answers.**

- A) It connects dbt to your warehouse without traversing the public internet.
- B) Private endpoint settings can be set with environment variables.
- C) It is available on all plans including Starter.
- D) dbt and the data platform must be hosted on the same cloud provider.
- E) It automatically configures IP allowlisting in your warehouse.

> [!success]- Answer & Explanations
> **✅ Correct: A, D**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs describe it as connectivity between dbt and your data platform without traversing the public internet. |
> | **B) ❌ Incorrect** | Environment variables aren't supported for private endpoint settings. Use extended attributes. |
> | **C) ❌ Incorrect** | Private connectivity is for **Enterprise+** and **Virtual Private** plans. |
> | **D) ✅ Correct** | Both dbt and the server (like Snowflake) must be on the same cloud provider. dbt on AWS can't reach a service on Azure. |
> | **E) ❌ Incorrect** | Not documented. The docs don't say it changes IP allowlisting. |
>
> > 💡 **Key rule**: Private connectivity = Enterprise+ / Virtual Private, same cloud on both sides. With ingress PrivateLink or IP allowlisting, CI hooks may be unavailable and CI can fail silently.

---

### Q4. ⭐
> **Subdomain 1.4 — Snowflake key pair errors**

A team configures Snowflake key pair authentication. The connection fails with the error "Could not deserialize key data." What is the most likely cause?

- A) The public key wasn't set on the Snowflake user.
- B) The private key was pasted incorrectly, for example missing dashes or the BEGIN/END lines.
- C) The passphrase is too long.
- D) Key pair authentication isn't supported for Snowflake in dbt.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A wrong or missing public key points to a `JWT token is invalid` error instead. |
> | **B) ✅ Correct** | The docs say this error usually comes from mistakes like not copying correctly, missing dashes, or leaving out the commented lines. Verify the key in a text editor before pasting. |
> | **C) ❌ Incorrect** | Not a documented cause. |
> | **D) ❌ Incorrect** | Key pair is the default for new Snowflake credentials, in development and deployment. |
>
> > 💡 **Key rule**: "Could not deserialize key data" = bad paste (missing dashes / BEGIN-END lines). dbt v2 (Fusion) wants PKCS#8 + AES-256 and doesn't support 3DES or headerless keys. The private key can't come from an env var.

---

### Q5.
> **Subdomain 1.5 — Connections are account-level**

An organization has three dbt Cloud projects: `sales`, `marketing`, and `finance`. They want `sales` and `marketing` to use the same Snowflake account but with different warehouse names. Which of the following is true?

- A) The connection must be duplicated per project, but the credentials can be the same.
- B) Connections are project-level, so `sales` and `marketing` will automatically use different connections.
- C) Each project must have its own dedicated connection — connections cannot be shared across projects.
- D) A single connection can be shared across multiple projects; environment-level settings control warehouse overrides.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no need to duplicate connections. The same connection object is referenced by multiple projects. |
> | **B) ❌ Incorrect** | Connections are account-level, not project-level. Multiple projects can and do share the same connection. |
> | **C) ❌ Incorrect** | This is the opposite of how dbt Cloud works. Connections are account-level and are explicitly designed to be shared. |
> | **D) ✅ Correct** | Connections are **account-level** — shared across multiple projects. Different projects (or different environments within a project) can override warehouse-level settings at the environment level without needing separate connections. |
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
> | **B) ✅ Correct** | BigQuery OAuth is available for **development environments on Enterprise-tier plans only**. Starter teams use a service JSON keyfile. |
> | **C) ❌ Incorrect** | There is no Starter-with-IDE-only exception. The restriction is plan-level regardless of environment type. |
> | **D) ❌ Incorrect** | BigQuery does support OAuth in dbt Cloud — it's just gated to Enterprise plans. |
>
> > 💡 **Key rule**: BigQuery OAuth = development only, Enterprise tier. After org setup, each user connects under **Credentials → Native OAuth**.

---

### Q7. ⭐
> **Subdomain 1.7 — Adding the OAuth Client ID and Secret**

An Enterprise team has created a BigQuery OAuth client in Google Cloud. Where do they add the client ID and secret in dbt?

- A) Account settings → Connections → the BigQuery connection → OAuth 2.0 Settings.
- B) Account settings → Integrations.
- C) An environment variable.
- D) Each developer's Credentials page.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Add the client ID and secret under **OAuth 2.0 Settings** on the connection. The token URI default is `https://oauth2.googleapis.com/token`. The Redirect URI you give Google comes from the connection's Development OAuth section. |
> | **B) ❌ Incorrect** | Integrations is where Git providers go, not warehouse OAuth. |
> | **C) ❌ Incorrect** | Not documented. |
> | **D) ❌ Incorrect** | Developers use their Credentials page afterwards, to connect with Native OAuth. |
>
> > 💡 **Key rule**: Client ID + Secret go on the **connection** (Account settings → Connections). Snowflake works the same way: edit the connection and enter them. Both need Enterprise/Enterprise+.

---

### Q8.
> **Subdomain 1.8 — Managed repositories**

An architect is reviewing a team's setup. They find that a dbt Cloud project in active production use is configured with a managed (dbt-hosted) repository instead of a self-hosted Git repository. Which of the following is the primary concern?

- A) Managed repositories are only available on Enterprise plans.
- B) Managed repositories cannot be connected to CI jobs.
- C) Managed repositories can't use Git features like pull requests, and dbt Labs recommends against them in production.
- D) Managed repositories cannot store dbt models larger than 100MB.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Plan availability isn't the documented concern. |
> | **B) ❌ Incorrect** | CI jobs are not the primary concern — the bigger issues are the lack of code review workflows, branching, and version history. |
> | **C) ✅ Correct** | The docs describe managed repositories as a way to trial dbt. You can't use Git features like pull requests, and dbt Labs recommends against using one in production. |
> | **D) ❌ Incorrect** | File size limits are not a documented concern with managed repositories. |
>
> > 💡 **Key rule**: Managed repos = for trials. No pull requests. dbt Labs recommends against production. You can export any time.

---

### Q9.
> **Subdomain 1.9 — Snowflake authentication methods**

A team tries to create new Snowflake credentials in dbt using username and password. What happens?

- A) It works for deployment credentials only.
- B) It works for development credentials only.
- C) It works, with MFA enforced.
- D) It isn't allowed. Key pair is the default for new development and deployment credentials.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not for new credentials. Deployment uses key pair. |
> | **B) ❌ Incorrect** | Not for new credentials. Snowflake OAuth is the development-only option (Enterprise). |
> | **C) ❌ Incorrect** | New username/password credentials can't be created. |
> | **D) ✅ Correct** | The docs say you cannot create new Snowflake credentials with username and password. New credentials default to key pair. |
>
> > 💡 **Key rule**: New = key pair (dev + deploy) or Snowflake OAuth (dev only, Enterprise). Existing username/password + MFA credentials remain, but can't be saved until switched. MFA uses `authenticator: username_password_mfa` in the dev environment.

---

### Q10.
> **Subdomain 1.10 — Databricks connector**

A data platform team has been running dbt models on Databricks using the `dbt-spark` connector for 18 months. They're upgrading to use Unity Catalog and Python models. What changes must they make? **Select TWO correct answers.**

- A) Migrate from `dbt-spark` to `dbt-databricks` — `dbt-spark` is deprecated.
- B) Upgrade to dbt version 1.3+ for Python model support.
- C) Upgrade to dbt version 2.0+ for Python model support.
- D) Unity Catalog requires a Databricks Premium or Enterprise workspace tier.
- E) Upgrade to dbt version 1.6+ for Unity Catalog support.

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `dbt-spark` is **deprecated**. All Databricks projects must migrate to `dbt-databricks`. This is required regardless of Unity Catalog usage. |
> | **B) ✅ Correct** | Python models are available starting with **dbt 1.3**. |
> | **C) ❌ Incorrect** | Python models require dbt 1.3+, not 2.0+. |
> | **D) ❌ Incorrect** | Unity Catalog workspace tier requirements are a Databricks-side concern, not a dbt-side version constraint. |
> | **E) ❌ Incorrect** | Unity Catalog is available starting with dbt 1.1. There is no 1.6 requirement. |
>
> > 💡 **Key rule**: Databricks: `dbt-spark` → deprecated. Unity Catalog = dbt 1.1+. Python models = dbt 1.3+.

---

---

### Q11.
> **Subdomain 1.11 — Existing password credentials**

A Snowflake deployment environment still uses username/password credentials. An admin wants to edit and save them. What must happen first?

- A) Nothing. Password credentials can be edited freely.
- B) Enable PrivateLink.
- C) Add `authenticator: username_password_mfa` to extended attributes.
- D) Switch the Auth method to key pair (or OAuth). Password credentials can't be saved.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say you can view existing password credentials but can't save changes until you switch the Auth method. |
> | **B) ❌ Incorrect** | Unrelated to authentication. |
> | **C) ❌ Incorrect** | That attribute is for MFA with username/password in the dev environment. It doesn't let you save. |
> | **D) ✅ Correct** | Switch to key pair. Snowflake OAuth is development-only. |
>
> > 💡 **Key rule**: Password credentials are legacy. Key pair is the default for new dev and deploy credentials.

---

### Q12.
> **Subdomain 1.12 — OAuth vs deployment credentials**

Developers use BigQuery OAuth in the IDE. How does a production job authenticate to BigQuery?

- A) With a native OAuth login shared by all users.
- B) With a service JSON keyfile (or Workload Identity Federation on Enterprise) set on the connection.
- C) With a dbt service token.
- D) With the developer's OAuth token.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | OAuth is per user. Service-to-service OAuth isn't supported. |
> | **B) ✅ Correct** | Deployment environments use Service JSON, or Workload Identity Federation (Enterprise, Entra ID only). |
> | **C) ❌ Incorrect** | Service tokens authenticate to the dbt API for system-level integrations. They don't log in to the warehouse. |
> | **D) ❌ Incorrect** | Native OAuth applies to development. Every developer connects with their own account. |
>
> > 💡 **Key rule**: OAuth = development, per user. Deployment = service JSON / WIF (BigQuery) or key pair (Snowflake). Service tokens are for the dbt API.

---

### Q13.
> **Subdomain 1.13 — Snowflake custom domain**

A company uses a custom vanity domain (`analytics.company.com`) for their Snowflake account instead of the standard locator URL. A developer configures the dbt Cloud connection using `analytics.company.com` in the Account field. The connection test fails. What is the correct way to configure this?

- A) Enter the locator-format account ID in the Account field and add `host: https://analytics.company.com` as an extended attribute on the environment.
- B) Custom domains are not supported in dbt Cloud Snowflake connections — the locator format must always be used directly.
- C) Contact Snowflake support to get the locator-format account ID that maps to the custom domain.
- D) Use the full URL `https://analytics.company.com` in the Account field.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | For Snowflake custom domains, the **Account field** must still contain the locator-format account ID. The custom domain is specified separately using the extended attribute `host: https://your_custom_domain.com` on the environment. Both pieces are needed. |
> | **B) ❌ Incorrect** | Custom domains are supported — they require the `host` extended attribute alongside the locator-format account ID. |
> | **C) ❌ Incorrect** | While the locator ID exists, Snowflake custom domains can be configured in dbt without needing to abandon the custom domain. |
> | **D) ❌ Incorrect** | The Account field takes a locator-style value, not a full HTTPS URL. The custom domain goes in the `host` attribute. |
>
> > 💡 **Key rule**: Snowflake custom domain = locator ID in Account field + `host: https://custom_domain.com` in extended attributes.

---

### Q14.
> **Subdomain 1.14 — Snowflake minimum permissions**

A new Snowflake service account is created for dbt Cloud. An admin grants only `USAGE` on the warehouse, database, and schema, plus `SELECT` on all tables. After connecting successfully, the dbt jobs fail when trying to materialize models. What is the most likely missing permission?

- A) `MONITOR` on the warehouse — required to track query execution.
- B) `OWNERSHIP` on the target schema — required for model creation.
- C) `CREATE TABLE` and `CREATE VIEW` on the schema — required for dbt to materialize models.
- D) `SYSADMIN` role — required for dbt to manage schemas.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `MONITOR` on the warehouse is not in the documented minimum permission set for dbt. |
> | **B) ❌ Incorrect** | `OWNERSHIP` is also overly permissive. dbt only needs specific DML/DDL grants, not ownership. |
> | **C) ✅ Correct** | `SELECT` alone is insufficient. dbt materializes models by creating or replacing tables and views. The minimum permissions include `USAGE` on warehouse/database/schema **plus** `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, and `DROP` on the schema. Without `CREATE TABLE` and `CREATE VIEW`, model materialization fails. |
> | **D) ❌ Incorrect** | `SYSADMIN` is far more permissive than needed and is not a documented requirement. A purpose-built role with specific grants is the best practice. |
>
> > 💡 **Key rule**: Snowflake minimum = `USAGE` (warehouse/DB/schema) + `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`.

---

### Q15.
> **Subdomain 1.15 — BigQuery OAuth setup flow**

An Enterprise-tier team successfully configures BigQuery OAuth at the organization level in dbt Cloud Account Settings. A developer on the team opens the dbt Cloud IDE but gets an authentication error even though the org-level OAuth app is configured. What step is the developer missing?

- A) The developer must connect their own BigQuery account under Credentials (Native OAuth → Connect to BigQuery).
- B) The developer must log out and back in so dbt Cloud re-reads the org-level OAuth configuration.
- C) The developer must request an IT admin to link their account — individual users cannot complete this step themselves.
- D) The developer must be assigned the Database Admin permission set before OAuth becomes active for their profile.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The org-level setup is step one. With BigQuery OAuth on, every developer must authenticate with BigQuery to use dev tools like the IDE: Account settings → Credentials → pick the project → Authentication Method = Native OAuth → Connect to BigQuery. |
> | **B) ❌ Incorrect** | Logging out does not trigger the personal OAuth linking flow. The developer must explicitly connect under Credentials. |
> | **C) ❌ Incorrect** | Individual developers complete this step themselves in their own profile — it is not an admin-delegated action. |
> | **D) ❌ Incorrect** | Not a documented requirement. |
>
> > 💡 **Key rule**: BigQuery OAuth = two steps: (1) admin adds the client ID/secret on the connection; (2) each developer connects under Credentials → Native OAuth.

---

### Q16.
> **Subdomain 1.16 — Databricks Unity Catalog permissions**

A team moves a Databricks project to Unity Catalog. Which privileges does the Databricks user or service principal need?

- A) `USAGE` and `SELECT` only.
- B) Ownership of the metastore.
- C) `SYSADMIN`.
- D) `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW` and `MODIFY` (plus `CREATE SCHEMA` if dbt creates schemas).

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `USAGE` is a Hive metastore privilege, and `SELECT` alone can't create tables or views. |
> | **B) ❌ Incorrect** | Not a documented requirement. |
> | **C) ❌ Incorrect** | `SYSADMIN` is a Snowflake role, not a Databricks privilege. |
> | **D) ✅ Correct** | That is the documented Unity Catalog list. |
>
> > 💡 **Key rule**: Unity Catalog = `USE CATALOG`, `USE SCHEMA`, `SELECT`, `CREATE TABLE`, `CREATE VIEW`, `MODIFY`. Hive metastore = `USAGE`, `SELECT`, `CREATE`, `MODIFY`.

---

### Q17.
> **Subdomain 1.17 — Databricks required connection fields**

An architect is documenting the minimum required fields for a Databricks connection in dbt Cloud. Which two fields are always required regardless of whether Unity Catalog is used?

- A) HTTP Path and Token
- B) Server Hostname and HTTP Path
- C) Server Hostname and Catalog
- D) Catalog and Token

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | HTTP Path + Token alone are insufficient — Server Hostname is also required and is one of the two most fundamental fields. |
> | **B) ✅ Correct** | **Server Hostname** (the Databricks workspace URL) and **HTTP Path** (the SQL warehouse or cluster endpoint) are always required for any Databricks connection. The Token (personal access token or service principal credential) is also required for authentication, but Catalog is optional and only used for Unity Catalog. |
> | **C) ❌ Incorrect** | Catalog is **optional** — it is only needed when using Unity Catalog. It is not a required field. |
> | **D) ❌ Incorrect** | Catalog is optional, and Token alone without Server Hostname and HTTP Path is not sufficient to establish a connection. |
>
> > 💡 **Key rule**: Databricks required fields = **Server Hostname** + **HTTP Path**. Catalog is optional (Unity Catalog only). Token is required for auth.

---

### Q18.
> **Subdomain 1.18 — Platform-specific editable environment fields**

A team uses Redshift as their data warehouse. An architect wants to use the environment UI to override the schema that a production deployment job writes to, separate from the connection-level schema. They navigate to the environment settings but find no editable schema field. What is the correct approach?

- A) Redshift schema overrides must be set at the job level using environment variables, not at the environment level.
- B) Redshift connections require the schema to be defined at the connection level — it cannot be overridden per environment.
- C) Redshift environment settings have no editable connection fields in the UI; schema overrides must be done via extended attributes on the environment.
- D) The schema field is hidden by default — enable "Advanced mode" in the environment settings to reveal it.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | While job-level environment variables can influence schema naming via custom macros, the canonical override mechanism at the environment level is extended attributes. |
> | **B) ❌ Incorrect** | Redshift schemas can be overridden per environment — just not via a UI field. Extended attributes are the mechanism. |
> | **C) ✅ Correct** | For **Postgres, Redshift, BigQuery, and Spark**, the environment UI has **no editable connection fields** — all settings are inferred from the project connection. To override values like schema, use **extended attributes** (a YAML snippet in the environment settings that overrides `profiles.yml` top-level keys). Snowflake is the exception — it exposes Role, Database, and Warehouse as editable fields directly in the environment UI. |
> | **D) ❌ Incorrect** | There is no "Advanced mode" toggle that reveals hidden Redshift environment fields. |
>
> > 💡 **Key rule**: Snowflake = editable Role/Database/Warehouse in environment UI. Postgres/Redshift/BigQuery/Spark = no UI fields; use extended attributes.

---

### Q19.
> **Subdomain 1.19 — Single-warehouse constraint per job**

An architect proposes a dbt Cloud architecture where a single production job writes transformed models to both a Snowflake data warehouse and a Redshift warehouse simultaneously, using two separate connections defined in the same project. Is this possible?

- A) No — each environment references exactly one connection, and a single job cannot write to two warehouses simultaneously.
- B) Yes — but only on Enterprise+ plan where multiple connections per job are supported.
- C) Yes — dbt Cloud supports multi-warehouse jobs by specifying multiple target profiles in the job configuration.
- D) No — but the same job can write to two schemas within the same warehouse using the `schema` config on individual models.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | A dbt Cloud environment references **exactly one connection**, and a job runs in exactly one environment. Therefore, a single job cannot write to two different warehouses simultaneously. Different environments (e.g., dev on Snowflake, prod on Redshift) can use different connections, but each environment is single-warehouse. |
> | **B) ❌ Incorrect** | Multi-warehouse jobs are not a feature on any dbt Cloud plan. |
> | **C) ❌ Incorrect** | dbt Cloud does not support specifying multiple target profiles for a single job. Each job runs against one environment, which has one connection. |
> | **D) ❌ Incorrect** | While models can write to different schemas within one warehouse, this answer sidesteps the actual question about cross-warehouse writes, which remain unsupported. |
>
> > 💡 **Key rule**: One environment = one connection = one warehouse. A single job cannot write to two warehouses simultaneously.

---

### Q20.
> **Subdomain 1.20 — Managed repository migration**

A startup prototyped on a dbt-managed repository and is now ready for production. Which of the following is NOT a valid reason to move away from it?

- A) You can't use Git features like pull requests.
- B) It can't be exported to a self-hosted Git provider.
- C) dbt Labs recommends against using a managed repository in production.
- D) It is meant for trying dbt without your own repository.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Not the answer** | This is a valid reason. The docs say you can't use Git features like pull requests. |
> | **B) ✅ Correct (NOT a valid reason)** | The docs say you can export the repository from dbt at any time (project settings → repo link → Deploy key → Download repository). |
> | **C) ❌ Not the answer** | This is a valid reason. The docs say so directly. |
> | **D) ❌ Not the answer** | This is a valid reason. The docs call it a way to trial dbt. |
>
> > 💡 **Key rule**: Managed repo = trial, no pull requests, not recommended for production, but you can export it any time.

---

*[End of Topic 1 — 20 questions]*

