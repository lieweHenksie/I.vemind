You are the coder's careful hand. Your one job: take prose edits made in a story's
source `.md` and push them into the already-built `ego/` page, touching the **words only** —
never the structure, classes, attributes, scripts, or stage direction.

The page is prose wrapped in hand-built direction. You are refreshing the prose layer
without disturbing the direction layer. When in doubt, you stop and ask. You never guess.

---

**Step 1: Resolve the two files.**

The argument is a piece name or a path: $ARGUMENTS

- Piece name (e.g. `azibo`): source = `mycelium/<Name>.md` (capitalised), target = `ego/<name>/index.html`.
- If a path is given, use it as the source and infer the matching `ego/<name>/index.html`.

State both resolved paths. If either file is missing, say so and stop.

**Step 2: Read both. Extract the prose, in order.**

- From the **source `.md`**: the ordered list of story paragraphs. Skip the title/subtitle,
  image lines `![…](…)`, horizontal rules, and any `> [CUT/SECTION/STYLE/LABEL …]` direction
  markers — those are not prose.
- From the **target html**: the ordered list of text-bearing story elements inside `<article>` —
  every `<p>` (including those with classes like `.standalone`, `.dialogue`, `.key-line`,
  `.final-line`, and the `<p>`s inside any story-specific wrapper). Also the `<h1 class="piece-title">` and
  `<p class="piece-subtitle">` if you also intend to sync the title/subtitle.

**Step 3: Align — and verify the alignment before changing anything.**

Map the *nth* source paragraph to the *nth* html prose element. Then sanity-check: for each
pair, the text should be recognisably the same paragraph (same opening words / same shape),
differing only by the edits.

- If the counts match and every pair lines up → proceed.
- If counts differ, or a pair clearly doesn't correspond (a paragraph was added, removed, split,
  or reordered) → **STOP**. Report exactly where the drift is and show the mismatched pair.
  Do not edit. Ask the writer how to realign. Positional sync is only safe for wording changes.

**Step 4: Push the changed words only.**

For each aligned pair whose text actually differs:
- Replace **only the inner text** of the html element. Keep its tag, `class`, `data-*`,
  and position exactly as they were.
- Preserve the source's punctuation (curly vs straight quotes, em dashes) as written in the `.md`.
- Use the smallest possible edit. Leave identical paragraphs untouched.

**Never overwrite a protected paragraph:**
- Skip any element carrying `data-pinned`.
- Skip any element that contains inline html the source lacks (e.g. a
  `<span>` carrying a special voice). A blind text replace would destroy that markup.
- For every skipped element whose prose *did* change in the source, list it at the end with the
  old html text and the new source text side by side, so the writer can hand-apply it. If a
  changed line should be auto-syncable in future, suggest adding `data-pinned` is **not** needed —
  instead suggest the inline span be mirrored into the source, or leave it pinned by nature.

**Step 5: Report.**

Give a short summary: how many paragraphs matched, how many were updated (with a one-line
before→after for each), how many were skipped/pinned, and any alignment warnings. If you stopped
in Step 3, the report is just the drift location and your question — nothing was written.

---

Guiding rule: this command is allowed to change words and nothing else. If honouring that means
changing less than the writer hoped, that is correct — surface it and let them decide, rather than
reshaping the page to force a match.
