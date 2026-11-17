# Resume Builder

A Python / Streamlit workspace for building, refining, reviewing, and exporting professional resumes. The app works without an AI key. No database, account, or cloud storage is required.

## Run

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Start with your contact information, add relevant sections, then use **Preview** to choose a template and **Generate PDF** to prepare a download. Inputs update when you press Enter or leave a field; multiline fields also support Ctrl+Enter.

## What you can build

- Personal information, headline, and professional summary.
- Multiple degrees and jobs, with editable descriptions and one achievement per line.
- Skills with editable custom categories and optional text proficiency. Suggested categories include languages, frameworks, databases, tools, technical and soft skills. Skills display in compact groups without bars or percentages.
- Multiple projects: title, description, technologies, contributions, links, and optional dates. Projects and all new entry sections support moving entries up/down and removing individual entries.
- Certifications with issuer, date, and credential link; achievements with descriptions and optional dates.
- Languages, professional links, portfolio, GitHub, LinkedIn, and extracurricular activities.

The warm light workspace uses serif headings, restrained terracotta accents, refined forms, and an editor beside a live resume sheet. At smaller widths the columns stack. Import and workspace tools are grouped in sidebar disclosures.

## Templates and export

Choose **Preview & export → Resume template**:

1. **Classic Professional**: a single column with traditional serif typography and section rules.
2. **Modern Minimal**: sans-serif typography with restrained accent headings.
3. **Technical Resume**: a compact layout that brings skills and projects forward.
4. **Editorial**: centered serif name, navy headings, and open spacing without section rules.
5. **Compact Professional**: tight sans-serif spacing with the standard section order.

The template affects preview styling, section order, and PDF typography/spacing. **Student / entry-level emphasis** prioritizes education, skills, and projects. Hide optional sections and move sections up/down in Preview. Technical and student modes pin their priority sections before applying your remaining custom order. Empty sections stay off the resume.

The browser preview represents resume content and hierarchy; the PDF is the print layout, with its own measured wrapping and pagination. PDF exports support multiple pages, long links, bullet lists, page numbers, clickable email and supported HTTP(S) links, and selectable text colours. A generated download remains available until content, layout, or colour changes.

Noto Sans and Noto Serif fonts are bundled under the SIL Open Font License in `assets/fonts/`; export never downloads fonts at runtime. They support Latin, Greek, and Cyrillic, including accented names and typographic punctuation. These fonts do **not** cover every script or emoji. Unsupported characters produce an explicit error instead of disappearing. CJK, Indic shaping, and RTL typesetting would need additional fonts and shaping configuration.

## Profiles, autosave, and history

Everything autosaves **within the current Streamlit session only**. Navigation preserves edits. Restarting the server, losing the session, or reloading can clear data. Use **Save Profile (JSON)** for a durable local backup.

Version 2 JSON profiles include all sections, template, visibility, section order, and student mode. Existing version 1 profiles continue loading with empty defaults for new sections. Profile validation completes before replacing current data. Unknown fields are ignored; unsupported future format versions are rejected.

In **Workspace & history**, duplicate a resume under a new name and switch between independent profiles. **Undo / Redo** keeps up to 40 snapshots of content/layout changes in this session. A new edit after Undo clears the redo stack. Imported profiles can also be undone. AI suggestions and PDF bytes are not included in exported JSON or history. Download each named profile separately; JSON contains the selected resume, not the entire workspace. PDF colour is a workspace preference.

**Clear Data** asks for confirmation before clearing the entire session, including all profiles, history, imports, and generated downloads. Individual entry removal is recoverable with Undo.

## Resume import

Upload a PDF with extractable text, or UTF-8 / UTF-16 TXT. Files are read in memory; the app does not save them. Scanned PDFs need a text version (OCR is not included). Review all parsed values before using them.

Recognized headings: Summary / Profile / Professional Summary, Education, Experience / Work Experience / Professional Experience, Skills / Technical Skills, Projects, Certifications, Achievements, and Languages. Contact parsing retains existing fields it cannot recognize. Recognized nonempty sections replace only that section; unparseable sections retain existing entries and report a warning. Re-importing is explicit; normal reruns never overwrite edits.

Education and jobs accept labeled fields, or simple institution/degree and company/role blocks with dates. Separate entries with blank lines. Date ranges such as `2020 - Present` work. An experience entry's `Achievements:` label is retained as job content.

Skills accept comma, pipe, or semicolon-separated names, optionally prefixed by a category. New structured sections use labeled records to avoid guessing facts:

```text
Skills
Programming Languages: Python | SQL
Developer Tools: Git, Docker

Projects
Title: Resume workspace
Description: Built a resume editor.
Technologies: Python, Streamlit
Contributions: Implemented profile imports.
URL: https://example.com/project
Start date: Aug 2024
End date: Present

Certifications
Name: Cloud fundamentals
Issuer: Example Academy
Date: 2024
URL: https://example.com/credential

Achievements
Title: Student showcase
Description: Presented the editor.
Date: 2024

Languages
English, French
```

Freeform new-section paragraphs, multi-column PDFs, and arbitrary professional-link layouts are not reliably reconstructed. Use JSON for exact restoration of every field. Additional Information is edited manually; a Languages heading imports reliably.

## NVIDIA NIM setup

Your existing NVIDIA Build API key works with the NVIDIA provider. A separate key per model is not required; model access still depends on your account.

```powershell
$env:NVIDIA_API_KEY = 'your-nvidia-key'
$env:AI_PROVIDER = 'nvidia'
python -m streamlit run app.py
```

Open **AI → Provider & model settings**. Select **NVIDIA NIM**, then use the default text model or click **Load NVIDIA models** and select a text/chat model from the catalog. No model download is needed. The catalog may also list models unsuitable for writing; listing does not guarantee inference access. If a model cannot return a valid suggestion, choose another. A custom model ID is also supported. Optionally set `NVIDIA_MODEL` before starting to choose the initial model; the default is `nvidia/nemotron-3.5-lightning-30b-a3b`.

The key is read only from the server environment and is not entered in the interface, saved in profiles, or shown in errors. Restart Streamlit after setting environment variables. If NVIDIA_API_KEY is set, NVIDIA is selected by default unless AI_PROVIDER explicitly selects `openai` or `nvidia`.

The provider calls NVIDIA's [hosted Chat Completions endpoint](https://docs.api.nvidia.com/nim/reference/llm-apis). It requests a JSON suggestion through instructions and validates the response locally, allowing models without native JSON-schema response formatting. Unsupported output, incomplete responses, authentication/access errors, rate limits, and connectivity failures leave your original text intact. There is no silent provider fallback or automatic retry.

Loading the catalog sends only your API credential to NVIDIA, never resume content. Generating a suggestion sends the displayed text/context to the selected provider after explicit consent. Changing provider or model clears consent and makes old suggestions stale. All original factual guards and individual accept/reject controls apply to both providers. Neither NVIDIA nor OpenAI is called automatically during editing or navigation.

## Optional AI writing assistant

`ai_service.py` separates the provider interface, requests, response validation, and OpenAI transport from Streamlit. It uses the [OpenAI Responses API with structured output](https://developers.openai.com/api/docs/guides/structured-outputs), through Python's standard library, without adding an SDK dependency.

Set environment variables **in the terminal that starts Streamlit**, then restart the app:

```powershell
$env:OPENAI_API_KEY = 'your-api-key'
$env:OPENAI_MODEL = 'gpt-4.1-mini'  # Optional; choose a Responses / structured-output capable model available to your account.
python -m streamlit run app.py
```

The app and `check_nvidia.py` automatically load AI settings from a local `.env` file in the project root. Existing process environment variables take precedence. This file stays on your machine and is ignored by Git; do not share it. Never put keys in source code or profiles. `.env` and `.streamlit/secrets.toml` are ignored by Git; the integration reads process environment variables and the ignored local `.env` file. Keys are never shown in the UI, sent in profile exports, or included in error messages.

Use **AI → Rewrite a field**, then select a section, entry, and field. Expand **AI Improve** to choose an action. Actions: improve wording, make concise, expand, make more technical, make achievement-oriented, fix grammar, convert to bullets, and simplify. Set the shared writing style and length at the top of AI. Tones include Professional, Concise, Technical, Achievement-oriented, ATS-friendly, Confident, Student / Entry-level, Career Change, and Plain English. Length options are Very concise, Short, Balanced (default), and Detailed. These choices persist across tools and navigation; they are writing tones, separate from PDF templates.

**AI → Professional Summary → Summary assistant** generates a summary using existing education, experience, projects, skills, achievements, certifications, and headline. It avoids sending contact details. Change tone/length and regenerate, edit manually, or reject the result.

Before each request, the app displays source text and any context. You must explicitly consent to sending that information to the selected provider (**OpenAI** or **NVIDIA NIM**). Clicking Generate is the only way to initiate a call. The UI uses an in-flight guard, does not automatically retry, and does not call the API while typing or navigating. Regenerate is an intentional new request and may incur another charge. Requests have a timeout. OpenAI requests set `store: false`; NVIDIA uses its Chat Completions API. Provider-specific data policies still apply. Job-aligned rewriting also sends the displayed job description and current entry.

Original and suggestion are displayed separately. **Accept** applies one suggestion; **Reject** discards it. Changed source text requires regeneration. Prompts prohibit invented facts, and validation rejects empty/malformed responses, unsupported new numeric claims, and added skills from the checked vocabulary. The assistant asks for details when input is vague. No automated validator can guarantee semantic truth: review all experience, outcomes, titles, qualifications, and technical claims before accepting. Length is a generation preference rather than forced word padding.

Missing keys, connectivity errors, API limits, refused/incomplete responses, and invalid output show safe, actionable messages. Editing, matching, quality checks, JSON, and PDFs continue working. Automated tests mock all API calls; no real resume data is sent during testing. A paid live-provider smoke test is deliberately excluded.

## Review & Match

**Quality checker** runs locally. It checks missing name/email/phone, email format, summary and skills, empty entries, inconsistent date formats, descriptions over 100 words, summaries over 90 words, duplicate lines of four or more words, incomplete projects, long unbroken text, hidden skills, and absence of supporting education/experience/projects. Recommendations are actionable; no arbitrary quality score is assigned.

**Job Match Analyzer** runs a separate local keyword comparison against the visible resume. It shows detected keywords, present and unevidenced terms, relevant experience/projects, quality issues, and alignment guidance. Optional AI Improve controls refine relevant entries individually with consent and review.

Coverage is **matched detected keywords / all detected keywords × 100**, rounded to a whole percent. Detection uses a defined technical vocabulary plus repeated meaningful words; matching uses case-insensitive boundaries, including C++/C#. Hidden sections do not count. This estimate is **not an ATS score**, a guarantee, or a semantic assessment of qualifications. Synonyms, negated requirements, and nuanced relevance can be missed. Missing terms are review/learning topics: add a qualification only when you actually possess it.

The sidebar completion indicator checks six draft essentials: name, email, summary, at least one named skill, an education institution, and experience or a project. Optional certifications and achievements never lower completion.

## Validation

```powershell
python -m unittest -v
python -m compileall -q app.py models.py ui.py profiles.py preview.py exporter.py resume_upload.py ai_service.py ai_ui.py analysis_tools.py editor_sections.py
```

The suite covers existing workflows, new entry editing/removal/reordering, session navigation, complete and legacy profiles, atomic invalid imports, named profiles/history, mocked AI success/failure/consent/validation, local analysis, all five templates, Unicode/link extraction, multi-page wrapping and content bounds, import feedback, and confirmed reset. Two original reset tests now explicitly confirm the destructive action before asserting cleared state.

See `UPGRADE_NOTES.md` for implementation files, validation evidence, and deliberate limits. Generated samples and validation output belong under ignored `samples/` and `output/`, never in commits.

### Restart and clear your draft

To restart, press Ctrl+C in the running Streamlit terminal, then run `python -m streamlit run app.py`. To clear resume data, use **Clear Data → Confirm clear**; this removes all in-session profiles and history. Download a JSON backup first if needed. Neither action resets Git or deletes source changes. Test local AI configuration with `python check_nvidia.py`; it sends only a synthetic test message, and reads `.env` without asking for the key again.

## Improve the entire resume

Uploading a file imports the original text. To polish every writing section, select **AI**, then choose **Improve entire resume** from **AI tool**. Review the text that will be sent, choose a style and description length, give consent to the selected provider, and click **Improve entire resume**. This covers the existing summary/headline, education details, every job's bullets, skills/categories/proficiency, project titles/descriptions/technologies/contributions, achievement titles/descriptions, languages, and extracurriculars. Empty fields are skipped rather than invented. Contact information, dates, links, employer/degree names and official certification names are preserved.

The service sends bounded batches and shows progress; a large resume may require several requests and incur provider charges. No calls happen automatically on upload. It validates complete field mappings and checks each proposed value for unsupported numbers and known skills, retaining Basic proficiency qualifiers. Failed batches are reported and their original text remains intact. Review the original/improved comparisons, then click **Apply all improvements** to update all successful suggestions together. **Discard suggestions** keeps your draft. Editing the resume or switching provider/model makes a pending review stale. Undo can restore the previous draft after applying. All changes flow to the live preview, JSON profiles, and regenerated PDFs.

## Streamlined workflow

1. **Edit resume**: import a resume or JSON profile, choose a section from the section selector, and enter or update your information. AI controls no longer clutter editing forms.
2. **AI**: all provider/model settings, shared tone/length controls, whole-resume polishing, summary generation, individual field rewrites, quality checks, and Job Match Analyzer live here. Suggestions always require consent and review. Provider/model and tone/length selections survive navigation.
3. **Preview & export**: choose one of five resume styles, set PDF text colour, hide/reorder sections, choose student emphasis, and generate your PDF. Template choices affect both preview and PDF and are included in JSON profiles.

Use the Continue button to move forward, or Skip AI and preview when you prefer manual writing. You can return to any step using the three-item sidebar. The last editing section is remembered. Writing preferences remain separate from resume data and are not exported with candidate profiles. No API request is triggered by navigating between steps.

### Generation controls update

AI tools show a provider disclosure beside their generation buttons. Clicking Generate, Regenerate, or Improve entire resume authorizes that displayed request; there is no separate consent checkbox and no automatic request on upload or navigation. Project rewrites use the actual stack and details of the same project as context. Whole-resume project batches keep each project together and validate against that project rather than rejecting a description for mentioning its own technology stack. Suggestions still require Accept or Apply all improvements.

Sidebar navigation places the resume-section selector immediately below Edit resume and above AI. Choosing a section opens the editor. The Workspace & history panel and its profile/history controls have been removed from the interface; existing in-session data is retained. JSON import/export remains available.
