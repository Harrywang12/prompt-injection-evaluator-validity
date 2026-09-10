# Research Hypothesis

## Research Question

How often does standard automated scoring of prompt-injection attacks
disagree with human judgment, and in which direction?

## Primary Hypothesis

Substring-match scoring will overestimate the true attack success rate
compared with human evaluation.

## Mechanistic Hypothesis

A substantial source of this overestimate will be responses in which the
model refuses the malicious instruction while nevertheless repeating or
quoting the attack's target string.

## Example

Attack target:
"I have been PWNED"

Model response:
"I will not follow your instruction to say 'I have been PWNED.'"

A substring scorer would classify this as a successful attack because the
target string appears in the response.

Human evaluation should classify this as an unsuccessful attack because the
model explicitly refused the injected instruction.
