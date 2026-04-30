# Topic 6: Monitoring & Alerting — Practice Questions

> Open in **reading mode** (`Cmd+E`). Click an answer callout to reveal.
> 20 questions | Architect-level | ⭐ = High-Yield

---

### Q1. ⭐
> **Subdomain 6.1 — Webhook silent auto-disable**

A team configures a webhook to send job failure alerts to a Slack channel. Three weeks later, they realize the Slack channel has been silent even though production jobs have been failing. Investigation reveals the webhook endpoint was briefly unreachable for a few days earlier in the month. What happened to the webhook?

- A) The webhook paused delivery temporarily and resumed automatically once the endpoint was reachable again.
- B) After 5 consecutive delivery failures, the webhook silently auto-disabled — no alert was sent when it disabled.
- C) After 3 delivery failures, dbt Cloud sent an email to the account admin before disabling the webhook.
- D) Webhooks have a 30-minute retry window — if delivery fails within that window, the event is dropped but the webhook stays active.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Webhooks do not auto-resume — once disabled by 5 consecutive failures, they remain disabled until manually re-enabled. |
> | **B) ✅ Correct** | After **5 consecutive delivery failures**, dbt Cloud **silently auto-disables** the webhook — no notification is sent to alert the team. This is a critical monitoring gap: if a webhook endpoint goes down even briefly, alerts can stop permanently without any warning. Proactively monitor webhook health status in dbt Cloud or via external uptime checks. |
> | **C) ❌ Incorrect** | There is no email notification when a webhook is auto-disabled. The disable is entirely silent. |
> | **D) ❌ Incorrect** | The retry/failure tracking is based on consecutive failures across events, not a 30-minute window. |
>
> > 💡 **Key rule**: **5 consecutive failures = silent webhook auto-disable**. Monitor webhook status proactively.

---

### Q2. ⭐
> **Subdomain 6.2 — Webhook event timing and artifacts**

A team's webhook handler listens for `job.run.errored` events and immediately queries the dbt Cloud API for the run's artifacts (manifest, catalog, sources) to post a diagnostic report to their incident channel. The handler fails to retrieve any artifacts. Why?

- A) `job.run.errored` events don't include the run ID needed to query artifacts.
- B) Artifacts are only stored for successful runs — errored runs have no artifacts.
- C) `job.run.errored` fires **before** artifact ingestion — artifacts are not yet available at handler time. Use `job.run.completed` instead.
- D) The webhook needs the `artifact_read` scope on its service token to access artifacts.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `job.run.errored` events include the run ID and other run metadata. |
> | **B) ❌ Incorrect** | Artifacts can be generated for errored runs (partial artifacts) — the issue is timing, not existence. |
> | **C) ✅ Correct** | `job.run.errored` fires **immediately** when an error is detected — before dbt Cloud has finished ingesting artifacts. `job.run.completed` fires **after** artifact ingestion is complete, making it the correct event for any handler that needs to query the API for run artifacts. Use `errored` only when you need the fastest possible notification and don't need artifacts. |
> | **D) ❌ Incorrect** | Artifact access is controlled by service token permission sets, not a specific `artifact_read` scope. |
>
> > 💡 **Key rule**: `errored` = fires before artifacts (fast notification). `completed` = fires after artifacts (use when you need API data).

---

### Q3.
> **Subdomain 6.3 — Webhook event types**

Which of the following are valid dbt Cloud webhook event types? **Select TWO correct answers.**

- A) `job.run.started`
- B) `job.run.queued`
- C) `job.run.completed`
- D) `job.run.cancelled`
- E) `job.run.timeout`

> [!success]- Answer & Explanations
> **✅ Correct: A, C**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | `job.run.started` fires when a job run begins execution. It's one of the three supported webhook event types. |
> | **B) ❌ Incorrect** | `job.run.queued` is not a supported webhook event type. There is no webhook for when a job enters the queue. |
> | **C) ✅ Correct** | `job.run.completed` fires after the run finishes (success or partial) AND after artifact ingestion. One of the three supported event types. |
> | **D) ❌ Incorrect** | `job.run.cancelled` is not a supported webhook event type. |
> | **E) ❌ Incorrect** | `job.run.timeout` is not a supported webhook event type. |
>
> > 💡 **Key rule**: Three webhook events only: `job.run.started`, `job.run.completed`, `job.run.errored`.

---

### Q4.
> **Subdomain 6.4 — Webhook response requirements**

A team implements a webhook handler in AWS Lambda that processes dbt Cloud job events. The Lambda function takes an average of 25 seconds to complete processing. What is the risk?

- A) No risk — dbt Cloud webhooks have no response time requirements.
- B) The Lambda response time exceeds the 10-second window — dbt Cloud treats the delivery as failed, incrementing the failure counter toward the 5-failure auto-disable threshold.
- C) The webhook will deliver successfully but the payload will be truncated after 10 seconds.
- D) Responses over 15 seconds are retried automatically by dbt Cloud with exponential backoff.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud has a strict 10-second response window for webhook handlers. |
> | **B) ✅ Correct** | Webhook handlers must return a **2xx HTTP status within 10 seconds**. If the handler takes 25 seconds to respond, dbt Cloud marks the delivery as a **failure** — incrementing toward the 5-failure silent auto-disable threshold. Fix: respond immediately with `200 OK`, then process the event asynchronously (e.g., push to SQS, return 200, Lambda processes separately). |
> | **C) ❌ Incorrect** | The payload is not truncated — the connection times out and dbt marks it as a delivery failure. |
> | **D) ❌ Incorrect** | dbt Cloud does retry failed deliveries, but the 10-second timeout is the trigger for failure, not a 15-second threshold. And exponential backoff is not the documented retry mechanism. |
>
> > 💡 **Key rule**: Webhook handler must return **2xx within 10 seconds**. Slow handlers = delivery failure = risk of auto-disable.

---

### Q5.
> **Subdomain 6.5 — Webhook delivery history**

A security audit requires reviewing all webhook deliveries for a specific webhook over the past 45 days. Is this possible in dbt Cloud?

- A) Yes — dbt Cloud stores complete webhook delivery history indefinitely.
- B) No — dbt Cloud stores only the last 30 days of webhook delivery history. Events older than 30 days are not accessible.
- C) Yes — 60 days of delivery history is available in Account Settings → Webhooks.
- D) No — webhook delivery history is not stored; only the webhook configuration is retained.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Webhook history is retained for a fixed window, not indefinitely. |
> | **B) ✅ Correct** | dbt Cloud retains **30 days** of delivery history per webhook. The 45-day audit request cannot be fulfilled from dbt Cloud — events older than 30 days are no longer accessible. For longer retention, webhook payloads should be persisted to an external store (e.g., S3, database) in the handler. |
> | **C) ❌ Incorrect** | The retention window is 30 days, not 60 days. |
> | **D) ❌ Incorrect** | Delivery history is stored — but only for 30 days. |
>
> > 💡 **Key rule**: Webhook delivery history = **30 days only**. For longer retention, persist payloads in your handler.

---

---

### Q6.
> **Subdomain 6.6 — Email notifications**

A small team on the Starter plan wants to receive alerts when their nightly dbt production job fails. They do not want to build a webhook handler. What is the simplest solution, and are there any plan restrictions?

- A) Email notifications require Enterprise plan — Starter teams must use webhooks.
- B) Email notifications can be configured per job on any plan (including Starter) — no plan restriction applies. They can trigger on success, failure, or both.
- C) Email notifications are only available for CI jobs — deploy jobs require webhooks.
- D) Email notifications require a verified custom domain on the account.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Email notifications have no plan restriction — they are available on all plans including Starter and Developer. |
> | **B) ✅ Correct** | **Email notifications** are the simplest alerting option in dbt Cloud. They are configured per job and have **no plan restrictions**. They can be set to trigger on success, failure, or both. For teams that don't need programmatic handling, email notifications are the recommended starting point before investing in webhook infrastructure. |
> | **C) ❌ Incorrect** | Email notifications work for both CI jobs and deploy jobs. |
> | **D) ❌ Incorrect** | Custom domain verification is not required for email notifications — they use dbt Cloud's email service. |
>
> > 💡 **Key rule**: Email notifications = no plan restriction, per-job config, success/failure/both. Simplest alerting option — no webhook required.

---

### Q7.
> **Subdomain 6.7 — job.run.started event**

A team builds a webhook handler to pre-provision compute resources before a dbt job begins. They want the handler to fire as early as possible in the job lifecycle. Which webhook event should they subscribe to?

- A) `job.run.completed` — fired when the job finishes, allowing post-run provisioning.
- B) `job.run.errored` — fired if the job encounters errors.
- C) `job.run.started` — fired when the job begins execution, before any models run.
- D) There is no webhook event for job start — only completion and error events exist.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `job.run.completed` fires after the job finishes — too late for pre-provisioning compute before the run. |
> | **B) ❌ Incorrect** | `job.run.errored` fires only when there is an error — it is not reliable for pre-run provisioning. |
> | **C) ✅ Correct** | `job.run.started` fires at the **beginning of job execution**, before any models run. This is the correct event for tasks that must happen before the run begins, such as resuming a suspended warehouse, pre-warming a cache, or provisioning compute resources. |
> | **D) ❌ Incorrect** | dbt Cloud has three webhook event types including `job.run.started`. |
>
> > 💡 **Key rule**: `job.run.started` = fires at job start (before any models). Use for pre-run provisioning tasks.

---

### Q8.
> **Subdomain 6.8 — job.run.completed timing**

A team's webhook handler subscribes to `job.run.errored` and tries to immediately fetch the dbt Cloud run artifacts (manifest, catalog) via the API to send a diagnostic report. The API calls return empty or 404. A colleague suggests switching to `job.run.completed` instead. Why would this help?

- A) `job.run.completed` fires faster than `job.run.errored`, so the API has more time to populate.
- B) `job.run.errored` fires **before** artifact ingestion into the API. `job.run.completed` fires **after** artifacts have been ingested, so the API will have the run data available.
- C) The artifacts endpoint requires an OAuth token, which is only generated after `job.run.completed`.
- D) `job.run.errored` only includes partial run data — `job.run.completed` is always required to access full artifacts.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | `job.run.errored` actually fires faster than `job.run.completed` — it fires immediately on error. Speed is not the differentiator; artifact availability is. |
> | **B) ✅ Correct** | **`job.run.errored`** fires **immediately** when the job encounters an error — before dbt Cloud has finished ingesting run artifacts into the API. **`job.run.completed`** fires after **both** job completion AND artifact ingestion. If your handler needs to query the API for run artifacts (manifest, catalog, sources, run results), use `job.run.completed` to guarantee the data is available. The trade-off: `completed` is slightly delayed compared to `errored`. |
> | **C) ❌ Incorrect** | OAuth token generation is not tied to webhook event type. API authentication is independent of which event fired. |
> | **D) ❌ Incorrect** | Both events can eventually lead to full artifact access — the difference is timing, not data completeness. |
>
> > 💡 **Key rule**: `job.run.errored` = fast, but artifacts not yet in API. `job.run.completed` = delayed, but artifacts are ready. Use `completed` when you need artifacts.

---

### Q9.
> **Subdomain 6.9 — Three webhook event types**

A team is designing their dbt Cloud monitoring stack. Which of the following correctly describes all three webhook event types and their primary use case?

- A) `job.run.started` (pre-run prep), `job.run.completed` (post-run with artifacts available), `job.run.errored` (immediate error alert — no artifact guarantee)
- B) `job.run.started` (fires at completion), `job.run.completed` (fires mid-run), `job.run.errored` (fires at start)
- C) `job.run.started`, `job.run.paused`, `job.run.completed`
- D) `job.run.queued`, `job.run.completed`, `job.run.errored`

> [!success]- Answer & Explanations
> **✅ Correct: A**
>
> | | |
> |---|---|
> | **A) ✅ Correct** | The three dbt Cloud webhook event types are: **`job.run.started`** — fires when a job begins (before any models run; use for pre-run provisioning); **`job.run.completed`** — fires after completion AND artifact ingestion (safe to query API for artifacts); **`job.run.errored`** — fires immediately on error (fastest for alerting, but API artifacts may not yet be available). |
> | **B) ❌ Incorrect** | The timings described are all wrong — this inverts the actual behavior of each event. |
> | **C) ❌ Incorrect** | `job.run.paused` is not a documented dbt Cloud webhook event type. |
> | **D) ❌ Incorrect** | `job.run.queued` is not a documented dbt Cloud webhook event type. The three events are `started`, `completed`, and `errored`. |
>
> > 💡 **Key rule**: Three events = `started` (pre-run), `completed` (post-run + artifacts ready), `errored` (fast alert, no artifact guarantee).

---

### Q10.
> **Subdomain 6.10 — Webhook signature validation**

A security engineer asks how to verify that incoming webhook payloads are genuinely from dbt Cloud and not spoofed by a third party. What mechanism does dbt Cloud use?

- A) Webhook payloads include an API key in the URL query string that matches the dbt Cloud account's API key.
- B) dbt Cloud signs payloads using **SHA256 HMAC** and includes the signature in the **Authorization header** — recipients should compute the expected signature and compare.
- C) dbt Cloud uses mutual TLS — the receiving endpoint must present a valid certificate from dbt Labs' CA.
- D) Webhook payloads are encrypted using the account's public key — only the account's private key can decrypt them.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | API keys in query strings are not the dbt Cloud webhook security model and would be visible in logs. |
> | **B) ✅ Correct** | dbt Cloud webhook payloads are signed using **SHA256 HMAC** with a shared secret. The signature is included in the **Authorization header** of each webhook delivery. Recipients should compute their own HMAC SHA256 signature using the shared secret and compare it to the header value. A mismatch indicates a spoofed or tampered payload. This is the same pattern used by GitHub, Stripe, and other services for webhook security. |
> | **C) ❌ Incorrect** | dbt Cloud does not use mutual TLS for webhook delivery. Standard HTTPS is used for the transport, with HMAC for payload integrity. |
> | **D) ❌ Incorrect** | dbt Cloud does not use asymmetric encryption for webhook payloads. |
>
> > 💡 **Key rule**: Webhook security = **SHA256 HMAC signature** in Authorization header. Verify by computing expected HMAC and comparing.

---

### Q11.
> **Subdomain 6.11 — Re-enabling a disabled webhook**

A team discovers their webhook was silently disabled after consecutive delivery failures. After fixing the endpoint, how do they re-enable the webhook?

- A) The webhook auto-re-enables after the endpoint returns a successful 2xx response to dbt Cloud's health check.
- B) The webhook must be deleted and recreated with the same URL and secret.
- C) The webhook must be manually re-enabled in the dbt Cloud UI — it does not auto-recover.
- D) Contact dbt Cloud support to re-enable webhooks that have been auto-disabled.

> [!success]- Answer & Explanations
> **✅ Correct: C**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | There is no documented health check mechanism that auto-re-enables disabled webhooks. |
> | **B) ❌ Incorrect** | Deleting and recreating is not required — the webhook can be re-enabled directly. |
> | **C) ✅ Correct** | After a webhook is auto-disabled due to 5 consecutive delivery failures, it must be **manually re-enabled** in the dbt Cloud UI. It does not auto-recover. This is why proactive monitoring of webhook status is critical — the disable is silent, and re-enabling requires a human action. Navigate to Account Settings → Webhooks, find the disabled webhook, and toggle it back on after fixing the endpoint. |
> | **D) ❌ Incorrect** | Re-enabling a disabled webhook is self-service in the dbt Cloud UI — support is not required. |
>
> > 💡 **Key rule**: Disabled webhook (after 5 failures) = **manual re-enable required** in dbt Cloud UI. No auto-recovery.

---

### Q12.
> **Subdomain 6.12 — Webhook response window**

A team builds a webhook handler that performs heavy data processing synchronously — querying multiple APIs and writing to a database — before returning a response. The average processing time is 12 seconds. What is the risk?

- A) No risk — dbt Cloud waits up to 60 seconds for a response.
- B) The webhook delivery will be counted as a failure — dbt Cloud requires a 2xx response within **10 seconds**. Exceeding this causes a timeout failure, which counts toward the 5-failure auto-disable threshold.
- C) The webhook will succeed but dbt Cloud will throttle future deliveries for that endpoint.
- D) A 12-second response is within the acceptable range — the timeout is 30 seconds.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | The timeout is 10 seconds, not 60 seconds. |
> | **B) ✅ Correct** | dbt Cloud requires a **2xx HTTP response within 10 seconds**. If the handler takes longer than 10 seconds, dbt Cloud treats the delivery as a timeout failure — even if the processing eventually succeeds. Each timeout counts toward the **5-failure auto-disable threshold**. The fix: respond with a 200 immediately, then process asynchronously (e.g., push to a queue or trigger a background job). |
> | **C) ❌ Incorrect** | dbt Cloud does not implement throttling per se — the consequence of slow responses is failure counting and eventual disable. |
> | **D) ❌ Incorrect** | The timeout is 10 seconds, not 30. |
>
> > 💡 **Key rule**: Webhook = must return 2xx within **10 seconds**. Respond immediately and process asynchronously.

---

### Q13.
> **Subdomain 6.13 — Job auto-deactivation**

An engineer notices that a scheduled dbt job has stopped enqueuing runs automatically, even though the schedule is still configured. Investigation shows the job has failed on every run for the past 3 months. What feature likely caused this?

- A) dbt Cloud automatically pauses jobs that exceed their configured run timeout.
- B) The job reached the **100 consecutive failure** threshold and was auto-deactivated by the job auto-deactivation Beta feature — it stopped auto-enqueueing new runs.
- C) The run slot quota was exhausted — no new jobs can be scheduled until existing queued runs complete.
- D) The job's cron schedule expired — cron jobs must be renewed after 90 days.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Run timeout causes individual runs to cancel, not the job to be deactivated. |
> | **B) ✅ Correct** | The **job auto-deactivation** feature (Beta) automatically stops a scheduled job from auto-enqueueing new runs after **100 consecutive failures**. This prevents a persistently broken job from consuming run slots indefinitely. The job itself is not deleted — it can be manually re-enabled and re-run. This is a housekeeping feature to prevent runaway broken jobs. |
> | **C) ❌ Incorrect** | Run slot exhaustion would delay queuing, not permanently stop auto-enqueueing. |
> | **D) ❌ Incorrect** | cron jobs do not expire on a 90-day cycle in dbt Cloud. |
>
> > 💡 **Key rule**: Job auto-deactivation Beta = scheduled job stops auto-enqueueing after **100 consecutive failures**. Job is not deleted — manually re-enable after fixing the root cause.

---

### Q14.
> **Subdomain 6.14 — Run slots**

An organization on the **Starter plan** has two production jobs: Job A (takes 45 minutes) and Job B (takes 20 minutes). Both are scheduled to start at 6:00 AM. What happens?

- A) Both jobs start simultaneously at 6:00 AM — Starter plan supports concurrent execution.
- B) Job A starts at 6:00 AM. Job B queues and starts only after Job A completes at approximately 6:45 AM — Starter plan has **1 run slot**.
- C) dbt Cloud cancels the lower-priority job (Job B) to ensure Job A completes without interference.
- D) Both jobs run in parallel but share the same compute resources, slowing both down.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Starter plan has only 1 run slot — concurrent execution is not possible for deploy jobs. |
> | **B) ✅ Correct** | **Developer and Starter plans have exactly 1 run slot**. Only one deploy job can run at a time. When two jobs are scheduled simultaneously, the second job queues and waits for the first to finish. With Job A taking 45 minutes, Job B would start around 6:45 AM instead of 6:00 AM. Note: CI jobs bypass the run slot system entirely. |
> | **C) ❌ Incorrect** | dbt Cloud queues jobs — it does not cancel lower-priority ones. |
> | **D) ❌ Incorrect** | dbt Cloud does not share compute between jobs — each job runs in its own isolated execution environment. |
>
> > 💡 **Key rule**: Developer/Starter = **1 run slot**. Second job queues until first completes. CI jobs bypass slots entirely.

---

### Q15.
> **Subdomain 6.15 — Memory limit per run pod**

A team uses a dbt macro to load a large reference dataset into a Jinja variable during compilation. The macro reads the dataset using `run_query()` and stores it in a variable for downstream use across hundreds of models. Jobs start failing with out-of-memory errors. What is the cause and what is the limit?

- A) The default thread count (4) causes memory contention — reduce threads to 1.
- B) dbt Cloud imposes a **600 MiB memory limit** per run pod on all plans. Loading large datasets into Jinja variables via macros exhausts this limit.
- C) The `run_query()` function is limited to 10,000 rows — the macro is truncating data.
- D) The memory limit is 2 GiB on Enterprise+ and 512 MiB on other plans.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Thread count affects warehouse concurrency, not the dbt run pod memory. |
> | **B) ✅ Correct** | dbt Cloud enforces a **600 MiB memory limit per run pod** on **all plans** — this is not configurable. Loading large datasets into Jinja variables (via `run_query()`) is the most common cause of OOM failures. The data must fit within the pod's memory budget. The fix: move large lookups to the warehouse layer rather than loading them into dbt compilation memory. |
> | **C) ❌ Incorrect** | `run_query()` is not row-limited — it returns all results, which is exactly what causes the memory issue. |
> | **D) ❌ Incorrect** | The memory limit is **600 MiB on all plans** — it does not vary by plan tier. |
>
> > 💡 **Key rule**: dbt Cloud run pod memory limit = **600 MiB, all plans, not configurable**. Loading large datasets into macros causes OOM failures.

---

### Q16.
> **Subdomain 6.16 — Thread count**

A team increases the thread count on their dbt Cloud job from the default of 4 to 32, hoping to significantly speed up their 500-model deployment job. What is the likely outcome?

- A) The job runs approximately 8× faster — thread count scales linearly with throughput.
- B) The job may actually slow down or cause errors — high thread counts cause warehouse connection contention and may exceed the warehouse's concurrent query limits.
- C) The job runs faster, but the cost increases proportionally to the thread count.
- D) Thread count above 16 is blocked by dbt Cloud and will revert to 16 automatically.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Thread count does not scale linearly. Warehouse concurrency limits, connection pooling, and query queue depth all constrain the practical benefit of high thread counts. |
> | **B) ✅ Correct** | The default thread count is **4**. Increasing it too aggressively causes **warehouse connection contention** — too many concurrent queries can overwhelm connection pools, cause queue buildup, or hit the warehouse's concurrent query limit. This can actually slow the job down or cause intermittent query failures. Increase thread count carefully and test the impact on job duration and warehouse performance. |
> | **C) ❌ Incorrect** | Cost is driven by warehouse compute (credits/DBU), not directly by dbt thread count. |
> | **D) ❌ Incorrect** | dbt Cloud does not automatically cap or revert the thread count setting. |
>
> > 💡 **Key rule**: Thread count default = **4**. Too high = warehouse contention and possible slowdown. Increase carefully and test.

---

### Q17.
> **Subdomain 6.17 — Interval scheduling drift**

A team schedules a job to run "every 1 hour" using dbt Cloud's interval scheduling. The first run starts at 9:07 AM due to a slight queue delay. At what time will the second run start, and why?

- A) 10:00 AM — interval scheduling is clock-aligned.
- B) 10:07 AM — interval scheduling counts elapsed time from the start of the previous run, not from a fixed clock time.
- C) 10:07 AM — interval scheduling counts elapsed time from the end of the previous run.
- D) 10:00 AM — dbt Cloud corrects for the initial queue delay automatically.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Interval scheduling is NOT clock-aligned. It drifts based on when the first run actually started. |
> | **B) ✅ Correct** | dbt Cloud's interval scheduling mode counts **elapsed time from the start of the previous run** — not from a fixed clock time. If the first run starts at 9:07 AM, the next run starts at **10:07 AM**, then 11:07 AM, and so on. The drift compounds over time. For precise clock-aligned schedules (e.g., exactly at 9:00 AM, 10:00 AM), use **cron syntax** instead of interval mode. |
> | **C) ❌ Incorrect** | The interval is measured from the start of the previous run, not from when it ends. |
> | **D) ❌ Incorrect** | dbt Cloud does not auto-correct for initial queue delays. |
>
> > 💡 **Key rule**: Interval scheduling = drifts (counts from run start, not clock). Use **cron syntax** for clock-aligned schedules.

---

### Q18.
> **Subdomain 6.18 — Job duration exceeds schedule frequency**

A job is scheduled to run "every 30 minutes" but each run takes 45 minutes to complete. What does dbt Cloud do?

- A) dbt Cloud runs both the current job and the next scheduled run concurrently, using two run slots.
- B) The scheduler cancels any queued runs and keeps only the newest — preventing queue buildup. The effective run frequency becomes approximately 45 minutes.
- C) The job is automatically suspended after the second overlap and must be manually re-enabled.
- D) The next scheduled run waits in the queue and starts immediately after the current run finishes, creating a permanent backlog.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Even if run slots were available, the scheduler's behavior is to prevent backlog, not to run concurrently. |
> | **B) ✅ Correct** | When a job's runtime exceeds its scheduling frequency, dbt Cloud's scheduler **cancels queued runs and keeps only the newest**. This prevents queue buildup — instead of accumulating a growing backlog of delayed runs, only the most recent scheduled invocation stays in queue. The effective execution frequency naturally becomes the actual job duration (approx. 45 minutes in this case). This is protective behavior, not an error state. |
> | **C) ❌ Incorrect** | Jobs are not suspended due to schedule/duration overlap. |
> | **D) ❌ Incorrect** | The queue backlog scenario is specifically what dbt Cloud's scheduler prevents by cancelling stale queued runs. |
>
> > 💡 **Key rule**: Job duration > schedule interval → scheduler cancels queued runs, keeps newest. Effective frequency = actual run duration.

---

### Q19.
> **Subdomain 6.19 — Email vs webhook notifications**

A data team is deciding between email notifications and webhooks for their job failure monitoring. Which statement correctly describes when each is the better choice?

- A) Webhooks are always better — email notifications are only for legacy setups.
- B) Email is simpler for basic per-job alerting with no infrastructure required. Webhooks are better when you need programmatic handling — triggering Slack bots, PagerDuty, incident management, or custom automation.
- C) Email notifications support richer content (with model-level failure details) while webhooks only provide a pass/fail signal.
- D) Webhooks are only available on Enterprise plan — Starter teams must use email.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | Email notifications are a fully supported feature with a clear use case — they are not deprecated. |
> | **B) ✅ Correct** | **Email notifications**: no plan restriction, no infrastructure, simple success/failure alerts per job — ideal for small teams or low-complexity monitoring. **Webhooks**: require an endpoint and handler, but enable programmatic responses — integrating with Slack, PagerDuty, incident management, or custom dashboards. Use email when you just need a notification; use webhooks when you need to act on the event or route it to another system. |
> | **C) ❌ Incorrect** | Webhooks actually include richer payload data (run ID, job details, timestamps). Email notifications are simpler in content, not richer. |
> | **D) ❌ Incorrect** | Webhooks are available on plans that support the feature — they are not exclusively Enterprise. Check current plan documentation for availability. |
>
> > 💡 **Key rule**: Email = simple, no infra, per-job alerts. Webhook = programmatic, integrate with Slack/PagerDuty/automation.

---

### Q20.
> **Subdomain 6.20 — Webhook retry and disable behavior**

A team's webhook endpoint is down for maintenance for 6 hours. During that time, dbt Cloud attempts to deliver webhook events for 5 job runs. All 5 deliveries fail (timeout). What happens after the 5th failure, and what must the team do to restore normal webhook operation?

- A) dbt Cloud queues the 5 failed deliveries and replays them once the endpoint is back online.
- B) After 5 consecutive failures, dbt Cloud **silently auto-disables** the webhook. The team must manually re-enable it in the dbt Cloud UI after restoring the endpoint.
- C) dbt Cloud sends an email alert to Account Admins warning that the webhook has been disabled.
- D) dbt Cloud retries each failed delivery up to 3 times with exponential backoff before marking it as failed.

> [!success]- Answer & Explanations
> **✅ Correct: B**
>
> | | |
> |---|---|
> | **A) ❌ Incorrect** | dbt Cloud does not queue and replay failed deliveries. Failed deliveries are lost. |
> | **B) ✅ Correct** | After **5 consecutive delivery failures**, the webhook is **silently auto-disabled** — no notification is sent. The team must **manually re-enable the webhook** in the dbt Cloud UI after their endpoint is restored. The 5 missed events are lost; there is no replay. The 30-day delivery history shows the failed attempts, but the data is not re-delivered. This is why proactive webhook monitoring is critical. |
> | **C) ❌ Incorrect** | No email alert is sent when a webhook is auto-disabled. The disable is silent — that is the critical gotcha. |
> | **D) ❌ Incorrect** | dbt Cloud does not implement exponential backoff retries for individual webhook deliveries. Each attempt either succeeds (2xx within 10 seconds) or fails. |
>
> > 💡 **Key rule**: 5 consecutive webhook failures = **silent auto-disable**. No notification sent. Must manually re-enable. Failed deliveries are not replayed.

---

*[End of Topic 6 — 20 questions]*

