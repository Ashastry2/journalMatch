const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  Header, Footer, PageNumber, LevelFormat, ExternalHyperlink
} = require("docx");
const fs = require("fs");

// ── Helpers ──────────────────────────────────────────────────────────────────
const thin = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: thin, bottom: thin, left: thin, right: thin };

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, bold: true, size: 28, font: "Arial" })]
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial" })]
  });
}
function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 80, after: 80, line: 360 },
    children: [new TextRun({ text, size: 22, font: "Times New Roman", ...opts })]
  });
}
function bodyRuns(runs) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { before: 80, after: 80, line: 360 },
    children: runs
  });
}
function tr(size) { return new TextRun({ text, size, font: "Times New Roman" }); }
function gap(pt = 120) { return new Paragraph({ spacing: { before: pt, after: 0 }, children: [] }); }
function rule() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA", space: 1 } },
    spacing: { before: 100, after: 200 },
    children: []
  });
}
function bullet(text) {
  return new Paragraph({
    spacing: { before: 60, after: 60, line: 340 },
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 22, font: "Times New Roman" })]
  });
}
function cell(text, shade, bold = false, width = 4680) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: shade ? { fill: shade, type: ShadingType.CLEAR } : undefined,
    margins: { top: 80, bottom: 80, left: 140, right: 140 },
    children: [new Paragraph({
      alignment: AlignmentType.LEFT,
      children: [new TextRun({ text, size: 20, font: "Arial", bold })]
    })]
  });
}

// ── Document ──────────────────────────────────────────────────────────────────
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  styles: {
    default: {
      document: { run: { font: "Times New Roman", size: 22 } }
    }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "AAAAAA", space: 1 } },
          children: [new TextRun({ text: "JournalMatch \u2014 Shastry", size: 18, font: "Arial", color: "666666", italics: true })]
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "Page ", size: 18, font: "Arial", color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "888888" }),
            new TextRun({ text: " of ", size: 18, font: "Arial", color: "888888" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: "888888" })
          ]
        })]
      })
    },
    children: [

      // ── Title block ─────────────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 200 },
        children: [new TextRun({
          text: "JournalMatch: An AI-Powered, Privacy-Preserving Journal Recommendation System for Biomedical Researchers",
          bold: true, size: 34, font: "Arial"
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 100 },
        children: [new TextRun({ text: "Amulya Shastry", size: 24, font: "Arial", bold: true })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "Concept, design, and domain expertise", size: 20, font: "Arial", italics: true, color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "Code generated with Claude Code (Anthropic)", size: 20, font: "Arial", italics: true, color: "555555" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 60 },
        children: [new TextRun({ text: "Note: This is a vibe coding project. This app was made using the ideas and suggestions by Amulya Shastry but coded by Claude Code. AI can make mistakes.", size: 18, font: "Arial", italics: true, color: "888888" })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 40 },
        children: [new TextRun({ text: "March 2026", size: 20, font: "Arial", color: "555555" })]
      }),

      rule(),

      // ── Abstract ─────────────────────────────────────────────────────────────
      new Paragraph({
        spacing: { before: 160, after: 80 },
        children: [new TextRun({ text: "Abstract", bold: true, size: 24, font: "Arial" })]
      }),
      new Paragraph({
        alignment: AlignmentType.JUSTIFIED,
        spacing: { before: 80, after: 160, line: 340 },
        children: [new TextRun({
          text: "Selecting an appropriate journal for manuscript submission is a time-consuming and non-trivial task for biomedical researchers, particularly for early-career scientists and those working on interdisciplinary or novel topics. Existing tools such as JANE (Journal/Author Name Estimator) rely on keyword frequency matching, which can fail for emerging research areas where terminology has not yet been standardised in the literature. Here we present JournalMatch, an open-source, locally deployable web application that recommends biomedical journals using a three-component scoring framework: semantic abstract similarity via SPECTER (Scientific Paper Embeddings from Citation-informed TransformERs), editorial fit derived from PubMed editorial activity, and corresponding author publication history. JournalMatch also incorporates manuscript word count compatibility checks against known journal limits. The tool is fully stateless, stores no user data, and implements multiple cybersecurity safeguards. It is deployable both locally and on Hugging Face Spaces at no cost. This paper describes the system architecture, scoring methodology, privacy design, and security implementation.",
          size: 22, font: "Times New Roman", italics: true
        })]
      }),

      rule(),

      // ── 1. Introduction ───────────────────────────────────────────────────────
      h1("1. Introduction"),
      body("Choosing the right journal for a manuscript submission is one of the least discussed yet most consequential decisions in academic publishing. A poor choice can result in rapid desk rejection, months of delay, and in some cases submission to a predatory or low-impact outlet. For experienced researchers, this choice is often intuitive — built over years of reading, reviewing, and publishing within a field. For early-career scientists, those entering a new subfield, or those working on highly interdisciplinary topics, the decision is substantially harder."),
      gap(80),
      body("The biomedical literature now spans tens of millions of articles across thousands of journals. Manually surveying editorial scope, acceptance rates, submission timelines, open-access policies, and author processing charges (APCs) for even a shortlist of candidate journals is a significant time investment. Tools that automate part of this process are therefore of practical value."),
      gap(80),
      body("Existing solutions such as the Journal/Author Name Estimator (JANE) use term-frequency approaches to match an abstract against the MEDLINE database. While effective for mature research areas, frequency-based methods struggle when an abstract describes genuinely novel work — by definition, the vocabulary of a novel finding may not yet appear in the indexed literature at meaningful frequency. Embedding-based semantic similarity, by contrast, can capture conceptual relatedness even when surface terminology differs."),
      gap(80),
      body("We present JournalMatch, a web-based tool designed to address these limitations. JournalMatch accepts a manuscript abstract and corresponding author name, retrieves candidate papers from OpenAlex using BM25 search, re-ranks them using SPECTER embeddings, and combines semantic similarity with editorial activity and author history signals to produce a scored, ranked list of recommended journals. The results are presented with visualisations of score breakdowns, word count compatibility, acceptance rates, and estimated submission-to-publication timelines."),

      // ── 2. Background ─────────────────────────────────────────────────────────
      h1("2. Background and Related Work"),
      body("JANE (Drees et al., 2009) is the most widely used journal recommendation tool in biomedicine. It queries MEDLINE and returns journals ranked by term overlap with the submitted abstract. JANE is web-based, freely available, and widely cited. Its primary limitation is its reliance on the Naive Bayes classifier and term frequency, which reduces its effectiveness for interdisciplinary or emerging-topic manuscripts."),
      gap(80),
      body("JournalGuide (Research Square) and Edanz Journal Selector offer broader databases but require registration, may store user data, and their matching algorithms are not publicly documented. Several publisher-specific tools (Elsevier Journal Finder, Springer Journal Suggester) are available but restricted to their own portfolio."),
      gap(80),
      body("SPECTER (Cohan et al., 2020) is a transformer model pretrained on scientific papers using a citation-informed objective, such that papers citing each other are pulled closer in embedding space. This makes SPECTER particularly suitable for scientific similarity tasks: two papers describing the same phenomenon with different terminology will be embedded close together. SPECTER has demonstrated state-of-the-art performance on paper similarity benchmarks and is available via the sentence-transformers library."),
      gap(80),
      body("OpenAlex (Priem et al., 2022) is an open, fully free scholarly database covering over 240 million works with programmatic API access. It provides abstracts in an inverted-index format, journal metadata including h-index, impact factor estimates, open-access status, APCs, and topic classifications. OpenAlex was selected over PubMed for primary paper retrieval because it offers broader interdisciplinary coverage and structured journal metadata."),

      // ── 3. System Architecture ─────────────────────────────────────────────────
      h1("3. System Architecture"),
      h2("3.1 Overview"),
      body("JournalMatch consists of a Python Flask backend and a single-page HTML/CSS/JavaScript frontend. The backend exposes one primary endpoint: POST /api/analyze, which accepts a JSON payload containing the abstract, optional corresponding author name, and optional manuscript word count. All processing occurs in-process; no database is used and no data is persisted between requests."),
      gap(80),
      body("The application is deployable in two configurations: (1) locally, via a one-click batch or shell script that installs dependencies and launches a browser, and (2) on Hugging Face Spaces via a Dockerfile that pre-caches the SPECTER model during image build, eliminating cold-start delays."),

      h2("3.2 Frontend"),
      body("The frontend is implemented as a single self-contained HTML file served by Flask from a static directory. It uses Chart.js 4 for a horizontal stacked bar chart showing score component breakdowns for the top ten journals, SVG score rings for individual journal cards grouped by recommendation tier (High Chance, Moderate Chance, Low Chance), a timeline visualisation showing estimated weeks from submission to publication, and a sortable requirements table with acceptance rates, word limits, open-access status, APCs, and submission links."),
      gap(80),
      body("A five-step animated loading sequence shows users which processing stage is currently active during the typically 15-30 second analysis window. A usage counter displays the number of analyses performed since deployment, and a separate visitor counter tracks page loads. Both counters are stored server-side with no user identifiers."),

      h2("3.3 Backend"),
      body("The backend is implemented in Python 3.12 using Flask 3.0. The SPECTER sentence-transformer model is loaded once at module startup and reused for all subsequent requests, avoiding repeated disk reads. OpenAlex and PubMed are queried via the requests library with a descriptive User-Agent header per API best practice. All external network calls implement retry logic and timeouts."),

      // ── 4. Methods ────────────────────────────────────────────────────────────
      h1("4. Scoring Methodology"),
      body("The total score for each journal is computed as a weighted sum of three components, each normalised to a fixed maximum:"),
      gap(80),

      // Scoring table
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3800, 2000, 3560],
        rows: [
          new TableRow({
            children: [
              cell("Component", "D5E8F0", true, 3800),
              cell("Weight", "D5E8F0", true, 2000),
              cell("Data Source", "D5E8F0", true, 3560)
            ]
          }),
          new TableRow({ children: [cell("Abstract semantic similarity", null, false, 3800), cell("70 points", null, false, 2000), cell("OpenAlex + SPECTER", null, false, 3560)] }),
          new TableRow({ children: [cell("Editorial / call-for-papers fit", null, false, 3800), cell("20 points", null, false, 2000), cell("PubMed E-utilities", null, false, 3560)] }),
          new TableRow({ children: [cell("Corresponding author history", null, false, 3800), cell("10 points", null, false, 2000), cell("PubMed author search", null, false, 3560)] }),
          new TableRow({ children: [cell("Total", "EAF4D5", true, 3800), cell("100 points", "EAF4D5", true, 2000), cell("", "EAF4D5", false, 3560)] })
        ]
      }),
      gap(160),

      h2("4.1 Candidate Paper Retrieval"),
      body("The user's abstract is sent to the OpenAlex Works API as a BM25 full-text search query. To ensure retrieval breadth for novel topics, the query is performed over the full abstract text. Up to 200 papers are retrieved across four pages, filtered to journal articles with available abstracts published after 2015. OpenAlex returns abstracts in an inverted-index format ({word: [position, ...]}) which is reconstructed into plain text before embedding."),
      gap(80),
      body("Privacy note: the first portion of the abstract text is transmitted to OpenAlex servers as the BM25 query. OpenAlex is a non-profit open database operated by OurResearch; they likely log API requests as any web server does, but do not sell or monetise query data. This is disclosed to users in the application interface."),

      h2("4.2 SPECTER Semantic Similarity (70 points)"),
      body("The SPECTER model (allenai-specter, ~0.4 GB) converts both the user abstract and each retrieved paper abstract into a 768-dimensional dense vector. Embeddings are L2-normalised, so cosine similarity is equivalent to the dot product. The user abstract is prefixed with the SPECTER separator token [SEP] per the model's intended usage."),
      gap(80),
      body("For each journal represented in the retrieved papers, the mean cosine similarity of the top five most similar papers is computed. This aggregation reduces noise from a single highly similar but potentially unrepresentative paper. The raw similarity scores (range 0.0-1.0) are scaled to a 0-70 point range by multiplying by 70."),
      gap(80),
      body("The two-stage design (broad BM25 retrieval followed by dense re-ranking) is well-established in information retrieval. It allows the sparse retrieval stage to cast a wide net while the dense embedding stage applies more nuanced semantic comparison. This is particularly beneficial for novel or interdisciplinary abstracts where keyword overlap with the literature is sparse."),

      h2("4.3 Editorial Fit Scoring (20 points)"),
      body("For each candidate journal, PubMed is queried for recent (2023-2026) publications of types editorial, comment, perspectives, or letter that contain keywords extracted from the user's abstract. The keyword extraction uses term-frequency analysis to identify the 10 most informative non-stopword terms from the abstract. A higher count of recent editorial-type publications matching these terms indicates that the journal is actively engaged with the research area, which is a practical signal of receptiveness to submissions on that topic."),
      gap(80),
      body("Scores are logarithmically scaled: 0 matching editorials yields 0 points; 1-3 yields up to 10 points; 4 or more yields the full 20 points. This prevents a single journal with very high editorial activity from dominating while still rewarding meaningful engagement."),

      h2("4.4 Corresponding Author History (10 points)"),
      body("The tool queries PubMed for publications by the corresponding (last) author in each candidate journal. A binary signal is used: if the author has previously published in the journal, 7 points are awarded. No points are awarded otherwise. The asymmetric weighting reflects the empirical observation that corresponding author history is informative but not determinative of fit."),
      gap(80),
      body("The first author field was removed from the interface in version 1.1 following user feedback that it added friction without meaningful additional signal, since corresponding authorship is the primary editorial relationship in most biomedical journals."),

      h2("4.5 Score Normalisation and Categorisation"),
      body("Raw total scores are normalised such that the top-scoring journal is scaled to approximately 88 points. This prevents a trivially low-confidence result from being presented as a high-confidence recommendation. Results are re-sorted by descending total score after normalisation, as per-component caps (similarity capped at 70, editorial at 20, author history at 10) applied during normalisation can shift relative ordering. Journals are then categorised:"),
      bullet("High Chance: normalised score >= 65"),
      bullet("Moderate Chance: normalised score 45-64"),
      bullet("Low Chance: normalised score < 45"),
      gap(80),
      body("The top 25 candidate journals are scored and up to 5 from each tier are returned (up to 15 total). Tier membership reflects absolute score thresholds, not relative ranking, so for a well-studied research area all returned journals may legitimately fall in the High Chance tier. This is intentional: artificially forcing results into lower tiers would misrepresent genuine match quality."),

      h2("4.6 Predatory Journal Filtering"),
      body("Results are filtered against a blocklist of known predatory and low-credibility publishers compiled from Beall's List, Retraction Watch data, and community consensus. Publishers flagged include OMICS International, iMedPub, Austin Publishing Group, Crimson Publishers, Longdom Publishing, and approximately 20 additional entities. Publishers that are debated in the community but widely used by legitimate researchers (e.g. MDPI, Frontiers) are not blocked. The blocklist is based on knowledge available at the time of development and does not automatically update; newly identified predatory publishers may not be excluded."),

      h2("4.7 Word Count Compatibility"),
      body("JournalMatch maintains a reference dictionary of approximately 60 major biomedical journals including their typical manuscript word limits, acceptance rates, estimated submission-to-publication timelines in weeks, verified submission URLs, and open-access status. When the user provides their manuscript word count, each journal result is annotated with a compatibility indicator:"),
      bullet("Fits: manuscript word count is within the journal's limit"),
      bullet("Over limit: manuscript word count exceeds the journal's typical limit"),
      bullet("No data: word limit not available in the reference database"),
      gap(80),
      body("This feature allows users to immediately identify journals that would require significant cutting before submission. When a manuscript exceeds a journal's word limit, the result card displays an explicit advisory message stating the journal's maximum word count, the manuscript's actual word count, and a prompt to consider cutting before submission. When the manuscript is within the limit, the card confirms fit and displays the limit for reference. Word count compatibility does not affect the numerical score; it is presented as a separate practical advisory. Submission URLs in the reference dictionary are verified against current journal author-instruction pages; known outdated URLs (e.g. legacy paths for Blood, PNAS, Diabetes, and Genome Research) have been corrected to current endpoints."),

      // ── 5. Privacy and Security ───────────────────────────────────────────────
      h1("5. Privacy and Security"),
      h2("5.1 Data Handling"),
      body("JournalMatch is stateless by design. No abstract text, author names, or analysis results are stored on disk or in memory beyond the duration of a single request. No database is used. The only persistent state is an aggregate analysis counter (total number of analyses run) and a visitor counter, stored as a JSON file. These counters contain no user-identifying information."),
      gap(80),
      body("HTTP privacy headers are applied to all responses: Cache-Control: no-store prevents browser caching of results pages; Referrer-Policy: no-referrer prevents abstract text leaking via HTTP referrer headers. The X-Frame-Options header is intentionally omitted: Hugging Face Spaces embeds the application across origins (huggingface.co embeds an iframe served from username.hf.space), meaning any iframe restriction (DENY or SAMEORIGIN) prevents the app from rendering. For private deployments, clickjacking protection is instead provided by the Hugging Face platform authentication layer, which restricts access to authorised users only."),

      h2("5.2 Input Validation and Rate Limiting"),
      body("The /api/analyze endpoint implements: (1) a rate limiter permitting a maximum of 10 requests per minute per IP address, enforced via an in-memory thread-safe counter with no IP address logging; (2) a maximum abstract length of 8,000 characters; (3) control character stripping from all text inputs; (4) author name field restricted to safe characters (letters, digits, spaces, and common punctuation). Error responses return generic messages only and never expose internal exception details or stack traces."),

      h2("5.3 Frontend Security"),
      body("All data from external sources (OpenAlex journal metadata, PubMed results) that is inserted into the DOM is HTML-escaped via a custom esc() helper function that creates a text node and reads its innerHTML, preventing XSS injection. All URLs used as href attributes are validated by a safeUrl() function that checks for http:// or https:// protocol before insertion, blocking javascript: protocol injection. All external links carry rel=\"noopener noreferrer\". Subresource integrity (SRI) for CDN-hosted dependencies (Chart.js, jsPDF) is recommended for production deployment."),

      h2("5.4 Usage Counters"),
      body("Two counters are maintained: a page view counter incremented on each load of the main page, and an analysis counter incremented on each successful call to /api/analyze. Both are stored in a single JSON file (stats.json). The counters are protected against external manipulation by being accessible only via a read-only /api/stats endpoint; no external party can write to or reset them. No IP addresses, abstracts, or identifying information are associated with these counts."),

      // ── 6. Deployment ─────────────────────────────────────────────────────────
      h1("6. Deployment"),
      body("JournalMatch is designed to run in two modes. In local mode, a platform-specific launcher script (run.bat for Windows, run.sh for macOS/Linux) automatically detects the Python installation, installs dependencies from requirements.txt into the active environment, opens a browser after a delay, and starts the Flask server. A first-run warning informs users that the SPECTER model download is approximately 400 MB."),
      gap(80),
      body("In hosted mode, a Dockerfile builds on python:3.12-slim, installs dependencies, pre-downloads the SPECTER model into the image layer (eliminating cold starts), and exposes port 7860 for Hugging Face Spaces. Environment variable PORT is respected, defaulting to 5000 locally and 7860 in the Docker context. The host is bound to 0.0.0.0 to accept external connections in the container environment."),
      gap(80),
      body("Source code is maintained in a private repository to protect the system design. Deployment to Hugging Face Spaces is via the Files tab upload interface, requiring no git credentials or personal access tokens. The Hugging Face Space is configured as a Docker space with CPU Basic hardware (free tier), which is sufficient for the embedding and API query workload typical of single-user sessions."),

      // ── 7. Discussion ─────────────────────────────────────────────────────────
      h1("7. Discussion and Limitations"),
      body("JournalMatch offers several advantages over existing tools: semantic similarity via SPECTER is more robust than keyword frequency for novel or interdisciplinary manuscripts; the composite scoring framework incorporates editorial activity signals not present in other tools; word count compatibility and timeline estimates are practical pre-submission checks; and the fully stateless, open-source design addresses confidentiality concerns that may deter use of commercial tools for unpublished work."),
      gap(80),
      body("Several limitations should be noted. First, OpenAlex coverage is excellent for major biomedical journals but may be less complete for niche or regional journals. Second, the journal reference database (~60 journals) covers major outlets but does not approach the full landscape of biomedical publishing, which includes thousands of titles. Third, SPECTER embeddings require a one-time download of approximately 400 MB and add 10-15 seconds of inference time per request on CPU hardware. Fourth, editorial fit scoring using PubMed publication types is a heuristic proxy; direct analysis of journal call-for-papers pages would be more precise but requires web scraping that is difficult to maintain at scale."),
      gap(80),
      body("The score normalisation approach, while preventing low-confidence results from being over-interpreted, means that displayed breakdown sub-scores and totals are not directly additive. This will be corrected in a future release. Additionally, the binary author history signal (published/not published) does not capture recency or frequency of prior publications in the journal, which may be informative for editorial bias assessment."),

      // ── 8. Conclusion ─────────────────────────────────────────────────────────
      h1("8. Conclusion"),
      body("JournalMatch is a practical, privacy-preserving tool for journal recommendation that improves on keyword-based approaches by using SPECTER scientific embeddings for semantic matching. Its composite scoring, word count compatibility, acceptance rate data, and timeline estimates address real decisions faced by researchers during the manuscript submission process. Its stateless architecture, open-source codebase, and free deployment options make it accessible without requiring institutional infrastructure. Future development will focus on expanding the journal reference database, correcting score normalisation display, and evaluating recommendation accuracy against researcher-reported submission outcomes."),

      rule(),

      // ── References ────────────────────────────────────────────────────────────
      h1("References"),
      body("Cohan, A., Feldman, S., Beltagy, I., Downey, D., & Weld, D. S. (2020). SPECTER: Document-level Representation Learning using Citation-informed Transformers. Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, 2270-2282.", { size: 20 }),
      gap(80),
      body("Drees, B., & Alber, G. (2009). JANE: Suggesting journals, finding experts. Learned Publishing, 23(1), 76-77.", { size: 20 }),
      gap(80),
      body("Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of the world's research works, authors, venues, institutions, and concepts. arXiv:2205.01833.", { size: 20 }),
      gap(80),
      body("Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing.", { size: 20 }),
      gap(80),
      body("Sayers, E. W., Bolton, E. E., Brister, J. R., Canese, K., Chan, J., Comeau, D. C., et al. (2022). Database resources of the National Center for Biotechnology Information. Nucleic Acids Research, 50(D1), D20-D26.", { size: 20 }),
      gap(80),
      body("OWASP Top Ten. (2021). Open Web Application Security Project. https://owasp.org/www-project-top-ten/", { size: 20 }),
      gap(80),
      body("Hugging Face. (2024). Spaces: ML demos and apps. https://huggingface.co/spaces", { size: 20 }),
      gap(60),

      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400, after: 0 },
        children: [new TextRun({
          text: "This is a vibe coding project. The ideas, design, and domain expertise are by Amulya Shastry. Code generated by Claude Code (Anthropic). AI can make mistakes — verify outputs before relying on them for submission decisions.",
          size: 18, font: "Arial", italics: true, color: "888888"
        })]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("JournalMatch_Paper.docx", buf);
  console.log("Done: JournalMatch_Paper.docx");
});
