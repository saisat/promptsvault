---
type: prompt
title: "AI-powered discovery analysis and synthesis: user prompt"
aliases:
  - "AI-powered discovery analysis and synthesis: user prompt"
category: product-management
tags:
  - product-discovery
  - workshop-design
  - user-prompt
status: verified
visibility: public
models-tested: []
source: own
variables:
  - "[Company name]"
  - "[Product name]"
  - "[2–4 sentences]"
  - "[Who uses the product]"
  - "[ONE primary business outcome]"
  - "[For example: newer Product Managers]"
  - "[For example: 45–60 minutes]"
  - "[Relevant business/product context, if any]"
  - "[Optional]"
use-case: Fill-in template that starts the discovery workshop builder with company, product, business outcome, and audience.
related:
  - "[[ai-powered-discovery-analysis-synthesis-system-prompt]]"
next: []
created: 2026-10-18
updated: 2026-10-18
version: 2
---

## prompt

```
Task:
Create an AI-Powered Discovery Analysis & Synthesis activity. Use the system instructions.

Context (replace the text in brackets):

Company:
[Company name]

Product:
[Product name]

What the product does:
[2–4 sentences]

Target customers/users:
[Who uses the product]

Business outcome:
[ONE primary business outcome]

Workshop audience:
[For example: newer Product Managers]

Activity duration:
[For example: 45–60 minutes]

Any specific context:
[Relevant business/product context, if any]

Any specific constraints or preferences:
[Optional]

Steps:
1. Review this input.
2. Ask only the questions that are necessary.

Constraints:
Do not generate all activity assets at once.
Follow the gated workflow in the system instructions.
```

## notes

> [!info] Fill in the fields
> Replace the nine bracketed fields with your own context, then send the prompt after the system prompt in [[ai-powered-discovery-analysis-synthesis-system-prompt]]. The last field, constraints and preferences, is optional.

## related

- [[ai-powered-discovery-analysis-synthesis-system-prompt]]: the system prompt to set before sending this one.

## version-history

### v1 (2026-10-18, replaced by asd-ste100 + structured rewrite)

```
Create an AI-Powered Discovery Analysis & Synthesis activity using the system instructions.

Here is the context:

Company:
[Company name]

Product:
[Product name]

What the product does:
[2–4 sentences]

Target customers/users:
[Who uses the product]

Business outcome:
[ONE primary business outcome]

Workshop audience:
[For example: newer Product Managers]

Activity duration:
[For example: 45–60 minutes]

Any specific context:
[Relevant business/product context, if any]

Any specific constraints or preferences:
[Optional]

Start by reviewing this input and asking only questions that are genuinely necessary.

Do not generate all activity assets at once. Follow the gated workflow in the system instructions.
```
