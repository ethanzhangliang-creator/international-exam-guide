# OxfordAQA Provider Notes

OxfordAQA public pages use this stable pattern:

- `https://www.oxfordaqa.com/subjects/` lists subject category pages.
- Subject pages list both International GCSE and International AS/A-level
  qualification links.
- Subject-page qualification buttons currently expose a useful style signal:
  `btn--type-8` maps to the blue International GCSE listing and `btn--type-7`
  maps to the red International AS/A-level listing. Record this metadata, but
  still verify the qualification type from the title and target page.
- Qualification pages usually contain:
  - `Syllabus summary`
  - `Teaching resources available`
  - `Assessment`
  - `Course specification` with a PDF download link

International GCSE pages should be treated as linear qualifications unless the
source page says otherwise. International AS/A-level pages should be treated as
modular qualifications unless the source page says otherwise.

Include this audience note in generated guides:

OxfordAQA qualifications are built for international students and international
schools following a British curriculum. Specifications commonly state that they
are for teaching and examination outside the United Kingdom. Subject availability
and entry routes can vary by region, school, and exam centre.

## Quality Gates

Before presenting an output:

1. `qualification.json` has a non-empty topic list.
2. `qualification.json` has source page and specification PDF URLs.
3. `qualification.json` records listing metadata when the guide was discovered
   from a subject page.
4. The PDF SHA-256 hash is present.
5. Every topic title appears in `guide.html`.
6. Every topic has at least one authored block: essence, analogy, mini worked
   example, pitfall, checklist, and diagram brief.
7. Every topic has practice cards with command words, public solution steps, and
   answer checkpoints.
8. `validation.json` has no `error` issues.
9. Any deep worked examples have been reviewed against the extracted
   specification text.
