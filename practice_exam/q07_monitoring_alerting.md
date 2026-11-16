# Topic 6: Monitoring & Alerting — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 6.1 — Webhook auto-archive**

A webhook's endpoint keeps failing. What does dbt do?

- A) Archives the webhook after 1,000 consecutive failed deliveries or 7 consecutive days of failed deliveries, whichever comes first.
- B) Disables it after 5 consecutive failed deliveries.
- C) Never disables it. It keeps retrying forever.
- D) Pauses it for 30 minutes after each failure, then resumes.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say dbt automatically archives a webhook after 1,000 consecutive failed deliveries or 7 consecutive days of failed deliveries, whichever comes first. |
> | **B) ❌ Incorrect** | Five is how many times dbt retries each event, not the archive threshold. |
> | **C) ❌ Incorrect** | dbt does archive failing webhooks. |
> | **D) ❌ Incorrect** | Not documented. |
>
> > 💡 **Key rule**: Each event is retried **5 times**. A webhook is archived after **1,000 consecutive failures or 7 days** of failures. Reactivate by changing the endpoint URL (UI) or `PUT` with `active: true` (API).

---

### Q2. ⭐
> **Subdomain 6.2 — Webhook event timing and artifacts**

A team's webhook handler listens for `job.run.errored` events and immediately queries the dbt Cloud API for the run's artifacts (manifest, catalog, sources) to post a diagnostic report to their incident channel. The handler fails to retrieve any artifacts. Why?

- A) The webhook needs the `artifact_read` scope on its service token to access artifacts.
- B) `job.run.errored` fires **before** artifact ingestion — artifacts are not yet available at handler time. Use `job.run.completed` instead.
- C) Artifacts are only stored for successful runs — errored runs have no artifacts.
- D) `job.run.errored` events don't include the run ID needed to query artifacts.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Artifact access is controlled by service token permission sets, not a specific `artifact_read` scope. |
> | **B) ✅ Correct** | `job.run.errored` fires **immediately** when an error is detected — before dbt Cloud has finished ingesting artifacts. `job.run.completed` fires **after** artifact ingestion is complete, making it the correct event for any handler that needs to query the API for run artifacts. Use `errored` only when you need the fastest possible notification and don't need artifacts. |
> | **C) ❌ Incorrect** | The issue is timing. The docs say that on `job.run.errored` the job's metadata and artifacts might not have been ingested yet. |
> | **D) ❌ Incorrect** | `job.run.errored` events include the run ID and other run metadata. |
>
> > 💡 **Key rule**: `errored` = fires before artifacts (fast notification). `completed` = fires after artifacts (use when you need API data).

---

### Q3.
> **Subdomain 6.3 — Webhook event types**

Which of the following are valid dbt Cloud webhook event types? **Select TWO correct answers.**

- A) `job.run.completed`
- B) `job.run.timeout`
- C) `job.run.queued`
- D) `job.run.started`
- E) `job.run.cancelled`

> [!success]- Answer & Explanations
> **✅ Correct: A, D**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `job.run.completed` fires after the run finishes (success or failure) AND after artifact ingestion. One of the three supported event types. |
> | **B) ❌ Incorrect** | `job.run.timeout` is not a supported webhook event type. |
> | **C) ❌ Incorrect** | `job.run.queued` is not a supported webhook event type. There is no webhook for when a job enters the queue. |
> | **D) ✅ Correct** | `job.run.started` fires when a job run begins execution. It's one of the three supported webhook event types. |
> | **E) ❌ Incorrect** | `job.run.cancelled` is not a supported webhook event type. |
>
> > 💡 **Key rule**: Three webhook events only: `job.run.started`, `job.run.completed`, `job.run.errored`.

---

### Q4.
> **Subdomain 6.4 — Webhook response requirements**

A team implements a webhook handler in AWS Lambda that processes dbt Cloud job events. The Lambda function takes an average of 25 seconds to complete processing. What is the risk?

- A) The Lambda takes longer than the 10-second timeout, so dbt records the delivery as failed even if the function eventually succeeds.
- B) Responses over 15 seconds are retried automatically by dbt Cloud with exponential backoff.
- C) No risk — dbt Cloud webhooks have no response time requirements.
- D) The webhook will deliver successfully but the payload will be truncated after 10 seconds.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | A webhook in dbt has a timeout of **10 seconds**. A slow endpoint can record success on its own side while dbt records a failure. Fix: respond right away, then process the event asynchronously (for example, queue it). |
> | **B) ❌ Incorrect** | dbt retries each event five times, but the timeout is 10 seconds, not 15. Backoff isn't documented. |
> | **C) ❌ Incorrect** | dbt Cloud has a strict 10-second response window for webhook handlers. |
> | **D) ❌ Incorrect** | The payload is not truncated — the connection times out and dbt marks it as a delivery failure. |
>
> > 💡 **Key rule**: Webhook timeout = **10 seconds**. A slow handler counts as a failed delivery. Respond fast, process async.

---

### Q5.
> **Subdomain 6.5 — Webhook delivery history**

A security audit requires reviewing all webhook deliveries for a specific webhook over the past 45 days. Is this possible in dbt Cloud?

- A) No — webhook delivery history is not stored; only the webhook configuration is retained.
- B) Yes — 60 days of delivery history is available in Account Settings → Webhooks.
- C) Yes — dbt Cloud stores complete webhook delivery history indefinitely.
- D) No — dbt keeps a log of each webhook delivery for only 7 days.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Delivery history is stored — but only for 7 days. |
> | **B) ❌ Incorrect** | The retention window is 7 days, not 60. |
> | **C) ❌ Incorrect** | Webhook history is retained for a fixed window, not indefinitely. |
> | **D) ✅ Correct** | dbt keeps a log of each webhook delivery for **7 days** (the Recent Deliveries section). A 45-day audit can't be served from dbt. Persist the payloads in your handler if you need longer. |
>
> > 💡 **Key rule**: Webhook delivery history = **7 days**. For longer retention, persist payloads in your handler.

---

---

### Q6.
> **Subdomain 6.6 — Email notifications**

A small team on the Starter plan wants to receive alerts when their nightly dbt production job fails. They do not want to build a webhook handler. What is the simplest solution, and are there any plan restrictions?

- A) Email notifications require Enterprise plan — Starter teams must use webhooks.
- B) Email notifications are only available for CI jobs — deploy jobs require webhooks.
- C) Email notifications are set up under your profile's Notification settings. You choose the events (succeeds, warns, fails, is canceled). No webhook handler needed.
- D) Email notifications require a verified custom domain on the account.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs don't tie email notifications to the Enterprise plan. |
> | **B) ❌ Incorrect** | Job notifications aren't limited to CI jobs. |
> | **C) ✅ Correct** | Email is the simplest option. Developers set up their own email notifications under Notification settings, and pick the events: succeeds, warns, fails, is canceled. |
> | **D) ❌ Incorrect** | Custom domain verification is not required for email notifications — they use dbt Cloud's email service. |
>
> > 💡 **Key rule**: Email = profile → Notification settings. Events: succeeds, warns, fails, is canceled. No webhook needed.

---

### Q7.
> **Subdomain 6.7 — job.run.started event**

A team builds a webhook handler to pre-provision compute resources before a dbt job begins. They want the handler to fire as early as possible in the job lifecycle. Which webhook event should they subscribe to?

- A) `job.run.completed` — fired when the job finishes, allowing post-run provisioning.
- B) There is no webhook event for job start — only completion and error events exist.
- C) `job.run.started` — fired when the job begins execution, before any models run.
- D) `job.run.errored` — fired if the job encounters errors.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `job.run.completed` fires after the job finishes — too late for pre-provisioning compute before the run. |
> | **B) ❌ Incorrect** | dbt Cloud has three webhook event types including `job.run.started`. |
> | **C) ✅ Correct** | `job.run.started` fires at the **beginning of job execution**, before any models run. This is the correct event for tasks that must happen before the run begins, such as resuming a suspended warehouse, pre-warming a cache, or provisioning compute resources. |
> | **D) ❌ Incorrect** | `job.run.errored` fires only when there is an error — it is not reliable for pre-run provisioning. |
>
> > 💡 **Key rule**: `job.run.started` = fires at job start (before any models). Use for pre-run provisioning tasks.

---

### Q8.
> **Subdomain 6.8 — job.run.completed timing**

A team's webhook handler subscribes to `job.run.errored` and tries to immediately fetch the dbt Cloud run artifacts (manifest, catalog) via the API to send a diagnostic report. The API calls return empty or 404. A colleague suggests switching to `job.run.completed` instead. Why would this help?

- A) The artifacts endpoint requires an OAuth token, which is only generated after `job.run.completed`.
- B) `job.run.errored` fires **before** artifact ingestion into the API. `job.run.completed` fires **after** artifacts have been ingested, so the API will have the run data available.
- C) `job.run.errored` only includes partial run data — `job.run.completed` is always required to access full artifacts.
- D) `job.run.completed` fires faster than `job.run.errored`, so the API has more time to populate.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | OAuth token generation is not tied to webhook event type. API authentication is independent of which event fired. |
> | **B) ✅ Correct** | **`job.run.errored`** fires **immediately** when the job encounters an error — before dbt Cloud has finished ingesting run artifacts into the API. **`job.run.completed`** fires after **both** job completion AND artifact ingestion. If your handler needs to query the API for run artifacts (manifest, catalog, sources, run results), use `job.run.completed` to guarantee the data is available. The trade-off: `completed` is slightly delayed compared to `errored`. |
> | **C) ❌ Incorrect** | Both events can eventually lead to full artifact access — the difference is timing, not data completeness. |
> | **D) ❌ Incorrect** | `job.run.errored` actually fires faster than `job.run.completed` — it fires immediately on error. Speed is not the differentiator; artifact availability is. |
>
> > 💡 **Key rule**: `job.run.errored` = fast, but artifacts not yet in API. `job.run.completed` = delayed, but artifacts are ready. Use `completed` when you need artifacts.

---

### Q9.
> **Subdomain 6.9 — Three webhook event types**

A team is designing their dbt Cloud monitoring stack. Which of the following correctly describes all three webhook event types and their primary use case?

- A) `job.run.started` (pre-run prep), `job.run.completed` (post-run with artifacts available), `job.run.errored` (immediate error alert — no artifact guarantee)
- B) `job.run.started` (fires at completion), `job.run.completed` (fires mid-run), `job.run.errored` (fires at start)
- C) `job.run.queued`, `job.run.completed`, `job.run.errored`
- D) `job.run.started`, `job.run.paused`, `job.run.completed`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The three dbt Cloud webhook event types are: **`job.run.started`** — fires when a job begins (before any models run; use for pre-run provisioning); **`job.run.completed`** — fires after completion AND artifact ingestion (safe to query API for artifacts); **`job.run.errored`** — fires immediately on error (fastest for alerting, but API artifacts may not yet be available). |
> | **B) ❌ Incorrect** | The timings described are all wrong — this inverts the actual behavior of each event. |
> | **C) ❌ Incorrect** | `job.run.queued` is not a documented dbt Cloud webhook event type. The three events are `started`, `completed`, and `errored`. |
> | **D) ❌ Incorrect** | `job.run.paused` is not a documented dbt Cloud webhook event type. |
>
> > 💡 **Key rule**: Three events = `started` (pre-run), `completed` (post-run + artifacts ready), `errored` (fast alert, no artifact guarantee).

---

### Q10.
> **Subdomain 6.10 — Webhook signature validation**

A security engineer asks how to verify that incoming webhook payloads are genuinely from dbt Cloud and not spoofed by a third party. What mechanism does dbt Cloud use?

- A) Webhook payloads include an API key in the URL query string that matches the dbt Cloud account's API key.
- B) Webhook payloads are encrypted using the account's public key — only the account's private key can decrypt them.
- C) dbt Cloud uses mutual TLS — the receiving endpoint must present a valid certificate from dbt Labs' CA.
- D) dbt Cloud signs payloads using **SHA256 HMAC** and includes the signature in the **Authorization header** — recipients should compute the expected signature and compare.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | API keys in query strings are not the dbt Cloud webhook security model and would be visible in logs. |
> | **B) ❌ Incorrect** | dbt Cloud does not use asymmetric encryption for webhook payloads. |
> | **C) ❌ Incorrect** | dbt Cloud does not use mutual TLS for webhook delivery. Standard HTTPS is used for the transport, with HMAC for payload integrity. |
> | **D) ✅ Correct** | The `Authorization` header holds a SHA256 hash (HMAC) of the request body, with your webhook's secret token as the key. Compute the same hash on your server and compare. The docs strongly recommend this check to catch spoofed requests. |
>
> > 💡 **Key rule**: Webhook security = **SHA256 HMAC signature** in Authorization header. Verify by computing expected HMAC and comparing.

---

### Q11.
> **Subdomain 6.11 — Reactivating a webhook**

A webhook was archived after repeated failures and the endpoint is now fixed. How do you reactivate it in the UI?

- A) Contact dbt support.
- B) Wait. dbt retries archived webhooks every hour.
- C) Update the webhook's endpoint URL. dbt reactivates it automatically when the URL changes.
- D) Delete it and recreate it with the same secret.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | It's self-service. |
> | **B) ❌ Incorrect** | Not documented. Archived webhooks aren't retried on a timer. |
> | **C) ✅ Correct** | The docs say dbt automatically reactivates the webhook when the URL changes. Through the API, use `PUT` with `active` set to `true`, or update `client_url`. |
> | **D) ❌ Incorrect** | Not needed. |
>
> > 💡 **Key rule**: Reactivate = change the endpoint URL (UI) or `PUT` with `active: true` (API).

---

### Q12.
> **Subdomain 6.12 — Webhook response window**

A team builds a webhook handler that performs heavy data processing synchronously — querying multiple APIs and writing to a database — before returning a response. The average processing time is 12 seconds. What is the risk?

- A) The delivery is recorded as a failure — dbt's webhook timeout is **10 seconds**.
- B) No risk — dbt Cloud waits up to 60 seconds for a response.
- C) The webhook will succeed but dbt Cloud will throttle future deliveries for that endpoint.
- D) A 12-second response is within the acceptable range — the timeout is 30 seconds.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The docs say a webhook in dbt has a timeout of **10 seconds**. A slow endpoint can record success on its side while dbt records a failure. Fix: respond immediately, then process asynchronously. |
> | **B) ❌ Incorrect** | The timeout is 10 seconds, not 60 seconds. |
> | **C) ❌ Incorrect** | Not documented. The consequence is a failed delivery. |
> | **D) ❌ Incorrect** | The timeout is 10 seconds, not 30. |
>
> > 💡 **Key rule**: Webhook timeout = **10 seconds**. Respond immediately and process asynchronously.

---

### Q13.
> **Subdomain 6.13 — Job auto-deactivation**

An engineer notices that a scheduled dbt job has stopped enqueuing runs automatically, even though the schedule is still configured. Investigation shows the job has failed on every run for the past 3 months. What feature likely caused this?

- A) The job's cron schedule expired — cron jobs must be renewed after 90 days.
- B) The run slot quota was exhausted — no new jobs can be scheduled until existing queued runs complete.
- C) The job reached the **100 consecutive failure** threshold and was auto-deactivated — it stopped auto-enqueueing new runs.
- D) dbt Cloud automatically pauses jobs that exceed their configured run timeout.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | cron jobs do not expire on a 90-day cycle in dbt Cloud. |
> | **B) ❌ Incorrect** | Run slot exhaustion would delay queuing, not permanently stop auto-enqueueing. |
> | **C) ✅ Correct** | dbt deactivates a deploy job or a CI job after **100 consecutive failing runs**, so it's no longer enqueued from schedules or triggers. Reactivate it by editing and saving the job, or with **Run now**. |
> | **D) ❌ Incorrect** | Run timeout causes individual runs to cancel, not the job to be deactivated. |
>
> > 💡 **Key rule**: Auto-deactivation = a deploy or CI job stops being enqueued after **100 consecutive failures**. Edit and save it, or **Run now**, to reactivate.

---

### Q14.
> **Subdomain 6.14 — Job notification events**

Which events can you choose for job notifications?

- A) Starts, queued, times out.
- B) Succeeds and fails only.
- C) Success, error, skipped.
- D) Succeeds, warns, fails, is canceled.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not job notification events. |
> | **B) ❌ Incorrect** | There are two more: warns and is canceled. |
> | **C) ❌ Incorrect** | Not the documented event names. |
> | **D) ✅ Correct** | Warns comes from warning-level lines in data tests or source freshness, so a run that shows Success can still send a Warns notification. |
>
> > 💡 **Key rule**: Job notification events = succeeds, warns, fails, is canceled. Channels: email, Slack (public channels only), Teams.

---

### Q15.
> **Subdomain 6.15 — Memory limit per run pod**

A team uses a dbt macro to load a large reference dataset into a Jinja variable during compilation. The macro reads the dataset using `run_query()` and stores it in a variable for downstream use across hundreds of models. Jobs start failing with out-of-memory errors. What is the cause and what is the limit?

- A) The `run_query()` function is limited to 10,000 rows — the macro is truncating data.
- B) dbt Cloud imposes a **600 MiB memory limit** per run pod on all plans. Loading large datasets into Jinja variables via macros exhausts this limit.
- C) The default thread count (4) causes memory contention — reduce threads to 1.
- D) The memory limit is 2 GiB on Enterprise+ and 512 MiB on other plans.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Not a documented limit. |
> | **B) ✅ Correct** | All dbt accounts have a pod memory of **600 MiB**, applied per run. It's set at the account level and can't be customized per job. A run that exceeds it is terminated with a "memory limit error". Keep large lookups in the warehouse. |
> | **C) ❌ Incorrect** | Thread count affects warehouse concurrency, not the dbt run pod memory. |
> | **D) ❌ Incorrect** | The memory limit is **600 MiB on all plans** — it does not vary by plan tier. |
>
> > 💡 **Key rule**: dbt Cloud run pod memory limit = **600 MiB, all plans, not configurable**. Loading large datasets into macros causes OOM failures.

---

### Q16.
> **Subdomain 6.16 — Thread count**

A team increases the thread count on their dbt Cloud job from the default of 4 to 32, hoping to significantly speed up their 500-model deployment job. What is the likely outcome?

- A) Thread count above 16 is blocked by dbt Cloud and will revert to 16 automatically.
- B) The job runs approximately 8× faster — thread count scales linearly with throughput.
- C) The job runs faster, but the cost increases proportionally to the thread count.
- D) Run time can drop, but only as far as the dependency graph and the warehouse's concurrent-query limit allow, and the extra load can queue other tools' queries.

> [!success]- Answer & Explanations
> **✅ Correct: D**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The docs state no maximum on threads. |
> | **B) ❌ Incorrect** | Not linear. The dependency graph limits how many models can run at once, and the warehouse's concurrent-query limit can make models queue. |
> | **C) ❌ Incorrect** | The docs say more threads increase the load on your warehouse. They don't say cost scales with threads. |
> | **D) ✅ Correct** | The default thread count is **4**. More threads usually cut run time, but they add load on the warehouse and may queue other tools' queries. The graph and the warehouse's concurrent-query limit cap the benefit. The docs advise testing different values. |
>
> > 💡 **Key rule**: Default threads = **4**. More threads usually shorten runs but add warehouse load. Limited by the DAG and warehouse concurrency. Test different values.

---

### Q17.
> **Subdomain 6.17 — Interval scheduling**

A job uses the Intervals schedule type, every 2 hours. How does dbt time the runs?

- A) At fixed hours in the account's local time zone.
- B) Every 2 hours counted from midnight UTC, with the same gap each time (a run at 00:04 is followed by one at 02:04).
- C) 2 hours after the previous run finishes.
- D) At clock hours in each user's time zone.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt uses UTC for all jobs. It doesn't convert to local time or adjust for daylight saving. |
> | **B) ✅ Correct** | The docs say Intervals run every N hours starting from midnight UTC, and the gap between runs stays constant. |
> | **C) ❌ Incorrect** | The docs describe a constant gap between runs, not a gap from when the previous run finishes. |
> | **D) ❌ Incorrect** | All scheduling is UTC. |
>
> > 💡 **Key rule**: Intervals = every N hours from midnight UTC, constant gap. Specific hours = whole UTC hours. Cron = exact times. All UTC.

---

### Q18.
> **Subdomain 6.18 — Job duration exceeds schedule frequency**

A job is scheduled to run "every 30 minutes" but each run takes 45 minutes to complete. What does dbt Cloud do?

- A) The scheduler cancels any queued runs and keeps only the newest — preventing queue buildup. The effective run frequency becomes approximately 45 minutes.
- B) The job is automatically suspended after the second overlap and must be manually re-enabled.
- C) dbt Cloud runs both the current job and the next scheduled run concurrently, using two run slots.
- D) The next scheduled run waits in the queue and starts immediately after the current run finishes, creating a permanent backlog.

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | When a job's runtime exceeds its scheduling frequency, dbt Cloud's scheduler **cancels queued runs and keeps only the newest**. This prevents queue buildup — instead of accumulating a growing backlog of delayed runs, only the most recent scheduled invocation stays in queue. The effective execution frequency naturally becomes the actual job duration (approx. 45 minutes in this case). This is protective behavior, not an error state. |
> | **B) ❌ Incorrect** | Jobs are not suspended due to schedule/duration overlap. |
> | **C) ❌ Incorrect** | Even if run slots were available, the scheduler's behavior is to prevent backlog, not to run concurrently. |
> | **D) ❌ Incorrect** | The queue backlog scenario is specifically what dbt Cloud's scheduler prevents by cancelling stale queued runs. |
>
> > 💡 **Key rule**: Job duration > schedule interval → scheduler cancels queued runs, keeps newest. Effective frequency = actual run duration.

---

### Q19.
> **Subdomain 6.19 — Email vs webhook notifications**

A data team is deciding between email notifications and webhooks for their job failure monitoring. Which statement correctly describes when each is the better choice?

- A) Email notifications support richer content (with model-level failure details) while webhooks only provide a pass/fail signal.
- B) Webhooks are only available on Enterprise plan — Starter teams must use email.
- C) Email is simpler for basic per-job alerting with no infrastructure required. Webhooks are better when you need programmatic handling — triggering Slack bots, PagerDuty, incident management, or custom automation.
- D) Webhooks are always better — email notifications are only for legacy setups.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Webhooks actually include richer payload data (run ID, job details, timestamps). Email notifications are simpler in content, not richer. |
> | **B) ❌ Incorrect** | Webhooks work on Starter or Enterprise-tier plans, not only Enterprise. |
> | **C) ✅ Correct** | **Email notifications**: no plan restriction, no infrastructure, simple success/failure alerts per job — ideal for small teams or low-complexity monitoring. **Webhooks**: require an endpoint and handler, but enable programmatic responses — integrating with Slack, PagerDuty, incident management, or custom dashboards. Use email when you just need a notification; use webhooks when you need to act on the event or route it to another system. |
> | **D) ❌ Incorrect** | Email notifications are a fully supported feature with a clear use case — they are not deprecated. |
>
> > 💡 **Key rule**: Email = simple, no infra, per-job alerts. Webhook = programmatic, integrate with Slack/PagerDuty/automation.

---

### Q20.
> **Subdomain 6.20 — Webhook permissions**

Which users can create webhooks on an Enterprise-tier plan?

- A) Only Account Admins.
- B) Anyone with a Read-Only license.
- C) Users, or service tokens, with the Account Admin, Admin or Developer permission set.
- D) Security Admins.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Admin and Developer permission sets work too. |
> | **B) ❌ Incorrect** | Read-Only users don't have write access. |
> | **C) ✅ Correct** | The docs say you, or the API service token, must have the Account Admin, Admin or Developer permission set for write access. On Starter, the UI needs a Developer license. |
> | **D) ❌ Incorrect** | Security Admin isn't one of the permission sets listed. |
>
> > 💡 **Key rule**: Create webhooks: Enterprise-tier = Account Admin, Admin or Developer permission set. Starter = Developer license. Plan: Starter or Enterprise-tier.

---

*[End of Topic 6 — 20 questions]*

