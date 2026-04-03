import os
import sqlite3
from datetime import datetime
from typing import Dict, List

import requests


LOCAL_NUTRITION_DATA = {
    "banana": {
        "calories": 89,
        "protein": 1.1,
        "carbohydrates": 22.8,
        "fats": 0.3,
        "fiber": 2.6,
        "sugar": 12.2,
        "sodium": 1,
        "vitamins": "Vitamin B6, Vitamin C, Potassium",
    },
    "apple": {
        "calories": 52,
        "protein": 0.3,
        "carbohydrates": 13.8,
        "fats": 0.2,
        "fiber": 2.4,
        "sugar": 10.4,
        "sodium": 1,
        "vitamins": "Vitamin C, Vitamin K",
    },
    "pizza": {
        "calories": 266,
        "protein": 11.0,
        "carbohydrates": 33.0,
        "fats": 10.0,
        "fiber": 2.3,
        "sugar": 3.8,
        "sodium": 598,
        "vitamins": "Calcium, Vitamin A",
    },
    "hamburger": {
        "calories": 295,
        "protein": 17.0,
        "carbohydrates": 30.0,
        "fats": 14.0,
        "fiber": 1.3,
        "sugar": 5.0,
        "sodium": 414,
        "vitamins": "Vitamin B12, Iron",
    },
    "broccoli": {
        "calories": 35,
        "protein": 2.4,
        "carbohydrates": 7.2,
        "fats": 0.4,
        "fiber": 3.3,
        "sugar": 1.4,
        "sodium": 41,
        "vitamins": "Vitamin C, Vitamin K, Folate",
    },
    "ice cream": {
        "calories": 207,
        "protein": 3.5,
        "carbohydrates": 24.0,
        "fats": 11.0,
        "fiber": 0.7,
        "sugar": 21.0,
        "sodium": 80,
        "vitamins": "Calcium, Vitamin A",
    },
    "mixed food": {
        "calories": 180,
        "protein": 7.0,
        "carbohydrates": 20.0,
        "fats": 8.0,
        "fiber": 2.0,
        "sugar": 6.0,
        "sodium": 220,
        "vitamins": "Not available",
    },
}


def _normalize_food_name(food_name: str) -> str:
    return " ".join(food_name.lower().strip().split())


def _extract_usda_nutrients(food: Dict) -> Dict:
    nutrients = {item.get("nutrientId"): item.get("value") for item in food.get("foodNutrients", [])}

    return {
        "calories": round(float(nutrients.get(1008, 0)), 2),
        "protein": round(float(nutrients.get(1003, 0)), 2),
        "carbohydrates": round(float(nutrients.get(1005, 0)), 2),
        "fats": round(float(nutrients.get(1004, 0)), 2),
        "fiber": round(float(nutrients.get(1079, 0)), 2),
        "sugar": round(float(nutrients.get(2000, 0)), 2),
        "sodium": round(float(nutrients.get(1093, 0)), 2),
        "vitamins": "Depends on product; USDA micronutrients available in full detail.",
    }


def fetch_nutrition_data(food_name: str) -> Dict:
    """Fetch nutrition from USDA API when configured, otherwise use local data."""
    normalized = _normalize_food_name(food_name)
    usda_api_key = os.getenv("USDA_API_KEY", "").strip()

    if usda_api_key:
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {"query": normalized, "pageSize": 1, "api_key": usda_api_key}

        try:
            response = requests.get(url, params=params, timeout=8)
            response.raise_for_status()
            payload = response.json()
            foods = payload.get("foods", [])
            if foods:
                nutrition = _extract_usda_nutrients(foods[0])
                nutrition["food_name"] = foods[0].get("description", food_name)
                nutrition["source"] = "USDA API"
                return nutrition
        except requests.RequestException:
            pass

    fallback = LOCAL_NUTRITION_DATA.get(normalized, LOCAL_NUTRITION_DATA["mixed food"]).copy()
    fallback["food_name"] = food_name.title()
    fallback["source"] = "Local fallback dataset"
    return fallback


def calculate_health_rating(nutrition: Dict) -> Dict:
    score = 100

    if nutrition["calories"] > 300:
        score -= 20
    elif nutrition["calories"] > 200:
        score -= 10

    if nutrition["sugar"] > 15:
        score -= 25
    elif nutrition["sugar"] > 8:
        score -= 10

    if nutrition["sodium"] > 500:
        score -= 20
    elif nutrition["sodium"] > 300:
        score -= 10

    if nutrition["protein"] >= 10:
        score += 10

    if nutrition["fiber"] >= 4:
        score += 10

    score = max(0, min(100, score))

    if score >= 75:
        label = "Healthy"
        color = "success"
    elif score >= 50:
        label = "Moderate"
        color = "warning"
    else:
        label = "Unhealthy"
        color = "danger"

    return {"score": score, "label": label, "color": color}


def generate_dietary_suggestions(nutrition: Dict, health_rating: Dict) -> List[str]:
    suggestions = []

    if nutrition["protein"] >= 12:
        suggestions.append("High protein food. Great for muscle recovery.")
    elif nutrition["protein"] < 5:
        suggestions.append("Low protein. Pair with legumes, eggs, or yogurt.")

    if nutrition["fiber"] < 3:
        suggestions.append("Low fiber detected. Add fruits or vegetables to improve satiety.")

    if nutrition["sugar"] > 12:
        suggestions.append("Reduce sugar intake by limiting dessert portions.")

    if nutrition["sodium"] > 400:
        suggestions.append("High sodium. Balance with water and low-salt foods.")

    if health_rating["label"] == "Healthy":
        suggestions.append("Balanced choice. Keep portions aligned with daily goals.")

    if not suggestions:
        suggestions.append("Nutritional profile looks moderate. Combine with fresh whole foods.")

    return suggestions


def init_database(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_type TEXT NOT NULL,
                input_text TEXT,
                detected_food TEXT NOT NULL,
                calories REAL,
                protein REAL,
                carbohydrates REAL,
                fats REAL,
                health_rating TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_history(db_path: str, item: Dict) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO history (
                query_type, input_text, detected_food, calories, protein,
                carbohydrates, fats, health_rating, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("query_type"),
                item.get("input_text"),
                item.get("detected_food"),
                item.get("calories"),
                item.get("protein"),
                item.get("carbohydrates"),
                item.get("fats"),
                item.get("health_rating"),
                datetime.utcnow().isoformat(timespec="seconds"),
            ),
        )
        conn.commit()


def get_recent_history(db_path: str, limit: int = 10) -> List[Dict]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT *
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_usage_analytics(db_path: str) -> Dict:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        total_queries = conn.execute("SELECT COUNT(*) AS count FROM history").fetchone()["count"]
        image_queries = conn.execute(
            "SELECT COUNT(*) AS count FROM history WHERE query_type IN ('image', 'image_url')"
        ).fetchone()["count"]
        text_queries = conn.execute(
            "SELECT COUNT(*) AS count FROM history WHERE query_type = 'text'"
        ).fetchone()["count"]
        top_food = conn.execute(
            """
            SELECT detected_food, COUNT(*) AS count
            FROM history
            GROUP BY detected_food
            ORDER BY count DESC
            LIMIT 1
            """
        ).fetchone()

    return {
        "total_queries": total_queries,
        "image_queries": image_queries,
        "text_queries": text_queries,
        "top_food": top_food["detected_food"] if top_food else "No data yet",
    }
