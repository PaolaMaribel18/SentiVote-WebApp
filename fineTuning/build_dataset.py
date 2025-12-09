# fineTuning/build_dataset.py
import json
import re
import random
from pathlib import Path
from collections import Counter

# --------- CONFIG ---------
INPUT_JSON = Path("../backend/data/corpus_completo.json")  # ajusta si tu ruta es distinta
OUTPUT_JSON = Path("./dataset_politico_auto_2000.json")
OUTPUT_REVIEW_CSV = Path("./dataset_needs_review.csv")

TARGET_N = 2000
MIN_CHARS = 20            # filtra textos muy cortos
SEED = 42
USE_DOUBLE_VOTE = True    # True = RoBERTuito + BETO deben coincidir
CONF_THRESHOLD = 0.60     # confianza mínima para aceptar etiqueta automática
BATCH_SIZE = 32

# Modelos HF
MODEL_PRIMARY = "pysentimiento/robertuito-sentiment-analysis"
MODEL_SECONDARY = "finiteautomata/beto-sentiment-analysis"  # opcional como 2do voto

random.seed(SEED)

# --------- LIMPIEZA / NORMALIZACIÓN ---------
url_re = re.compile(r"https?://\S+|www\.\S+")
mention_re = re.compile(r"@\w+")
rt_re = re.compile(r"\brt\b", re.IGNORECASE)

def normalize_for_dedup(text: str) -> str:
    """Normaliza solo para deduplicar (no destruye demasiado el contenido)."""
    t = text.strip()
    t = url_re.sub("", t)
    t = mention_re.sub("", t)
    t = rt_re.sub("", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()

def extract_texts(corpus):
    """Extrae textos de posts y comentarios según tu estructura."""
    texts = []
    for post in corpus:
        t_post = post.get("texto")
        if t_post:
            texts.append({
                "text": t_post,
                "candidato": post.get("candidato"),
                "fecha": post.get("fecha"),
                "source": "post",
            })
        for c in post.get("comentarios", []):
            t_com = c.get("texto_comentario")
            if t_com:
                texts.append({
                    "text": t_com,
                    "candidato": post.get("candidato"),
                    "fecha": post.get("fecha"),
                    "source": "comment",
                })
    return texts

# --------- PRE-ETIQUETADO AUTOMÁTICO ---------
def load_pipelines():
    from transformers import pipeline
    primary = pipeline("sentiment-analysis", model=MODEL_PRIMARY, truncation=True)
    secondary = None
    if USE_DOUBLE_VOTE:
        secondary = pipeline("sentiment-analysis", model=MODEL_SECONDARY, truncation=True)
    return primary, secondary

def map_label(label_str):
    """Mapea labels HF a tus 3 clases."""
    l = label_str.lower()
    # RoBERTuito suele dar 'NEG', 'NEU', 'POS' o similares
    if "neg" in l:
        return "negative"
    if "neu" in l:
        return "neutral"
    if "pos" in l:
        return "positive"
    # algunos modelos dan LABEL_0/1/2, asumimos orden NEG/NEU/POS
    if l == "label_0": return "negative"
    if l == "label_1": return "neutral"
    if l == "label_2": return "positive"
    return None

def batch_predict(pipe, texts):
    """Predice en batches para ir rápido."""
    outs = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        outs.extend(pipe(batch))
    return outs

# --------- MAIN ---------
def main():
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"No encuentro {INPUT_JSON}. Ajusta INPUT_JSON.")

    print("1) Cargando corpus...")
    corpus = json.loads(INPUT_JSON.read_text(encoding="utf-8"))

    print("2) Extrayendo textos...")
    items = extract_texts(corpus)
    print(f"   Textos brutos: {len(items)}")

    print("3) Filtrando cortos + deduplicando...")
    deduped = []
    seen = set()
    for it in items:
        text = it["text"]
        if not text or len(text) < MIN_CHARS:
            continue
        key = normalize_for_dedup(text)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    print(f"   Textos únicos útiles: {len(deduped)}")

    print("4) Cargando modelos HF...")
    primary, secondary = load_pipelines()

    texts_only = [it["text"] for it in deduped]

    print("5) Prediciendo con modelo principal...")
    pred_primary = batch_predict(primary, texts_only)

    pred_secondary = None
    if USE_DOUBLE_VOTE:
        print("6) Prediciendo con segundo modelo (doble voto)...")
        pred_secondary = batch_predict(secondary, texts_only)

    print("7) Construyendo dataset automático...")
    accepted = []
    needs_review = []

    for idx, it in enumerate(deduped):
        p1 = pred_primary[idx]
        label1 = map_label(p1["label"])
        score1 = float(p1.get("score", 0))

        if label1 is None:
            needs_review.append({**it, "label_auto": None, "score_auto": score1, "reason": "unmapped_label"})
            continue

        if score1 < CONF_THRESHOLD:
            needs_review.append({**it, "label_auto": label1, "score_auto": score1, "reason": "low_conf_primary"})
            continue

        if USE_DOUBLE_VOTE:
            p2 = pred_secondary[idx]
            label2 = map_label(p2["label"])
            score2 = float(p2.get("score", 0))

            if label2 is None or score2 < CONF_THRESHOLD:
                needs_review.append({**it, "label_auto": label1, "score_auto": score1,
                                    "label_2": label2, "score_2": score2, "reason": "low_conf_secondary"})
                continue

            if label1 != label2:
                needs_review.append({**it, "label_auto": label1, "score_auto": score1,
                                    "label_2": label2, "score_2": score2, "reason": "disagreement"})
                continue

        accepted.append({
            "id": f"auto_{idx:06d}",
            "text": it["text"],
            "label": label1,
            "source": it["source"],
            "meta": {
                "candidato": it.get("candidato"),
                "fecha": it.get("fecha")
            }
        })

    print(f"   Aceptados automáticos: {len(accepted)}")
    print(f"   Para revisión mínima: {len(needs_review)}")

    if len(accepted) == 0:
        raise RuntimeError("No se aceptó nada. Baja CONF_THRESHOLD o desactiva USE_DOUBLE_VOTE.")

    print("8) Balanceando y muestreando a TARGET_N...")
    # Balance simple por clase
    by_label = {"negative": [], "neutral": [], "positive": []}
    for a in accepted:
        by_label[a["label"]].append(a)

    for k in by_label:
        random.shuffle(by_label[k])

    per_class = TARGET_N // 3
    final = []
    for k in ["negative", "neutral", "positive"]:
        final.extend(by_label[k][:per_class])

    # Si falta por alguna clase, completa con el resto
    if len(final) < TARGET_N:
        remaining = []
        for k in by_label:
            remaining.extend(by_label[k][per_class:])
        random.shuffle(remaining)
        final.extend(remaining[:TARGET_N - len(final)])

    random.shuffle(final)
    print("   Distribución final:", Counter([x["label"] for x in final]))

    print("9) Guardando JSON final...")
    OUTPUT_JSON.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   -> {OUTPUT_JSON.resolve()}")

    print("10) Guardando CSV de revisión...")
    # CSV muy simple para que corrijas rápido en Excel/Sheets
    import csv
    with OUTPUT_REVIEW_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "text", "candidato", "fecha", "source",
            "label_auto", "score_auto", "label_2", "score_2", "reason"
        ])
        writer.writeheader()
        for r in needs_review:
            writer.writerow({
                "text": r.get("text"),
                "candidato": r.get("candidato"),
                "fecha": r.get("fecha"),
                "source": r.get("source"),
                "label_auto": r.get("label_auto"),
                "score_auto": r.get("score_auto"),
                "label_2": r.get("label_2"),
                "score_2": r.get("score_2"),
                "reason": r.get("reason"),
            })

    print(f"   -> {OUTPUT_REVIEW_CSV.resolve()}")
    print("\nListo. Corrige solo el CSV si quieres mejorar calidad, "
          "y usa el JSON para tu fine-tuning.")

if __name__ == "__main__":
    main()
