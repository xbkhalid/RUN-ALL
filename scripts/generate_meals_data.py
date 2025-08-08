import json
from pathlib import Path
import random

# مسار حفظ الملف
DATA_PATH = Path(__file__).parent.parent / "data" / "meals.json"

# أسماء مطاعم واقعية
restaurant_names = [
    "ماكدونالدز", "كنتاكي", "هارديز", "بيتزا هت", "برجر كنج",
    "صب واي", "فايف جايز", "أبل بيز", "شيك شاك", "بازوكا"
]

# أمثلة للوجبات
meal_names = [
    "برجر دجاج", "ماك تشكن", "برجر لحم", "دجاج مقلي", "بيتزا مارجريتا",
    "شاورما دجاج", "شاورما لحم", "ناغتس دجاج", "سلطة سيزر", "برجر دوبل"
]

# أمثلة للوصف
descriptions = [
    "وجبة لذيذة محضرة بمكونات طازجة",
    "طبق شهي مليء بالنكهات الفريدة",
    "مذاق لا يُقاوم مع تتبيلة خاصة",
    "أعدت بعناية لتمنحك أفضل تجربة طعام",
    "وجبة متكاملة ترضي جميع الأذواق"
]

# أمثلة للتعليقات
restaurant_comments_samples = [
    "الخدمة ممتازة والأكل طازج",
    "أفضل تجربة طعام مررت بها",
    "الأجواء رائعة والموظفون محترفون",
    "التوصيل سريع جدًا والتغليف رائع",
    "الأسعار مناسبة والجودة عالية"
]

meal_comments_samples = [
    "لذيذة جدًا وسأكرر التجربة",
    "الكمية ممتازة والسعر مناسب",
    "النكهة رائعة والمكونات طازجة",
    "أفضل وجبة جربتها منذ وقت طويل",
    "توصيل سريع وخدمة ممتازة"
]

def generate_data():
    data = []
    restaurant_id = 1

    for r_name in restaurant_names:
        restaurant_rating = round(random.uniform(3.5, 5), 1)  # تقييم المطعم
        restaurant_comments = random.sample(restaurant_comments_samples, 4)

        meals = []
        for i in range(5):  # لكل مطعم 5 وجبات
            meal_name = random.choice(meal_names)
            description = random.choice(descriptions)
            rating = round(random.uniform(3.5, 5), 1)
            price = random.randint(15, 60)
            comments = random.sample(meal_comments_samples, 3)

            meals.append({
                "id": i + 1,
                "name": meal_name,
                "description": description,
                "comments": comments,
                "rating": rating,
                "price": price
            })

        data.append({
            "restaurant_id": restaurant_id,
            "restaurant_name": r_name,
            "restaurant_rating": restaurant_rating,
            "restaurant_comments": restaurant_comments,
            "meals": meals
        })

        restaurant_id += 1

    return data

if __name__ == "__main__":
    dataset = generate_data()
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ تم إنشاء ملف البيانات: {DATA_PATH}")
