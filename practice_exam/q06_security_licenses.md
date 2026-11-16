# Topic 5: Security & Licenses — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 22 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 5.1 — IT license ignores group permissions**

A new hire needs to manage users, groups, and SSO settings, but should have no access to the dbt IDE, jobs, or data. An admin assigns them an IT license and adds them to the Account Admin group. What level of access will this user have?

- A) The assignment will fail — IT-licensed users cannot be added to the Account Admin group.
- B) Full Account Admin access — the Account Admin group overrides license restrictions for IT users.
- C) IT access plus the ability to run jobs since Account Admin includes job execution.
- D) Fixed IT access only: Security Admin + Billing Admin + edit Connections. The Account Admin group assignment has zero effect.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Technically you can add IT-licensed users to any group — but the group membership has zero effect on their access. |
> | **B) ❌ Incorrect** | IT and Read-Only licenses are the two license types that **do not inherit from any permission sets**. Group assignment is completely irrelevant for these users. |
> | **C) ❌ Incorrect** | IT license does not inherit job execution from Account Admin group. |
> | **D) ✅ Correct** | **IT-licensed users have fixed, non-overridable access**: Security Admin + Billing Admin + the ability to edit Connections. No matter which group they're in — including Account Admin — their access does not change. To get the admin's intended capability (user/group/SSO management), the IT license is actually correct for that purpose. But they'll never get IDE or job access. |
>
> > 💡 **Key rule**: IT and Read-Only licenses **ignore all group assignments**. License type = fixed access, no override possible.

---

### Q2. ⭐
> **Subdomain 5.2 — Read-Only license trap**

A contractor needs view-only access to a specific project's models in dbt Catalog. An admin assigns them a Read-Only license and adds them to the Developer group for that project. Can they now edit models in the IDE?

- A) No — Read-Only license users do not inherit from any permission sets. They can only view artifacts and the deploy section, regardless of group membership.
- B) Yes — the Developer group grants IDE access, which the Read-Only license allows at the project level.
- C) Yes — but only in the IDE's read-only mode (no execution, no saves).
- D) No — they can't access the IDE, but the Developer group gives them access to dbt Cloud's API.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Read-Only license users do not inherit rights from any permission sets**. Their access is identical regardless of which groups they belong to: view artifacts and the deploy section (jobs, runs, schedules) only. No IDE access, no job execution, no editing. The Developer group assignment has zero effect. |
> | **B) ❌ Incorrect** | The Developer group cannot elevate a Read-Only license — the license type always overrides group permissions. |
> | **C) ❌ Incorrect** | There is no "read-only IDE mode" — IDE access is binary, and Read-Only license users cannot access it at all. |
> | **D) ❌ Incorrect** | Read-Only license does not grant any elevated API access through group membership. |
>
> > 💡 **Key rule**: Read-Only license = **fixed access only** (view artifacts + deploy section). Groups irrelevant. Identical access for all Read-Only users.

---

### Q3. ⭐
> **Subdomain 5.3 — Service token: one-time visibility**

An admin creates a new service token to use in a CI/CD pipeline. They close the dialog before saving the token value. How can they recover the token?

- A) Contact dbt Cloud support with the token name to retrieve the value.
- B) The token can be re-revealed by clicking "Show Token" in the service token settings.
- C) The token value is shown only once — it cannot be recovered. Delete it, create a new one, and update all integrations.
- D) The token value can be retrieved from Account Settings → API Tokens at any time.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Labs support cannot reveal stored token values — they are not stored in recoverable form. |
> | **B) ❌ Incorrect** | There is no "Show Token" button after initial creation — the value is permanently obscured. |
> | **C) ✅ Correct** | Service token values are shown **exactly once** at creation time. If the dialog is closed before saving the value, it is permanently unrecoverable. The only path forward is to delete the existing token, create a new one, and update all integrations that used the old token. |
> | **D) ❌ Incorrect** | After the initial creation dialog is closed, the token value is not stored in a retrievable form in the UI. |
>
> > 💡 **Key rule**: Service token = **one-time reveal**. Save immediately. Lost token = delete → create new → update all integrations.

---

### Q4. ⭐
> **Subdomain 5.4 — Service token 403 error**

A service token is configured correctly and has the right permission sets, but all API calls return `403 Forbidden`. The token was created recently and the credentials haven't changed. What is the most likely cause?

- A) The service token was created before the last SSO configuration change and needs to be rotated.
- B) The calling IP address is not on the account's IP allowlist — service tokens honor IP restrictions just like human logins.
- C) The service token needs to be assigned to a specific project before it can make API calls.
- D) The service token has expired — tokens expire after 90 days by default.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | SSO configuration changes do not invalidate service tokens — service tokens are separate from SSO. |
> | **B) ✅ Correct** | **Service tokens honor IP restriction allowlists** exactly like human user logins. If the CI server or automation tool's IP is not on the account's allowlist, all API calls will return `403 Forbidden` — even if the token itself is valid and correctly permissioned. |
> | **C) ❌ Incorrect** | Service tokens can be scoped to projects, but a missing project assignment would result in a permissions error on project-specific endpoints, not a blanket `403` on all API calls. |
> | **D) ❌ Incorrect** | Service tokens do not have a 90-day expiration — they don't expire on a time schedule (unlike OAuth tokens). |
>
> > 💡 **Key rule**: Service token `403` = check **IP allowlist** first. Service tokens respect IP restrictions.

---

### Q5. ⭐
> **Subdomain 5.5 — Security Admin cannot trigger jobs**

During an incident, a Security Admin is the only person available. They need to manually trigger a production job to restore data. They find they cannot access the Jobs page at all. Why?

- A) Security Admin has zero access to jobs, runs, or environments — it is purely an administrative role for user/group/SSO/IP management.
- B) Jobs can only be triggered by the Account Owner during incidents.
- C) The Security Admin needs to be temporarily added to the Job Runner group.
- D) Security Admin requires 2FA to access the Jobs page during an incident.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Security Admin has zero data access** — no IDE, no jobs, no runs, no environments. It is scoped purely to: managing users, groups, licenses, SSO configuration, and IP restrictions. To trigger jobs in an incident, the correct role is **Job Admin** or **Job Runner**. |
> | **B) ❌ Incorrect** | Job triggering is not exclusive to Account Owners. |
> | **C) ❌ Incorrect** | This suggestion reflects the correct fix but the question asks why they can't currently trigger jobs — Security Admin's scope doesn't include jobs. |
> | **D) ❌ Incorrect** | 2FA for incident access is not a documented dbt Cloud requirement. |
>
> > 💡 **Key rule**: Security Admin = **zero data access**. No IDE, no jobs, no runs. For job execution: Job Admin or Job Runner.

---

### Q6.
> **Subdomain 5.6 — Database Admin and IDE access**

A Database Admin user wants to write a quick SQL fix directly in the dbt Cloud IDE. Can they?

- A) Yes — but only in view mode; they cannot execute queries.
- B) No — Database Admin manages data platform configs and Semantic Layer settings but has no IDE access.
- C) Yes — Database Admin includes IDE access equivalent to the Developer role.
- D) Yes — Database Admin includes read/write IDE access for all projects they manage.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no "view mode" IDE access — IDE access is binary based on role. |
> | **B) ✅ Correct** | **Database Admin does not include IDE access**. The role is scoped to: data platform configurations, environment variables, and Semantic Layer configuration. To write code in the IDE, a user needs the Developer, Analyst, or Admin permission set. This is a common trap — "Database Admin" sounds like it should have more data access than it does. |
> | **C) ❌ Incorrect** | Database Admin ≠ Developer. They are distinct roles with different scopes. |
> | **D) ❌ Incorrect** | Database Admin is explicitly a non-IDE role focused on platform configuration. |
>
> > 💡 **Key rule**: Database Admin = **no IDE**. IDE access requires: Developer, Analyst, Admin, or Account Admin.

---

### Q7. ⭐
> **Subdomain 5.7 — Project Admin cannot create projects**

A project-level Admin user needs to create a new dbt project for a new data team. They navigate to the account settings but find the "Create New Project" button is greyed out. Why?

- A) The user needs to log out and back in to see the new project creation option.
- B) New project creation is disabled after the account reaches its project limit on the current plan.
- C) Creating projects is restricted to Account Admin and Project Creator roles — project-level Admin cannot create new projects.
- D) The user needs to be in the Owner group to create projects.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is a permissions issue, not a session issue. |
> | **B) ❌ Incorrect** | While plan limits exist, the question describes a permissions issue (greyed out button), not a plan limit error. |
> | **C) ✅ Correct** | **Project-level Admin cannot create new projects** — Admin gives full control within *existing* projects only. Creating new projects requires **Account Admin** (account-level) or the **Project Creator** (account-level) permission set. This is one of the most important Admin vs Account Admin distinctions on the exam. |
> | **D) ❌ Incorrect** | The Owner group doesn't directly map to "create projects" permission — the specific roles that enable this are Account Admin and Project Creator. |
>
> > 💡 **Key rule**: **Admin ≠ Account Admin**. Admin = full control of existing projects. Create new projects = **Account Admin** or **Project Creator** only.

---

### Q8.
> **Subdomain 5.8 — SSO enforced, admin locked out**

An organization enforces SSO for all dbt Cloud users. The Identity Provider (IdP) goes down and all users are locked out. Can administrators still access dbt Cloud?

- A) Yes — but only if they previously enabled the "Admin Password Bypass" setting in Account Settings.
- B) No — when SSO is enforced, all users including admins must use SSO. IdP downtime = complete lockout.
- C) No — but they can contact dbt Cloud support to temporarily disable SSO enforcement.
- D) Yes — admins retain password-based login access by default even when SSO is enforced.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no "Admin Password Bypass" setting that must be explicitly enabled — it's the default behavior. |
> | **B) ❌ Incorrect** | Full lockout would be a catastrophic single point of failure. dbt explicitly preserves admin access via password when SSO is enforced. |
> | **C) ❌ Incorrect** | Support escalation may be a last resort, but admins have a built-in path (password login) that doesn't require support intervention. |
> | **D) ✅ Correct** | By default, **admins retain password-based login** even when SSO is enforced for the organization. This is a deliberate design to prevent admin lockout during IdP outages. (You can turn this off with **Allow password logins for account administrators** in SSO & SCIM.) |
>
> > 💡 **Key rule**: SSO enforced + IdP down = **admins can still log in with password** (default behavior, unless explicitly restricted).

---

### Q9.
> **Subdomain 5.9 — License mapping precedence**

An SSO user belongs to IdP groups that are mapped to both Read-Only and Developer in the license mappings. Which license do they get, and when does it apply?

- A) Developer, the next time they sign in.
- B) Read-Only, immediately.
- C) The account's default license.
- D) Both licenses at once.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | Developer wins over Read-Only. License mapping changes take effect the next time users sign in with SSO. |
> | **B) ❌ Incorrect** | Developer takes precedence, and mappings apply at sign-in. |
> | **C) ❌ Incorrect** | The default license is for users who match no mapping. |
> | **D) ❌ Incorrect** | The docs describe a single resolved license per user. |
>
> > 💡 **Key rule**: License mappings use **IdP group names**. In both mapped groups → Developer. In neither → the account default license. Applied at sign-in.

---

### Q10.
> **Subdomain 5.10 — Default groups and new user access**

A company wants all new contractors to join the organization without automatically receiving any project access. Currently, new users are being added to projects as soon as they're created. What should the admin change?

- A) Customize the permissions of both the Member and Everyone groups, since new users are added to both.
- B) Require manual approval for all new user accounts before they're activated.
- C) Change the default license type from Developer to Read-Only.
- D) Set the Member group to have no permissions.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say dbt adds new users to both the Member and Everyone groups. Member is broad (it restricts only features that alter billing or security), and Everyone is yours to customize. Adjust both to limit what new users get. |
> | **B) ❌ Incorrect** | Manual account approval is not a built-in dbt Cloud feature. |
> | **C) ❌ Incorrect** | Changing the default license type would affect what features users can access, but the root issue is group membership auto-assignment. |
> | **D) ❌ Incorrect** | Setting Member group to no permissions would affect all existing members, not just new contractors. Also, new users land in both Member AND Everyone — just fixing Member is insufficient. |
>
> > 💡 **Key rule**: New users are auto-added to **both Member and Everyone**. Customize both to limit default access.

---

### Q11.
> **Subdomain 5.11 — Most permissive group wins**

A user is in two groups: "ReadOnly-Team" (Stakeholder permissions) and "Data-Team" (Developer permissions). What is their effective access level?

- A) A blend of both — they get read access everywhere but write access only in Data-Team projects.
- B) Developer — the most permissive group wins.
- C) The last group they were added to determines their access.
- D) Stakeholder — the most restrictive group wins to protect data.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Permissions are not blended or intersected — the most permissive set wins in full. |
> | **B) ✅ Correct** | When a user belongs to multiple groups, the **most permissive group wins**. The Developer permission set from "Data-Team" overrides the Stakeholder from "ReadOnly-Team". This means adding a user to any high-permission group grants them that access — you cannot restrict someone with a low-access group if they're also in a high-access group. |
> | **C) ❌ Incorrect** | Membership order has no effect — it's always the most permissive group. |
> | **D) ❌ Incorrect** | dbt uses most-permissive, not most-restrictive. This is the opposite of some IAM systems and is an important gotcha. |
>
> > 💡 **Key rule**: **Most permissive group wins**. A user in both a restrictive and permissive group gets the permissive access.

---

### Q12.
> **Subdomain 5.12 — Stakeholder vs Account Viewer**

A data governance officer needs read-only access to dbt Cloud **including the full sensitive audit log** (which contains user actions and PII-adjacent activity). Which role should they be assigned?

- A) Stakeholder (project-level) — read-only access to everything including the audit log.
- B) Read-Only license — provides access to all audit log entries.
- C) Account Viewer — read-only across the account, including the full sensitive audit log.
- D) Security Admin — provides access to the audit log for compliance purposes.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Stakeholder is project-level and the audit log it provides access to **excludes sensitive information**. Not suitable for full compliance audit access. |
> | **B) ❌ Incorrect** | Read-Only license users have fixed access to artifacts and deploy section only — not the full audit log. |
> | **C) ✅ Correct** | **Account Viewer** gives read-only access to all settings, projects, environments and runs, and to audit logs including sensitive account-level information. Stakeholder and Read-Only exclude sensitive audit information. |
> | **D) ❌ Incorrect** | Security Admin provides administrative access to security settings but is not the designated role for read-only audit log access. |
>
> > 💡 **Key rule**: Account Viewer = full audit log including sensitive. Stakeholder / Read-Only = audit log without sensitive info.

---

### Q13. ⭐
> **Subdomain 5.13 — Semantic Layer service token**

A team needs to create a service token that allows an external BI tool to query the dbt Semantic Layer. Which permission set should be assigned to this service token?

- A) Job Admin — gives access to run jobs and query data.
- B) Database Admin — manages data platform configs including Semantic Layer.
- C) Semantic Layer — the only permission set scoped to Semantic Layer queries; service token exclusive.
- D) Developer — gives full project access including Semantic Layer queries.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Job Admin does not include Semantic Layer query access — it manages jobs and runs. |
> | **B) ❌ Incorrect** | Database Admin manages configuration, not query execution via the Semantic Layer. |
> | **C) ✅ Correct** | The **Semantic Layer** permission set is specifically designed for this purpose — it allows querying the Semantic Layer API and nothing else. It is also **service token exclusive** — it cannot be assigned to human users (they'd use normal project access). |
> | **D) ❌ Incorrect** | Developer is for building models. It isn't the set scoped to querying the Semantic Layer. |
>
> > 💡 **Key rule**: Semantic Layer queries via API = **Semantic Layer permission set** on a service token. Service token only — cannot assign to users.

---

### Q14.
> **Subdomain 5.14 — Who can create projects**

Which of the following users can create a new dbt Cloud project? **Select TWO correct answers.**

- A) A user with the Security Admin role.
- B) A user with the Account Admin role.
- C) A user with the Project Creator role.
- D) A user with the Developer license and Analyst role.
- E) A user with the project-level Admin role.

> [!success]- Answer & Explanations
> **✅ Correct: B, C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Security Admin manages users, groups, SSO, and IP restrictions — not project creation. |
> | **B) ✅ Correct** | **Account Admin** has full account-level access including project creation. |
> | **C) ✅ Correct** | **Project Creator** is an account-level role specifically designed to allow project creation and configuration without requiring full Account Admin access. |
> | **D) ❌ Incorrect** | Neither the Developer license nor the Analyst role grants project creation ability. |
> | **E) ❌ Incorrect** | Project-level **Admin** cannot create new projects — it only manages existing ones. This is the most critical distinction between Admin and Account Admin. |
>
> > 💡 **Key rule**: Create projects = **Account Admin** OR **Project Creator**. Project-level Admin cannot create new projects.

---

### Q15.
> **Subdomain 5.15 — Service token rotation**

A company wants to rotate an existing service token used in multiple integrations. What is the correct rotation procedure?

- A) Edit the existing token → change the "Expiry" field to extend its validity → save.
- B) Contact dbt Labs support to rotate the token cryptographically while preserving the existing value.
- C) Click "Rotate Token" on the existing token — the value updates in place and integrations continue working.
- D) Create a new service token → update all integrations with the new token value → delete the old token.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Service tokens don't have a user-configurable expiry field — and changing expiry wouldn't constitute rotation anyway. |
> | **B) ❌ Incorrect** | Token rotation is a self-service operation in dbt Cloud — support is not involved. |
> | **C) ❌ Incorrect** | There is no in-place rotation — service tokens cannot be updated to generate a new value while maintaining the same token identifier. |
> | **D) ✅ Correct** | Service tokens have **no in-place rotation mechanism**. The correct pattern is: create a new token → copy the value → update every integration that uses the old token → delete the old token. This zero-downtime rotation ensures continuous integration availability. |
>
> > 💡 **Key rule**: Token rotation = **create new → update integrations → delete old**. No in-place rotation.

---

---

### Q16.
> **Subdomain 5.16 — Environment write access default**

A group is given the **Developer** permission set. What does its "Environment write access" default to?

- A) Production only.
- B) All environments.
- C) Development only.
- D) None. The group is read-only on environments.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | It isn't limited to Production. |
> | **B) ✅ Correct** | In the enterprise permissions table Developer is read-only on environment settings, but when added to a group, the **Environment write access** field defaults to **All environments**. Check it. |
> | **C) ❌ Incorrect** | The default is broader than Development. |
> | **D) ❌ Incorrect** | The default isn't read-only. |
>
> > 💡 **Key rule**: Environment write access is by environment **type**, not a single environment. It lets a group create, edit and delete runs and jobs, not environments. Supported sets: Analyst, Database admin, Developer, Git admin, Job creator, Team admin.

---

### Q17.
> **Subdomain 5.17 — Setting up license mappings**

Where do you set up license mappings, and what do you enter?

- A) Account settings → SSO & SCIM, using dbt group names.
- B) Each user's profile.
- C) Account settings → Groups & Licenses → License mappings, using comma-separated IdP group names for Read-Only and Developer.
- D) The Everyone group's permission set.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | License mappings live under Groups & Licenses, and they use IdP group names. |
> | **B) ❌ Incorrect** | They're account-level, not set per user. |
> | **C) ✅ Correct** | The docs say license type mappings are based on IdP groups, not dbt groups. Changes take effect the next time users sign in. |
> | **D) ❌ Incorrect** | Permission sets don't assign licenses. |
>
> > 💡 **Key rule**: License mappings = Groups & Licenses → IdP group names → Read-Only / Developer. Default license: Developer, Read-Only or Analyst (IT can't be the default).

---

### Q18.
> **Subdomain 5.18 — Analyst vs Developer role**

A team lead needs to assign a role to a data analyst who needs to **write and run models in the dbt Cloud IDE** AND **view existing job run history** — but should NOT be able to create new jobs or edit existing ones. Which role is most appropriate?

- A) Analyst — they have IDE access, can run models interactively, and can view jobs/runs/environments without being able to create or edit jobs.
- B) Job Viewer — specifically designed for viewing job run history.
- C) Developer — they need IDE access and can view runs.
- D) Database Admin — provides read access to all platform configurations including job history.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Analyst** is built for users who run and analyze dbt models in the IDE but can't create or edit anything outside the IDE. |
> | **B) ❌ Incorrect** | Job Viewer has no IDE access — they can only view job results and logs, not write or run models. |
> | **C) ❌ Incorrect** | Developer is for building and maintaining models and managing production behavior. Analyst is the set for running and analyzing models without creating or editing outside the IDE. |
> | **D) ❌ Incorrect** | Database Admin manages platform configurations and has no IDE access for writing dbt code. |
>
> > 💡 **Key rule**: Analyst = run and analyze models in the IDE, can't create or edit outside it. Job Viewer = read-only job results, no IDE.

---

### Q19.
> **Subdomain 5.19 — Default group auto-add behavior**

A company discovers that every new user invited to their dbt Cloud account automatically gains read access to all projects in the account. An admin investigates and finds no explicit project permission assignments. What is the most likely cause?

- A) New users inherit the permissions of the user who invited them.
- B) The account is on Developer plan, which grants all users full read access.
- C) New users are automatically added to both the **Member** and **Everyone** groups, which are configured with broad default permissions including project read access.
- D) dbt Cloud grants all users read access by default — this must be manually revoked per project.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Permissions are not inherited from the inviting user. |
> | **B) ❌ Incorrect** | Plan tier does not grant blanket read access. The default group behavior is plan-agnostic. |
> | **C) ✅ Correct** | New users in dbt Cloud are automatically added to **both the Member group AND the Everyone group** by default. These two default groups typically have broad permissions that may include project read access. dbt adds new users to both by default. The fix: customize the Member and Everyone permissions. |
> | **D) ❌ Incorrect** | dbt Cloud does not grant read access as a platform default. The auto-add behavior of default groups is the mechanism. |
>
> > 💡 **Key rule**: New users auto-join **both Member and Everyone**. Customize both to limit default access.

---

### Q20.
> **Subdomain 5.20 — Owner group immutability**

A dbt Cloud Account Admin attempts to remove the Account Admin permission set from the **Owner group** to limit what account owners can do. They find the option is greyed out. Why?

- A) The Owner group permissions can only be changed by dbt Labs support, not by account admins.
- B) The Owner group is a managed group — it can only be edited during the initial account setup period.
- C) The Owner group permissions are locked until all Owner members approve the change via a majority vote workflow.
- D) The Owner group's permissions can't be changed. It's the default group for the people responsible for the whole account.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | This is not a support escalation scenario. The immutability is a product constraint, not an access control issue. |
> | **B) ❌ Incorrect** | There is no "initial account setup period" after which groups become locked. The Owner group is permanently immutable. |
> | **C) ❌ Incorrect** | There is no majority vote or approval workflow for group permission changes in dbt Cloud. |
> | **D) ✅ Correct** | The docs say you cannot change the permissions of the Owner group. Member and Everyone can be customized. |
>
> > 💡 **Key rule**: Owner group permissions can't be changed. Member and Everyone can be customized.

---

### Q21. ⭐
> **Subdomain 5.21 — PAT vs service token in production**

A production CI/CD pipeline calls the dbt API. Which token should it use?

- A) A personal access token from the engineer who built it.
- B) A deprecated user API key.
- C) An Account Admin service token.
- D) A service token with only the permission sets the pipeline needs.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A PAT inherits one person's permissions. The docs say to use a PAT only where it's needed and a service token for flows that need a service account. |
> | **B) ❌ Incorrect** | User API keys are deprecated and no longer work. |
> | **C) ❌ Incorrect** | An Account Admin token has full read + write access to the account. The docs say to use it with caution. |
> | **D) ✅ Correct** | Service tokens belong to the account, not a user, and carry explicit permission sets that can be scoped to specific projects. |
>
> > 💡 **Key rule**: Production automation → a service token with minimal permission sets. A PAT inherits the creator's permissions and is account-specific.

---

### Q22.
> **Subdomain 5.22 — Service token permissions and creation**

A team architect is configuring a new service token for a multi-project CI/CD integration on the **Enterprise** plan. They want the token to have:
- `Job Admin` permission on Project A only
- `Read-Only` permission on Project B only
- No access to any other project

Which of the following statements about this configuration are correct? **Select TWO correct answers.**

- A) The service token can be created by any user holding a Developer license — license type determines token-creation rights.
- B) Creating a service token takes a Developer license and account admin permissions.
- C) On a Developer or Starter plan, this configuration would be impossible — only Semantic Layer permission sets are available to service tokens on those tiers.
- D) A single service token can carry both permission sets simultaneously, with each permission set scoped to specific projects.
- E) The architect must create two separate service tokens (one per permission set) because each service token can only carry a single permission set.

> [!success]- Answer & Explanations
> **✅ Correct: B, D** *(C is also factually correct but the scenario specifies Enterprise, so it's not the issue here — see explanation)*
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | A Developer license alone isn't enough. Creating a service token also takes account admin permissions. |
> | **B) ✅ Correct** | The docs say you can generate service tokens if you have a Developer license **and** account admin permissions. Read-Only and IT licenses can't use service tokens. |
> | **C) ❌ Incorrect (in this scenario)** | This statement is factually true — on Developer/Starter plans, service tokens can only be assigned **Semantic Layer permissions**. However, the scenario specifies the **Enterprise plan**, so the architect has access to all permission sets. C is therefore not a correct answer for this question. |
> | **D) ✅ Correct** | A single service token can carry **multiple permission sets**, and each permission set can be scoped to **all projects** or to **specific projects**. The architect's intent — `Job Admin` on Project A + `Read-Only` on Project B in a single token — is exactly the canonical least-privilege pattern that service tokens are designed to support. |
> | **E) ❌ Incorrect** | Service tokens explicitly support multiple permission sets per token. Splitting into two tokens is unnecessary and reduces operational simplicity (more secrets to rotate). |
>
> > 💡 **Key rule**: Service tokens — multiple permission sets per token, each project-scopable. Created with a Developer license + account admin permissions. Permission set availability: Enterprise/Enterprise+ = any; Legacy Team = limited; Developer/Starter = Semantic Layer only.

---

*[End of Topic 5 — 22 questions]*

