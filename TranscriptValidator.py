import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# ----------------------------
# Text Cleaning
# ----------------------------

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

# ----------------------------
# Load Dataset
# ----------------------------

def load_dataset(csv_path):
    df = pd.read_csv(csv_path)

    # Adjust if your column name differs
    if "comment_text" not in df.columns:
        raise ValueError("Dataset must contain 'comment_text' column")

    X = df["comment_text"].astype(str)

    # Toxic labels
    y = df[[
        "toxic", "severe_toxic", "obscene",
        "threat", "insult", "identity_hate"
    ]]

    return X, y

# ----------------------------
# Train Model
# ----------------------------

def train_model(X, y):
    X = X.apply(clean_text)

    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    model = MultiOutputClassifier(LogisticRegression())
    model.fit(X_vec, y)

    return model, vectorizer

# ----------------------------
# Predict
# ----------------------------

def predict_text(model, vectorizer, text):
    text_clean = clean_text(text)
    text_vec = vectorizer.transform([text_clean])
    preds = model.predict(text_vec)[0]

    labels = [
        "toxic", "severe_toxic", "obscene",
        "threat", "insult", "identity_hate"
    ]

    return dict(zip(labels, preds))

# ----------------------------
# Generate PDF
# ----------------------------

def generate_pdf(transcript, predictions, output_path="report.pdf"):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("Transcript Toxicity Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"<b>Transcript:</b> {transcript}", styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>Prediction Results:</b>", styles["Heading2"]))
    content.append(Spacer(1, 10))

    for key, value in predictions.items():
        content.append(Paragraph(f"{key.capitalize()}: {value}", styles["Normal"]))
        content.append(Spacer(1, 6))

    # Final verdict
    overall = "Toxic" if any(predictions.values()) else "Clean"

    content.append(Spacer(1, 12))
    content.append(Paragraph(f"<b>Final Verdict:</b> {overall}", styles["Heading2"]))

    doc.build(content)

# ----------------------------
# Full Pipeline
# ----------------------------

def generate_report(csv_path, transcript, output_path="report.pdf"):
    X, y = load_dataset(csv_path)
    model, vectorizer = train_model(X, y)
    predictions = predict_text(model, vectorizer, transcript)
    generate_pdf(transcript, predictions, output_path)

    return {
        "transcript": transcript,
        "predictions": predictions,
        "output_file": output_path
    }

csv_path = "jigsaw-toxic-comment-train-processed-seqlen128.csv"

transcript = "You are completely useless and stupid"

result = generate_report(csv_path, transcript, "output_report.pdf")

print(result)
