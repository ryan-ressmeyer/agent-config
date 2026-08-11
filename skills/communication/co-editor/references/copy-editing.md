# Copy Editing

Copy editing checks determinate surface-level issues after the author is satisfied with the content and structure. It covers grammar, syntax, punctuation, spelling, typographical errors, formatting, citation and cross-reference syntax, and terminology consistency. It does not re-litigate claims, organization, or voice.

## Review method

For a small scope, review inline. For a long document, the top-level agent may parallelize inspection across independent chunks when doing so reduces latency.

Copy-editing subagents must:

- inspect only their assigned text;
- report candidate issues with exact locations, explanations, and proposed corrections;
- receive any document-wide terminology or formatting conventions needed for the check;
- make no file edits;
- create no review files or other artifacts.

The top-level agent must verify every candidate against the source and applicable document-wide conventions. Reject duplicates, context-dependent false positives, and suggestions that are merely stylistic preferences. Never relay unverified subagent output to the author.

## Present before editing

Present the verified findings in chat before changing the source. Group document-wide consistency decisions first, then move through localized errors in reading order. For each finding, give:

- location;
- current form;
- why it is an error or inconsistency;
- proposed correction.

Wait for the author's approval. Apply only approved corrections, then re-read the affected text and run relevant format or build checks.

For a very large set of findings, present manageable batches rather than one exhaustive wall of corrections. The author controls the pace and may reject a house-style normalization that is not a true error.
