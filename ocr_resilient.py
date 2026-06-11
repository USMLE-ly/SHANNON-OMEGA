"""Resilient OCR for Izhar ul-Haq - saves checkpoints incrementally.
Run if /tmp/ocr_izhar.py crashes: python3 ocr_resilient.py
Supports --resume to skip already-processed parts."""

import fitz, os, subprocess, json, re, time, sys, pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz
from collections import Counter

PDFS = [
    ("Part 1", "/tmp/codex-web-uploads/f-Bioi3Z/Kairanvi_Karanawi_Izhar_ul_haq_or_Truth_Revealed_Part_1_1864_1989.pdf"),
    ("Part 2", "/tmp/codex-web-uploads/f-4AAcky/Kairanvi_Karanawi_Izhar_ul_haq_or_Truth_Revealed_Part_2_1864_1989.pdf"),
    ("Part 3", "/tmp/codex-web-uploads/f-sAZw5E/Kairanvi_Karanawi_Izhar_ul_haq_or_Truth_Revealed_Part_3_1864_1989.pdf"),
    ("Part 4", "/tmp/codex-web-uploads/f-ojrrPQ/Kairanvi_Karanawi_Izhar_ul_haq_or_Truth_Revealed_Part_4_1864_1989.pdf"),
]

CHECKPOINT_FILE = "izhar_checkpoint.json"
KB_CHUNKS_FILE = "islamic_books_merged/chunks/all_chunks.json"

# Load existing chunks
with open(KB_CHUNKS_FILE, encoding="utf-8") as f:
    existing = json.load(f)

t0 = time.time()

# Determine which parts already processed
done_sources = set()
if os.path.exists(CHECKPOINT_FILE):
    checkpoint = json.load(open(CHECKPOINT_FILE))
    all_chunks = checkpoint["chunks"]
    done_sources = set(checkpoint.get("done_parts", []))
    print(f"Resumed from checkpoint: {len(all_chunks)} chunks, done: {done_sources}", flush=True)
else:
    all_chunks = []
    checkpoint = {}

for part_name, path in PDFS:
    if part_name in done_sources and "--resume" in sys.argv:
        print(f"Skipping {part_name} (already done)", flush=True)
        continue
    
    if not os.path.exists(path):
        print(f"File not found: {path}", flush=True)
        continue
    
    doc = fitz.open(path)
    print(f"OCR: {part_name} ({doc.page_count} pages)...", flush=True)
    for i in range(doc.page_count):
        page = doc[i]
        pix = page.get_pixmap(dpi=150)
        tp = f"/tmp/ocr_iz_{i}_{part_name[:3]}.png"
        pix.save(tp)
        try:
            r = subprocess.run(["tesseract", tp, "stdout", "-l", "eng", "--psm", "6"],
                              capture_output=True, text=True, timeout=30)
            txt = r.stdout.strip()
        except:
            txt = ""
        if os.path.exists(tp):
            os.unlink(tp)
        if len(txt) > 50:
            clean = re.sub(r'\s+', ' ', txt).strip()
            all_chunks.append({
                "source": "Izhar ul-Haq / Truth Revealed - Rahmatullah Kairanvi (English)",
                "part": part_name,
                "page": i + 1,
                "text": clean,
                "word_count": len(clean.split())
            })
        if (i + 1) % 20 == 0 or i == doc.page_count - 1:
            elapsed = time.time() - t0
            print(f"   p{i+1}/{doc.page_count} | {len(all_chunks)} total | {elapsed:.0f}s", flush=True)
    doc.close()
    
    # Save checkpoint after each part
    done_sources.add(part_name)
    json.dump({"chunks": all_chunks, "done_parts": list(done_sources)}, 
              open(CHECKPOINT_FILE, "w"), ensure_ascii=False)

print(f"\nOCR done: {len(all_chunks)} chunks in {time.time()-t0:.0f}s", flush=True)

# Merge with full KB
all_data = existing + all_chunks
with open(KB_CHUNKS_FILE, "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=1)
print(f"Merged: {len(existing)} + {len(all_chunks)} = {len(all_data)}", flush=True)

# Rebuild TF-IDF
STOPS = ["the","and","for","are","but","not","you","all","any","can","had","her","was","one","our","out","has","have","been","they","them","their","that","this","with","from","which","were","when","where","who","whom","why","how","will","about","into","over","than","then","some","such","only","after","before","between","through","during","more","also","very","well","just","like","said","would","could","should","may","might","shall","being","doing","having","there","these","those","other","من","في","إلى","عن","على","هذا","هذه","ذلك","كان","قد","لن","لم","و","ف","ثم","أو","كل","بعض","غير","ما","لا","هل"]
texts = [c["text"] for c in all_data]
vec = TfidfVectorizer(max_features=18000, stop_words=STOPS, ngram_range=(1,2), token_pattern=r"(?u)\b\w+\b")
matrix = vec.fit_transform(texts)
save_npz("islamic_books_merged/chunks/matrix.npz", matrix)
with open("islamic_books_merged/chunks/tfidf_config.pkl", "wb") as f:
    pickle.dump({"max_features":18000,"stop_words":STOPS,"ngram_range":(1,2),"vocabulary":vec.vocabulary_,"idf":vec.idf_}, f)

for s, count in Counter(c["source"] for c in all_data).most_common():
    words = sum(c["word_count"] for c in all_data if c["source"] == s)
    print(f"  {s[:55]:55s} | {count:4d} | {words:6,d}w", flush=True)
print(f"\n✅ {len(all_data)} total chunks", flush=True)

# Clean checkpoint
if os.path.exists(CHECKPOINT_FILE):
    os.unlink(CHECKPOINT_FILE)
