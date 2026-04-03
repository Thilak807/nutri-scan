# NutriScan AI Web App

NutriScan AI is a Flask + Bootstrap web application that helps users make healthier food choices.
Users can upload a food image or enter a food name, then get nutrition details, health scoring, and dietary suggestions.

## Features

- Upload food image with drag-and-drop support
- Manual food name input
- AI-based food recognition using MobileNetV2 (TensorFlow)
- Nutrition lookup via USDA API (when key is configured)
- Local nutrition fallback dataset (works without API key)
- Health rating engine: Healthy / Moderate / Unhealthy
- Dietary suggestion engine
- SQLite history tracking
- Optional admin dashboard for usage analytics
- Responsive mobile-friendly UI

## Project Structure

nutriscan_ai_web/
- app.py
- model.py
- utils.py
- requirements.txt
- templates/
  - base.html
  - index.html
  - upload.html
  - result.html
  - admin.html
- static/
  - css/styles.css
  - js/main.js
  - images/
  - uploads/

## Setup

1. Open a terminal in this folder:

```bash
cd nutriscan_ai_web
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure optional environment variables:

```bash
# Windows PowerShell example
$env:USDA_API_KEY="your_usda_api_key"
$env:FLASK_SECRET_KEY="change-me"
```

5. Run the app:

```bash
python app.py
```

6. Open in browser:

- http://127.0.0.1:5000

## Notes

- If `USDA_API_KEY` is not provided, the app uses a local nutrition fallback dataset.
- TensorFlow model weights are downloaded automatically on first run.
- Uploaded images are stored in `static/uploads/`.
- History data is stored in `nutriscan.db`.

## Future Enhancements

- User authentication and personalized history
- Barcode scanner integration
- Multi-food detection from one image
- Meal planner and calorie targets
- Diet chatbot assistant
