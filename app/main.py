from fastapi import FastAPI, Query
from qdrant_client import QdrantClient
from sentence_transformers import CrossEncoder, SentenceTransformer
from rapidfuzz import fuzz
from deep_translator import GoogleTranslator
import re

app = FastAPI()

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION = "meals"

qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
re_ranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def translate_to_arabic_if_needed(text: str) -> str:
    # لو فيه أي حرف لاتيني اعتبره يحتاج ترجمة
    if any("a" <= c.lower() <= "z" for c in text):
        try:
            return GoogleTranslator(source='auto', target='ar').translate(text)
        except Exception:
            return text
    return text

def normalize(text):
    if not text:
        return ""
    # حذف ال التعريف وتحويل ى إلى ي
    text = re.sub(r'(^|\s)ال', r'\1', text)
    text = text.replace('ى', 'ي').replace('ة', 'ه').strip().lower()
    return text

def get_embedding(text: str):
    return embedder.encode(text).tolist()

@app.get("/search")
def search_meals(query: str = Query(..., description="ابحث عن وجبة")):
    query = translate_to_arabic_if_needed(query)
    norm_query = normalize(query)
    embedding = get_embedding(query)
    sem_results = qdrant.search(
        collection_name=COLLECTION,
        query_vector=embedding,
        limit=15
    )

    if not sem_results:
        return {"message": f"لم نجد أي نتائج لكلمة '{query}'."}

    perfect_matches = []
    related_by_comments = []
    related_by_description = []
    candidates = []

    for res in sem_results:
        p = res.payload
        m_name = normalize(p.get("meal_name", "") or p.get("name", ""))
        desc = normalize(p.get("description", ""))
        m_comments = [normalize(c) for c in p.get("comments", []) or []]
        r_comments = [normalize(c) for c in p.get("restaurant_comments", []) or []]

        # تطابق قوي مع اسم الوجبة
        if fuzz.token_set_ratio(norm_query, m_name) >= 90:
            perfect_matches.append(res)
            continue
        # تطابق قوي في التعليقات
        elif any(fuzz.token_set_ratio(norm_query, c) >= 85 for c in m_comments + r_comments):
            related_by_comments.append(res)
            continue
        # تطابق قوي في الوصف
        elif fuzz.token_set_ratio(norm_query, desc) >= 85:
            related_by_description.append(res)
            continue
        else:
            candidates.append(res)

    # ترتيب النتائج
    if perfect_matches:
        results = []
        for r in perfect_matches:
            p = r.payload
            results.append({
                "اسم المطعم": p.get("restaurant_name", ""),
                "اسم الوجبة": p.get("meal_name", "") or p.get("name", ""),
                "الوصف": p.get("description", ""),
                "السعر": p.get("price", ""),
                "تقييم المطعم": p.get("restaurant_rating", ""),
                "تقييم الوجبة": p.get("meal_rating", p.get("rating", "")),
                "تعليقات الوجبة": p.get("comments", []),
                "تعليقات المطعم": p.get("restaurant_comments", [])
            })
        return {
            "query": query,
            "results": results
        }

    elif related_by_comments:
        results = []
        for r in related_by_comments:
            p = r.payload
            results.append({
                "اسم المطعم": p.get("restaurant_name", ""),
                "اسم الوجبة": p.get("meal_name", "") or p.get("name", ""),
                "الوصف": p.get("description", ""),
                "السعر": p.get("price", ""),
                "تقييم المطعم": p.get("restaurant_rating", ""),
                "تقييم الوجبة": p.get("meal_rating", p.get("rating", "")),
                "تعليقات الوجبة": p.get("comments", []),
                "تعليقات المطعم": p.get("restaurant_comments", [])
            })
        return {
            "query": query,
            "message": f"لا يوجد وجبة اسمها '{query}' لكن تم العثور على نتائج مرتبطة بالتعليقات.",
            "results": results
        }

    elif related_by_description:
        results = []
        for r in related_by_description:
            p = r.payload
            results.append({
                "اسم المطعم": p.get("restaurant_name", ""),
                "اسم الوجبة": p.get("meal_name", "") or p.get("name", ""),
                "الوصف": p.get("description", ""),
                "السعر": p.get("price", ""),
                "تقييم المطعم": p.get("restaurant_rating", ""),
                "تقييم الوجبة": p.get("meal_rating", p.get("rating", "")),
                "تعليقات الوجبة": p.get("comments", []),
                "تعليقات المطعم": p.get("restaurant_comments", [])
            })
        return {
            "query": query,
            "message": f"لا يوجد وجبة اسمها '{query}' لكن تم العثور على نتائج مرتبطة بالوصف.",
            "results": results
        }

    # اقتراحات دلالية
    candidates_texts = []
    candidates_objs = []
    for r in candidates:
        p = r.payload
        txt = f"{p.get('meal_name', '')} {p.get('description', '')} " + " ".join(p.get("comments", []) + p.get("restaurant_comments", []))
        candidates_texts.append(txt)
        candidates_objs.append(r)
    if not candidates_texts:
        return {
            "query": query,
            "message": f"لم نجد أي نتائج ذات صلة بـ '{query}'."
        }
    pairs = [(query, text) for text in candidates_texts]
    scores = re_ranker.predict(pairs)
    ranked = sorted(zip(scores, candidates_objs), key=lambda x: x[0], reverse=True)
    top_results = []
    for _, r in ranked[:5]:
        p = r.payload
        top_results.append({
            "اسم المطعم": p.get("restaurant_name", ""),
            "اسم الوجبة": p.get("meal_name", "") or p.get("name", ""),
            "الوصف": p.get("description", ""),
            "السعر": p.get("price", ""),
            "تقييم المطعم": p.get("restaurant_rating", ""),
            "تقييم الوجبة": p.get("meal_rating", p.get("rating", "")),
            "تعليقات الوجبة": p.get("comments", []),
            "تعليقات المطعم": p.get("restaurant_comments", [])
        })

    return {
        "query": query,
        "message": f"لم نجد تطابق قوي مع '{query}'، لكن هذه بعض الوجبات المقترحة:",
        "results": top_results
    }
