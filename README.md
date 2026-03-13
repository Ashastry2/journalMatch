---
title: JournalMatch
emoji: 🔬
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# JournalMatch

**AI-powered journal recommendation for biomedical scientists.**

Paste your abstract and author names — JournalMatch retrieves 200 semantically similar published papers using the [SPECTER](https://allenai.org/blog/specter) scientific embedding model, then scores journals on three criteria:

| Component | Weight |
|---|---|
| Abstract similarity (SPECTER cosine) | 70 % |
| Editorial / call-for-papers activity (PubMed) | 20 % |
| Author publication history | 10 % |

Results show a scored bar chart, acceptance rates, submission-to-publication timelines, and direct submission links for the top 10 journals.

**Privacy first** — your abstract is never stored or logged. The app is fully stateless.

> **This is a vibe coding project. This app was made using the ideas and suggestions by Amulya Shastry but coded by Claude Code. Please use this tool with the understanding that AI can make mistakes.**

---

## Try it online

> [Live app on Hugging Face Spaces](https://huggingface.co/spaces/YOUR_HF_USERNAME/journalmatch) ← replace with your Space URL after deployment

---

## Run locally

### Prerequisites

- Python 3.9 or newer — download from [python.org](https://www.python.org/downloads/)
- Internet connection (first run downloads the ~500 MB SPECTER model once)

### Windows (one double-click)

1. Clone or download this repository as a ZIP and unzip it.
2. Double-click **`run.bat`**.

The script finds Python automatically, installs all dependencies, and opens your browser at `http://localhost:5000`.

> **First-run note:** downloading the SPECTER model takes 5–15 minutes depending on your connection. Subsequent launches are instant.

### macOS / Linux

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/journalmatch.git
cd journalmatch
bash run.sh
```

### Manual install (any OS)

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/journalmatch.git
cd journalmatch
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` in your browser.

---

## How to use

1. Paste your abstract into the text box.
2. Enter the first author name and last (corresponding) author name.
3. Click **Analyze**.
4. Wait ~30–60 seconds while the app fetches papers and computes embeddings.
5. Review the ranked journals, timeline, and submission links.

---

## Score interpretation

| Category | Score range | Meaning |
|---|---|---|
| **High Chance** | 65 – 100 | Strong topical and author-history fit |
| **Moderate Chance** | 45 – 64 | Good fit; worth submitting |
| **Low Chance** | 0 – 44 | Possible stretch target |

---

## Deploy to Hugging Face Spaces (free)

1. Create a free account at [huggingface.co](https://huggingface.co).
2. Click **New Space** → choose **Docker** as the SDK.
3. Push this repository to the Space:

```bash
git remote add hf https://huggingface.co/spaces/YOUR_HF_USERNAME/journalmatch
git push hf main
```

The Dockerfile pre-caches the SPECTER model during the image build, so the first request is fast. The Space runs on Hugging Face's free CPU tier.

---

## Project structure

```
journalmatch/
├── app.py              # Flask backend + scoring logic
├── static/
│   └── index.html      # Single-page frontend (HTML + CSS + JS)
├── requirements.txt    # Python dependencies
├── run.bat             # Windows one-click launcher
├── run.sh              # macOS/Linux launcher
├── Dockerfile          # Hugging Face Spaces deployment
└── README.md
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found on Windows | Install from [python.org](https://www.python.org/downloads/) and check "Add Python to PATH" |
| First run takes very long | Normal — SPECTER (~500 MB) downloads once to `~/.cache/huggingface` |
| Port 5000 already in use | Set `PORT=5001 python app.py` |
| No results returned | Try a longer, more specific abstract (100+ words works best) |
| Torch install fails | Run `pip install torch --index-url https://download.pytorch.org/whl/cpu` then retry |

---

## Privacy

- Abstracts are processed in memory only and never written to disk.
- No database, no analytics, no third-party tracking.
- HTTP headers (`Cache-Control: no-store`) prevent browser caching of your abstract.
- **SPECTER embeddings** are computed entirely on the local machine — your abstract text never leaves for this step.
- **OpenAlex** receives the first ~500 characters of your abstract as a search query to find topically similar published papers. OpenAlex is a non-profit open database run by [OurResearch](https://ourresearch.org). They may log API requests like any web server, but they are not a commercial entity and do not monetise your data. The abstract text is sent solely to retrieve relevant comparison papers.
- **PubMed (NCBI)** receives only journal names and extracted keywords — no abstract text.

---

## License

MIT
