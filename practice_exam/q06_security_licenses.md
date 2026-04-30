# Topic 5: Security & Licenses — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 22 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 5.1 — IT license ignores group permissions**

A new hire needs to manage users, groups, and SSO settings, but should have no access to the dbt IDE, jobs, or data. An admin assigns them an IT license and adds them to the Account Admin group. What level of access will this user have?

- A) Full Account Admin access — the Account Admin group overrides license restrictions for IT users.
- B) Fixed IT access only: Security Admin + Billing Admin + edit Connections. The Account Admin group assignment has zero effect.
- C) IT access plus the ability to run jobs since Account Admin includes job execution.
- D) The assignment will fail — IT-licensed users cannot be added to the Account Admin group.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | IT and Read-Only licenses are the two license types that **do not inherit from any permission sets**. Group assignment is completely irrelevant for these users. |
> | **B) ✅ Correct** | **IT-licensed users have fixed, non-overridable access**: Security Admin + Billing Admin + the ability to edit Connections. No matter which group they're in — including Account Admin — their access does not change. To get the admin's intended capability (user/group/SSO management), the IT license is actually correct for that purpose. But they'll never get IDE or job access. |
> | **C) ❌ Incorrect** | IT license does not inherit job execution from Account Admin group. |
> | **D) ❌ Incorrect** | Technically you can add IT-licensed users to any group — but the group membership has zero effect on their access. |
>
> > 💡 **Key rule**: IT and Read-Only licenses **ignore all group assignments**. License type = fixed access, no override possible.

---

### Q2. ⭐
> **Subdomain 5.2 — Read-Only license trap**

A contractor needs view-only access to a specific project's models in dbt Catalog. An admin assigns them a Read-Only license and adds them to the Developer group for that project. Can they now edit models in the IDE?

- A) Yes — the Developer group grants IDE access, which the Read-Only license allows at the project level.
- B) No — Read-Only license users do not inherit from any permission sets. They can only view artifacts and the deploy section, regardless of group membership.
- C) Yes — but only in the IDE's read-only mode (no execution, no saves).
- D) No — they can't access the IDE, but the Developer group gives them access to dbt Cloud's API.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Developer group cannot elevate a Read-Only license — the license type always overrides group permissions. |
> | **B) ✅ Correct** | **Read-Only license users do not inherit rights from any permission sets**. Their access is identical regardless of which groups they belong to: view artifacts and the deploy section (jobs, runs, schedules) only. No IDE access, no job execution, no editing. The Developer group assignment has zero effect. |
> | **C) ❌ Incorrect** | There is no "read-only IDE mode" — IDE access is binary, and Read-Only license users cannot access it at all. |
> | **D) ❌ Incorrect** | Read-Only license does not grant any elevated API access through group membership. |
>
> > 💡 **Key rule**: Read-Only license = **fixed access only** (view artifacts + deploy section). Groups irrelevant. Identical access for all Read-Only users.

---

### Q3. ⭐
> **Subdomain 5.3 — Service token: one-time visibility**

An admin creates a new service token to use in a CI/CD pipeline. They close the dialog before saving the token value. How can they recover the token?

- A) The token value can be retrieved from Account Settings → API Tokens at any time.
- B) The token can be re-revealed by clicking "Show Token" in the service token settings.
- C) The token value is shown only once — it cannot be recovered. Delete it, create a new one, and update all integrations.
- D) Contact dbt Cloud support with the token name to retrieve the value.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | After the initial creation dialog is closed, the token value is not stored in a retrievable form in the UI. |
> | **B) ❌ Incorrect** | There is no "Show Token" button after initial creation — the value is permanently obscured. |
> | **C) ✅ Correct** | Service token values are shown **exactly once** at creation time. If the dialog is closed before saving the value, it is permanently unrecoverable. The only path forward is to delete the existing token, create a new one, and update all integrations that used the old token. |
> | **D) ❌ Incorrect** | dbt Labs support cannot reveal stored token values — they are not stored in recoverable form. |
>
> > 💡 **Key rule**: Service token = **one-time reveal**. Save immediately. Lost token = delete → create new → update all integrations.

---

### Q4. ⭐
> **Subdomain 5.4 — Service token 403 error**

A service token is configured correctly and has the right permission sets, but all API calls return `403 Forbidden`. The token was created recently and the credentials haven't changed. What is the most likely cause?

- A) The service token has expired — tokens expire after 90 days by default.
- B) The service token was created before the last SSO configuration change and needs to be rotated.
- C) The calling IP address is not on the account's IP allowlist — service tokens honor IP restrictions just like human logins.
- D) The service token needs to be assigned to a specific project before it can make API calls.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Service tokens do not have a 90-day expiration — they don't expire on a time schedule (unlike OAuth tokens). |
> | **B) ❌ Incorrect** | SSO configuration changes do not invalidate service tokens — service tokens are separate from SSO. |
> | **C) ✅ Correct** | **Service tokens honor IP restriction allowlists** exactly like human user logins. If the CI server or automation tool's IP is not on the account's allowlist, all API calls will return `403 Forbidden` — even if the token itself is valid and correctly permissioned. |
> | **D) ❌ Incorrect** | Service tokens can be scoped to projects, but a missing project assignment would result in a permissions error on project-specific endpoints, not a blanket `403` on all API calls. |
>
> > 💡 **Key rule**: Service token `403` = check **IP allowlist** first. Service tokens respect IP restrictions.

---

### Q5. ⭐
> **Subdomain 5.5 — Security Admin cannot trigger jobs**

During an incident, a Security Admin is the only person available. They need to manually trigger a production job to restore data. They find they cannot access the Jobs page at all. Why?

- A) Security Admin requires 2FA to access the Jobs page during an incident.
- B) Security Admin has zero access to jobs, runs, or environments — it is purely an administrative role for user/group/SSO/IP management.
- C) Jobs can only be triggered by the Account Owner during incidents.
- D) The Security Admin needs to be temporarily added to the Job Runner group.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | 2FA for incident access is not a documented dbt Cloud requirement. |
> | **B) ✅ Correct** | **Security Admin has zero data access** — no IDE, no jobs, no runs, no environments. It is scoped purely to: managing users, groups, licenses, SSO configuration, and IP restrictions. To trigger jobs in an incident, the correct role is **Job Admin** or **Job Runner**. |
> | **C) ❌ Incorrect** | Job triggering is not exclusive to Account Owners. |
> | **D) ❌ Incorrect** | This suggestion reflects the correct fix but the question asks why they can't currently trigger jobs — Security Admin's scope doesn't include jobs. |
>
> > 💡 **Key rule**: Security Admin = **zero data access**. No IDE, no jobs, no runs. For job execution: Job Admin or Job Runner.

---

### Q6.
> **Subdomain 5.6 — Database Admin and IDE access**

A Database Admin user wants to write a quick SQL fix directly in the dbt Cloud IDE. Can they?

- A) Yes — Database Admin includes read/write IDE access for all projects they manage.
- B) Yes — but only in view mode; they cannot execute queries.
- C) No — Database Admin manages data platform configs and Semantic Layer settings but has no IDE access.
- D) Yes — Database Admin includes IDE access equivalent to the Developer role.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Database Admin is explicitly a non-IDE role focused on platform configuration. |
> | **B) ❌ Incorrect** | There is no "view mode" IDE access — IDE access is binary based on role. |
> | **C) ✅ Correct** | **Database Admin does not include IDE access**. The role is scoped to: data platform configurations, environment variables, and Semantic Layer configuration. To write code in the IDE, a user needs the Developer, Analyst, or Admin permission set. This is a common trap — "Database Admin" sounds like it should have more data access than it does. |
> | **D) ❌ Incorrect** | Database Admin ≠ Developer. They are distinct roles with different scopes. |
>
> > 💡 **Key rule**: Database Admin = **no IDE**. IDE access requires: Developer, Analyst, Admin, or Account Admin.

---

### Q7. ⭐
> **Subdomain 5.7 — Project Admin cannot create projects**

A project-level Admin user needs to create a new dbt project for a new data team. They navigate to the account settings but find the "Create New Project" button is greyed out. Why?

- A) The user needs to be in the Owner group to create projects.
- B) Creating projects is restricted to Account Admin and Project Creator roles — project-level Admin cannot create new projects.
- C) New project creation is disabled after the account reaches its project limit on the current plan.
- D) The user needs to log out and back in to see the new project creation option.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Owner group doesn't directly map to "create projects" permission — the specific roles that enable this are Account Admin and Project Creator. |
> | **B) ✅ Correct** | **Project-level Admin cannot create new projects** — Admin gives full control within *existing* projects only. Creating new projects requires **Account Admin** (account-level) or the **Project Creator** (account-level) permission set. This is one of the most important Admin vs Account Admin distinctions on the exam. |
> | **C) ❌ Incorrect** | While plan limits exist, the question describes a permissions issue (greyed out button), not a plan limit error. |
> | **D) ❌ Incorrect** | This is a permissions issue, not a session issue. |
>
> > 💡 **Key rule**: **Admin ≠ Account Admin**. Admin = full control of existing projects. Create new projects = **Account Admin** or **Project Creator** only.

---

### Q8.
> **Subdomain 5.8 — SSO enforced, admin locked out**

An organization enforces SSO for all dbt Cloud users. The Identity Provider (IdP) goes down and all users are locked out. Can administrators still access dbt Cloud?

- A) No — when SSO is enforced, all users including admins must use SSO. IdP downtime = complete lockout.
- B) Yes — admins retain password-based login access by default even when SSO is enforced.
- C) Yes — but only if they previously enabled the "Admin Password Bypass" setting in Account Settings.
- D) No — but they can contact dbt Cloud support to temporarily disable SSO enforcement.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Full lockout would be a catastrophic single point of failure. dbt explicitly preserves admin access via password when SSO is enforced. |
> | **B) ✅ Correct** | By default, **admins retain password-based login** even when SSO is enforced for the organization. This is a deliberate design to prevent admin lockout during IdP outages. (Admins can choose to explicitly restrict their own access to SSO-only, but this is not the default.) |
> | **C) ❌ Incorrect** | There is no "Admin Password Bypass" setting that must be explicitly enabled — it's the default behavior. |
> | **D) ❌ Incorrect** | Support escalation may be a last resort, but admins have a built-in path (password login) that doesn't require support intervention. |
>
> > 💡 **Key rule**: SSO enforced + IdP down = **admins can still log in with password** (default behavior, unless explicitly restricted).

---

### Q9.
> **Subdomain 5.9 — SCIM sync timing**

A team uses SCIM with Okta to manage dbt Cloud users. An employee is offboarded — their Okta account is deprovisioned. How quickly is their dbt Cloud access removed?

- A) Immediately — SCIM propagates changes in real-time between Okta and dbt Cloud.
- B) Within 15 minutes — SCIM syncs on a scheduled interval.
- C) On their next login attempt — SCIM syncs on user login, not in real-time.
- D) After 24 hours — dbt Cloud re-authenticates all SSO sessions every 24 hours.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | SCIM in dbt Cloud does NOT sync in real-time — this is a key gotcha. |
> | **B) ❌ Incorrect** | SCIM is not on a fixed 15-minute interval in dbt Cloud. |
> | **C) ✅ Correct** | SCIM syncs **on user login**, not in real-time. A deprovisioned user's dbt Cloud access is not immediately revoked — it's removed when they next attempt to log in and SCIM validation fires. This is an important security consideration: for immediate access revocation, manually deactivate the user in dbt Cloud as well. |
> | **D) ❌ Incorrect** | The 24-hour figure refers to SSO re-authentication frequency — not SCIM sync timing. |
>
> > 💡 **Key rule**: SCIM syncs **on login** — not real-time. For immediate offboarding: manually deactivate in dbt Cloud too.

---

### Q10.
> **Subdomain 5.10 — Default groups and new user access**

A company wants all new contractors to join the organization without automatically receiving any project access. Currently, new users are being added to projects as soon as they're created. What setting must the admin change?

- A) Disable the **"Add all new users by default"** setting on the **Everyone** group.
- B) Set the Member group to have no permissions.
- C) Require manual approval for all new user accounts before they're activated.
- D) Change the default license type from Developer to Read-Only.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | New users are automatically added to **both the Member AND Everyone groups**. If the Everyone group has project permissions, all new users inherit them. Disabling **"Add all new users by default"** on the Everyone group prevents automatic access assignment — new users must be manually added to groups. |
> | **B) ❌ Incorrect** | Setting Member group to no permissions would affect all existing members, not just new contractors. Also, new users land in both Member AND Everyone — just fixing Member is insufficient. |
> | **C) ❌ Incorrect** | Manual account approval is not a built-in dbt Cloud feature. |
> | **D) ❌ Incorrect** | Changing the default license type would affect what features users can access, but the root issue is group membership auto-assignment. |
>
> > 💡 **Key rule**: New users → auto-added to **both Member AND Everyone**. Disable "Add all new users" on Everyone for RBAC isolation.

---

### Q11.
> **Subdomain 5.11 — Most permissive group wins**

A user is in two groups: "ReadOnly-Team" (Stakeholder permissions) and "Data-Team" (Developer permissions). What is their effective access level?

- A) Stakeholder — the most restrictive group wins to protect data.
- B) Developer — the most permissive group wins.
- C) A blend of both — they get read access everywhere but write access only in Data-Team projects.
- D) The last group they were added to determines their access.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt uses most-permissive, not most-restrictive. This is the opposite of some IAM systems and is an important gotcha. |
> | **B) ✅ Correct** | When a user belongs to multiple groups, the **most permissive group wins**. The Developer permission set from "Data-Team" overrides the Stakeholder from "ReadOnly-Team". This means adding a user to any high-permission group grants them that access — you cannot restrict someone with a low-access group if they're also in a high-access group. |
> | **C) ❌ Incorrect** | Permissions are not blended or intersected — the most permissive set wins in full. |
> | **D) ❌ Incorrect** | Membership order has no effect — it's always the most permissive group. |
>
> > 💡 **Key rule**: **Most permissive group wins**. A user in both a restrictive and permissive group gets the permissive access.

---

### Q12.
> **Subdomain 5.12 — Stakeholder vs Viewer**

A data governance officer needs read-only access to dbt Cloud **including the full sensitive audit log** (which contains user actions and PII-adjacent activity). Which role should they be assigned?

- A) Stakeholder (project-level) — read-only access to everything including the audit log.
- B) Viewer (account-level) — read-only across the entire account including the full sensitive audit log.
- C) Read-Only license — provides access to all audit log entries.
- D) Security Admin — provides access to the audit log for compliance purposes.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Stakeholder is project-level and the audit log it provides access to **excludes sensitive information**. Not suitable for full compliance audit access. |
> | **B) ✅ Correct** | **Viewer** is an account-level role that provides read-only access across the entire account, including the **full sensitive audit log**. This is distinct from Stakeholder (project-level, limited audit log) and is the correct role for audit/compliance purposes. |
> | **C) ❌ Incorrect** | Read-Only license users have fixed access to artifacts and deploy section only — not the full audit log. |
> | **D) ❌ Incorrect** | Security Admin provides administrative access to security settings but is not the designated role for read-only audit log access. |
>
> > 💡 **Key rule**: Viewer (account-level) = full audit log including sensitive. Stakeholder (project-level) = limited audit log.

---

### Q13. ⭐
> **Subdomain 5.13 — Semantic Layer service token**

A team needs to create a service token that allows an external BI tool to query the dbt Semantic Layer. Which permission set should be assigned to this service token?

- A) Job Admin — gives access to run jobs and query data.
- B) Developer — gives full project access including Semantic Layer queries.
- C) Semantic Layer — the only permission set scoped to Semantic Layer queries; service token exclusive.
- D) Database Admin — manages data platform configs including Semantic Layer.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Job Admin does not include Semantic Layer query access — it manages jobs and runs. |
> | **B) ❌ Incorrect** | Developer cannot be assigned to a service token — it's a user-only permission set. Service tokens have their own set of assignable permission sets. |
> | **C) ✅ Correct** | The **Semantic Layer** permission set is specifically designed for this purpose — it allows querying the Semantic Layer API and nothing else. It is also **service token exclusive** — it cannot be assigned to human users (they'd use normal project access). |
> | **D) ❌ Incorrect** | Database Admin manages configuration, not query execution via the Semantic Layer. |
>
> > 💡 **Key rule**: Semantic Layer queries via API = **Semantic Layer permission set** on a service token. Service token only — cannot assign to users.

---

### Q14.
> **Subdomain 5.14 — Who can create projects**

Which of the following users can create a new dbt Cloud project? **Select TWO correct answers.**

- A) A user with the Account Admin role.
- B) A user with the project-level Admin role.
- C) A user with the Project Creator role.
- D) A user with the Security Admin role.
- E) A user with the Developer license and Analyst role.

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Account Admin** has full account-level access including project creation. |
> | **B) ❌ Incorrect** | Project-level **Admin** cannot create new projects — it only manages existing ones. This is the most critical distinction between Admin and Account Admin. |
> | **C) ✅ Correct** | **Project Creator** is an account-level role specifically designed to allow project creation and configuration without requiring full Account Admin access. |
> | **D) ❌ Incorrect** | Security Admin manages users, groups, SSO, and IP restrictions — not project creation. |
> | **E) ❌ Incorrect** | Neither the Developer license nor the Analyst role grants project creation ability. |
>
> > 💡 **Key rule**: Create projects = **Account Admin** OR **Project Creator**. Project-level Admin cannot create new projects.

---

### Q15.
> **Subdomain 5.15 — Service token rotation**

A company wants to rotate an existing service token used in multiple integrations. What is the correct rotation procedure?

- A) Click "Rotate Token" on the existing token — the value updates in place and integrations continue working.
- B) Create a new service token → update all integrations with the new token value → delete the old token.
- C) Edit the existing token → change the "Expiry" field to extend its validity → save.
- D) Contact dbt Labs support to rotate the token cryptographically while preserving the existing value.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no in-place rotation — service tokens cannot be updated to generate a new value while maintaining the same token identifier. |
> | **B) ✅ Correct** | Service tokens have **no in-place rotation mechanism**. The correct pattern is: create a new token → copy the value → update every integration that uses the old token → delete the old token. This zero-downtime rotation ensures continuous integration availability. |
> | **C) ❌ Incorrect** | Service tokens don't have a user-configurable expiry field — and changing expiry wouldn't constitute rotation anyway. |
> | **D) ❌ Incorrect** | Token rotation is a self-service operation in dbt Cloud — support is not involved. |
>
> > 💡 **Key rule**: Token rotation = **create new → update integrations → delete old**. No in-place rotation.

---

---

### Q16.
> **Subdomain 5.16 — Environment access vs permission set**

A dbt Cloud admin configures a user group called "Ops Team" with the **Stakeholder** (read-only) permission set. A team lead then grants the Ops Team group **write access to the Production environment** (allowing job runs and run management). A member of the Ops Team successfully triggers a production job run. Is this expected behavior?

- A) No — Stakeholder permission set prevents any job execution, including through environment write access.
- B) Yes — environment write access (job/run operations) and permission set read-only are **independent controls**. A group can have read-only permissions but still be granted write access to specific environment types.
- C) No — write access to the Production environment requires at least a Developer permission set.
- D) Yes — but only because Stakeholder is a project-level role that doesn't apply to environment-level actions.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Stakeholder permission set restricts project/IDE/model access but does not automatically restrict environment-level job run operations. |
> | **B) ✅ Correct** | **Environment write access** (the ability to create/manage runs and jobs within an environment type) and **permission set read-only** are **independent controls** in dbt Cloud. A group can hold a read-only permission set AND be granted write access to environment types. This means an Ops Team with Stakeholder permissions can still trigger production job runs if their group is granted environment write access — even without Developer-level project permissions. |
> | **C) ❌ Incorrect** | There is no documented requirement that environment write access requires a Developer permission set. |
> | **D) ❌ Incorrect** | The independence of these controls is not because of a scope distinction — it is by design in dbt Cloud's RBAC model. |
>
> > 💡 **Key rule**: Environment write access (job/run ops) and permission set level are independent. Read-only permission set does not block environment write access.

---

### Q17.
> **Subdomain 5.17 — SCIM sync timing and case sensitivity**

An organization uses SCIM with Okta to manage dbt Cloud users. An admin renames a dbt Cloud group from `data-team` to `Data-Team` (capitalizing the D). The corresponding Okta group is still named `data-team` (lowercase). No members are immediately removed. Two weeks later, a user logs in and is unexpectedly removed from the `Data-Team` group in dbt. What are the two root causes?

- A) SCIM syncs in real-time — the mismatch should have been detected immediately.
- B) SCIM group name matching is **case-sensitive** — `data-team` and `Data-Team` are treated as different groups. SCIM syncs happen **on user login**, not in real-time, which is why the effect was delayed until the user next authenticated.
- C) SCIM only syncs group membership changes, not group name changes — the rename is ignored entirely.
- D) The delay was caused by a 14-day SCIM reconciliation cycle that runs automatically.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | SCIM does NOT sync in real-time — it syncs on user login. |
> | **B) ✅ Correct** | Two root causes: (1) **Case sensitivity** — SCIM group names must match **exactly** between the IdP (Okta) and dbt Cloud. `data-team` ≠ `Data-Team`. When the user logs in, SCIM sees no matching Okta group named `Data-Team`, so the user is not mapped to it. (2) **Sync on login** — SCIM changes only propagate when the user next authenticates, not in real-time. The 2-week delay is explained by the user not having logged in during that period. Fix: ensure group names match exactly (case-sensitive) in both systems. |
> | **C) ❌ Incorrect** | SCIM does process group name changes — the mismatch is interpreted as the user leaving one group and joining another. |
> | **D) ❌ Incorrect** | There is no documented 14-day reconciliation cycle. SCIM sync is triggered by user login. |
>
> > 💡 **Key rule**: SCIM group names = **case-sensitive** exact match. Sync happens **on user login** only — not real-time.

---

### Q18.
> **Subdomain 5.18 — Analyst vs Developer role**

A team lead needs to assign a role to a data analyst who needs to **write and run models in the dbt Cloud IDE** AND **view existing job run history** — but should NOT be able to create new jobs or edit existing ones. Which role is most appropriate?

- A) Developer — they need IDE access and can view runs.
- B) Analyst — they have IDE access, can run models interactively, and can view jobs/runs/environments without being able to create or edit jobs.
- C) Job Viewer — specifically designed for viewing job run history.
- D) Database Admin — provides read access to all platform configurations including job history.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Developer has IDE access but is explicitly designed for model builders — Developers cannot create/edit jobs, but the Analyst role is the better fit here as it explicitly includes the ability to view jobs/runs/environments as part of its scope. |
> | **B) ✅ Correct** | **Analyst** is the correct role. Analysts have: IDE access (write and run models), the ability to view jobs/runs/environments, but **cannot create jobs or edit environments**. This exactly matches the requirement. Developer is similar but Analyst's design intent is for data consumers who need IDE access plus observability into job outcomes — not job management. |
> | **C) ❌ Incorrect** | Job Viewer has no IDE access — they can only view job results and logs, not write or run models. |
> | **D) ❌ Incorrect** | Database Admin manages platform configurations and has no IDE access for writing dbt code. |
>
> > 💡 **Key rule**: Analyst = IDE access + view jobs/runs/environments. Cannot create/edit jobs. Developer = IDE + personal credentials. Job Viewer = read-only job results, no IDE.

---

### Q19.
> **Subdomain 5.19 — Default group auto-add behavior**

A company discovers that every new user invited to their dbt Cloud account automatically gains read access to all projects in the account. An admin investigates and finds no explicit project permission assignments. What is the most likely cause?

- A) dbt Cloud grants all users read access by default — this must be manually revoked per project.
- B) New users are automatically added to both the **Member** and **Everyone** groups, which are configured with broad default permissions including project read access.
- C) New users inherit the permissions of the user who invited them.
- D) The account is on Developer plan, which grants all users full read access.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not grant read access as a platform default. The auto-add behavior of default groups is the mechanism. |
> | **B) ✅ Correct** | New users in dbt Cloud are automatically added to **both the Member group AND the Everyone group** by default. These two default groups typically have broad permissions that may include project read access. Since both Member and Everyone have "Add all new users by default" enabled, any new invite immediately inherits both groups' permissions. The fix: customize Member and Everyone permissions, or disable "Add all new users by default" on both groups to enforce proper RBAC isolation. |
> | **C) ❌ Incorrect** | Permissions are not inherited from the inviting user. |
> | **D) ❌ Incorrect** | Plan tier does not grant blanket read access. The default group behavior is plan-agnostic. |
>
> > 💡 **Key rule**: New users auto-join **both Member AND Everyone** groups. Disable "Add all new users by default" on both to enforce RBAC isolation.

---

### Q20.
> **Subdomain 5.20 — Owner group immutability**

A dbt Cloud Account Admin attempts to remove the Account Admin permission set from the **Owner group** to limit what account owners can do. They find the option is greyed out. Why?

- A) The Owner group permissions can only be changed by dbt Labs support, not by account admins.
- B) The Owner group has **immutable permissions** — they cannot be changed by anyone, including Account Admins. This is by design to ensure the account always has at least one fully-privileged group.
- C) The Owner group permissions are locked until all Owner members approve the change via a majority vote workflow.
- D) The Owner group is a managed group — it can only be edited during the initial account setup period.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is not a support escalation scenario. The immutability is a product constraint, not an access control issue. |
> | **B) ✅ Correct** | The **Owner group** in dbt Cloud has **immutable permissions** — its permission sets cannot be changed by anyone, including Account Admins. This is intentional: the Owner group always retains full Account Admin access to ensure the account always has at least one group capable of managing everything. Contrast with the Member and Everyone groups, which are mutable and can be customized. |
> | **C) ❌ Incorrect** | There is no majority vote or approval workflow for group permission changes in dbt Cloud. |
> | **D) ❌ Incorrect** | There is no "initial account setup period" after which groups become locked. The Owner group is permanently immutable. |
>
> > 💡 **Key rule**: Owner group = **immutable permissions**. Cannot be changed by anyone. Member and Everyone groups are mutable.

---

### Q21. ⭐
> **Subdomain 5.21 — PAT vs Service Token in production**

A dbt Cloud Account Admin notices that a critical production CI/CD job has been failing with `401 Unauthorized` for the past 24 hours. Investigation shows:

- The job authenticates against the dbt Cloud API using a token created by a senior data engineer who left the company two days ago.
- The engineer's user account was deactivated as part of standard offboarding.
- No one rotated the token before the engineer's departure.

What kind of token was almost certainly in use, and what is the correct architectural fix? **Select TWO correct answers.**

- A) The token was a **personal access token (PAT)** — PATs are tied to a specific user and inherit that user's permissions. When the user is deactivated, all of their PATs are revoked, breaking any integration that depended on them.
- B) The token was a **service token** — service tokens are tied to the user who created them and die when that user is deactivated.
- C) The correct fix is to replace the PAT with a **service token** scoped to the minimum permission set needed for the job (e.g., Job Admin on the relevant project plus Read-Only as needed). Service tokens are account-level and persist independently of any individual user.
- D) The correct fix is to reactivate the engineer's account and grant their PAT to a different user via the "Transfer PAT ownership" workflow.
- E) The correct fix is to add the new user to the same RBAC group as the departed engineer — this automatically restores any PATs created under the old account.

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | This is the canonical "production job fails after employee X leaves" trap. **PATs are tied to a specific user** and inherit the user's license + group permissions. When the user is deactivated, **all of their PATs are revoked simultaneously**. PATs should never be used to authenticate production automation for exactly this reason. |
> | **B) ❌ Incorrect** | Service tokens are **account-level** and have no user identity — they persist independently of any individual user. A service token would not have failed in this scenario. |
> | **C) ✅ Correct** | The architecturally correct fix is a **service token with the minimum permission set required**. Service tokens (1) are account-level and outlive any user, (2) can be assigned multiple permission sets, each scoped to specific projects, and (3) provide explicit, narrowable permissions independent of any user. For a CI/CD job: typically `Job Admin` on the relevant project plus any read scopes the job needs. |
> | **D) ❌ Incorrect** | There is no "Transfer PAT ownership" workflow in dbt Cloud. PATs are non-transferable — they are tied to a specific user account permanently. |
> | **E) ❌ Incorrect** | RBAC group membership has no effect on existing PATs. PATs belong to specific users and cannot be inherited by other users via group membership. |
>
> > 💡 **Key rule**: PAT = user-tied, dies with the user, permissions inherited from user. Service token = account-level, persists independently, explicit permission sets, project-scopable. **Production = service token. Always.**

---

### Q22.
> **Subdomain 5.22 — Service token permissions and creation**

A team architect is configuring a new service token for a multi-project CI/CD integration on the **Enterprise** plan. They want the token to have:
- `Job Admin` permission on Project A only
- `Read-Only` permission on Project B only
- No access to any other project

Which of the following statements about this configuration are correct? **Select TWO correct answers.**

- A) A single service token can carry both permission sets simultaneously, with each permission set scoped to specific projects.
- B) The architect must create two separate service tokens (one per permission set) because each service token can only carry a single permission set.
- C) The service token can be created by any user holding a Developer license — license type determines token-creation rights.
- D) The Account Admin permission must be used to create or modify a service token; a Developer-licensed user cannot create the token themselves regardless of the permissions being assigned.
- E) On a Developer or Starter plan, this configuration would be impossible — only Semantic Layer permission sets are available to service tokens on those tiers.

> [!success]- Answer & Explanations
> **✅ Correct: A, D** *(E is also factually correct but the scenario specifies Enterprise, so it's not the issue here — see explanation)*
>
> | | |
> |---|---|
> | **A) ✅ Correct** | A single service token can carry **multiple permission sets**, and each permission set can be scoped to **all projects** or to **specific projects**. The architect's intent — `Job Admin` on Project A + `Read-Only` on Project B in a single token — is exactly the canonical least-privilege pattern that service tokens are designed to support. |
> | **B) ❌ Incorrect** | Service tokens explicitly support multiple permission sets per token. Splitting into two tokens is unnecessary and reduces operational simplicity (more secrets to rotate). |
> | **C) ❌ Incorrect** | License type does not determine service-token creation rights. **Account Admin permission** is required to create service tokens, regardless of the creator's license. |
> | **D) ✅ Correct** | Service token creation is gated by **Account Admin permission**, not by license type. A Developer-licensed user without Account Admin cannot create the token; either grant them Account Admin (likely overkill) or have an Account Admin create the token on their behalf. |
> | **E) ❌ Incorrect (in this scenario)** | This statement is factually true — on Developer/Starter plans, service tokens can only be assigned **Semantic Layer permissions**. However, the scenario specifies the **Enterprise plan**, so the architect has access to all permission sets. E is therefore not a correct answer for this question. |
>
> > 💡 **Key rule**: Service tokens — multiple permission sets per token, each project-scopable. Created by Account Admin only (not license-gated). Permission set availability: Enterprise/Enterprise+ = any; Legacy Team = limited; Developer/Starter = Semantic Layer only.

---

*[End of Topic 5 — 22 questions]*

