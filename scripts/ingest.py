from dotenv import load_dotenv
load_dotenv()
# Only index these extensions
ALLOWED_EXTS = {".txt", ".md", ".log", ".pdf", ".docx"}
from api.vectordb import upsert_chunks

import subprocess, shutil
import re, subprocess
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "api"))

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "tnf"

def read_text(path: Path) -> str:
    """Return plain text from .pdf, .docx, .txt, .md (best-effort)."""
    suf = path.suffix.lower()

    # 1) TXT / MD
    if suf in {".txt", ".md", ".log"}:
        try:
            return path.read_text(errors="ignore")
        except Exception:
            return ""

    # 2) DOCX (uses docx2txt)
    if suf == ".docx":
        try:
            import docx2txt  # from api/requirements.txt
            txt = docx2txt.process(path.as_posix())
            return txt or ""
        except Exception as e:
            print(f"[warn] docx read failed for {path.name}: {e}")
            return ""

    # 3) PDF → pdftotext (Poppler)
    if suf == ".pdf":
        if shutil.which("pdftotext") is None:
            print("[warn] 'pdftotext' not found; brew install poppler")
            return ""
        try:
            tmp_txt = Path(str(path) + ".txt")
            # -layout keeps columns reasonably; no overwrite errors if tmp exists
            subprocess.run(
                ["pdftotext", "-layout", path.as_posix(), tmp_txt.as_posix()],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if tmp_txt.exists():
                s = tmp_txt.read_text(errors="ignore")
                if s.strip():
                    return s
        except Exception as e:
            print(f"[warn] pdf read failed for {path.name}: {e}")
        return ""

    # 4) Fallback (treat as text)
    try:
        return path.read_text(errors="ignore")
    except Exception:
        return ""

def chunkify(text: str, size=900, overlap=120):
    text = re.sub(r"\s+"," ", text).strip()
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i+size])
        i += size - overlap
    return out

def chunk_text(text: str, meta: dict, chunk_size: int = 500, overlap: int = 50):
    """
    Split long text into overlapping chunks for embedding.
    Each chunk carries its metadata (like filename).
    """
    chunks = []
    words = text.split()
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append((chunk, meta))
        i += chunk_size - overlap
    return chunks

def main():
    chunks = []
    DATA_DIR = Path("data/tnf")
    ALLOWED_EXTS = {".txt", ".md", ".log", ".pdf", ".docx"}

    for p in sorted(DATA_DIR.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in ALLOWED_EXTS:
            print(f"[skip] {p.name} (unsupported extension)")
            continue

        text = read_text(p)
        if not text.strip():
            print(f"[warn] {p.name} is empty or unreadable.")
            continue
        if "\x00" in text:
            print(f"[skip] {p.name} (binary-like content)")
            continue

        file_chunks = chunk_text(text, meta={"file": p.name})
        chunks.extend(file_chunks)

    print(f"Collected {len(chunks)} chunks from {DATA_DIR}")
    upsert_chunks(chunks)

if __name__ == "__main__":
    main()
