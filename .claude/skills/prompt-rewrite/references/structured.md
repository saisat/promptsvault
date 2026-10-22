# Profile: structured

Reorganise the prompt into labelled sections so each part of the job is explicit. Keep the author's wording where it is already clear.

## Target shape
```
Role: who the model is and what expertise it has.
Context: the situation and any inputs, with placeholders for variables.
Task: the one thing to produce.
Steps: numbered, only if the task has an order.
Constraints: what to avoid or must hold true (length, tone, scope).
Output format: exact structure of the answer.
Verification: how the model should check its own answer before replying.
```

## Rules
- Drop a section if the original has nothing for it. Do not invent filler.
- Do not add new requirements. Move and label what exists.
- Put inputs and variables in Context. Put the single ask in Task.
- Make the output format concrete (headings, table columns, or length), not "clear and concise".
- Add a Verification line only when the original implies one or the user asks for it.
- Keep it in plain text or light markdown. Avoid XML tags unless the original uses them.

## Report back
Say which sections were created, which were skipped, and what, if anything, the original left unclear.
