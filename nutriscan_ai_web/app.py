import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import requests
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from model import FoodClassifier
from utils import (
    calculate_health_rating,
    extract_product_nutrition_from_image,
    fetch_nutrition_data,
    generate_dietary_suggestions,
    get_recent_history,
    get_usage_analytics,
    init_database,
    save_history,
)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
DB_PATH = BASE_DIR / "nutriscan.db"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB

classifier = FoodClassifier()
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
init_database(str(DB_PATH))


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image_from_url(image_url: str) -> Path:
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    extension = "jpg"
    if "png" in content_type:
        extension = "png"
    elif "jpeg" in content_type or "jpg" in content_type:
        extension = "jpg"
    elif "webp" in content_type:
        extension = "webp"

    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}.{extension}"
    save_path = UPLOAD_FOLDER / filename
    save_path.write_bytes(response.content)
    return save_path


def infer_consumable_name(prediction_details: dict) -> str:
    """Infer a consumable keyword when the model predicts packaging/non-food labels."""
    if not prediction_details:
        return ""

    possible_terms = set()

    raw_label = prediction_details.get("raw_label")
    if raw_label:
        possible_terms.add(str(raw_label).lower())

    for name, _ in prediction_details.get("candidates", []):
        possible_terms.add(str(name).lower())

    for name, _ in prediction_details.get("raw_candidates", []):
        possible_terms.add(str(name).lower())

    keyword_map = {
        "coca cola": ["coke", "cola", "soda", "soft drink"],
        "orange juice": ["juice", "fruit drink", "lemonade", "smoothie"],
        "potato chips": ["chips", "crisps", "snack packet"],
        "chocolate bar": ["chocolate", "candy bar"],
        "instant noodles": ["noodle cup", "instant noodle", "ramen cup"],
        "packaged drink": ["beverage", "drink", "bottle", "can", "carton"],
    }

    for target, keywords in keyword_map.items():
        for term in possible_terms:
            if any(keyword in term for keyword in keywords):
                return target

    return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    food_name = request.form.get("food_name", "").strip()
    image_url_input = request.form.get("image_url", "").strip()
    file = request.files.get("food_image")

    detected_food = ""
    prediction_details = None
    ocr_nutrition = {}
    image_url = None
    query_type = "text"
    input_text = food_name

    if file and file.filename:
        if not allowed_file(file.filename):
            flash("Unsupported file format. Please upload PNG, JPG, JPEG, or WEBP.", "danger")
            return redirect(url_for("upload_page"))

        safe_name = secure_filename(file.filename)
        extension = safe_name.rsplit(".", 1)[1].lower()
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}.{extension}"
        save_path = UPLOAD_FOLDER / filename
        file.save(save_path)

        prediction_details = classifier.predict_food(str(save_path))
        ocr_nutrition = extract_product_nutrition_from_image(str(save_path))
        detected_food = prediction_details.get("food_name", "")
        if not detected_food and ocr_nutrition:
            detected_food = ocr_nutrition.get("food_name", "")
        image_url = url_for("static", filename=f"uploads/{filename}")
        query_type = "image"
        input_text = safe_name
    elif image_url_input:
        try:
            save_path = save_image_from_url(image_url_input)
        except requests.RequestException:
            flash("Could not fetch that image URL. Please try another link or upload a file.", "danger")
            return redirect(url_for("upload_page"))

        prediction_details = classifier.predict_food(str(save_path))
        ocr_nutrition = extract_product_nutrition_from_image(str(save_path))
        detected_food = prediction_details.get("food_name", "")
        if not detected_food and ocr_nutrition:
            detected_food = ocr_nutrition.get("food_name", "")
        image_url = url_for("static", filename=f"uploads/{save_path.name}")
        query_type = "image_url"
        input_text = image_url_input

    if (
        prediction_details
        and not prediction_details.get("is_food", True)
        and not food_name
        and not ocr_nutrition
    ):
        inferred_food = infer_consumable_name(prediction_details)
        if inferred_food:
            detected_food = inferred_food
        else:
            label = prediction_details.get("raw_label", "unknown object")
            flash(
                f"The uploaded image looks like '{label}', not food. Enter a food or product name manually or upload a clearer image.",
                "warning",
            )
            return redirect(url_for("upload_page"))

    if food_name and not detected_food:
        detected_food = food_name

    if not detected_food:
        flash("Please upload an image or type a food name to continue.", "warning")
        return redirect(url_for("upload_page"))

    if ocr_nutrition:
        nutrition = ocr_nutrition
        if food_name:
            nutrition["food_name"] = food_name.title()
        elif detected_food:
            nutrition["food_name"] = detected_food.title()
    else:
        nutrition = fetch_nutrition_data(detected_food)

    health = calculate_health_rating(nutrition)
    suggestions = generate_dietary_suggestions(nutrition, health)

    save_history(
        str(DB_PATH),
        {
            "query_type": query_type,
            "input_text": input_text,
            "detected_food": nutrition["food_name"],
            "calories": nutrition["calories"],
            "protein": nutrition["protein"],
            "carbohydrates": nutrition["carbohydrates"],
            "fats": nutrition["fats"],
            "health_rating": health["label"],
        },
    )

    return render_template(
        "result.html",
        detected_food=nutrition["food_name"],
        nutrition=nutrition,
        health=health,
        suggestions=suggestions,
        prediction=prediction_details,
        image_url=image_url,
    )


@app.route("/admin")
def admin_panel():
    analytics = get_usage_analytics(str(DB_PATH))
    history = get_recent_history(str(DB_PATH), limit=20)
    return render_template("admin.html", analytics=analytics, history=history)


if __name__ == "__main__":
    app.run(debug=True)
