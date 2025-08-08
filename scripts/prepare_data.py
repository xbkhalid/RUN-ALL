import json
from pathlib import Path

# مسار ملف البيانات
DATA_PATH = Path(__file__).parent.parent / "data" / "meals.json"

def load_data():
    """تحميل البيانات من ملف meals.json"""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def prepare_text(meal, restaurant_name, restaurant_comments):
    """دمج البيانات في نص واحد لتحسين الفهم الدلالي"""
    name = meal.get("name", "")
    description = meal.get("description", "")
    meal_comments = " ".join(meal.get("comments", []))
    rest_comments = " ".join(restaurant_comments)
    
    return f"{restaurant_name}. {name}. {description}. {meal_comments}. {rest_comments}"

if __name__ == "__main__":
    data = load_data()
    combined_data = []

    for restaurant in data:
        restaurant_name = restaurant["restaurant_name"]
        restaurant_comments = restaurant["restaurant_comments"]
        restaurant_rating = restaurant["restaurant_rating"]

        for meal in restaurant["meals"]:
            text = prepare_text(meal, restaurant_name, restaurant_comments)
            combined_data.append({
                "id": meal["id"],  # لاحقًا سنعدل ليكون ID فريد لكل وجبة
                "meal_name": meal["name"],
                "description": meal["description"],
                "price": meal["price"],
                "meal_rating": meal["rating"],
                "restaurant_name": restaurant_name,
                "restaurant_rating": restaurant_rating,
                "combined_text": text
            })

    # عرض مثال للتأكد
    for item in combined_data[:3]:
        print("------")
        print(f"اسم المطعم: {item['restaurant_name']}")
        print(f"اسم الوجبة: {item['meal_name']}")
        print(f"النص المجهز: {item['combined_text']}")
