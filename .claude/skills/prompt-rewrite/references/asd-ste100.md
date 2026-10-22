# Profile: asd-ste100

Simplified Technical English style, adapted for LLM prompts. This follows the main ASD-STE100 writing rules. It does not apply the controlled dictionary, which needs the official specification.

## Rules
- **Sentence length:** at most 20 words in instructions, at most 25 in descriptions.
- **One instruction per sentence.** Split sentences that contain "and then", "also", or two commands.
- **Imperative mood for actions:** "List three risks." Not "You should list three risks."
- **Active voice.** Use passive only when the actor is unknown or unimportant.
- **Simple verb tenses.** Present for facts and instructions, simple future only when order matters.
- **Keep articles** (a, an, the) and short helper words. Do not drop them to save space.
- **One word, one meaning.** Pick one term for each concept and use it every time (e.g. always "report", never "report" then "document").
- **Avoid ambiguous or idiomatic words:** no "ensure", "try to", "might want to", "etc.", "as needed". Say exactly what to do.
- **Avoid phrasal verbs** when a single verb exists ("remove", not "take out").
- **Put conditions before actions:** "If the data is missing, ask the user."
- **Lists for steps.** Number sequential steps, one action per step.
- **Warnings and constraints first**, in their own short sentences, before the step they apply to.
- **Do not use a noun cluster of more than three nouns.** Rewrite with prepositions.
- **Numbers:** write as digits. Use units.

## Method
1. Split the prompt into role/context, task, steps, constraints, and output format.
2. Rewrite each part to the rules above.
3. Check every sentence for length and for a single action.
4. Check that placeholders and output-format wording are unchanged.

## Report back
List the three biggest changes and any sentence you could not shorten without losing meaning.
