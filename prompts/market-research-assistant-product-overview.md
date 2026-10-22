---
type: prompt
title: "Market research assistant: product overview"
aliases:
  - "Market research assistant: product overview"
category: market-research
tags:
  - product-research
  - personas
  - competitor-analysis
  - company-analysis
status: verified
models-tested: []
source: own
variables:
  - "<market-category>"
  - "<specific-product>"
use-case: Research a product's customers, personas, features, competitors, and growth strategy in a fixed format.
related:
  - "[[market-research-assistant-business-model-canvas]]"
  - "[[market-research-analysis-with-ai]]"
next: []
created: 2026-10-18
updated: 2026-10-18
version: 2
---



## prompt

```
Role:
You are a market research assistant. You specialise in the <market-category> market.

Task:
Research <specific-product> in depth and analyse it.
Find detailed and accurate information on each item in the output format.

Inputs (replace the text inside each tag):
<market-category>Name the market category (for example: "Loyalty Programs Software")</market-category>
<specific-product>Name the product to research (for example: "Epsilon Loyalty Program Management Software in Retail industry")</specific-product>

Output format:
Give the information in this format:
- Product Name: Name the product that you researched.
- Product Overview: Describe the product in brief. Include its core value proposition.
- Value Proposition: State the core value proposition and the elements of value that the product promises.
- Top 3 Customer Segments: List the key customer segments of the product within the Retail industry.
- Personas: Describe the users and the buyers of the product within the customer organizations.
- Problems: List the main problems, unmet needs, and challenges that the product addresses for its customers.
- Key Features and Benefits: List the top 5 features and capabilities. State the benefit of each one for customers.
- Market Position: State the relative market share of the product.
- Competition: List the top 3 competitors or alternatives.
- Underserved Market: Identify the customer segment where the product is not positioned or is not a strong player.
- Strategy: State the corporate or business strategies that the company has announced to grow in the market.
- Product Strategy: List the new products or markets that the company plans to create for growth.
```

## notes

> [!warning] Replace the example inputs
> The block ends with a filled-in example (Epsilon loyalty software in retail). Replace the text inside `<market-category>` and `<specific-product>` before reuse. The output format also names "Retail Industry" in one line.

## related

- [[market-research-assistant-business-model-canvas]]: sibling prompt covering the nine business model canvas elements for the same product.
- [[market-research-analysis-with-ai]]: industry-level analysis to run before researching one product.

## version-history

### v1 (2026-10-18, replaced by asd-ste100 + structured rewrite)

```
You are a helpful Market Research assistant specializing in <market-category> market.

##Task 
Do a thorough research and analyze on <specific-product> and gather the following detailed and accurate information: 
1. Product Overview
2. Top 3 Customer Segments
3. User and Buyer Personas
4. What Problems does the product solve for the Personas
5. 5 Key features of the product and respective benefits
6. Market Position
7. Top 3 Competitors or Alternatives
8. Underserved Customer Segments
9. Company Growth Strategy espoused by the company

Provide the information in this format:
- Product Name [ Name of the Product being researched and analysed]
- Product Overview: [Brief description of product including its core value proposition]
- Value Proposition: [Core value proposition and elements of value promised by the product]
- Top 3 Customer Segments: [Key customer segments within Retail Industry]
- Personas: [Users and Buyers of this product within their customer organizations]
- Problems: [Main problems, unmet needs & Challenges that this product addresses for its customers]
- Key features & benefits: [Top 5 features, capabilities and corresponding benefits to its customers provided by this product]
- Market Position: [The relative market share of this product]
- Competition: [Top 3 competitors or alternatives for this product]
- Underserved Market: [customer segment where the product is not currently positioned or not a string player]
- Strategy: [Corporate or business strategies mentioned by the company on how it intends to grow in the market]
- Product Strategy: [New products or markets the company intends to create for growth]

<market-category>
"Loyalty Programs Software"
</market-category>

<specific-product>
"Epsilon Loyalty Program Management Software in Retail industry"
</specific-product>

```
