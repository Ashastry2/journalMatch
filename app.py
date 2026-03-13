"""
JournalMatch — Biomedical Journal Recommendation Tool
Similarity: SPECTER (scientific paper embeddings) via sentence-transformers
Editorial: PubMed editorial/perspective search
Author history: PubMed last-author scoring (last=7%)
Word count: Manuscript length match against journal word limits
"""

import re
import time
from collections import defaultdict, Counter

import numpy as np
import requests
from flask import Flask, request, jsonify, send_from_directory

# ── Load SPECTER model once at startup ────────────────────────────────────────
try:
    from sentence_transformers import SentenceTransformer
    print("[JournalMatch] Loading SPECTER embedding model...")
    print("[JournalMatch] First run: downloading ~420 MB. After that, loads from local cache.")
    SPECTER = SentenceTransformer("allenai-specter")
    EMBEDDING_OK = True
    print("[JournalMatch] SPECTER model ready.")
except Exception as _e:
    SPECTER = None
    EMBEDDING_OK = False
    print(f"[JournalMatch] WARNING — embedding model unavailable ({_e}). "
          "Using keyword fallback. Install sentence-transformers to enable SPECTER.")

app = Flask(__name__, static_folder="static")

# ── API Endpoints ──────────────────────────────────────────────────────────────
NCBI_BASE   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
OA_BASE     = "https://api.openalex.org"
NCBI_PARAMS = {"tool": "JournalMatch", "email": "journalmatch@example.com"}
OA_HEADERS  = {"User-Agent": "JournalMatch/1.0 (mailto:journalmatch@example.com)"}

# ── Reference Data ────────────────────────────────────────────────────────────
# word_limit: typical maximum words for an original research article
JOURNAL_REF = {
    "new england journal of medicine": {
        "acceptance_rate": "~5%", "timeline_weeks": 5, "word_limit": 3000,
        "submission_url": "https://www.nejm.org/author-center/new-manuscripts",
    },
    "lancet": {
        "acceptance_rate": "~5%", "timeline_weeks": 6, "word_limit": 3000,
        "submission_url": "https://www.thelancet.com/authors",
    },
    "jama": {
        "acceptance_rate": "~5%", "timeline_weeks": 6, "word_limit": 3000,
        "submission_url": "https://jamanetwork.com/journals/jama/pages/instructions-for-authors",
    },
    "bmj": {
        "acceptance_rate": "~7%", "timeline_weeks": 8, "word_limit": 3000,
        "submission_url": "https://www.bmj.com/about-bmj/resources-authors",
    },
    "nature medicine": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 4000,
        "submission_url": "https://www.nature.com/nm/submission-guidelines",
    },
    "nature": {
        "acceptance_rate": "~7%", "timeline_weeks": 12, "word_limit": 3000,
        "submission_url": "https://www.nature.com/nature/for-authors",
    },
    "science": {
        "acceptance_rate": "~7%", "timeline_weeks": 10, "word_limit": 3000,
        "submission_url": "https://www.science.org/content/page/science-information-authors",
    },
    "cell": {
        "acceptance_rate": "~7%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/cell/authors",
    },
    "plos one": {
        "acceptance_rate": "~69%", "timeline_weeks": 6, "word_limit": 10000,
        "submission_url": "https://journals.plos.org/plosone/s/submission-guidelines",
    },
    "nature communications": {
        "acceptance_rate": "~30%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.nature.com/ncomms/submission-guidelines",
    },
    "scientific reports": {
        "acceptance_rate": "~50%", "timeline_weeks": 6, "word_limit": 10000,
        "submission_url": "https://www.nature.com/srep/submission-guidelines",
    },
    "elife": {
        "acceptance_rate": "~14%", "timeline_weeks": 10, "word_limit": 12000,
        "submission_url": "https://elifesciences.org/author-guide",
    },
    "proceedings of the national academy of sciences": {
        "acceptance_rate": "~17%", "timeline_weeks": 8, "word_limit": 6000,
        "submission_url": "https://www.pnas.org/page/authors/submission",
    },
    "pnas": {
        "acceptance_rate": "~17%", "timeline_weeks": 8, "word_limit": 6000,
        "submission_url": "https://www.pnas.org/page/authors/submission",
    },
    "immunity": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/immunity/authors",
    },
    "cancer cell": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/cancer-cell/authors",
    },
    "molecular cell": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/molecular-cell/authors",
    },
    "cell metabolism": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/cell-metabolism/authors",
    },
    "cell host & microbe": {
        "acceptance_rate": "~12%", "timeline_weeks": 10, "word_limit": 7000,
        "submission_url": "https://www.cell.com/cell-host-microbe/authors",
    },
    "cell host and microbe": {
        "acceptance_rate": "~12%", "timeline_weeks": 10, "word_limit": 7000,
        "submission_url": "https://www.cell.com/cell-host-microbe/authors",
    },
    "cell reports": {
        "acceptance_rate": "~25%", "timeline_weeks": 8, "word_limit": 7000,
        "submission_url": "https://www.cell.com/cell-reports/authors",
    },
    "journal of clinical investigation": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 7000,
        "submission_url": "https://www.jci.org/authors/instructions",
    },
    "jci insight": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 7000,
        "submission_url": "https://insight.jci.org/authors/instructions",
    },
    "annals of internal medicine": {
        "acceptance_rate": "~5%", "timeline_weeks": 6, "word_limit": 3500,
        "submission_url": "https://www.acpjournals.org/journal/aim/authors",
    },
    "circulation": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.ahajournals.org/journal/circ/author-instructions",
    },
    "jacc": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.jacc.org/author-center",
    },
    "gastroenterology": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.gastrojournal.org/content/authorinfo",
    },
    "gut": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 4500,
        "submission_url": "https://gut.bmj.com/pages/authors",
    },
    "hepatology": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://aasldpubs.onlinelibrary.wiley.com/hub/journal/15273350/homepage/forauthors.html",
    },
    "blood": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.hematology.org/publications/blood/authors",
    },
    "neuron": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/neuron/authors",
    },
    "nature neuroscience": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 4000,
        "submission_url": "https://www.nature.com/neuro/submission-guidelines",
    },
    "journal of neuroscience": {
        "acceptance_rate": "~25%", "timeline_weeks": 8, "word_limit": 15000,
        "submission_url": "https://www.jneurosci.org/content/information-authors",
    },
    "brain": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://academic.oup.com/brain/pages/general-instructions",
    },
    "cancer research": {
        "acceptance_rate": "~25%", "timeline_weeks": 6, "word_limit": 7000,
        "submission_url": "https://aacrjournals.org/cancerres/pages/instructions-for-authors",
    },
    "cancer discovery": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 6000,
        "submission_url": "https://aacrjournals.org/cancerdiscovery/pages/instructions-for-authors",
    },
    "journal of clinical oncology": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://ascopubs.org/jco/authors",
    },
    "annals of oncology": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://www.annalsofoncology.org/authors",
    },
    "nature cancer": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 5000,
        "submission_url": "https://www.nature.com/natcancer/submission-guidelines",
    },
    "american journal of respiratory and critical care medicine": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 4000,
        "submission_url": "https://www.atsjournals.org/page/ajrccm/submission",
    },
    "chest": {
        "acceptance_rate": "~20%", "timeline_weeks": 6, "word_limit": 4000,
        "submission_url": "https://journal.chestnet.org/authors",
    },
    "european respiratory journal": {
        "acceptance_rate": "~18%", "timeline_weeks": 10, "word_limit": 4000,
        "submission_url": "https://erj.ersjournals.com/pages/authors",
    },
    "radiology": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 3500,
        "submission_url": "https://pubs.rsna.org/page/radiology/submission",
    },
    "plos medicine": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 5000,
        "submission_url": "https://journals.plos.org/plosmedicine/s/submission-guidelines",
    },
    "plos biology": {
        "acceptance_rate": "~12%", "timeline_weeks": 10, "word_limit": 7500,
        "submission_url": "https://journals.plos.org/plosbiology/s/submission-guidelines",
    },
    "nature biotechnology": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 4000,
        "submission_url": "https://www.nature.com/nbt/submission-guidelines",
    },
    "nature genetics": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 4000,
        "submission_url": "https://www.nature.com/ng/submission-guidelines",
    },
    "genome biology": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 8000,
        "submission_url": "https://genomebiology.biomedcentral.com/submission-guidelines",
    },
    "genome research": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 8000,
        "submission_url": "https://genome.cshlp.org/misc/ifora.shtml",
    },
    "american journal of human genetics": {
        "acceptance_rate": "~15%", "timeline_weeks": 8, "word_limit": 5500,
        "submission_url": "https://www.cell.com/ajhg/authors",
    },
    "nature chemical biology": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 3500,
        "submission_url": "https://www.nature.com/nchembio/submission-guidelines",
    },
    "journal of experimental medicine": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://rupress.org/jem/pages/manuscript-preparation",
    },
    "nature immunology": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 5000,
        "submission_url": "https://www.nature.com/ni/submission-guidelines",
    },
    "journal of allergy and clinical immunology": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 6000,
        "submission_url": "https://www.jacionline.org/content/authorinfo",
    },
    "diabetes": {
        "acceptance_rate": "~20%", "timeline_weeks": 8, "word_limit": 5000,
        "submission_url": "https://diabetes.diabetesjournals.org/content/information-for-authors",
    },
    "nature metabolism": {
        "acceptance_rate": "~8%", "timeline_weeks": 10, "word_limit": 5000,
        "submission_url": "https://www.nature.com/natmetab/submission-guidelines",
    },
    "cell stem cell": {
        "acceptance_rate": "~10%", "timeline_weeks": 10, "word_limit": 8000,
        "submission_url": "https://www.cell.com/cell-stem-cell/authors",
    },
    "stem cell reports": {
        "acceptance_rate": "~25%", "timeline_weeks": 8, "word_limit": 7000,
        "submission_url": "https://www.cell.com/stem-cell-reports/authors",
    },
}

BIOMEDICAL_STOP = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "into", "through", "during", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "this", "that", "these", "those",
    "we", "our", "their", "its", "which", "who", "when", "where", "how", "all",
    "both", "each", "more", "most", "other", "some", "such", "not", "only", "same",
    "than", "very", "just", "also", "here", "there", "can", "using", "used",
    "study", "studies", "result", "results", "show", "shown", "showed", "found",
    "find", "findings", "data", "analysis", "patients", "patient", "methods",
    "however", "therefore", "thus", "although", "while", "between", "among",
    "after", "before", "within", "without", "significant", "significantly",
    "compared", "associated", "association", "including", "based", "due", "related",
    "relative", "high", "low", "novel", "clinical", "treatment", "therapy", "group",
    "effect", "effects", "level", "levels", "role", "function", "potential",
    "important", "increased", "decreased", "risk", "response", "activity",
    "expression", "model", "type", "mechanism", "mechanisms", "current", "present",
    "suggest", "suggests", "indicate", "indicates", "demonstrate", "demonstrates",
    "report", "reports", "further", "well", "known", "different", "large", "small",
    "number", "total", "single", "multiple", "whether", "either", "case", "cases",
    "specific", "provide", "identify", "identified", "observed", "evaluated",
    "assessed", "performed", "conducted", "investigated", "demonstrated", "revealed",
    "given", "including", "across", "within", "upon",
}


# ── Utility Helpers ────────────────────────────────────────────────────────────

def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", name.lower())).strip()


def extract_keywords(abstract: str, n: int = 10) -> list[str]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z-]{3,}\b", abstract.lower())
    words = [w for w in words if w not in BIOMEDICAL_STOP]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(n)]


def get_ref(journal_name: str) -> dict:
    key = normalize_name(journal_name)
    if key in JOURNAL_REF:
        return JOURNAL_REF[key]
    for ref_key, ref_val in JOURNAL_REF.items():
        if ref_key in key or key in ref_key:
            return ref_val
    return {
        "acceptance_rate": "See journal website",
        "timeline_weeks": None,
        "word_limit": None,
        "submission_url": None,
    }


def compute_word_fit(word_count: int, word_limit: int | None) -> dict:
    """Return fit status for a manuscript word count against a journal's word limit."""
    if not word_count or not word_limit:
        return {"status": "unknown", "label": "—", "pct": None}
    pct = round(word_count / word_limit * 100)
    if word_count <= word_limit:
        if word_count <= word_limit * 0.7:
            return {
                "status": "well_within",
                "label": f"Well within limit ({word_count:,} / {word_limit:,} words)",
                "pct": pct,
            }
        return {
            "status": "fits",
            "label": f"Within limit ({word_count:,} / {word_limit:,} words)",
            "pct": pct,
        }
    over = word_count - word_limit
    return {
        "status": "over",
        "label": f"Exceeds by {over:,} words ({word_count:,} / {word_limit:,} limit)",
        "pct": pct,
    }


# ── SPECTER Embedding Helpers ─────────────────────────────────────────────────

def reconstruct_abstract(inv_idx: dict) -> str:
    """Convert OpenAlex abstract_inverted_index to plain text."""
    if not inv_idx:
        return ""
    pos_map: dict[int, str] = {}
    for word, positions in inv_idx.items():
        for p in positions:
            pos_map[p] = word
    if not pos_map:
        return ""
    return " ".join(pos_map[i] for i in sorted(pos_map))


def fetch_papers_openalex(query: str, n_pages: int = 4) -> list[dict]:
    """Fetch up to n_pages × 50 papers from OpenAlex matching the query."""
    works: list[dict] = []
    for page in range(1, n_pages + 1):
        params = {
            "search": query,
            "filter": (
                "type:article,"
                "primary_location.source.type:journal,"
                "has_abstract:true,"
                "publication_year:>2015"
            ),
            "per_page": 50,
            "page": page,
            "select": "id,title,abstract_inverted_index,primary_location",
        }
        try:
            r = requests.get(f"{OA_BASE}/works", params=params,
                             headers=OA_HEADERS, timeout=30)
            if r.status_code == 200:
                results = r.json().get("results", [])
                works.extend(results)
                if len(results) < 50:
                    break
        except Exception as e:
            print(f"[OpenAlex fetch] page {page}: {e}")
            break
        time.sleep(0.15)
    return works


def fetch_papers_with_abstracts(abstract: str, keywords: list[str]) -> list[dict]:
    """
    Three-query retrieval for robustness with short or novel abstracts:
      1. Primary query: first 500 chars of abstract (BM25 on full text).
      2. Keyword query: always runs to supplement primary results.
      3. Broad keyword query: individual top keywords if still sparse.
    Deduplicates by OpenAlex work ID.
    """
    seen_ids: set[str] = set()
    all_works: list[dict] = []

    # Primary: abstract text (capped at 500 chars to avoid URL length issues)
    primary_query = abstract[:500].strip()
    if primary_query:
        primary = fetch_papers_openalex(primary_query, n_pages=4)
        for w in primary:
            wid = w.get("id", "")
            if wid and wid not in seen_ids:
                seen_ids.add(wid)
                all_works.append(w)

    # Always run keyword query — critical for short abstracts (< 150 words)
    if keywords:
        kw_query = " ".join(keywords[:8])
        supplemental = fetch_papers_openalex(kw_query, n_pages=4)
        for w in supplemental:
            wid = w.get("id", "")
            if wid and wid not in seen_ids:
                seen_ids.add(wid)
                all_works.append(w)

    # Third pass with individual top keywords if still sparse
    if len(all_works) < 30 and keywords:
        for kw in keywords[:4]:
            extra = fetch_papers_openalex(kw, n_pages=2)
            for w in extra:
                wid = w.get("id", "")
                if wid and wid not in seen_ids:
                    seen_ids.add(wid)
                    all_works.append(w)
            if len(all_works) >= 50:
                break

    return all_works


def specter_journal_scores(
    user_abstract: str,
    works: list[dict],
) -> tuple[dict[str, float], dict[str, dict]]:
    """
    Two-stage retrieval:
      1. Encode user abstract + all retrieved paper abstracts with SPECTER.
      2. Compute cosine similarity between user abstract and every paper.
      3. For each journal: take mean of its top-5 paper similarities → journal score.
    """
    texts: list[str] = []
    paper_jids: list[str] = []
    journal_meta: dict[str, dict] = {}

    for work in works:
        inv = work.get("abstract_inverted_index") or {}
        abstract_text = reconstruct_abstract(inv)
        # Lowered threshold so short-text papers still contribute
        if not abstract_text or len(abstract_text) < 10:
            continue

        title = work.get("title") or ""
        specter_text = f"{title} [SEP] {abstract_text}"

        loc = work.get("primary_location") or {}
        src = loc.get("source") or {}
        jid = src.get("id", "")
        if not jid:
            continue

        texts.append(specter_text)
        paper_jids.append(jid)

        if jid not in journal_meta:
            journal_meta[jid] = {
                "name":     src.get("display_name", ""),
                "homepage": src.get("homepage_url", ""),
                "issn":     src.get("issn_l", ""),
                "oa_id":    jid,
            }

    if not texts:
        return {}, {}

    user_text = f"[SEP] {user_abstract}"
    all_texts = [user_text] + texts

    embeddings: np.ndarray = SPECTER.encode(
        all_texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    user_emb  = embeddings[0]
    paper_emb = embeddings[1:]
    sims: np.ndarray = paper_emb @ user_emb

    journal_sim_lists: dict[str, list[float]] = defaultdict(list)
    for i, jid in enumerate(paper_jids):
        journal_sim_lists[jid].append(float(sims[i]))

    journal_scores: dict[str, float] = {}
    for jid, sim_list in journal_sim_lists.items():
        top_k = sorted(sim_list, reverse=True)[:5]
        journal_scores[jid] = float(np.mean(top_k))

    return journal_scores, journal_meta


def keyword_journal_scores_fallback(
    works: list[dict],
) -> tuple[dict[str, float], dict[str, dict]]:
    """Fallback when SPECTER is unavailable: rank journals by BM25 position."""
    journal_weights: dict[str, float] = defaultdict(float)
    journal_meta: dict[str, dict] = {}

    for i, work in enumerate(works):
        loc = work.get("primary_location") or {}
        src = loc.get("source") or {}
        jid = src.get("id", "")
        if not jid:
            continue
        weight = 1.0 / (0.05 * i + 1)
        journal_weights[jid] += weight
        if jid not in journal_meta:
            journal_meta[jid] = {
                "name":     src.get("display_name", ""),
                "homepage": src.get("homepage_url", ""),
                "issn":     src.get("issn_l", ""),
                "oa_id":    jid,
            }

    max_w = max(journal_weights.values()) if journal_weights else 1.0
    journal_scores = {jid: w / max_w for jid, w in journal_weights.items()}
    return journal_scores, journal_meta


# ── PubMed Functions ───────────────────────────────────────────────────────────

def pubmed_search(query: str, retmax: int = 200, sort: str = "relevance") -> list[str]:
    params = {
        **NCBI_PARAMS,
        "db": "pubmed", "term": query,
        "retmax": retmax, "retmode": "json", "sort": sort,
    }
    try:
        r = requests.get(f"{NCBI_BASE}/esearch.fcgi", params=params, timeout=20)
        if r.status_code == 200:
            return r.json().get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        print(f"[PubMed search] {e}")
    return []


def pubmed_summary(ids: list[str]) -> dict:
    if not ids:
        return {}
    params = {
        **NCBI_PARAMS,
        "db": "pubmed", "id": ",".join(ids[:200]), "retmode": "json",
    }
    try:
        r = requests.get(f"{NCBI_BASE}/esummary.fcgi", params=params, timeout=30)
        if r.status_code == 200:
            return r.json().get("result", {})
    except Exception as e:
        print(f"[PubMed summary] {e}")
    return {}


def pubmed_editorial_count(journal_name: str, keywords: list[str]) -> int:
    kw_query = " OR ".join(keywords[:4]) if keywords else ""
    query = (
        f'"{journal_name}"[Journal] AND '
        f'(editorial[pt] OR comment[pt] OR perspectives[pt] OR letter[pt]) AND '
        f'({kw_query}) AND 2023:2026[pdat]'
    )
    params = {**NCBI_PARAMS, "db": "pubmed", "term": query, "retmode": "json", "retmax": 1}
    try:
        r = requests.get(f"{NCBI_BASE}/esearch.fcgi", params=params, timeout=15)
        if r.status_code == 200:
            return int(r.json().get("esearchresult", {}).get("count", 0))
    except Exception as e:
        print(f"[Editorial count] {e}")
    return 0


def pubmed_author_journals(author_name: str) -> set[str]:
    ids = pubmed_search(f"{author_name}[Author]", retmax=100, sort="date")
    time.sleep(0.34)
    if not ids:
        return set()
    summary = pubmed_summary(ids[:100])
    time.sleep(0.34)
    journals: set[str] = set()
    for uid in summary.get("uids", []):
        name = summary.get(uid, {}).get("fulljournalname", "")
        if name:
            journals.add(normalize_name(name))
    return journals


# ── OpenAlex Journal Metadata ─────────────────────────────────────────────────

def openalex_source(source_id: str) -> dict:
    try:
        r = requests.get(f"{OA_BASE}/sources/{source_id}",
                         headers=OA_HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[OpenAlex source] {e}")
    return {}


def openalex_topic_overlap(source_data: dict, keywords: list[str]) -> float:
    topic_words: set[str] = set()
    for topic in source_data.get("topics", []):
        dn = topic.get("display_name", "").lower()
        topic_words.update(re.findall(r"[a-z]{4,}", dn))
    kw_set = set(keywords)
    if not kw_set:
        return 0.0
    return len(kw_set & topic_words) / len(kw_set)


# ── Main Analysis ──────────────────────────────────────────────────────────────

def analyze(abstract: str, last_author: str, word_count: int | None) -> dict:
    keywords = extract_keywords(abstract, n=12)

    # ── Step 1: Retrieve candidate papers (two-query approach) ────────────────
    papers = fetch_papers_with_abstracts(abstract, keywords)
    total_papers = len(papers)

    # ── Step 2: Compute embedding-based journal scores ────────────────────────
    if EMBEDDING_OK and papers:
        raw_scores, oa_meta = specter_journal_scores(abstract, papers)
        similarity_method = "SPECTER"
    elif papers:
        raw_scores, oa_meta = keyword_journal_scores_fallback(papers)
        similarity_method = "keyword_fallback"
    else:
        raw_scores, oa_meta = {}, {}
        similarity_method = "keyword_fallback"

    print(f"[JournalMatch] Similarity method: {similarity_method}, "
          f"{len(raw_scores)} candidate journals from {total_papers} papers")

    if not raw_scores:
        return {"results": [], "keywords": keywords, "total_similar_works": 0,
                "similarity_method": similarity_method}

    # ── Step 3: Author history (last author only, 0–7 pts) ────────────────────
    last_author_journals: set[str] = set()
    if last_author:
        last_author_journals = pubmed_author_journals(last_author)

    # ── Step 4: Select top 15 journals for deep scoring ───────────────────────
    top_jids = sorted(raw_scores, key=lambda x: raw_scores[x], reverse=True)[:15]
    max_raw  = raw_scores[top_jids[0]] if top_jids else 1.0

    # ── Step 5: Score each journal ────────────────────────────────────────────
    results: list[dict] = []

    for jid in top_jids:
        meta     = oa_meta.get(jid, {})
        src_data = openalex_source(jid)
        time.sleep(0.12)
        ref_data = get_ref(meta.get("name", ""))

        # Similarity score (0–70)
        sim_score = (raw_scores[jid] / max_raw) * 70.0

        # Editorial / Call-for-Papers score (0–20)
        ed_count    = pubmed_editorial_count(meta.get("name", ""), keywords[:4])
        time.sleep(0.34)
        ed_score_a  = min(10.0, ed_count * 1.5)
        topic_match = openalex_topic_overlap(src_data, keywords)
        ed_score_b  = topic_match * 10.0
        editorial_score = ed_score_a + ed_score_b

        # Author history (0–10, last author only = 7 pts max)
        norm_name      = normalize_name(meta.get("name", ""))
        last_published = norm_name in last_author_journals
        author_score   = 7 if last_published else 0

        total_score = sim_score + editorial_score + author_score

        # OpenAlex metadata
        stats     = src_data.get("summary_stats", {}) or {}
        h_index   = stats.get("h_index", 0) or 0
        impact_f  = round(stats.get("2yr_mean_citedness", 0) or 0, 2)
        is_oa     = src_data.get("is_oa", False)
        apc_usd   = src_data.get("apc_usd", None)
        homepage  = src_data.get("homepage_url", "") or meta.get("homepage", "")
        publisher = src_data.get("host_organization_name", "Unknown") or "Unknown"
        issn      = src_data.get("issn_l", "") or meta.get("issn", "")
        topics    = [t.get("display_name", "") for t in (src_data.get("topics") or [])[:5]]

        submission_url  = ref_data.get("submission_url") or homepage or ""
        timeline_weeks  = ref_data.get("timeline_weeks")
        acceptance_rate = ref_data.get("acceptance_rate", "See journal website")
        word_limit      = ref_data.get("word_limit")

        # Word count fit
        wc_fit = compute_word_fit(word_count, word_limit)

        results.append({
            "name":                   meta.get("name", "Unknown"),
            "issn":                   issn,
            "publisher":              publisher,
            "homepage":               homepage,
            "submission_url":         submission_url,
            "is_oa":                  is_oa,
            "apc_usd":                apc_usd,
            "h_index":                h_index,
            "impact_factor":          impact_f,
            "topics":                 topics,
            "last_author_published":  last_published,
            "acceptance_rate":        acceptance_rate,
            "timeline_weeks":         timeline_weeks,
            "timeline_label":         f"~{timeline_weeks} weeks" if timeline_weeks else "See journal website",
            "word_limit":             word_limit,
            "word_fit":               wc_fit,
            "similarity_score":       round(sim_score, 1),
            "editorial_score":        round(editorial_score, 1),
            "author_score":           round(author_score, 1),
            "total_score":            round(total_score, 1),
            "similarity_method":      similarity_method,
        })

    # ── Step 6: Normalise and categorise ──────────────────────────────────────
    results.sort(key=lambda x: x["total_score"], reverse=True)

    if results:
        max_score = results[0]["total_score"]
        if max_score > 0:
            scale = 88.0 / max_score
            for r in results:
                r["total_score"]      = round(min(100, r["total_score"]      * scale), 1)
                r["similarity_score"] = round(min(70,  r["similarity_score"] * scale), 1)
                r["editorial_score"]  = round(min(20,  r["editorial_score"]  * scale), 1)
                r["author_score"]     = round(min(10,  r["author_score"]     * scale), 1)

    for r in results:
        s = r["total_score"]
        r["category"] = "high" if s >= 65 else ("moderate" if s >= 45 else "low")

    return {
        "results":             results[:10],
        "keywords":            keywords[:10],
        "total_similar_works": total_papers,
        "similarity_method":   similarity_method,
    }


# ── Flask Routes ───────────────────────────────────────────────────────────────

@app.after_request
def privacy_headers(response):
    """Prevent browsers from caching responses that contain abstract text."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    body        = request.get_json(force=True) or {}
    abstract    = (body.get("abstract") or "").strip()
    last_author = (body.get("last_author") or "").strip()
    word_count  = body.get("word_count")

    if word_count is not None:
        try:
            word_count = int(word_count)
            if word_count <= 0:
                word_count = None
        except (ValueError, TypeError):
            word_count = None

    if not abstract:
        return jsonify({"error": "Abstract is required"}), 400
    if len(abstract) < 50:
        return jsonify({"error": "Please provide a complete abstract (at least a few sentences)"}), 400

    try:
        data = analyze(abstract, last_author, word_count)
        if not data["results"]:
            return jsonify({
                "error": (
                    "No matching journals found. OpenAlex may not have papers indexed "
                    "for this specific topic yet. Try rephrasing key terms in your abstract, "
                    "or check your internet connection and try again."
                )
            }), 404
        return jsonify(data)
    except Exception as exc:
        import traceback; traceback.print_exc()
        return jsonify({"error": f"Analysis error: {exc}"}), 500


if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", debug=debug, port=port)
