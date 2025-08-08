import json
from qdrant_client import QdrantClient, models
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "meals_with_embeddings.json"
COLLECTION_NAME = "meals"
VECTOR_SIZE = 384  # تأكد أنه نفس حجم embedding المستخدم

# الاتصال بـ Qdrant (محلي)
client = QdrantClient(host="localhost", port=6333)

# إعادة إنشاء الـ Collection (سيحذف القديم ويرفع الجديد)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

payloads = []
vectors = []
ids = []
for i, item in enumerate(data):
    vectors.append(item["embedding"])
    ids.append(i + 1)  # أو استخدم item["id"] لو أردت id نصي
    payload = {
        "meal_name": item["meal_name"],
        "description": item["description"],
        "price": item["price"],
        "meal_rating": item["meal_rating"],
        "restaurant_name": item["restaurant_name"],
        "restaurant_rating": item["restaurant_rating"],
        "meal_comments": item.get("meal_comments", []),
        "restaurant_comments": item.get("restaurant_comments", [])
    }
    payloads.append(payload)

# رفع البيانات دفعة واحدة
client.upload_collection(
    collection_name=COLLECTION_NAME,
    vectors=vectors,
    payload=payloads,
    ids=ids,
    batch_size=64,
)

print(f"✅ تم رفع {len(data)} عنصرًا إلى Qdrant في Collection: {COLLECTION_NAME}")
