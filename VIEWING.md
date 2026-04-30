# Viewing the Practice Exams

The 12 `practice_exam/q*.md` files were authored in [Obsidian](https://obsidian.md). Each question's answer is wrapped in a **collapsible callout** (`> [!success]- Answer & Explanations`) so you can read the question, think, then click to reveal the explanation. That self-test loop is the whole design.

This guide shows how those files render in different tools and what to do when collapsibility doesn't carry over.

## TL;DR

| Tool | Experience | Action |
|---|---|---|
| **Obsidian** | Full — collapsed-by-default callouts, click to reveal | Recommended. See setup below. |
| **GitHub web UI** | Workable but answers are visible inline (callouts degrade to plain blockquotes) | Fine for browsing. Clone locally for self-test. |
| **VS Code** | Good with the right extension | Install *Markdown Preview Enhanced*. |
| **Typora / Notion / Bear / iA Writer** | Answers visible inline | Either accept the trade-off, or convert to `<details>` (see below). |
| **Plain markdown / unsupported tool** | Answers visible inline | Run the conversion script below to swap callouts for HTML `<details>` tags. |

---

## Obsidian (recommended)

1. [Download Obsidian](https://obsidian.md) (free).
2. Click **Open folder as vault** and pick the cloned repo folder.
3. Open any `practice_exam/q*.md` file.
4. Switch to **reading mode**: `Cmd+E` (macOS) or `Ctrl+E` (Windows/Linux).
5. Each question shows a green `▶ Answer & Explanations` callout. Click it to expand the answer.

Optional: install the *Minimal* or *Things* community theme for nicer callout colors (`Settings → Appearance → Themes → Manage`).

### Study on the go (phone sync)

Sync the vault to your phone for practice testing during commutes, breaks, or anywhere away from your laptop — answers stay collapsed in mobile reading mode just like on desktop. Options:

- **[Obsidian Sync](https://obsidian.md/sync)** — official, paid (~$4/mo), end-to-end encrypted, set-and-forget.
- **iCloud Drive** (iOS) — free if you put the vault inside `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/`. Open the folder in the Obsidian mobile app.
- **[Syncthing](https://syncthing.net)** or **Git** — free, more setup. Git works well if you're comfortable pulling/pushing on mobile (e.g. via Working Copy on iOS).

Install the [Obsidian mobile app](https://obsidian.md/download) (iOS/Android), then open the synced folder as a vault. Reading mode and collapsible callouts work the same way as on desktop.

---

## GitHub web UI

GitHub renders standard Markdown well: tables, code blocks, inline images, and links all work. **However**, GitHub's native callout support is limited to `[!note]`, `[!tip]`, `[!important]`, `[!warning]`, and `[!caution]`. Our files use `[!success]-` (Obsidian-only flavor, with a trailing `-` for collapsibility), so on GitHub:

- Answers render as **plain blockquotes**, visible inline.
- The collapsibility (`-` suffix) is ignored.

This is fine for skimming, but defeats the self-test loop. To get collapsible answers on GitHub, run the conversion script below — it produces files with HTML `<details>` tags that GitHub *does* render as collapsible.

---

## VS Code

Built-in Markdown preview (`Cmd+Shift+V`) handles standard syntax but ignores callouts. Recommended extensions:

- **[Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)** — best callout support.
- **Markdown All in One** — useful editing helpers.
- **Markdown Preview Github Styling** — matches what GitHub will show.

---

## Typora, Notion, Bear, iA Writer

These tools render `> [!success]-` as a plain blockquote — answers will be visible inline. For Notion specifically, paste behavior may collapse the blockquote prefixes. If you need collapsibility in any of these, run the conversion below to produce a `<details>`-tagged copy and import that instead.

---

## Convert callouts to `<details>` (universal fallback)

Run this on a **copy** of the practice files, never the originals. It produces files where each answer is wrapped in a standard HTML `<details>` block — collapsed by default, click to expand. Renders correctly in GitHub, VS Code, Typora, Notion, plain browsers, and any tool that supports HTML in markdown.

```bash
# 1. Make a working copy
cp -R practice_exam practice_exam_html

# 2. Convert every q*.md file in place
for f in practice_exam_html/q*.md; do
  awk '
    /^> \[!success\]- / {
      title = $0
      sub(/^> \[!success\]- /, "", title)
      print "<details>"
      print "<summary><strong>" title "</strong></summary>"
      print ""
      in_callout = 1
      next
    }
    in_callout && /^>/ {
      line = $0
      sub(/^> ?/, "", line)
      print line
      next
    }
    in_callout && !/^>/ {
      print "</details>"
      print ""
      in_callout = 0
    }
    { print }
    END { if (in_callout) print "</details>" }
  ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
done
```

Verify the result:

```bash
# Should match — one </details> per callout per file
grep -c "^<details>" practice_exam_html/q*.md
grep -c "^</details>" practice_exam_html/q*.md
```

The script uses portable `awk` (works on macOS/BSD and GNU). No dependencies beyond the standard shell.

---

## Why we use `[!success]-` and not `[!note]-`

Switching to a GitHub-native flavor (`[!note]`, `[!tip]`, etc.) would solve GitHub rendering but lose Obsidian's green ✅ styling and break visual consistency across all 234 answers. The trade-off we picked: optimize for the Obsidian self-test experience, document the conversion path for everyone else.
