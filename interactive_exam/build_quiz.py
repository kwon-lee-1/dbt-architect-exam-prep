#!/usr/bin/env python3
"""
build_quiz.py  —  Parse practice_exam/q*.md and generate quiz.html.
Usage: python build_quiz.py
Output: quiz.html (self-contained, open in any browser)
"""

import re
import json
import sys
import webbrowser
from pathlib import Path

EXAM_DIR = Path(__file__).parent.parent / "practice_exam"

# ── Regex patterns ─────────────────────────────────────────────────────────────

TOPIC_HEADER_RE = re.compile(
    r"^#\s+Topic\s+(.+?):\s+(.+?)\s+—\s+Practice Questions",
    re.MULTILINE,
)
QN_RE = re.compile(r"###\s+Q(\d+)\.\s*(⭐)?")
SUBDOMAIN_RE = re.compile(
    r">\s+\*\*Subdomain\s+([\d.a-z]+)\s+—\s+(.+?)\*\*", re.MULTILINE
)
QUESTION_TEXT_RE = re.compile(
    r">\s+\*\*Subdomain[^\n]+\n\n(.*?)\n\n- A\)", re.DOTALL
)
OPTION_RE = re.compile(r"^- ([A-E])\)\s+(.+)$", re.MULTILINE)
CORRECT_RE = re.compile(r">\s+\*\*✅ Correct:\s+([A-E,\s]+)\*\*")
EXPL_ROW_RE = re.compile(
    r"^\s*>\s+\|\s+\*\*([A-E])\)\s+([^*]+)\*\*\s+\|\s+(.+)$", re.MULTILINE
)
KEYRULE_RE = re.compile(
    r">\s+>\s+💡\s+\*\*Key rule\*\*:\s+(.+)", re.MULTILINE
)


# ── Parser ─────────────────────────────────────────────────────────────────────

def parse_block(block, file_id, topic_num, topic_name):
    qn_m = QN_RE.search(block)
    if not qn_m:
        return None

    question_num = int(qn_m.group(1))
    high_yield = bool(qn_m.group(2))

    sub_m = SUBDOMAIN_RE.search(block)
    subdomain_id = sub_m.group(1) if sub_m else ""
    subdomain_topic = sub_m.group(2) if sub_m else ""

    qt_m = QUESTION_TEXT_RE.search(block)
    question_text = qt_m.group(1).strip() if qt_m else ""

    options = {}
    for m in OPTION_RE.finditer(block):
        options[m.group(1)] = m.group(2).strip()

    correct_m = CORRECT_RE.search(block)
    correct_raw = correct_m.group(1).strip() if correct_m else ""
    correct_answers = [x.strip() for x in correct_raw.split(",")] if correct_raw else ["A"]

    explanations = {}
    for m in EXPL_ROW_RE.finditer(block):
        letter = m.group(1)
        label = m.group(2).strip()
        text = m.group(3).rstrip(" |").strip()
        explanations[letter] = {"label": label, "text": text}

    keyrule_m = KEYRULE_RE.search(block)
    key_rule = keyrule_m.group(1).strip() if keyrule_m else ""

    return {
        "id": f"{file_id}_Q{question_num}",
        "file_id": file_id,
        "topic_num": topic_num,
        "topic_name": topic_name,
        "question_num": question_num,
        "high_yield": high_yield,
        "subdomain_id": subdomain_id,
        "subdomain_topic": subdomain_topic,
        "question_text": question_text,
        "is_multi_select": len(correct_answers) > 1,
        "options": options,
        "correct_answers": correct_answers,
        "explanations": explanations,
        "key_rule": key_rule,
    }


def parse_file(path):
    content = path.read_text(encoding="utf-8")
    file_id = path.stem.split("_")[0]

    header_m = TOPIC_HEADER_RE.search(content)
    topic_num = header_m.group(1).strip() if header_m else "?"
    topic_name = header_m.group(2).strip() if header_m else path.stem

    blocks = re.split(r"\n-{3,}\n", content)
    questions = []
    for block in blocks:
        if not re.search(r"###\s+Q\d+", block):
            continue
        q = parse_block(block.strip(), file_id, topic_num, topic_name)
        if q:
            questions.append(q)
    return questions


def validate(questions):
    errors = []
    for q in questions:
        qid = q["id"]
        if not q["correct_answers"]:
            errors.append(f"{qid}: empty correct_answers")
        if len(q["options"]) < 4:
            errors.append(f"{qid}: only {len(q['options'])} options parsed")
        if not q["explanations"]:
            errors.append(f"{qid}: no explanations parsed")
        for letter in q["correct_answers"]:
            if letter not in q["options"]:
                errors.append(f"{qid}: correct answer {letter!r} not in options")
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)


# ── HTML template ──────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>dbt Architect Exam Quiz</title>
<style>
:root {
  --c-correct: #16a34a;
  --c-correct-bg: #f0fdf4;
  --c-wrong: #dc2626;
  --c-wrong-bg: #fef2f2;
  --c-sel: #2563eb;
  --c-sel-bg: #eff6ff;
  --c-rule-bg: #fefce8;
  --c-rule-border: #ca8a04;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: #f3f4f6;
  min-height: 100vh;
  color: #111827;
  line-height: 1.5;
}
#header {
  position: sticky;
  top: 0;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 10px 16px;
  z-index: 100;
}
.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
}
.score-badge {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
  min-width: 130px;
}
.progress-wrap {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar {
  height: 100%;
  background: #2563eb;
  border-radius: 3px;
  transition: width 0.3s ease;
  width: 0%;
}
.header-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  max-width: 820px;
  margin: 0 auto;
  flex-wrap: wrap;
}
#filter-select {
  flex: 1;
  min-width: 180px;
  padding: 5px 10px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  cursor: pointer;
  color: #374151;
}
#shuffle-btn {
  padding: 5px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 13px;
  background: #fff;
  cursor: pointer;
  color: #374151;
  white-space: nowrap;
  transition: background 0.15s, color 0.15s;
}
#shuffle-btn.on { background: #2563eb; color: #fff; border-color: #2563eb; }
#main {
  max-width: 820px;
  margin: 20px auto 80px;
  padding: 0 16px;
}
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.05);
  padding: 28px 28px 24px;
}
.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.topic-pill {
  font-size: 11px;
  font-weight: 500;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 2px 10px;
  color: #6b7280;
}
.star-badge {
  font-size: 11px;
  font-weight: 600;
  background: #fef9c3;
  border: 1px solid #fde047;
  border-radius: 999px;
  padding: 2px 8px;
  color: #713f12;
}
.q-counter {
  margin-left: auto;
  font-size: 13px;
  color: #9ca3af;
  font-weight: 500;
}
.subdomain {
  font-size: 11px;
  color: #9ca3af;
  margin-bottom: 14px;
  font-style: italic;
}
.question-text {
  font-size: 15px;
  line-height: 1.65;
  color: #111827;
  margin-bottom: 20px;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
}
.opt {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  text-align: left;
  padding: 11px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
  line-height: 1.5;
  color: #111827;
  transition: border-color 0.12s, background 0.12s;
  font-family: inherit;
}
.opt:hover:not([disabled]) { border-color: #93c5fd; background: #f0f7ff; }
.opt[disabled] { cursor: default; }
.opt-letter { font-weight: 700; min-width: 18px; color: #9ca3af; flex-shrink: 0; }
.opt.selected { border-color: var(--c-sel); background: var(--c-sel-bg); }
.opt.selected .opt-letter { color: var(--c-sel); }
.opt.correct { border-color: var(--c-correct); background: var(--c-correct-bg); }
.opt.correct .opt-letter { color: var(--c-correct); }
.opt.wrong-sel { border-color: var(--c-wrong); background: var(--c-wrong-bg); }
.opt.wrong-sel .opt-letter { color: var(--c-wrong); }
.action-row { display: flex; align-items: center; gap: 12px; }
.btn-submit {
  padding: 9px 22px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s;
}
.btn-submit:hover:not([disabled]) { background: #1d4ed8; }
.btn-submit[disabled] { background: #9ca3af; cursor: default; }
.select-hint { font-size: 13px; color: #9ca3af; }
.divider { border: none; border-top: 1px solid #f3f4f6; margin: 20px 0; }
.expl-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.expl-item { border-radius: 8px; padding: 11px 14px; border-left: 3px solid transparent; }
.expl-item.correct { background: var(--c-correct-bg); border-left-color: var(--c-correct); }
.expl-item.wrong-sel { background: var(--c-wrong-bg); border-left-color: var(--c-wrong); }
.expl-item.neutral { background: #f9fafb; border-left-color: #e5e7eb; }
.expl-head { font-size: 13px; font-weight: 600; margin-bottom: 3px; }
.expl-text { font-size: 13px; color: #374151; line-height: 1.5; }
.key-rule {
  background: var(--c-rule-bg);
  border-left: 4px solid var(--c-rule-border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  line-height: 1.55;
  margin-bottom: 16px;
}
.btn-next {
  padding: 9px 22px;
  background: #16a34a;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.12s;
}
.btn-next:hover { background: #15803d; }
.kbd-hint { text-align: center; font-size: 11px; color: #d1d5db; margin-top: 14px; }
.end-wrap { text-align: center; padding: 60px 24px; }
.end-score { font-size: 56px; font-weight: 700; line-height: 1; color: #111827; margin-bottom: 8px; }
.end-pct { font-size: 28px; font-weight: 600; color: #6b7280; margin-bottom: 6px; }
.end-sub { font-size: 15px; color: #9ca3af; margin-bottom: 32px; }
.btn-restart {
  padding: 12px 36px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}
.btn-restart:hover { background: #1d4ed8; }
code {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.875em;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 3px;
  padding: 1px 4px;
}
strong { font-weight: 600; }
a { color: #2563eb; }
</style>
</head>
<body>

<div id="header">
  <div class="header-top">
    <span class="score-badge" id="score-badge">Score: —</span>
    <div class="progress-wrap">
      <div class="progress-bar" id="progress-bar"></div>
    </div>
  </div>
  <div class="header-controls">
    <select id="filter-select"></select>
    <button id="shuffle-btn">Shuffle: OFF</button>
  </div>
</div>

<div id="main">
  <div class="card" id="card"></div>
  <div class="kbd-hint" id="kbd-hint"></div>
</div>

<script>
const ALL_QUESTIONS = QUESTIONS_JSON_PLACEHOLDER;

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  qs: [],
  idx: 0,
  sel: [],
  done: false,
  score: { ok: 0, total: 0 },
  filter: 'all',
  shuffle: false,
};

// ── Utilities ─────────────────────────────────────────────────────────────────
function fisherYates(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function md(text) {
  return esc(text)
    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

// ── Filter / shuffle ──────────────────────────────────────────────────────────
function applyFilter() {
  let pool = ALL_QUESTIONS;
  if (state.filter === 'hy') pool = pool.filter(q => q.high_yield);
  else if (state.filter !== 'all') pool = pool.filter(q => q.file_id === state.filter);
  state.qs = state.shuffle ? fisherYates(pool) : pool.slice();
  state.idx = 0;
  state.sel = [];
  state.done = false;
  state.score = { ok: 0, total: 0 };
}

// ── Header ────────────────────────────────────────────────────────────────────
function renderHeader() {
  const { ok, total } = state.score;
  const pct = total ? Math.round(ok / total * 100) : null;
  document.getElementById('score-badge').textContent =
    total === 0 ? 'Score: —' : 'Score: ' + ok + '/' + total + ' (' + pct + '%)';
  const progress = state.qs.length ? (state.idx / state.qs.length * 100) : 0;
  document.getElementById('progress-bar').style.width = progress + '%';
}

// ── Question card ─────────────────────────────────────────────────────────────
function renderQ() {
  const card = document.getElementById('card');
  const q = state.qs[state.idx];
  if (!q) { renderEnd(); return; }

  const letters = Object.keys(q.options).sort();

  const optHtml = letters.map(function(letter) {
    const isCorrect = q.correct_answers.indexOf(letter) >= 0;
    const isSel = state.sel.indexOf(letter) >= 0;
    let cls = 'opt';
    if (state.done) {
      if (isCorrect) cls += ' correct';
      else if (isSel) cls += ' wrong-sel';
    } else if (isSel) {
      cls += ' selected';
    }
    return '<button class="' + cls + '" data-l="' + letter + '"' +
           (state.done ? ' disabled' : '') + '>' +
           '<span class="opt-letter">' + letter + '</span>' +
           '<span>' + md(q.options[letter]) + '</span>' +
           '</button>';
  }).join('');

  const hint = q.is_multi_select ? 'Select 2 answers' : 'Select 1 answer';
  const canSub = state.sel.length > 0;
  const actionHtml = state.done ? '' :
    '<div class="action-row">' +
    '<button class="btn-submit" id="sub-btn"' + (canSub ? '' : ' disabled') + '>Submit</button>' +
    '<span class="select-hint">' + hint + '</span>' +
    '</div>';

  let explHtml = '';
  if (state.done) {
    const items = letters.map(function(letter) {
      const isCorrect = q.correct_answers.indexOf(letter) >= 0;
      const isSel = state.sel.indexOf(letter) >= 0;
      const expl = q.explanations[letter] || {};
      const label = expl.label || (isCorrect ? '\\u2705 Correct' : '\\u274c Incorrect');
      const text = expl.text || '';
      let cls = 'expl-item ';
      if (isCorrect) cls += 'correct';
      else if (isSel) cls += 'wrong-sel';
      else cls += 'neutral';
      return '<div class="' + cls + '">' +
             '<div class="expl-head">' + letter + ') ' + md(label) + '</div>' +
             '<div class="expl-text">' + md(text) + '</div>' +
             '</div>';
    }).join('');

    const ruleHtml = q.key_rule
      ? '<div class="key-rule">💡 <strong>Key rule:</strong> ' + md(q.key_rule) + '</div>'
      : '';

    const isLast = state.idx >= state.qs.length - 1;
    explHtml = '<hr class="divider">' +
               '<div class="expl-list">' + items + '</div>' +
               ruleHtml +
               '<button class="btn-next" id="next-btn">' + (isLast ? 'See Results' : 'Next →') + '</button>';
  }

  card.innerHTML =
    '<div class="card-meta">' +
    '<span class="topic-pill">Topic ' + esc(q.topic_num) + ': ' + esc(q.topic_name) + '</span>' +
    (q.high_yield ? '<span class="star-badge">\\u2b50 High-Yield</span>' : '') +
    '<span class="q-counter">Q' + (state.idx + 1) + ' / ' + state.qs.length + '</span>' +
    '</div>' +
    '<div class="subdomain">' + esc(q.subdomain_id) + ' — ' + md(q.subdomain_topic) + '</div>' +
    '<div class="question-text">' + md(q.question_text) + '</div>' +
    '<div class="options">' + optHtml + '</div>' +
    actionHtml +
    explHtml;

  card.querySelectorAll('.opt').forEach(function(btn) {
    btn.addEventListener('click', function() { toggleOpt(btn.dataset.l); });
  });
  const subBtn = document.getElementById('sub-btn');
  if (subBtn) subBtn.addEventListener('click', submit);
  const nextBtn = document.getElementById('next-btn');
  if (nextBtn) nextBtn.addEventListener('click', nextQ);

  document.getElementById('kbd-hint').textContent = state.done
    ? 'Enter or → to continue'
    : 'Keys: 1–' + letters.length + ' select · Enter submit';

  renderHeader();
}

// ── Interactions ──────────────────────────────────────────────────────────────
function toggleOpt(letter) {
  if (state.done) return;
  const q = state.qs[state.idx];
  if (q.is_multi_select) {
    const i = state.sel.indexOf(letter);
    if (i >= 0) state.sel.splice(i, 1);
    else state.sel.push(letter);
  } else {
    state.sel = [letter];
  }
  renderQ();
}

function submit() {
  if (state.done || state.sel.length === 0) return;
  const q = state.qs[state.idx];
  const correct = q.correct_answers.slice().sort().join(',');
  const selected = state.sel.slice().sort().join(',');
  state.done = true;
  state.score.total++;
  if (selected === correct) state.score.ok++;
  renderQ();
}

function nextQ() {
  if (state.idx >= state.qs.length - 1) { renderEnd(); return; }
  state.idx++;
  state.sel = [];
  state.done = false;
  renderQ();
}

// ── End screen ────────────────────────────────────────────────────────────────
function renderEnd() {
  const { ok, total } = state.score;
  const pct = total ? Math.round(ok / total * 100) : 0;
  const grade = pct >= 80 ? '\\u2705 Pass' : pct >= 60 ? '\\u26a0\\ufe0f Close' : '\\u274c Keep studying';
  document.getElementById('card').innerHTML =
    '<div class="end-wrap">' +
    '<div class="end-score">' + ok + '/' + total + '</div>' +
    '<div class="end-pct">' + pct + '%</div>' +
    '<div class="end-sub">' + grade + ' · ' + total + ' questions answered</div>' +
    '<button class="btn-restart" id="restart-btn">Try Again</button>' +
    '</div>';
  document.getElementById('progress-bar').style.width = '100%';
  document.getElementById('kbd-hint').textContent = '';
  document.getElementById('restart-btn').addEventListener('click', function() {
    applyFilter();
    renderQ();
  });
}

// ── Keyboard ──────────────────────────────────────────────────────────────────
document.addEventListener('keydown', function(e) {
  if (document.activeElement === document.getElementById('filter-select')) return;
  const q = state.qs[state.idx];
  if (!q) return;
  const letters = Object.keys(q.options).sort();
  const numMap = { '1': 0, '2': 1, '3': 2, '4': 3, '5': 4 };
  if (!state.done) {
    if (e.key in numMap) {
      const letter = letters[numMap[e.key]];
      if (letter) { toggleOpt(letter); e.preventDefault(); }
    } else if (e.key === 'Enter' && state.sel.length > 0) {
      submit(); e.preventDefault();
    }
  } else {
    if (e.key === 'Enter' || e.key === 'ArrowRight' || e.key === 'n') {
      nextQ(); e.preventDefault();
    }
  }
});

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
  const topicMap = {};
  let hyCount = 0;
  ALL_QUESTIONS.forEach(function(q) {
    if (q.high_yield) hyCount++;
    if (!topicMap[q.file_id]) {
      topicMap[q.file_id] = { num: q.topic_num, name: q.topic_name, count: 0 };
    }
    topicMap[q.file_id].count++;
  });

  const sel = document.getElementById('filter-select');
  sel.innerHTML =
    '<option value="all">All Topics (' + ALL_QUESTIONS.length + ')</option>' +
    '<option value="hy">\\u2b50 High-Yield (' + hyCount + ')</option>' +
    Object.keys(topicMap).map(function(fid) {
      const t = topicMap[fid];
      return '<option value="' + fid + '">Topic ' + esc(t.num) + ': ' + esc(t.name) + ' (' + t.count + ')</option>';
    }).join('');

  sel.addEventListener('change', function(e) {
    state.filter = e.target.value;
    applyFilter();
    renderQ();
  });

  const shuffleBtn = document.getElementById('shuffle-btn');
  shuffleBtn.addEventListener('click', function() {
    state.shuffle = !state.shuffle;
    shuffleBtn.textContent = 'Shuffle: ' + (state.shuffle ? 'ON' : 'OFF');
    shuffleBtn.classList.toggle('on', state.shuffle);
    applyFilter();
    renderQ();
  });

  applyFilter();
  renderQ();
});
</script>
</body>
</html>"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    files = sorted(EXAM_DIR.glob("q*.md"))
    if len(files) != 12:
        print(f"Warning: expected 12 files, found {len(files)}")

    all_questions = []
    for path in files:
        qs = parse_file(path)
        all_questions.extend(qs)
        print(f"  {path.name}: {len(qs)} questions")

    print(f"\nParsed {len(all_questions)} questions from {len(files)} files.")

    validate(all_questions)

    high_yield = sum(1 for q in all_questions if q["high_yield"])
    multi_select = sum(1 for q in all_questions if q["is_multi_select"])
    print(f"  High-yield: {high_yield}")
    print(f"  Multi-select: {multi_select}")

    questions_json = json.dumps(all_questions, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("QUESTIONS_JSON_PLACEHOLDER", questions_json)

    out_path = Path(__file__).parent / "quiz.html"
    out_path.write_text(html, encoding="utf-8")
    size_kb = out_path.stat().st_size // 1024
    print(f"\nWritten: quiz.html ({size_kb} KB)")
    webbrowser.open(out_path.as_uri())
    print("Opening quiz.html in your browser...")


if __name__ == "__main__":
    main()
