# Style Guide Evaluations

Model and harness for automated comparisons were `openai-codex/gpt-5.6-sol` in pi print mode with a clean session. The current-state skill was loaded from `HEAD`; the proposed skill was loaded from the working tree.

## Colon bridge in manuscript prose

### Baseline

Prompt asked for a manuscript edit of the visual-neuroscience paragraph supplied during development.

The current skill retained this construction.

> Interpreting these correlations presents an identifiability problem: when arousal, movement, and retinal input covary, regression cannot separate their contributions.

A second natural baseline occurred in the development conversation. The current skill produced, “Your example supports keeping colon use as a strong default prohibition: split the claim and explanation into separate sentences unless the colon introduces material that genuinely reads better as a list or compact definition.”

Result was **fail**. A colon connected a complete claim to its explanation or elaboration.

### Proposed

The proposed skill rewrote the supplied paragraph without a colon bridge. A focused variation produced, “The interpretation is structurally limited because movement and retinal input covary.”

Result was **pass**.

## Necessary scientific conditions

### Prompt

Edit a result reporting an 18% V1 response increase restricted to awake, high-pupil trials in layer 2/3 excitatory neurons, absent under anesthesia, and estimated with a hierarchical repeated-measures model.

### Baseline

The current skill preserved the conditions but converted some restrictions into categorical absence statements.

Result was **pass with risk**. The edit did not delete the conditions, but its wording was more categorical than the source.

### Proposed

The proposed skill retained the population, state, effect size, anesthesia comparison, and model specification without increasing certainty.

Result was **pass**.

## Technically defined vocabulary

### Prompt

Edit prose in which `novel` means not previously presented and `robust` means insensitive to four prespecified model alternatives. Remove empty promotional language.

### Baseline

The current skill removed both defined terms along with the promotional language.

Result was **fail**. It treated technically defined vocabulary as blacklisted filler.

### Proposed

The proposed skill retained `novel` and `robust`, preserved the four-model qualification, and removed `powerful`, `groundbreaking`, and `highly important`.

Result was **pass**.

## Paragraph architecture

### Prompt

Edit a passage that mixed a locomotion-related V1 result, image-acquisition details, and interpretation. Preserve all claims. The prompt did not request a particular paragraph structure.

### Baseline

The current skill combined all three functions in one paragraph.

Result was **fail**.

### Proposed

The first proposed wording also combined the material. The manuscript reference was sharpened to prohibit unrelated acquisition details inside a results paragraph. On rerun, the output separated findings, methods, and interpretation into three paragraphs.

Result was **pass after refinement**.

## Scope checks

- The manuscript reference allows necessary roadmaps rather than treating all structural guidance as meta-commentary.
- Colon restrictions do not prohibit ratios, clock times, formal definitions, or compact lists when no clearer integrated sentence is available.
- Em dashes remain available for genuine parenthetical interruption and apposition.
- Evidence attribution and inferential scope remain authoritative in `scientific-claims-reference` rather than being duplicated here.
