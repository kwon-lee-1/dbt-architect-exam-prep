# Topic 2: Git Connections — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 2.1 — GitLab personal repos**

A developer on a team sets up a GitLab OAuth connection in dbt Cloud pointing to a repository under their personal GitLab account (e.g., `gitlab.com/alice/my-dbt-project`). dbt can't use the repository. What is the root cause?

- A) The developer does not have Maintainer role on the repository.
- B) The developer used `read_api` scope instead of `api` scope for the GitLab OAuth app.
- C) GitLab Free does not report CI status back to merge requests.
- D) GitLab repos must belong to a **GitLab group** — personal account repos are not supported for native integration.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Maintainer role is required to set up the connection, but a missing role isn't the problem here. The repo is in a personal account. |
> | **B) ❌ Incorrect** | The docs list `api` as the scope for the GitLab OAuth app, but scope isn't what this question is about. The problem is where the repo lives. |
> | **C) ❌ Incorrect** | That is a real GitLab Free limitation, but it's about job status, not about which repos dbt can read. |
> | **D) ✅ Correct** | Repos must belong to a **GitLab group** (e.g., `gitlab.com/my-org/repo`). The docs say it plainly: dbt will not read repos associated with a user. |
>
> > 💡 **Key rule**: GitLab repos must be in a **GitLab group**, not a personal account. Personal repos are unsupported.

---

### Q2. ⭐
> **Subdomain 2.2 — Azure DevOps plan requirements**

A company on the dbt Cloud Starter plan connects their Azure DevOps repository using deploy keys. Developers complain that CI jobs never trigger automatically when PRs are opened. The team asks if upgrading to Enterprise would fix this. Is it correct?

- A) No — Azure DevOps CI triggers require a separate webhook configuration regardless of plan.
- B) No — CI triggers with Azure DevOps are available on all plans; the deploy key setup is likely misconfigured.
- C) Yes — Azure DevOps native integration (which enables automatic CI triggers) is **Enterprise-only**. Starter can only use deploy keys, which don't support auto CI.
- D) Yes — but only if they also switch from deploy keys to Service Principal authentication.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Webhooks are part of the native integration — not an additional manual step that works on all plans. |
> | **B) ❌ Incorrect** | Deploy keys intentionally do not support automatic CI triggers on any plan. This is not a misconfiguration — it's a plan limitation. |
> | **C) ✅ Correct** | Azure DevOps **native integration** is **Enterprise/Enterprise+ only**. On Starter and Developer you can connect with a deploy key and still develop, but you can't configure automated CI jobs. |
> | **D) ❌ Incorrect** | While Service Principal is the recommended auth method for Azure DevOps on Enterprise, the issue in the question is the plan limitation — not the auth method. |
>
> > 💡 **Key rule**: Azure DevOps native integration = **Enterprise/Enterprise+ only**. Starter/Developer = deploy keys, no auto CI.

---

### Q3.
> **Subdomain 2.3 — GitHub profile linking (Enterprise)**

A company on the dbt Enterprise plan has installed the GitHub native app. Why does each developer still need to connect their personal GitHub profile to dbt?

- A) GitHub requires a separate app approval for every developer.
- B) The Studio IDE checks each developer's read/write access to the repo, so each developer must link their own profile.
- C) Linking a profile is what turns on the native GitHub integration for the whole account.
- D) Without a linked profile, dbt can't run scheduled jobs.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The app is installed once, by a GitHub org owner. Nothing in the docs asks for a per-developer approval. |
> | **B) ✅ Correct** | On Enterprise/Enterprise+, every developer must connect their GitHub profile, because the Studio IDE verifies each developer's read/write access to the dbt repo. |
> | **C) ❌ Incorrect** | The org-level install (GitHub org owner + dbt Owner/Account Admin) turns on the integration. Profile linking is a separate, per-developer step. |
> | **D) ❌ Incorrect** | The docs tie profile linking to IDE/CLI access, not to scheduled jobs. |
>
> > 💡 **Key rule**: Enterprise/Enterprise+ = every developer links their GitHub profile (the IDE checks read/write access). Starter = optional but recommended.

---

### Q4.
> **Subdomain 2.4 — GitLab Free Plan CI status**

A team migrates their Git provider from GitHub to GitLab Free. After the migration, dbt CI jobs run successfully in dbt Cloud and tests pass, but developers say they see no green checkmark on their Merge Requests in GitLab. What is the cause?

- A) The GitLab repo is set to private, blocking dbt from writing status back.
- B) The repo belongs to a personal GitLab account instead of a GitLab group.
- C) Status checks only appear in GitLab after the MR is merged, not while it's open.
- D) dbt CI runs on GitLab Free don't post status checks back to Merge Requests — this is a Free plan limitation.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Repo visibility is not the documented reason. The documented reason is the GitLab plan. |
> | **B) ❌ Incorrect** | dbt would not read a repo tied to a personal account, so CI would not run at all. The question says CI runs succeed. |
> | **C) ❌ Incorrect** | On supported GitLab plans, status is reported while the MR is open. What the question describes is a plan limitation. |
> | **D) ✅ Correct** | On **GitLab Free**, MRs still trigger CI jobs, but the job status (success or failure) is **not reported back** to GitLab. Native CI needs a paid or self-hosted GitLab that supports webhooks and project access tokens. |
>
> > 💡 **Key rule**: GitLab Free → CI triggers work but **no status posted back to MRs**. Use a paid or self-hosted GitLab for status checks.

---

### Q5.
> **Subdomain 2.5 — Case-sensitive repository names**

A dbt Cloud account admin connects a GitHub repository named `Analytics-Core` to a project. The connection is configured as `analytics-core` (all lowercase) in the dbt Cloud UI. CI jobs are set up and appear functional. What is the likely outcome?

- A) The repo name must match the case in the GitHub URL, so cloning will fail or jobs will error.
- B) Git connections are case-insensitive on GitHub, so the mismatch will have no effect.
- C) dbt Cloud normalizes repository names to lowercase automatically — no issue will occur.
- D) The case mismatch only matters for GitHub Enterprise, not GitHub.com.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say the repository name must exactly match the case used in the GitHub URL (`Analytics-Core`, not `analytics-core`) to avoid cloning errors or job failures. |
> | **B) ❌ Incorrect** | The docs say the name must match the case in the GitHub URL exactly. |
> | **C) ❌ Incorrect** | dbt Cloud does not normalize repository names. The exact string is used as entered. |
> | **D) ❌ Incorrect** | The docs give the case rule for GitHub repos in general, not just for Enterprise. |
>
> > 💡 **Key rule**: Repo name must match the GitHub URL **exactly, including case**. `Analytics-Core` ≠ `analytics-core` → clone errors or job failures.

---

### Q6.
> **Subdomain 2.6 — BitBucket and CodeCommit**

An organization uses AWS CodeCommit for version control. They want to set up automated CI in dbt Cloud so that jobs trigger on every pull request. Which approach is required?

- A) CodeCommit CI works automatically when using an IAM role-based connection in dbt Cloud.
- B) Use the dbt Cloud native CodeCommit integration available in Account Settings → Integrations.
- C) Use the Git URL (deploy key) method to connect the repo, then trigger CI jobs through the dbt Administrative API.
- D) CodeCommit PRs cannot trigger dbt CI under any configuration — use GitHub or GitLab instead.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | CodeCommit is set up with an IAM user and a dbt-generated key. There is no automated CI for it. |
> | **B) ❌ Incorrect** | There is **no native CodeCommit integration** in dbt Cloud. It is not listed in Account Settings integrations. |
> | **C) ✅ Correct** | CodeCommit (and BitBucket) have no native integration, so you connect with the **Git clone / deploy key** method and use the **dbt Administrative API** to trigger CI jobs. API triggering needs Enterprise/Enterprise+. |
> | **D) ❌ Incorrect** | CI can be triggered through the Administrative API. |
>
> > 💡 **Key rule**: BitBucket and CodeCommit = **no native integration**, no automated CI. Use Git clone + dbt Admin API (Enterprise/Enterprise+) to trigger CI.

---

### Q7.
> **Subdomain 2.7 — Azure DevOps Server (on-premises)**

A large enterprise runs Azure DevOps Server on-premises. They are evaluating upgrading to dbt Cloud Enterprise to get the Azure DevOps native integration. Will the upgrade enable native integration for their on-premises instance?

- A) No — Azure DevOps Server (on-premises) has no native dbt Cloud integration on any plan. They must use the Git URL method.
- B) Yes — but only if the on-premises server is accessible via a public FQDN.
- C) Yes — dbt Cloud Enterprise enables native Azure DevOps integration for both cloud-hosted and on-premises instances.
- D) No — on-premises Azure DevOps requires PrivateLink before native integration can be configured.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | **Azure DevOps Server (on-premises)** has **no native dbt Cloud integration on any plan** — not even Enterprise+. Teams using on-premises ADO must connect via the Git URL/deploy key method regardless of their dbt Cloud plan tier. |
> | **B) ❌ Incorrect** | Public FQDN accessibility is not a documented path to native integration for on-prem ADO. |
> | **C) ❌ Incorrect** | The native integration is for Azure DevOps cloud accounts. The docs say it does not support Azure DevOps Server (on-premise). |
> | **D) ❌ Incorrect** | PrivateLink is a network feature — it doesn't unlock native provider integrations. |
>
> > 💡 **Key rule**: Azure DevOps Server (on-prem) = **no native integration on any plan**. Cloud ADO = Enterprise/Enterprise+ only.

---

### Q8.
> **Subdomain 2.8 — GitLab OAuth setup requirements**

A company on dbt Cloud Enterprise is setting up GitLab as their Git provider. Which of the following steps are required? **Select TWO correct answers.**

- A) The OAuth app credentials must be added to each project individually, not at the account level.
- B) The dbt user must have the Owner role on the GitLab project.
- C) The GitLab OAuth app must be created with the `api` scope.
- D) The repository must be in a GitLab group, not under a personal user account.
- E) The GitLab instance must be version 14.0 or higher.

> [!success]- Answer & Explanations
> **✅ Correct: C, D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | On Enterprise, an admin creates a group-owned OAuth app and adds the Application ID + Secret to **Account Settings → Integrations** — it's configured once at the account level. |
> | **B) ❌ Incorrect** | The required role is **Maintainer**, not Owner. Owner is more permissive than required. |
> | **C) ✅ Correct** | The group-owned GitLab OAuth app is created with the **`api` scope**. |
> | **D) ✅ Correct** | Repositories must belong to a **GitLab group** (e.g., `gitlab.com/my-org/repo`). Personal account repos are not supported for the native integration. |
> | **E) ❌ Incorrect** | There is no documented GitLab version requirement at 14.0+ — this is not a listed constraint. |
>
> > 💡 **Key rule**: GitLab = `api` scope + repo must be in a **GitLab group** + **Maintainer role** required.

---

---

### Q9.
> **Subdomain 2.9 — GitLab webhook and project access token**

A GitLab repo is connected to dbt with the native integration. What does dbt set up in GitLab automatically so CI can run and report back?

- A) A scheduled poll that checks GitLab for new merge requests.
- B) A group-owned OAuth app for the whole account.
- C) A webhook that triggers jobs in dbt, and a project access token that sends the job status back to GitLab.
- D) A deploy key that dbt uses to comment on merge requests.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt listens for notifications from the Git provider (the webhook). It doesn't poll. |
> | **B) ❌ Incorrect** | On Enterprise, the admin creates the OAuth app themselves before connecting any repo. dbt doesn't create it during repo setup. |
> | **C) ✅ Correct** | When you configure the repo, dbt registers a **webhook** (triggers jobs in dbt) and creates a **project access token** (sends the job run status back to GitLab). dbt refreshes the token automatically. |
> | **D) ❌ Incorrect** | Deploy keys belong to the Git clone method, not the native integration. |
>
> > 💡 **Key rule**: GitLab native CI = webhook (triggers) + project access token (reports status). CI not triggering? Check the webhook in GitLab (Settings → Webhooks): enabled, correct URL and secret.

---

### Q10.
> **Subdomain 2.10 — GitLab Maintainer role**

A developer with **Developer** role (not Maintainer) on a GitLab group repository attempts to set up the GitLab OAuth connection in dbt Cloud. The connection setup fails. What is the reason?

- A) The Developer role in GitLab cannot generate OAuth tokens at all.
- B) Only GitLab group Owners can connect repositories to external tools like dbt Cloud.
- C) GitLab Developer role cannot read repository contents, which dbt requires.
- D) Setting up the GitLab native integration requires **Maintainer** role on the repository — Developer role is insufficient.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not what the docs say. The documented requirement is the Maintainer role. |
> | **B) ❌ Incorrect** | Owner is not required — Maintainer is sufficient. |
> | **C) ❌ Incorrect** | GitLab Developer role has read access to repository contents. Read access is not the issue. |
> | **D) ✅ Correct** | The docs say only users with **Maintainer** permissions can set up repository connections. Developer role is insufficient. |
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

- A) Service User — Service Principal requires Enterprise+ while Service User works on Enterprise.
- B) Either method is acceptable — the choice depends on whether the team uses Entra ID or Active Directory.
- C) Service Principal (via Microsoft Entra ID) — it is the recommended method; Service User is a legacy approach.
- D) Service User — it provides more granular permissions than Service Principal.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs list both methods as available to all accounts with the Azure DevOps integration. |
> | **B) ❌ Incorrect** | dbt explicitly recommends Service Principal over Service User — this is not a neutral choice. |
> | **C) ✅ Correct** | **Service Principal** is the **recommended** authentication method for Azure DevOps. The docs label Service User as **legacy**. |
> | **D) ❌ Incorrect** | The docs label Service User as legacy and Service Principal as recommended. |
>
> > 💡 **Key rule**: Azure DevOps auth = **Service Principal** (recommended) via Entra ID. Service User = legacy, not recommended for new setups.

---

### Q13.
> **Subdomain 2.13 — Azure DevOps admin coordination**

An organization wants to enable dbt Cloud's native Azure DevOps integration. A project manager says "just have the dbt admin configure it." An architect pushes back, saying it requires coordination across multiple teams. Who is correct, and which teams are involved?

- A) The project manager — if Service User auth is chosen, only one admin is needed.
- B) The project manager — only the dbt Account Admin needs to configure the integration from Account Settings.
- C) The architect — setup requires both the dbt admin and the Azure DevOps admin, but Entra ID is not involved.
- D) The architect — setup requires coordination across three admin teams: dbt admins, Azure Entra ID admins, and Azure DevOps admins.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say you need all three admin teams no matter which approach you take. |
> | **B) ❌ Incorrect** | The dbt admin alone cannot complete the setup — Azure-side configuration is required in systems the dbt admin does not control. |
> | **C) ❌ Incorrect** | Entra ID is central to the recommended Service Principal method and must be involved. |
> | **D) ✅ Correct** | The docs say you need admins for **dbt, Azure Entra ID, and Azure DevOps** to complete the integration. |
>
> > 💡 **Key rule**: Azure DevOps native integration = 3-team coordination: dbt admins + Azure Entra ID admins + Azure DevOps admins.

---

### Q14.
> **Subdomain 2.14 — API-triggered CI and schema cleanup**

A team uses BitBucket and triggers dbt CI jobs through the dbt Administrative API when PRs are opened. What will dbt **not** do for them automatically?

- A) Delete the temporary CI schema after the PR is closed or merged.
- B) Read the repo using the deploy key.
- C) Build the modified models in the CI job.
- D) Run the CI job.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say dbt will not auto-delete the temporary schema for API-triggered CI. Automatic deletion relies on webhooks from the Git provider, which only native integrations have. |
> | **B) ❌ Incorrect** | The deploy key is how dbt clones the repo with the Git clone method. |
> | **C) ❌ Incorrect** | The job still runs its commands. |
> | **D) ❌ Incorrect** | The API call starts the CI job as normal. |
>
> > 💡 **Key rule**: Non-native provider + Admin API for CI (Enterprise/Enterprise+) = you clean up the temp CI schema yourself.

---

### Q15.
> **Subdomain 2.15 — Switching to a custom GitHub app**

A company has used the shared dbt GitHub app and switches to its own custom GitHub app. What happens to developers' existing GitHub profile links?

- A) They carry over automatically.
- B) Every existing link is invalidated, and everyone on the account must relink their GitHub profile.
- C) Only account admins have to relink.
- D) Only Starter developers have to relink.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs say switching to your own application invalidates every existing GitHub profile link. |
> | **B) ✅ Correct** | Every existing link is invalidated, so everyone on the account has to relink. |
> | **C) ❌ Incorrect** | It affects everyone on the account, not just admins. |
> | **D) ❌ Incorrect** | It isn't tied to a plan. |
>
> > 💡 **Key rule**: Shared app → custom app = everyone relinks. Also: **one GitHub app per dbt account**, not per project.

---

### Q16.
> **Subdomain 2.16 — GitHub org owner requirement**

A dbt Cloud account admin tries to set up the GitHub native app integration but is not the GitHub organization owner — they are only a repository admin. They complete the dbt Cloud side of the setup but CI jobs never trigger. What is the root cause?

- A) GitHub requires the dbt app to be installed by a GitHub **org owner**. A repository admin cannot install org-level GitHub apps, so the app was never actually installed.
- B) The GitHub app requires a separate token from the repo admin to authorize CI triggers.
- C) GitHub apps only work with GitHub Enterprise, not GitHub.com accounts.
- D) Repository admins can install GitHub apps — the issue must be elsewhere in the CI job configuration.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say you must be a **GitHub organization owner** to install the dbt GitHub App. That person also needs Owner or Account Admin permissions in dbt. |
> | **B) ❌ Incorrect** | No separate token from the repo admin is required. The org-level app installation handles authorization. |
> | **C) ❌ Incorrect** | The shared dbt GitHub App is available to any org connecting to `github.com`. |
> | **D) ❌ Incorrect** | Repository admins cannot install organization-level GitHub apps — only org owners can. |
>
> > 💡 **Key rule**: GitHub native app must be installed by the **GitHub org owner** — repository admin is insufficient.

---

### Q17.
> **Subdomain 2.17 — Fork PR CI failure**

A contributor forks a dbt Cloud-connected GitHub repository and opens a pull request from their fork. The job fails at the Clone Git Repository step with "Failed to checkout to specified revision." What is the cause and how should the team handle it?

- A) The contributor's fork is private — they must make it public before dbt can access it.
- B) Fork PRs require a deploy key to be added to the fork repository before CI can run.
- C) The CI job needs to be reconfigured with "allow fork PRs" enabled in the job's Git Trigger settings.
- D) dbt Cloud cannot check out commits from fork repositories — the contributor must push their branch directly to the origin repository instead.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Visibility is not the issue. dbt can't check out commits that belong to a fork. |
> | **B) ❌ Incorrect** | Not a documented fix. dbt can only check out commits from the original repo. |
> | **C) ❌ Incorrect** | Not a documented setting. |
> | **D) ✅ Correct** | The docs say dbt can only check out commits that belong to the **original repository**, not commits that belong to a fork. Push the branch to the original repo instead. |
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
> | **B) ✅ Correct** | dbt won't trigger a CI run if the latest commit in a PR has already triggered a run for that job. If PR 1 is abandoned and PR 2 is opened from the same branch (same commit) into `main`, no new run starts. Use a new branch or a new commit. |
> | **C) ❌ Incorrect** | Branch protection rules are an Azure DevOps configuration — they would block PR creation entirely, not just CI triggering. |
> | **D) ❌ Incorrect** | CI run quotas are not a documented dbt Cloud billing constraint. |
>
> > 💡 **Key rule**: Azure DevOps CI won't trigger on a new PR whose latest commit already triggered a run (e.g. branch reused after an abandoned PR). Use a new branch or a new commit.

---

### Q19.
> **Subdomain 2.19 — Deploy key limitations**

An organization on a Starter plan uses a deploy key to connect their GitHub repository to dbt Cloud. They want CI jobs to trigger automatically on every pull request. What is the limitation they will encounter?

- A) Deploy keys expire after 90 days and must be rotated, causing periodic CI outages.
- B) Deploy keys require a self-hosted dbt runner to function.
- C) Deploy keys (the Git clone method) don't support automated CI jobs, because there is no native integration with the Git host.
- D) Deploy keys only work with GitHub and not with GitLab or Azure DevOps.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs don't describe key expiry as a limitation. |
> | **B) ❌ Incorrect** | Deploy keys work with dbt Cloud-hosted runners — no self-hosted runner is required. |
> | **C) ✅ Correct** | The Git clone method has no native integration, so dbt can't use features that need a tight integration with the Git host, like updating PRs with run statuses. Automated CI needs a native integration. To trigger CI anyway, use the Administrative API (Enterprise/Enterprise+). |
> | **D) ❌ Incorrect** | Deploy keys work with GitHub, GitLab, Azure DevOps, and other providers — they're a standard Git mechanism, not GitHub-specific. |
>
> > 💡 **Key rule**: Deploy key (Git clone) = no automated CI, no PR status updates. The key needs **read and write** access.

---

### Q20.
> **Subdomain 2.20 — GitHub Enterprise Server / on-prem GitHub**

A company on the dbt **Starter** plan runs GitHub Enterprise Server on their own domain (`github.company.com`). They want to connect it to dbt. Which connection method works?

- A) PrivateLink — required for any on-premises Git provider.
- B) Git URL / deploy key — on plans below Enterprise, this is how on-prem GitHub connects.
- C) Azure DevOps native integration, since on-premises GitHub requires a Microsoft product for integration.
- D) The shared dbt GitHub App — it works with any GitHub domain.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | PrivateLink is a network feature, not a Git connection method. |
> | **B) ✅ Correct** | On Enterprise/Enterprise+ you can use the native integration by registering a **custom GitHub application** (private beta). On other plans, like Starter, connect with a **Git URL**, which supports fewer Git features. |
> | **C) ❌ Incorrect** | Azure DevOps native integration is for Azure DevOps, not GitHub Enterprise. |
> | **D) ❌ Incorrect** | The shared dbt GitHub App only reaches `github.com`. It can't reach on-prem GitHub (or `ghe.com`). |
>
> > 💡 **Key rule**: On-prem GitHub or `ghe.com`: Enterprise/Enterprise+ → custom GitHub app (private beta). Other plans → Git URL / deploy key. The shared dbt app can't reach either.

---

*[End of Topic 2 — 20 questions]*

