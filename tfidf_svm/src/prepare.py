# src/prepare.py
import pandas as pd
import re
import os

RAW_PATH = os.path.join("data", "tickets.csv")
PROCESSED_PATH = os.path.join("data", "processed.csv")

def clean_text(text):
    """Clean and anonymize the ticket text."""
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"\S+@\S+", "[EMAIL]", text)      # remove emails
    text = re.sub(r"http\S+", "[URL]", text)        # remove URLs
    text = re.sub(r"\d+", "[NUM]", text)            # remove numbers
    text = re.sub(r"[^a-zA-Z\u0600-\u06FF\s]", " ", text)  # keep arabic+latin
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    print("📂 Loading dataset from:", RAW_PATH)

    # Read CSV safely: comma-separated, skip malformed rows
    df = pd.read_csv(
        RAW_PATH,
        sep=",",                # Explicit separator
        quotechar='"',
        escapechar="\\",
        engine="python",
        on_bad_lines="skip"     # Skip any malformed rows
    )

    # Verify expected columns
    if "Document" not in df.columns or "Topic_group" not in df.columns:
        raise ValueError("Expected columns: 'Document' and 'Topic_group'")

    # Remove duplicates and missing data
    df = df.drop_duplicates(subset="Document")
    df = df.dropna(subset=["Document", "Topic_group"])

    # Clean text
    df["Document"] = df["Document"].apply(clean_text)

    # Remove very short tickets
    df = df[df["Document"].str.len() > 10]

    # Save cleaned dataset
    os.makedirs("data", exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)

    print(f"✅ Cleaned dataset saved at {PROCESSED_PATH}")
    print(f"Rows: {len(df)}, Columns: {list(df.columns)}")

if __name__ == "__main__":
    main()
