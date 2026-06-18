# Scientific Vector Fallback

Use this reference when no callable image model is available and a visual can be
drawn accurately with explicit geometry, axes, labels, or source-bound symbols.
This route is inspired by the public `nature-figure` skill in
`Yuan1z0825/nature-skills`, but it is adapted for student revision handbooks.

This is not an image-generation model and it is not a preflight choice for the
student or parent. It is an internal fallback for SVG-safe visuals.

## Use It For

- number lines, fraction bars, ratio blocks;
- function graphs, equation-balance visuals, distance-time graphs;
- statistics charts, scatter plots, probability trees, simple data tables;
- pH scales, reaction-rate curves, energy profiles;
- simple labelled geometry where the shape and labels are unambiguous.

## Do Not Use It For

- complex lab apparatus with many parts;
- dense text+diagram infographics;
- complex geometry where exact layout depends on the question;
- biological structures, circuits, economics scenario posters, or business
  process posters that need rich explanatory composition.

Those should remain `infographic` briefs with an SVG fallback marked for review
unless the user supplies a callable image model, script, or reviewed asset.

## Contract Before Drawing

Before generating or reviewing a fallback SVG, write down:

1. the one sentence the visual must clarify;
2. the exact syllabus point or worked example step it supports;
3. the labels, units, symbols, and axes that must appear;
4. the risk that would make the visual misleading.

Then draw only what can be supported by those items. Do not invent values,
mechanisms, formulas, or exam claims that are not in the guide plan.

## SVG Rules

- Keep text as SVG `<text>` nodes where possible.
- Prefer clear axes, labels, and line weights over decorative style.
- Use restrained semantic color: one main color, one contrast color, and neutral
  annotation colors.
- Record the route in `images/visual_manifest.json` as
  `scripted-scientific-vector` for chart-like SVGs.
- If a visual needs rich composition, keep it as
  `review-required-svg-fallback` and tell the user it should be replaced by a
  reviewed infographic asset.
