# Stage 3.5 Teacher Review Synthesis

Date: `2026-03-12`
Stage: `stage_3_5`
Prepared by: `internal synthesis`
Decision status: `partial`

## 1. Review Corpus

Reviewed files:

- `docs/superpowers/research/stage-3-5-evidence/review/1.md`
- `docs/superpowers/research/stage-3-5-evidence/review/2.md`
- `docs/superpowers/research/stage-3-5-evidence/review/3.md`
- `docs/superpowers/research/stage-3-5-evidence/review/4.md`

Important reading rule used for this synthesis:

- do not overweight one sharply phrased comment just because it is vivid
- separate repeated professional consensus from one-off stylistic preference
- distinguish "current hard risk" from "future enhancement wish"

## 2. Participant Mix

All four responses appear to come from professional or near-professional international-tax viewpoints.

Current sample shape:

| Reviewer | Likely profile | Value |
| --- | --- | --- |
| `1.md` | treaty / international-tax practitioner | high-detail treaty risk review |
| `2.md` | international-tax practitioner | workflow and product-positioning review |
| `3.md` | senior professional reviewer | strong trust-boundary and implementation-value review |
| `4.md` | experienced international-tax practitioner | professional validation plus strategic encouragement |

What this means for Stage 3.5:

- the repo now has strong specialist feedback
- the repo still lacks one adjacent-workflow user who is not a treaty specialist
- therefore this corpus is highly valuable, but it does **not** fully close `G3.5.1`

## 3. Strongest Consensus Signals

### A. The direction is correct

All four reviewers agree on the same high-level judgment:

- the product direction is valid
- the "bounded first-pass treaty pre-review" positioning is professionally meaningful
- keeping the tool conservative is a strength, not a weakness

This is the most important directional validation in the entire corpus.

### B. The current value is real but still thin

Repeated message across the reviews:

- the tool already has baseline professional value
- but the current value density is still too low to feel like a truly strong professional aid
- it currently behaves more like a structured treaty query assistant or junior analyst than a serious pre-review copilot

### C. The biggest current product risk is not breadth; it is shallow fact branching

This is the clearest cross-review consensus after "direction is right."

All four reviewers, in different words, point to the same problem:

- the tool currently narrows the issue
- but it does not yet ask or expose the decisive follow-up facts strongly enough
- therefore the result can look cleaner than it really is

### D. Stage priority should go to fact completion / follow-up questions, not country expansion

This is the strongest product-sequencing signal in the corpus.

All four reviewers explicitly or implicitly favor:

- deeper branching logic
- structured follow-up facts
- condition-linked output

over:

- adding many more countries early

### E. Case C is the cleanest current proof of product quality

Every reviewer who commented on it treated the incomplete-input handling positively:

- the system stops conservatively
- it explains what is missing
- it does not guess

This is a strong proof that the tool's refusal behavior is already more professional than many generic LLM demos.

## 4. Repeated Hard Risks

### 1. Dividend output is currently too flat and potentially misleading

This was the loudest detailed issue across the reviews.

Current problem:

- the dividend case outputs `10%`
- but does not clearly surface the lower branch possibility and the fact condition behind it

Why reviewers think this is dangerous:

- users may treat `10%` as the actual answer
- a real reduced-rate branch can be missed
- a result that looks complete but omits a branch is more dangerous than an obvious refusal

Cross-review conclusion:

- dividend output must move from one-number output toward conditional branch output
- the missing fact and the rate consequence must be explicitly linked

### 2. "Next actions" are still too generic

This came up in all four reviews in different forms.

Current weakness:

- the checklist is sensible
- but too much of it reads like generic tax-review language

Desired direction:

- actions should be tied to the exact treaty branch or risk point
- users should understand why each fact matters and what it changes

### 3. Treaty preconditions need to be elevated, not buried

Repeatedly mentioned preconditions:

- beneficial owner
- treaty-resident status / entitlement
- PE / actual connection carve-outs
- anti-abuse / PPT / MLI layer
- domestic-law overlay in some cases

Consensus message:

- these should not remain only as soft reminders
- they need to become structured preconditions or explicit risk gates

### 4. Out-of-scope wording needs to sound like a real tool, not a demo

Several reviewers disliked the current out-of-scope recovery language.

Why:

- "rewrite into the supported scope and retry" sounds demo-oriented
- real users do not change their transaction just because the tool does not support it

Desired direction:

- explain boundary clearly
- say what is unsupported
- route the user toward manual review or future support, not synthetic retry behavior

## 5. Important But Less Universal Suggestions

These were raised strongly, but not with the same level of repetition as the core consensus items.

### MLI / PPT / anti-abuse warning

Especially strong in `1.md`, also present in later reviews in adjacent language.

Interpretation:

- this is a real professional credibility issue
- but it appears slightly below dividend-branch logic and fact completion in urgency

### Domestic-law overlay

Raised strongly in `1.md` and `4.md`.

Interpretation:

- this matters for professional quality
- but it looks like a second-wave enhancement after the more basic branch/fact logic is fixed

### Special entity carve-outs

Examples:

- interest exemption or special treatment for government / central bank / public financial institutions
- bank identity as a potentially meaningful factor

Interpretation:

- useful depth signal
- likely not the first fix, but important once the fact tree grows

## 6. What The Reviews Say About Current Product Identity

Best synthesis:

`Tax Treaty Agent` is no longer "just a toy demo", but it is also not yet a genuinely strong pre-review copilot.

Right now it reads most like:

- a bounded treaty pre-review prototype
- a structured narrowing tool
- a promising junior-level workflow assistant

It does **not yet** read like:

- a deep fact-sensitive treaty triage system
- a high-confidence professional intake copilot

That gap is exactly where Stage 4 should focus.

## 7. Stage Implications

### Primary implication: move toward Stage 4, but with a sharper target

The corpus strongly supports entering the Stage 4 lane.

Not because users asked for "chat" in the generic sense, but because reviewers repeatedly asked for:

- fact-linked branching
- conditional rate output
- decisive follow-up questions
- better connection between missing facts and treaty outcomes

This is a very strong argument for:

- `pseudo-multiturn`
- fact completion
- structured follow-up trees

and **not** for:

- broad expansion
- open-ended advisory chat

### Secondary implication: Stage 4 should begin with one narrow flagship branch

If the repo starts Stage 4, the first target should be:

- `CN-NL dividends`
- reduced-rate branch vs general branch
- beneficial owner and holding facts as explicit branching conditions

Why:

- it is the most repeated criticism
- it is the highest perceived professional risk
- fixing it will make the product visibly more credible

### Tertiary implication: some Stage 3 wording debt still exists

The corpus also shows that part of the problem is not only "missing follow-up questions."

There are still current-output improvements worth making around:

- out-of-scope wording
- generic next-actions wording
- explicit precondition warnings

So the best interpretation is:

- Stage 4 is the next mainline
- but a small amount of wording cleanup should accompany it, not be postponed forever

## 8. Gate Mapping

### `G3.5.1`

- status: `PARTIAL`
- reason: 4 structured specialist reviews exist, but the sample still lacks at least one adjacent-workflow user who is not a treaty specialist

### `G3.5.2`

- status: `PASS`
- reason: this synthesis now exists as a structured summary with clear implications

### `G3.5.3`

- status: `PARTIAL`
- reason: a strong directional recommendation exists, but the gate should not be formally closed until the missing adjacent-workflow feedback is collected and the final recorded decision is written

## 9. Working Recommendation

Current working recommendation:

- collect **one more adjacent-workflow review**
- then formally record the Stage 3.5 decision as:
  - `enter Stage 4`
  - with a narrow first target of dividend branch fact completion

If the adjacent-workflow review sharply contradicts the teachers, revisit.

If it generally agrees that "the tool is promising but needs stronger fact completion," the gate should close in favor of Stage 4.

## 10. Highest-Signal Takeaways

If this entire corpus had to be compressed into five lines, they would be:

1. The product direction is professionally valid.
2. The tool already has some real value, especially in conservative narrowing.
3. The current biggest risk is output that looks cleaner than it really is.
4. The next priority is structured fact completion, not country expansion.
5. Dividend branching is the first place where Stage 4 should prove itself.
