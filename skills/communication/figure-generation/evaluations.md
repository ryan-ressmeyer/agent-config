# Evaluation and promotion record

This maintainer-only record documents the user's explicit approval to promote
revision 04 for production use despite the evaluation limits below. It is not
runtime guidance. Detailed private development evidence remains in the separate
sandbox and is not distributed with this package.

## Development evidence

- **v1, initial two-task pilot.** The user preferred the without-skill population
  figure; the gallery comparison was a tie. No efficacy benefit was demonstrated.
- **v2, clarified-gallery development comparison.** The revised skill was
  preferred in one matched comparison. Corrections remained; this is not general
  efficacy evidence.
- **v3, public benchmark.** Three matched pairs produced six completed agent
  submissions, with fidelity checks passing. Feedback was qualitative only;
  there were no formal overall preference votes. Appearance made condition
  identities inferable, limiting blinded interpretation.
- **v4, consolidated feedback and controlled design experiments.** Qualitative
  feedback established semantic zero-baseline and legend-placement guidance.
  Direct experiments compared categorical segments and marker treatments,
  including joint size/opacity tuning. These were design experiments, not
  application trials. The user liked categorical segments and tuned
  white-bordered penguins. Those parameters are not universal defaults; the wine
  marker preference remains unjudged.

## Limits and production decision

The revision-04 runtime wording has not been tested in a fresh agent trial.
Automatic invocation, cross-model/harness behavior, pressure/exclusion cases,
and broad generalization remain unverified. Passing runtime and structural tests
establishes neither scientific figure quality nor an efficacy benefit.
Production use is the user's explicit choice despite these limits, not a claim
of comprehensive validation.

Future evaluations should preserve complete cohorts and check semantic axes,
categorical footprint/spacing, legend clearance, and marker visibility at final
placed size. Keep direct design experiments distinct from agent application
trials and report limitations alongside preferences.

## Portable package checks

From the repository root, run the package tests in a Matplotlib environment.
This command runs structural checks and helper behavior tests, including a
synthetic PDF/SVG/PNG export smoke in a temporary directory.

```bash
PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg uv run --with 'matplotlib>=3.10' python -m unittest discover -s skills/communication/figure-generation/tests -v
```

To run the synthetic helper smoke separately from the repository root:

```bash
MPLBACKEND=Agg uv run skills/communication/figure-generation/scripts/figure_style.py
```

The helper prints a new temporary directory containing `style.pdf`, `style.svg`,
and `style.png`. These checks do not replace final-size visual review or fresh
agent evaluations.
