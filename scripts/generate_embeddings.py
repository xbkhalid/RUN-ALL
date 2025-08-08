import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# مسارات الملفات
DATA_PATH = Path(__file__).parent.parent / "data" / "meals.json"
OUT_PATH = Path(__file__).parent.parent / "data" / "meals_with_embeddings.json"

# تحميل نموذج التضمين
model = SentenceTransformer("all-MiniLM-L6-v2")

def prepare_text(meal, restaurant_name, restaurant_comments):
    meal_comments = " ".join(meal.get("comments", []))
    rest_comments = " ".join(restaurant_comments)
    return f"{restaurant_name}. {meal.get('name','')}. {meal.get('description','')}. {meal_comments}. {rest_comments}"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

output = []
for restaurant in data:
    restaurant_name = restaurant["restaurant_name"]
    restaurant_comments = restaurant.get("restaurant_comments", [])
    restaurant_rating = restaurant["restaurant_rating"]
    for meal in restaurant["meals"]:
        combined_text = prepare_text(meal, restaurant_name, restaurant_comments)
        embedding = model.encode(combined_text).tolist()
        output.append({
            "id": f"{restaurant_name}_{meal['id']}",
            "meal_name": meal["name"],
            "description": meal["description"],
            "price": meal["price"],
            "meal_rating": meal["rating"],
            "restaurant_name": restaurant_name,
            "restaurant_rating": restaurant_rating,
            "meal_comments": meal.get("comments", []),          # أضف التعليقات هنا
            "restaurant_comments": restaurant_comments,         # أضف تعليقات المطعم هنا
            "embedding": embedding
        })

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ تم حفظ البيانات مع Embeddings في: {OUT_PATH}")
