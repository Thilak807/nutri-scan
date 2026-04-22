import os
from typing import Dict, List, Tuple
import importlib
import logging

import numpy as np

TENSORFLOW_AVAILABLE = False
logger = logging.getLogger(__name__)


class FoodClassifier:
    """Load a pretrained MobileNet model and infer likely food items."""

    FOOD_HINTS = {
        "banana": ["banana"],
        "apple": ["apple", "granny_smith"],
        "orange": ["orange", "clementine"],
        "strawberry": ["strawberry"],
        "pineapple": ["pineapple"],
        "broccoli": ["broccoli"],
        "cauliflower": ["cauliflower"],
        "cucumber": ["cucumber"],
        "bell pepper": ["bell_pepper"],
        "pizza": ["pizza"],
        "hamburger": ["hamburger", "cheeseburger"],
        "hotdog": ["hotdog"],
        "spaghetti": ["spaghetti", "carbonara"],
        "ice cream": ["ice_cream"],
        "bagel": ["bagel"],
        "french fries": ["french_fries"],
        "guacamole": ["guacamole"],
        "omelette": ["omelet", "egg"],
        "sushi": ["sushi"],
        "salad": ["salad"],
        "sandwich": ["sandwich", "sub", "hoagie"],
        "rice": ["rice"],
        "noodles": ["ramen", "noodle"],
        "chicken": ["chicken", "hen"],
        "fish": ["salmon", "tuna", "fish"],
        "steak": ["steak"],
        "cake": ["cake"],
        "donut": ["dough", "donut"],
    }

    FOOD_KEYWORDS = {
        keyword
        for keywords in FOOD_HINTS.values()
        for keyword in keywords
    }

    FOOD_KEYWORDS.update(
        {
            "plate",
            "dish",
            "meal",
            "soup",
            "bread",
            "pasta",
            "taco",
            "burrito",
            "cookie",
            "dessert",
            "fruit",
            "vegetable",
        }
    )

    def __init__(self) -> None:
        self.model = None
        self._mobilenet_module = None
        self._image_module = None
        self._decode_predictions = None
        self._preprocess_input = None
        self._backend_attempted = False

    def _load_backend(self) -> None:
        global TENSORFLOW_AVAILABLE
        if self._backend_attempted:
            return

        self._backend_attempted = True
        try:
            self._mobilenet_module = importlib.import_module(
                "tensorflow.keras.applications.mobilenet_v2"
            )
            self._image_module = importlib.import_module("tensorflow.keras.preprocessing.image")
            self._decode_predictions = getattr(self._mobilenet_module, "decode_predictions")
            self._preprocess_input = getattr(self._mobilenet_module, "preprocess_input")
            self.model = getattr(self._mobilenet_module, "MobileNetV2")(weights="imagenet")
            TENSORFLOW_AVAILABLE = True
        except KeyboardInterrupt:
            # If model loading is interrupted, continue with filename fallback mode.
            TENSORFLOW_AVAILABLE = False
            self.model = None
            logger.warning("Model loading interrupted. Running in fallback mode.")
        except Exception:
            TENSORFLOW_AVAILABLE = False
            self.model = None

    def _map_imagenet_label_to_food(self, label: str) -> str:
        normalized = label.lower().replace(" ", "_")
        for food_name, keywords in self.FOOD_HINTS.items():
            if any(keyword in normalized for keyword in keywords):
                return food_name
        return label.replace("_", " ")

    def _fallback_from_filename(self, image_path: str) -> Dict:
        name = os.path.basename(image_path).lower()
        for food_name in self.FOOD_HINTS:
            token = food_name.replace(" ", "")
            if food_name in name or token in name:
                return {
                    "food_name": food_name,
                    "confidence": 0.45,
                    "candidates": [(food_name, 0.45)],
                    "source": "filename_heuristic",
                    "is_food": True,
                    "raw_label": food_name,
                }

        return {
            "food_name": "",
            "confidence": 0.0,
            "candidates": [("unknown", 0.0)],
            "source": "fallback",
            "is_food": False,
            "raw_label": "unknown",
        }

    def _is_food_label(self, label: str) -> bool:
        normalized = label.lower().replace(" ", "_")
        return any(keyword in normalized for keyword in self.FOOD_KEYWORDS)

    def predict_food(self, image_path: str, top_k: int = 3) -> Dict:
        """Return normalized food prediction details for a given image."""
        self._load_backend()

        if not self.model or not TENSORFLOW_AVAILABLE:
            return self._fallback_from_filename(image_path)

        img = self._image_module.load_img(image_path, target_size=(224, 224))
        x = self._image_module.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = self._preprocess_input(x)

        preds = self.model.predict(x, verbose=0)
        decoded: List[Tuple[str, str, float]] = self._decode_predictions(preds, top=top_k)[0]

        candidates = []
        raw_candidates = []
        for _, label, score in decoded:
            food_name = self._map_imagenet_label_to_food(label)
            candidates.append((food_name, float(score)))
            raw_candidates.append((label.replace("_", " "), float(score)))

        best_food, best_score = candidates[0]
        best_raw_label, _ = raw_candidates[0]
        is_food = self._is_food_label(best_raw_label) or best_food in self.FOOD_HINTS

        if not is_food and best_score < 0.55:
            return {
                "food_name": "",
                "confidence": best_score,
                "candidates": candidates,
                "raw_candidates": raw_candidates,
                "source": "mobilenetv2",
                "is_food": False,
                "raw_label": best_raw_label,
            }

        return {
            "food_name": best_food,
            "confidence": best_score,
            "candidates": candidates,
            "raw_candidates": raw_candidates,
            "source": "mobilenetv2",
            "is_food": True,
            "raw_label": best_raw_label,
        }
