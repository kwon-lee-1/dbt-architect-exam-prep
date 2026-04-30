# Topic 2: Git Connections — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 2.1 — GitLab personal repos**

A developer on a team sets up a GitLab OAuth connection in dbt Cloud pointing to a repository under their personal GitLab account (e.g., `gitlab.com/alice/my-dbt-project`). The OAuth connection succeeds and CI jobs trigger, but no CI runs execute in dbt. What is the root cause?

- A) The developer used `read_api` scope instead of `api` scope for the GitLab OAuth app.
- B) GitLab repos must belong to a **GitLab group** — personal account repos are not supported for native integration.
- C) The developer does not have Maintainer role on the repository.
- D) CI triggers are only supported for GitLab Pro and higher — not GitLab Free.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Using `read_api` instead of `api` scope would prevent the OAuth app from functioning entirely, not just cause CI runs to fail silently. However, the question states the connection "succeeds" — suggesting scope is not the issue here. |
> | **B) ✅ Correct** | dbt Cloud's GitLab native integration only works with repos that belong to a **GitLab group** (e.g., `gitlab.com/my-org/repo`). Personal user account repos (`gitlab.com/alice/repo`) are not supported — the integration will appear to connect but CI will not execute. |
> | **C) ❌ Incorrect** | Maintainer role is required to *set up* the connection, but once it's configured, lacking this role would not cause silent CI failures if the integration was previously established. |
> | **D) ❌ Incorrect** | CI jobs trigger on GitLab Free — the limitation on Free is that **status is not posted back** to Merge Requests, not that CI won't trigger. |
>
> > 💡 **Key rule**: GitLab repos must be in a **GitLab group**, not a personal account. Personal repos are unsupported.

---

### Q2. ⭐
> **Subdomain 2.2 — Azure DevOps plan requirements**

A company on the dbt Cloud Starter plan connects their Azure DevOps repository using deploy keys. Developers complain that CI jobs never trigger automatically when PRs are opened. The team asks if upgrading to Enterprise would fix this. Is it correct?

- A) No — CI triggers with Azure DevOps are available on all plans; the deploy key setup is likely misconfigured.
- B) Yes — Azure DevOps native integration (which enables automatic CI triggers) is **Enterprise-only**. Starter can only use deploy keys, which don't support auto CI.
- C) Yes — but only if they also switch from deploy keys to Service Principal authentication.
- D) No — Azure DevOps CI triggers require a separate webhook configuration regardless of plan.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deploy keys intentionally do not support automatic CI triggers on any plan. This is not a misconfiguration — it's a plan limitation. |
> | **B) ✅ Correct** | Azure DevOps **native integration** (which enables automatic CI triggers and PR status checks) is **Enterprise/Enterprise+ only**. On Starter, teams are limited to deploy keys, which require manual CI triggering via the API. |
> | **C) ❌ Incorrect** | While Service Principal is the recommended auth method for Azure DevOps on Enterprise, the issue in the question is the plan limitation — not the auth method. |
> | **D) ❌ Incorrect** | Webhooks are part of the native integration — not an additional manual step that works on all plans. |
>
> > 💡 **Key rule**: Azure DevOps native integration = **Enterprise/Enterprise+ only**. Starter/Developer = deploy keys, no auto CI.

---

### Q3.
> **Subdomain 2.3 — GitHub native app installation**

A company sets up the GitHub native app integration in dbt Cloud. The account admin completes the dbt Cloud side of the setup, but developers report that CI jobs are not triggering on their pull requests. What is the most likely missing step?

- A) The GitHub App was not approved by GitHub's internal review team, causing a 24-hour delay.
- B) Each developer must link their personal GitHub profile in dbt Cloud separately — org-level setup alone is insufficient.
- C) The dbt Cloud account needs to be on Enterprise plan for GitHub CI triggers to work.
- D) The GitHub repository must be set to public for CI triggers to function.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | GitHub Apps don't require review after installation. There is no 24-hour approval delay. |
> | **B) ✅ Correct** | Even after the org-level GitHub native app is installed (requiring both a GitHub org owner AND a dbt Account Admin/Owner), **each developer must separately link their personal GitHub account** in dbt Cloud via their Profile settings. Without this, their PRs won't trigger CI. |
> | **C) ❌ Incorrect** | GitHub CI triggers are available on all plans that support CI jobs — not just Enterprise. |
> | **D) ❌ Incorrect** | Private repositories are fully supported for CI triggers with the GitHub native integration. |
>
> > 💡 **Key rule**: GitHub native app requires two steps: org-level install (org owner + dbt admin) AND each developer links personal profile separately.

---

### Q4.
> **Subdomain 2.4 — GitLab Free Plan CI status**

A team migrates their Git provider from GitHub to GitLab Free. After the migration, dbt CI jobs run successfully in dbt Cloud and tests pass, but developers say they see no green checkmark on their Merge Requests in GitLab. What is the cause?

- A) The OAuth app is missing the `api` scope — only `read_api` was granted, preventing status write-back.
- B) dbt CI runs on GitLab Free don't post status checks back to Merge Requests — this is a Free plan limitation.
- C) The GitLab repo is set to private, blocking dbt from writing status back.
- D) Status checks only appear in GitLab after the MR is merged, not while it's open.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | If `api` scope was missing, CI would not trigger at all — not trigger but fail to post status. The question states CI runs succeed. |
> | **B) ✅ Correct** | **GitLab Free** has a known limitation: CI jobs trigger and run in dbt Cloud, but **CI status is not posted back to Merge Requests**. Developers see no green/red check in the GitLab UI. This requires GitLab Pro or higher, or switching providers. |
> | **C) ❌ Incorrect** | Private repository visibility doesn't affect dbt's ability to post status back once the OAuth connection is authorized. |
> | **D) ❌ Incorrect** | On GitLab Pro+, status checks appear in real-time on open MRs — not after merge. The behavior described is a plan limitation, not intended functionality. |
>
> > 💡 **Key rule**: GitLab Free → CI triggers work but **no status posted back to MRs**. Upgrade to Pro for status checks.

---

### Q5.
> **Subdomain 2.5 — Case-sensitive repository names**

A dbt Cloud account admin connects a GitHub repository named `Analytics-Core` to a project. The connection is configured as `analytics-core` (all lowercase) in the dbt Cloud UI. CI jobs are set up and appear functional. What is the likely outcome?

- A) dbt Cloud normalizes repository names to lowercase automatically — no issue will occur.
- B) The connection will experience silent clone failures because repository names are case-sensitive in the dbt UI.
- C) CI jobs will fail with an explicit "repository not found" error, making the issue easy to diagnose.
- D) Git connections are case-insensitive on GitHub, so the mismatch will have no effect.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not normalize repository names. The exact string is used as entered. |
> | **B) ✅ Correct** | Repository names in the dbt UI are **case-sensitive**. A mismatch between `Analytics-Core` and `analytics-core` causes **silent clone failures** — not an obvious error, making this a difficult bug to diagnose. |
> | **C) ❌ Incorrect** | The failure is described as "silent" in dbt documentation — it doesn't always produce a clear error message, which is what makes it a notable gotcha. |
> | **D) ❌ Incorrect** | While GitHub itself may be case-insensitive in some contexts, the dbt UI performs an exact string match — case mismatches cause failures. |
>
> > 💡 **Key rule**: Repo name is **case-sensitive** in dbt UI. `Analytics-Core` ≠ `analytics-core` → silent clone failure.

---

### Q6.
> **Subdomain 2.6 — BitBucket and CodeCommit**

An organization uses AWS CodeCommit for version control. They want to set up automated CI in dbt Cloud so that jobs trigger on every pull request. Which approach is required?

- A) Use the dbt Cloud native CodeCommit integration available in Account Settings → Integrations.
- B) Use the Git URL (deploy key) method to connect the repo, then manually trigger CI via the dbt Admin API when PRs are opened.
- C) CodeCommit PRs cannot trigger dbt CI under any configuration — use GitHub or GitLab instead.
- D) CodeCommit CI works automatically when using an IAM role-based connection in dbt Cloud.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is **no native CodeCommit integration** in dbt Cloud. It is not listed in Account Settings integrations. |
> | **B) ✅ Correct** | For CodeCommit (and BitBucket), the only option is the **Git URL / deploy key** method for the repo connection. To trigger CI automatically, teams must set up a webhook or pipeline in CodeCommit that calls the **dbt Admin API** to trigger a job run. This is a manual integration. |
> | **C) ❌ Incorrect** | It is *possible* to trigger CI — just not automatically via a native integration. The API-based approach enables it with extra engineering effort. |
> | **D) ❌ Incorrect** | dbt Cloud does not support IAM role-based authentication for CodeCommit connections. |
>
> > 💡 **Key rule**: BitBucket and CodeCommit = **no native integration**. Use Git clone + dbt Admin API to trigger CI manually.

---

### Q7.
> **Subdomain 2.7 — Azure DevOps Server (on-premises)**

A large enterprise runs Azure DevOps Server on-premises. They are evaluating upgrading to dbt Cloud Enterprise to get the Azure DevOps native integration. Will the upgrade enable native integration for their on-premises instance?

- A) Yes — dbt Cloud Enterprise enables native Azure DevOps integration for both cloud-hosted and on-premises instances.
- B) No — Azure DevOps Server (on-premises) has no native dbt Cloud integration on any plan. They must use the Git URL method.
- C) Yes — but only if the on-premises server is accessible via a public FQDN.
- D) No — on-premises Azure DevOps requires PrivateLink before native integration can be configured.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The Enterprise Azure DevOps native integration only works with the **cloud-hosted** Azure DevOps (dev.azure.com). On-premises Azure DevOps Server is explicitly excluded. |
> | **B) ✅ Correct** | **Azure DevOps Server (on-premises)** has **no native dbt Cloud integration on any plan** — not even Enterprise+. Teams using on-premises ADO must connect via the Git URL/deploy key method regardless of their dbt Cloud plan tier. |
> | **C) ❌ Incorrect** | Public FQDN accessibility is not a documented path to native integration for on-prem ADO. |
> | **D) ❌ Incorrect** | PrivateLink is a network feature — it doesn't unlock native provider integrations. |
>
> > 💡 **Key rule**: Azure DevOps Server (on-prem) = **no native integration on any plan**. Cloud ADO = Enterprise/Enterprise+ only.

---

### Q8.
> **Subdomain 2.8 — GitLab OAuth setup requirements**

A company on dbt Cloud Enterprise is setting up GitLab as their Git provider. Which of the following steps are required? **Select TWO correct answers.**

- A) The GitLab OAuth app must be granted the `api` scope (not just `read_api`).
- B) The repository must be in a GitLab group, not under a personal user account.
- C) The dbt user must have the Owner role on the GitLab project.
- D) The GitLab instance must be version 14.0 or higher.
- E) The OAuth app credentials must be added to each project individually, not at the account level.

> [!success]- Answer & Explanations
> **✅ Correct: A, B**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The GitLab OAuth app requires the **`api` scope** — not just `read_api`. The `api` scope grants read/write access to the API including posting CI status back to MRs. Using only `read_api` breaks CI status write-back. |
> | **B) ✅ Correct** | Repositories must belong to a **GitLab group** (e.g., `gitlab.com/my-org/repo`). Personal account repos are not supported for the native integration. |
> | **C) ❌ Incorrect** | The required role is **Maintainer**, not Owner. Owner is more permissive than required. |
> | **D) ❌ Incorrect** | There is no documented GitLab version requirement at 14.0+ — this is not a listed constraint. |
> | **E) ❌ Incorrect** | On Enterprise, an admin creates a group-owned OAuth app and adds the Application ID + Secret to **Account Settings → Integrations** — it's configured once at the account level. |
>
> > 💡 **Key rule**: GitLab = `api` scope (not `read_api`) + repo must be in a **GitLab group** + **Maintainer role** required.

---

---

### Q9.
> **Subdomain 2.9 — GitLab OAuth scope**

A team sets up GitLab integration in dbt Cloud using an OAuth app configured with `read_api` scope. CI jobs trigger successfully and runs execute, but developers report that after a CI run completes, no status check (pass/fail indicator) appears on their GitLab Merge Requests. What is the cause?

- A) GitLab Free Plan does not allow status checks regardless of OAuth scope.
- B) The OAuth app was configured with `read_api` scope instead of `api` scope — dbt cannot post status back to MRs without write API access.
- C) MR status checks require the GitLab native integration, which is only available on Enterprise tier.
- D) Status checks are only posted for `job.run.completed` webhook events, not for CI runs.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | GitLab Free Plan does suppress status checks — but that is a separate scenario. This question states runs execute, suggesting a paid plan. The proximate cause here is the OAuth scope. |
> | **B) ✅ Correct** | The GitLab OAuth app **requires `api` scope**, not just `read_api`. The `api` scope grants read/write API access, which is needed for dbt to write CI status back to Merge Requests. `read_api` only allows reading — dbt can trigger and run jobs but cannot post status checks to the MR. |
> | **C) ❌ Incorrect** | GitLab native integration is available on multiple tiers. The issue here is OAuth scope, not plan tier. |
> | **D) ❌ Incorrect** | CI status checks are posted directly from the dbt Cloud CI system to GitLab via the API, not via webhooks. |
>
> > 💡 **Key rule**: GitLab OAuth app must have **`api` scope** (not `read_api`). Without it, dbt can run CI but cannot post status back to Merge Requests.

---

### Q10.
> **Subdomain 2.10 — GitLab Maintainer role**

A developer with **Developer** role (not Maintainer) on a GitLab group repository attempts to set up the GitLab OAuth connection in dbt Cloud. The connection setup fails. What is the reason?

- A) GitLab Developer role cannot read repository contents, which dbt requires.
- B) Setting up the GitLab native integration requires **Maintainer** role on the repository — Developer role is insufficient.
- C) Only GitLab group Owners can connect repositories to external tools like dbt Cloud.
- D) The Developer role in GitLab cannot generate OAuth tokens at all.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | GitLab Developer role has read access to repository contents. Read access is not the issue. |
> | **B) ✅ Correct** | The dbt Cloud GitLab native integration requires **Maintainer role** on the repository or group. Developer role is insufficient. The Maintainer role is needed to configure hooks and OAuth app settings that enable CI integration. |
> | **C) ❌ Incorrect** | Owner is not required — Maintainer is sufficient. |
> | **D) ❌ Incorrect** | Any GitLab user can generate personal OAuth tokens. The restriction is around what the token can do based on role, not whether a token can be generated. |
>
> > 💡 **Key rule**: GitLab integration requires **Maintainer role** minimum. Developer role is insufficient.

---

### Q11.
> **Subdomain 2.11 — GitLab Enterprise vs Starter setup flow**

An organization on dbt Cloud Enterprise is setting up GitLab integration. A developer on the same account who is on a personal Starter project is also trying to connect to GitLab. Which statement correctly distinguishes the two setup flows?

- A) Both flows are identical — all plans use personal GitLab OAuth apps connected via Profile Settings.
- B) On Enterprise, an admin creates a **group-owned OAuth app** and configures it in Account Settings → Integrations. On Starter/Developer, each user connects their personal GitLab account via Profile Settings → Linked Accounts.
- C) On Enterprise, dbt Cloud uses a pre-built GitLab app that doesn't need manual OAuth configuration. On Starter, a manual deploy key must be used.
- D) On Starter, the group-owned OAuth app method is used. On Enterprise, personal OAuth apps are used for greater isolation.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The flows differ significantly between Enterprise and Starter/Developer tiers. |
> | **B) ✅ Correct** | **Enterprise**: A dbt Cloud admin creates a **group-owned GitLab OAuth app**, then adds the Application ID and Secret to **Account Settings → Integrations**. All users in the account share this app. **Starter/Developer**: Each user connects their personal GitLab account individually via **Profile Settings → Linked Accounts**. There is no account-level shared app setup. |
> | **C) ❌ Incorrect** | dbt Cloud does not provide a pre-built GitLab app — admins must create their own OAuth app in GitLab. |
> | **D) ❌ Incorrect** | This reverses the actual behavior. Enterprise uses the shared group-owned app; personal account linking is for Starter/Developer. |
>
> > 💡 **Key rule**: GitLab Enterprise = admin creates group OAuth app → Account Settings → Integrations. Starter/Developer = each user links personally via Profile Settings.

---

### Q12.
> **Subdomain 2.12 — Azure DevOps recommended authentication**

A platform team is setting up Azure DevOps native integration in dbt Cloud for the first time. They are choosing between two authentication methods: **Service User** and **Service Principal**. Which should they choose, and why?

- A) Service User — it provides more granular permissions than Service Principal.
- B) Service Principal (via Microsoft Entra ID) — it is the recommended method; Service User is a legacy approach.
- C) Either method is acceptable — the choice depends on whether the team uses Entra ID or Active Directory.
- D) Service User — Service Principal requires Enterprise+ while Service User works on Enterprise.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Service User is actually the older, less preferred method. Service Principal provides better security through Entra ID-managed credentials. |
> | **B) ✅ Correct** | **Service Principal** (configured through Microsoft Entra ID) is the **recommended authentication method** for Azure DevOps integration in dbt Cloud. Service User is a legacy approach that dbt still supports but does not recommend for new setups. Service Principal offers better credential management and aligns with modern Azure security practices. |
> | **C) ❌ Incorrect** | dbt explicitly recommends Service Principal over Service User — this is not a neutral choice. |
> | **D) ❌ Incorrect** | There is no plan-tier difference between these two auth methods. Both are available on Enterprise. |
>
> > 💡 **Key rule**: Azure DevOps auth = **Service Principal** (recommended) via Entra ID. Service User = legacy, not recommended for new setups.

---

### Q13.
> **Subdomain 2.13 — Azure DevOps admin coordination**

An organization wants to enable dbt Cloud's native Azure DevOps integration. A project manager says "just have the dbt admin configure it." An architect pushes back, saying it requires coordination across multiple teams. Who is correct, and which teams are involved?

- A) The project manager — only the dbt Account Admin needs to configure the integration from Account Settings.
- B) The architect — setup requires coordination across three admin teams: dbt admins, Azure Entra ID admins, and Azure DevOps admins.
- C) The architect — setup requires both the dbt admin and the Azure DevOps admin, but Entra ID is not involved.
- D) The project manager — if Service User auth is chosen, only one admin is needed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The dbt admin alone cannot complete the setup — Azure-side configuration is required in systems the dbt admin does not control. |
> | **B) ✅ Correct** | Azure DevOps native integration in dbt Cloud requires **three admin teams**: (1) **dbt admins** to configure the integration in dbt Cloud Account Settings; (2) **Azure Entra ID admins** to register the Service Principal app and manage credentials; (3) **Azure DevOps admins** to grant the Service Principal access to the DevOps organization and repositories. Attempting to do this without all three will fail. |
> | **C) ❌ Incorrect** | Entra ID is central to the recommended Service Principal method and must be involved. |
> | **D) ❌ Incorrect** | Even with Service User auth, Azure DevOps admin involvement is required to create and grant the user. The three-team coordination is inherent to the integration. |
>
> > 💡 **Key rule**: Azure DevOps native integration = 3-team coordination: dbt admins + Azure Entra ID admins + Azure DevOps admins.

---

### Q14.
> **Subdomain 2.14 — BitBucket and CodeCommit CI setup**

A team uses BitBucket as their Git provider. They want CI jobs to trigger automatically on every pull request in dbt Cloud. What is the required approach?

- A) Enable the BitBucket native integration in dbt Cloud Account Settings → Integrations.
- B) Use the git URL / deploy key method to connect the repo and configure the dbt Admin API to trigger CI jobs manually on each PR via a BitBucket webhook.
- C) BitBucket is not supported by dbt Cloud in any configuration.
- D) Use BitBucket Pipelines to call `dbt build` directly — no dbt Cloud CI setup is needed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no native BitBucket integration in dbt Cloud. BitBucket (like AWS CodeCommit) has no native dbt Cloud support. |
> | **B) ✅ Correct** | BitBucket and AWS CodeCommit have **no native dbt Cloud integration** on any plan. The workaround: connect the repo via **git URL + deploy key**, then configure a BitBucket webhook that calls the **dbt Admin API** to programmatically trigger CI job runs on pull request events. This mimics the auto-trigger behavior but requires custom setup. |
> | **C) ❌ Incorrect** | BitBucket repos can connect to dbt Cloud via the git URL method — they're just not natively integrated with auto-triggers. |
> | **D) ❌ Incorrect** | Calling `dbt build` via BitBucket Pipelines bypasses dbt Cloud entirely and would not populate dbt Cloud run history, artifacts, or UI features. |
>
> > 💡 **Key rule**: BitBucket + CodeCommit = no native integration on any plan. Use git URL/deploy key + dbt Admin API calls to trigger CI.

---

### Q15.
> **Subdomain 2.15 — GitHub personal profile linking**

A company sets up the GitHub native app integration in dbt Cloud and all CI jobs are configured. A new developer joins the team, is granted dbt Cloud access, and tries to open a PR. The CI job fails with an authentication error when trying to post status back to GitHub. What is the likely cause?

- A) The new developer's GitHub account is not in the GitHub organization and must be added by the org owner.
- B) The new developer has not linked their personal GitHub account to their dbt Cloud profile via Profile Settings.
- C) The GitHub app installation only covers the initial admin — new team members require the app to be re-installed.
- D) The CI job needs to be reconfigured with the new developer's GitHub credentials.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | GitHub org membership is separate from dbt Cloud profile linking. Being in the GitHub org does not automatically link the account in dbt. |
> | **B) ✅ Correct** | Even after the org-level GitHub app is installed, **each developer must individually link their personal GitHub account** to their dbt Cloud profile via **Profile Settings**. This linking enables dbt to authenticate actions (like posting PR status) on behalf of that developer. Failing to link results in authentication errors for that individual. |
> | **C) ❌ Incorrect** | The GitHub app installation is account-level and covers all users — it does not need to be re-installed per user. |
> | **D) ❌ Incorrect** | CI jobs are not reconfigured per developer. The CI job runs under the shared app credential; the developer linking is for personal activity attribution. |
>
> > 💡 **Key rule**: GitHub native app = org-level install (once) + each developer must separately link their personal GitHub profile via Profile Settings.

---

### Q16.
> **Subdomain 2.16 — GitHub org owner requirement**

A dbt Cloud account admin tries to set up the GitHub native app integration but is not the GitHub organization owner — they are only a repository admin. They complete the dbt Cloud side of the setup but CI jobs never trigger. What is the root cause?

- A) Repository admins can install GitHub apps — the issue must be elsewhere in the CI job configuration.
- B) GitHub requires the dbt app to be installed by a GitHub **org owner**. A repository admin cannot install org-level GitHub apps, so the app was never actually installed.
- C) The GitHub app requires a separate token from the repo admin to authorize CI triggers.
- D) GitHub apps only work with GitHub Enterprise, not GitHub.com accounts.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Repository admins cannot install organization-level GitHub apps — only org owners can. |
> | **B) ✅ Correct** | The GitHub native app must be installed by a **GitHub organization owner**. Repository admins lack the permissions to install apps at the org level. If the org owner hasn't installed the app, the integration appears to complete on the dbt side but no CI triggers fire because GitHub never registered the app. |
> | **C) ❌ Incorrect** | No separate token from the repo admin is required. The org-level app installation handles authorization. |
> | **D) ❌ Incorrect** | The GitHub native app works with github.com. GitHub Enterprise on non-`ghe.com` domains requires a different approach (git URL / deploy key), but standard GitHub.com is fully supported. |
>
> > 💡 **Key rule**: GitHub native app must be installed by the **GitHub org owner** — repository admin is insufficient.

---

### Q17.
> **Subdomain 2.17 — Fork PR CI failure**

A contributor forks a dbt Cloud-connected GitHub repository and opens a pull request from their fork. The CI job immediately fails with "unable to check out commit." What is the cause and how should the team handle it?

- A) The contributor's fork is private — they must make it public before dbt can access it.
- B) dbt Cloud cannot check out commits from fork repositories — the contributor must push their branch directly to the origin repository instead.
- C) Fork PRs require a deploy key to be added to the fork repository before CI can run.
- D) The CI job needs to be reconfigured with "allow fork PRs" enabled in the job's Git Trigger settings.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Repository visibility is not the issue. dbt Cloud fundamentally cannot check out commits from any fork, public or private. |
> | **B) ✅ Correct** | dbt Cloud CI cannot check out commits from **forked repositories** — this is an architectural limitation. The contributor must push their branch directly to the origin (upstream) repository. Org teams should document this in their contribution guide: fork PRs are not supported for dbt Cloud CI. |
> | **C) ❌ Incorrect** | Deploy keys on the fork do not resolve this — the limitation is that dbt Cloud only has access credentials for the origin repo, not forks. |
> | **D) ❌ Incorrect** | There is no "allow fork PRs" toggle in dbt Cloud job settings. Fork-based CI is simply not supported. |
>
> > 💡 **Key rule**: Fork PRs = dbt CI cannot check out commits. Contributors must push branches directly to the origin repo.

---

### Q18.
> **Subdomain 2.18 — Azure DevOps reused branch**

A developer on an Azure DevOps project closes a pull request without merging and then opens a new PR using the exact same branch name. The CI job does not trigger for the new PR. What is the cause?

- A) Azure DevOps requires CI jobs to be manually re-enabled after a PR is closed without merging.
- B) dbt Cloud CI will not trigger on a new PR that reuses the same branch name from a previously closed or abandoned PR.
- C) The branch protection rule is preventing new PRs from being opened on used branches.
- D) This is a billing issue — the organization has exceeded its CI run quota for the month.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no manual re-enable step required for CI jobs after a PR is closed. |
> | **B) ✅ Correct** | dbt Cloud has a known CI behavior with Azure DevOps: if a branch name was used in a **previously closed or abandoned PR**, opening a new PR with the **same branch name** (or using the same commit SHA) will not trigger CI. Always use a new branch name for new PRs to ensure CI triggers reliably. |
> | **C) ❌ Incorrect** | Branch protection rules are an Azure DevOps configuration — they would block PR creation entirely, not just CI triggering. |
> | **D) ❌ Incorrect** | CI run quotas are not a documented dbt Cloud billing constraint. |
>
> > 💡 **Key rule**: Azure DevOps CI won't trigger on new PRs that reuse a branch name from an abandoned/closed PR. Always use a fresh branch name.

---

### Q19.
> **Subdomain 2.19 — Deploy key limitations**

An organization on a Starter plan uses a deploy key to connect their GitHub repository to dbt Cloud. They want CI jobs to trigger automatically on every pull request. What is the limitation they will encounter?

- A) Deploy keys expire after 90 days and must be rotated, causing periodic CI outages.
- B) Deploy keys provide read-only repository access — they support manual job triggers but not automatic CI triggers on pull requests.
- C) Deploy keys only work with GitHub and not with GitLab or Azure DevOps.
- D) Deploy keys require a self-hosted dbt runner to function.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Deploy keys do not have a 90-day expiration by default unless set explicitly. Key rotation is best practice but not a hard limitation on CI triggering. |
> | **B) ✅ Correct** | Deploy keys provide **read-only repository access** for dbt to clone the code — they do not give dbt the ability to receive PR webhook events or post status checks back to the Git provider. Automatic CI triggers on pull requests require a **native integration** (GitHub App, Azure DevOps native, GitLab OAuth) — not deploy keys. Starter plan on Azure DevOps is the classic example: deploy keys work for manual runs but auto-CI requires upgrading to Enterprise. |
> | **C) ❌ Incorrect** | Deploy keys work with GitHub, GitLab, Azure DevOps, and other providers — they're a standard Git mechanism, not GitHub-specific. |
> | **D) ❌ Incorrect** | Deploy keys work with dbt Cloud-hosted runners — no self-hosted runner is required. |
>
> > 💡 **Key rule**: Deploy keys = repo clone access only. No automatic PR-triggered CI. Native integration required for auto-triggers.

---

### Q20.
> **Subdomain 2.20 — GitHub Enterprise on non-ghe.com domain**

A company runs GitHub Enterprise Server on their own domain (`github.company.com` — not a `ghe.com` subdomain). They want to connect it to dbt Cloud. Which connection method is required?

- A) GitHub native app integration — it supports any GitHub Enterprise domain.
- B) Azure DevOps native integration, since on-premises GitHub requires a Microsoft product for integration.
- C) Git URL / deploy key method — GitHub Enterprise on non-`ghe.com` domains does not support the native GitHub app integration.
- D) PrivateLink — required for any on-premises Git provider.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The GitHub native app integration supports GitHub.com and GitHub Enterprise on `ghe.com` (GitHub's hosted enterprise offering) — but NOT self-hosted GitHub Enterprise on custom domains. |
> | **B) ❌ Incorrect** | Azure DevOps native integration is for Azure DevOps, not GitHub Enterprise. |
> | **C) ✅ Correct** | GitHub Enterprise Server on a **custom domain** (e.g., `github.company.com`) that is not a `ghe.com` subdomain requires the **git URL / deploy key** connection method. The native GitHub app integration only supports `github.com` and `*.ghe.com` domains. Custom on-premises GitHub Enterprise instances fall back to the deploy key approach. |
> | **D) ❌ Incorrect** | PrivateLink is a network topology feature for VPC-to-VPC connectivity — it is not a Git connection method. |
>
> > 💡 **Key rule**: GitHub Enterprise on custom domain (not `ghe.com`) = git URL / deploy key only. Native app = github.com and `*.ghe.com` only.

---

*[End of Topic 2 — 20 questions]*

