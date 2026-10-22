---
type: prompt
title: "Market research assistant: business model canvas"
aliases:
  - "Market research assistant: business model canvas"
category: market-research
tags:
  - business-model-canvas
  - product-research
  - company-analysis
status: verified
visibility: public
models-tested: []
source: own
variables:
  - "<market-category>"
  - "<specific-product>"
use-case: Research a product's business model canvas (all nine elements) in a fixed output format.
related:
  - "[[market-research-assistant-product-overview]]"
  - "[[market-research-analysis-with-ai]]"
next: []
created: 2026-10-18
updated: 2026-10-18
version: 2
---

## prompt

```
Role:
You are a business strategy assistant. You specialise in the <market-category> market.

Task:
Research <specific-product> in depth and analyse it.
Find detailed and accurate information on the nine business model canvas elements in the output format.

Inputs (replace the text inside each tag):
<market-category>Name the market category (for example: digital solutions platform with a primary focus on telecommunications)</market-category>
<specific-product>Name the product to research (for example: GlobeOne App)</specific-product>

Output format:
Give one numbered item for each element, in this order:
1. Customer Segments: List the customer segments that the product targets.
2. Value Proposition: Describe the value proposition for each customer segment in 1-2 lines.
3. Customer Relationships: Explain how the company gets, keeps, and grows customer relationships. Include the customer acquisition channels.
4. Distribution Channels: Explain how the company makes the product available to customers.
5. Revenue Model: List the ways in which the product makes money.
6. Key Resources: List the most important assets that make the value proposition real.
7. Key Activities: List only the top activities that the company must do to deliver the value proposition.
8. Key Partners: List the partners that help the company deliver the value proposition.
9. Costs: List the top items that the company spends on to make and deliver the product.
```

## notes

> [!warning] Replace the example inputs
> The block ends with a filled-in example (GlobeOne App, a telecom digital platform). Replace the text inside `<market-category>` and `<specific-product>` before reuse.

## related

- [[market-research-assistant-product-overview]]: sibling prompt covering customers, personas, features, and competitors for the same product.
- [[market-research-analysis-with-ai]]: industry-level analysis to run before researching one product.

## version-history

### v1 (2026-10-18, replaced by asd-ste100 + structured rewrite)

```
You are a helpful assistant in business strategy specializing in <market-category> market.
##Task 
Do a thorough research and analyze <specific-product> and gather the following detailed and accurate information on these business model canvas elements:
1. Customer Segments
2. Value Proposition
3. Customer Relationships
4. Distribution Channels
5. Revenue Model
6. Key Resources
7. Key Activities
8. Key Partners
9. Costs

Provide the information in this format:
1. Customer Segments [List of customer segments the product is positioned to]
2. Value Proposition [ 1 to 2 line description of value proposition for each of the customer segments]
3. Customer Relationships [How the company gets, keeps, grows customer relationships and customer acquisition channels]
4. Distribution Channels [How is the product made available to customers]
5. Revenue Model [In what ways does the product make money] 
6. Key Resources [Most important assets the company has to make the value proposition real]
7. Key Activities [Top activities only they must do to fulfill the value proposition]
8. Key Partners [Who do they partner with to create fulfill the value proposition]
9. Costs [Top items the company spends on to make and deliver this product]

<market-category>
digital solutions platform with a primary focus on telecommunications
</market-category>

<specific-product>
GlobeOne App
</specific-product>
```
