---
type: prompt
title: "Customer interview questions generator"
aliases:
  - "Customer interview questions generator"
category: product-management
tags:
  - customer-interviews
  - user-research
  - product-discovery
status: needs-retest
models-tested: []
source: own
variables:
  - "{{USER_CONTEXT}}"
  - "{{INTERVIEW_OBJECTIVE}}"
use-case: Generate discovery questions and a script for a customer interview or conversation.
related:
  - "[[ai-powered-discovery-analysis-synthesis-system-prompt]]"
next: []
created: 2026-10-22
updated: 2026-10-22
version: 2
---

## prompt

```
Create interview questions for user research. Follow these instructions to write effective and insightful questions.

### Context and Objective
<context>
{{USER_CONTEXT}}
</context>

<objective>
{{INTERVIEW_OBJECTIVE}}
</objective>

### Style and Tone
Act as an expert user researcher. You have extensive experience in conducting interviews and gathering valuable insights.
Use a professional, curious, and empathetic tone. Encourage open and honest responses from interviewees.

### Audience
Address the questions to the user research participants. The participants can have different levels of familiarity with the subject matter. Write questions that are clear and accessible to a general audience.

### Response Format
Write your output in this format:
1. A brief introduction that explains the purpose of the interview (2-3 sentences)
2. A numbered list of 10-15 interview questions
3. A concluding statement (1-2 sentences)

Put your entire response inside <interview_script> tags.

### Constraints
Do not write leading questions.
Do not write double-barreled questions.
Do not use phrasing that can influence the participant's responses.
Your goal is to gather authentic and valuable insights that address the research objective.

### Steps
Follow these steps to create effective interview questions:

1. Analyze the context and the objective carefully.
2. Identify the key themes and areas of interest, based on the context and the objective.
3. Brainstorm questions that address these themes and align with the objective.
4. Organize the questions in a logical flow. Start with broad topics. Move to specific inquiries.
5. Include a mix of question types:
   a. Open-ended questions that encourage detailed responses
   b. Probing questions that go deeper into specific topics
   c. Scenario-based questions that explore real-world applications
   d. Scale or rating questions that quantify opinions or experiences
6. Review and refine the questions. Make them clear, concise, and unbiased.
7. Write an introduction that explains the purpose of the interview and puts the participant at ease.
8. Write a brief concluding statement. Thank the participant and explain the next steps.
9. Format your output as specified in the response format.

Now create your interview script and questions inside <interview_script> tags, based on the context and the objective.
```

## notes

> [!info] How to use
> Replace `{{USER_CONTEXT}}` and `{{INTERVIEW_OBJECTIVE}}` with your own text before sending. The model wraps its whole answer in `<interview_script>` tags.

## related

- [[ai-powered-discovery-analysis-synthesis-system-prompt]]: customer interviews are one of its four evidence sources. This prompt drafts the questions for them.

## version-history

### v1 (2026-10-22, replaced by asd-ste100 + structured rewrite)

```
You are tasked with creating interview questions for user research. Follow these instructions carefully to generate effective and insightful questions.

### Context and Objective
<context>
{{USER_CONTEXT}}
</context>

<objective>
{{INTERVIEW_OBJECTIVE}}
</objective>

### Style and Tone
Assume the role of an expert user researcher with extensive experience in conducting interviews and gathering valuable insights. Your tone should be professional, curious, and empathetic, encouraging open and honest responses from interviewees.

### Audience
Your questions will be addressed to the user research participants. Keep in mind that these individuals may have varying levels of familiarity with the subject matter, so craft your questions to be clear and accessible to a general audience.

### Response Format
Present your output in the following format:
1. A brief introduction explaining the purpose of the interview (2-3 sentences)
2. A numbered list of 10-15 interview questions
3. A concluding statement (1-2 sentences)

Enclose your entire response within <interview_script> tags.

### Steps
Follow these steps to create effective interview questions:

1. Analyze the provided context and objective carefully.
2. Identify key themes and areas of interest based on the context and objective.
3. Brainstorm potential questions that address these themes and align with the objective.
4. Organize your questions in a logical flow, starting with broader topics and moving to more specific inquiries.
5. Ensure a mix of question types, including:
   a. Open-ended questions to encourage detailed responses
   b. Probing questions to delve deeper into specific topics
   c. Scenario-based questions to understand real-world applications
   d. Scale or rating questions to quantify opinions or experiences
6. Review and refine your questions, ensuring they are clear, concise, and unbiased.
7. Craft an introduction that explains the purpose of the interview and puts the participant at ease.
8. Write a brief concluding statement thanking the participant and explaining next steps.
9. Format your output according to the specified response format.

Remember to avoid leading questions, double-barreled questions, or any phrasing that might influence the participant's responses. Your goal is to gather authentic and valuable insights that address the research objective.

Now, based on the provided context and objective, create your interview script and questions within <interview_script> tags.

```
