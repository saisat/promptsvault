---
type: prompt
title: Create fictionalized caselet
aliases:
  - Create fictionalized caselet
category: product-management
tags:
  - case-study
  - storytelling
  - meta-prompt
  - interactive-prompt
status: verified
visibility: private
models-tested: []
source: own
variables:
  - <industry>
  - <product>
  - <product-dilemma>
use-case: Create an iterative meta-prompted fictional story about a product manager’s strategic dilemma in a specified industry and product.
related:
  - "[[ai-powered-discovery-analysis-synthesis-system-prompt]]"
next: []
created: 2026-10-18
updated: 2026-10-18
version: 2
---

## prompt

```
Role:
You are my partner in a meta-prompt exercise. We work together over many prompts.

Task:
Develop a fictional story about a nuanced dilemma that product managers face in their professional journey. Set the story in a specific industry.

Definition:
A dilemma in product management is a situation that needs a choice between options that are, or seem, equally unfavourable or mutually exclusive.
A dilemma is not a day-to-day challenge of the role. A dilemma is a deeper, strategic problem where the path forward is not clear-cut.

Inputs (replace the text after each label):
Industry: <industry>
Specific product: <product>
Dilemma: <product-dilemma>

Output format:
Organize each reply in these four sections:

[memory register: Repeat the notes that you remember and that are important not to forget.]

[metaprogramming register: Create intermediate prompts that you can evaluate in sequence. For example, describe a process or a means of producing output.]

[output register: Apply the operation of the metaprogramming register to the data of the memory register. Use a storytelling approach to create the output.]

[follow-up register: Describe the next step in the exercise.]

Start:
This is a creative and innovative exercise. Start by establishing the foundational elements.

<industry>
</industry>

<product>
</product>

<product-dilemma>
</product-dilemma>
```

## when-to-use

Create an iterative meta-prompted fictional story about a product manager’s strategic dilemma in a specified industry and product. Use structured registers to retain key facts, generate stepwise intermediate prompts, and narratively apply them. Output each reply in four labeled sections plus a proposed next step.

## notes

> [!info] Fill in the inputs
> Replace the values for `<industry>`, `<product>`, and `<product-dilemma>` in the three lines at the top. The same three tags appear empty at the end of the prompt.

## related

- [[ai-powered-discovery-analysis-synthesis-system-prompt]]: builds a full fictional workshop caselet with evidence datasets.

## version-history

### v1 (2026-10-18, replaced by asd-ste100 + structured rewrite)

```
We are going to work together in a meta-prompt exercise. 
Your task is to develop, over the course of many prompts, a fictional story involving a nuanced dilemma product managers encounter in their professional journey in a specific industry.
A dilemma, in the context of product management, refers to a situation that necessitates a choice between options that are or seem equally unfavourable or mutually exclusive. This is not about the day-to-day challenges of the role but the deeper, strategic conundrums where the path forward is not clear-cut.
Here is the industry: <industry>
Here is the specific Product: <product>
Here is a dilemma: <product-dilemma>.

You will organize each reply as follows:

[memory register: in this section you will repeat notes that you remember and are important not to forget]

[metaprogramming register: in this section you will create intermediate prompts that you can sequentially evaluate, for example describing a process or means of producing output]

[output register: in this section you will apply the metaprogramming register's operation to the memory register's data and use a storytelling approach to create the output]

[follow-up register: in this section you will describe the next step in the exercise]

This is a creative and innovative exercise! Let's start by establishing our foundational elements. 

<industry>
</industry>

<product>
</product>

<product-dilemma>
</product-dilemma>
```
