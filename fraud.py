import streamlit as st
import openai
from openai import OpenAI
import base64
from PIL import Image
import io
import json
import os
from cryptography.fernet import Fernet
from PyPDF2 import PdfReader
from datetime import datetime

# File paths for storing the API key, Fernet key, and analysis history
API_KEY_FILE = "api_key.json"
FERNET_KEY_FILE = "fernet_key.key"
HISTORY_FILE = "analysis_history.json"

# Function to generate or load Fernet key
def get_fernet_key():
    if os.path.exists(FERNET_KEY_FILE):
        with open(FERNET_KEY_FILE, "rb") as f:
            return Fernet(f.read())
    else:
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(key)
        return Fernet(key)

# Function to save encrypted API key
def save_api_key(api_key):
    fernet = get_fernet_key()
    encrypted_key = fernet.encrypt(api_key.encode())
    with open(API_KEY_FILE, "w") as f:
        json.dump({"encrypted_key": encrypted_key.decode()}, f)

# Function to load encrypted API key
def load_api_key():
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, "r") as f:
            data = json.load(f)
        fernet = get_fernet_key()
        try:
            decrypted_key = fernet.decrypt(data["encrypted_key"].encode()).decode()
            return decrypted_key
        except Exception:
            return ""
    return ""

# Function to save analysis history
def save_analysis_history(analysis_type, input_data, output_data, filename=None):
    history = load_analysis_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": analysis_type,
        "input": input_data,
        "output": output_data,
        "filename": filename
    }
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# Function to load analysis history
def load_analysis_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Initialize session state for API key
if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = load_api_key()

# Function to initialize OpenAI client
def get_openai_client():
    api_key = st.session_state.openai_api_key or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("Bitte geben Sie einen OpenAI API-Schlüssel in den Einstellungen ein.")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Fehler beim Initialisieren des OpenAI-Clients: {str(e)}")
        return None

# Function to analyze text for fraud/phishing
def detect_fraud_text(text):
    client = get_openai_client()
    if not client:
        return "Kein gültiger OpenAI-Client verfügbar."
    
    try:
        prompt = f"""
        Analysiere den folgenden Text auf Anzeichen von Phishing oder Betrug. Gib:
        1. Eine Wahrscheinlichkeit (0-100%) für Betrug.
        2. Eine kurze Erklärung der Ergebnisse.
        Achte auf typische Phishing-Merkmale wie dringende Sprache, verdächtige Links, Aufforderungen zur Eingabe persönlicher Daten oder Imitation vertrauenswürdiger Quellen.

        Text: "{text}"

        Antwortformat:
        Wahrscheinlichkeit: X%
        Erklärung: [Deine Erklärung hier]
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für die Erkennung von Phishing und Betrug in Texten."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Textanalyse: {str(e)}"

# Function to analyze image for fraud/phishing
def detect_fraud_image(image, filename):
    client = get_openai_client()
    if not client:
        return "Kein gültiger OpenAI-Client verfügbar."
    
    try:
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        prompt = """
        Analysiere das folgende Bild auf Anzeichen von Phishing oder Betrug (z. B. verdächtige E-Mails, gefälschte Websites oder betrügerische Nachrichten). Gib:
        1. Eine Wahrscheinlichkeit (0-100%) für Betrug.
        2. Eine kurze Erklärung der Ergebnisse.
        Achte auf visuelle Hinweise wie gefälschte Logos, Rechtschreibfehler, verdächtige Links oder Aufforderungen zur Eingabe persönlicher Daten.

        Antwortformat:
        Wahrscheinlichkeit: X%
        Erklärung: [Deine Erklärung hier]
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein Experte für die Erkennung von Phishing und Betrug in Bildern."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_str}"}}
                    ]
                }
            ],
            max_tokens=200,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Bildanalyse: {str(e)}"

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip() if text else "Kein Text im PDF gefunden."
    except Exception as e:
        return f"Fehler beim Extrahieren des Textes: {str(e)}"

# Streamlit app
# Display logo at the top
st.image(
    "https://raw.githubusercontent.com/your-username/fraud-detection-app/main/assets/logo.png",
    caption="Fraud Detection App",
    use_column_width=True
)
st.title("Betrugserkennung (Phishing & Co.)")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Textanalyse", "Fotoanalyse", "PDF-Analyse", "Einstellungen", "Historie"])

# Tab 1: Text Analysis
with tab1:
    st.subheader("Textanalyse")
    st.write("Geben Sie den Text (z. B. eine E-Mail oder Nachricht) ein, um ihn auf Phishing oder Betrug zu überprüfen.")
    user_text = st.text_area("Text hier eingeben:", height=200, key="text_input")
    if st.button("Text analysieren"):
        if user_text.strip():
            with st.spinner("Analysiere Text..."):
                result = detect_fraud_text(user_text)
                st.subheader("Ergebnis")
                st.write(result)
                # Save to history
                save_analysis_history("text", user_text, result)
        else:
            st.error("Bitte geben Sie einen Text ein.")

    # Example text
    st.sidebar.header("Beispieltext")
    st.sidebar.write("Testen Sie das Tool mit diesem Beispiel:")
    st.sidebar.code("""
    Sehr geehrter Kunde,
    Ihr Konto wurde gesperrt. Bitte klicken Sie hier [Link] und geben Sie Ihre Zugangsdaten ein, um die Sperre aufzuheben.
    Mit freundlichen Grüßen,
    Ihr Bank-Team
    """)

# Tab 2: Image Analysis
with tab2:
    st.subheader("Fotoanalyse")
    st.write("Laden Sie ein Bild (z. B. einen Screenshot einer E-Mail oder Website) hoch, um es auf Phishing oder Betrug zu überprüfen.")
    uploaded_file = st.file_uploader("Bild auswählen", type=["png", "jpg", "jpeg"], key="image_upload")
    if uploaded_file:
        image = Image.open(uploaded_file)
        filename = uploaded_file.name
        st.image(image, caption="Hochgeladenes Bild", use_column_width=True)
        if st.button("Bild analysieren"):
            with st.spinner("Analysiere Bild..."):
                result = detect_fraud_image(image, filename)
                st.subheader("Ergebnis")
                st.write(result)
                # Save to history
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                save_analysis_history("image", img_str, result, filename)

# Tab 3: PDF Analysis
with tab3:
    st.subheader("PDF-Analyse")
    st.write("Laden Sie eine PDF-Datei (z. B. eine E-Mail oder ein Dokument) hoch, um sie auf Phishing oder Betrug zu überprüfen.")
    uploaded_pdf = st.file_uploader("PDF auswählen", type=["pdf"], key="pdf_upload")
    if uploaded_pdf:
        filename = uploaded_pdf.name
        with st.spinner("Extrahiere Text aus PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_pdf)
        st.text_area("Extrahierter Text", extracted_text, height=200, disabled=True)
        if st.button("PDF analysieren"):
            if extracted_text and not extracted_text.startswith("Fehler"):
                with st.spinner("Analysiere PDF-Inhalt..."):
                    result = detect_fraud_text(extracted_text)
                    st.subheader("Ergebnis")
                    st.write(result)
                    # Save to history
                    save_analysis_history("pdf", extracted_text, result, filename)
            else:
                st.error("Kein analysierbarer Text im PDF gefunden.")

# Tab 4: Settings
with tab4:
    st.subheader("Einstellungen")
    st.write("Geben Sie Ihren OpenAI API-Schlüssel ein. Der Schlüssel wird verschlüsselt gespeichert und bleibt nach Neustart erhalten.")
    api_key_input = st.text_input(
        "OpenAI API-Schlüssel",
        type="password",
        value=st.session_state.openai_api_key,
        help="Der Schlüssel wird nur als Sternchen angezeigt."
    )
    if st.button("API-Schlüssel speichern"):
        if api_key_input:
            st.session_state.openai_api_key = api_key_input
            save_api_key(api_key_input)
            st.success("API-Schlüssel gespeichert!")
        else:
            st.error("Bitte geben Sie einen API-Schlüssel ein.")

# Tab 5: History
with tab5:
    st.subheader("Analyse-Historie")
    st.write("Hier sehen Sie alle bisherigen Analysen mit Eingaben und Ergebnissen.")
    history = load_analysis_history()
    if history:
        for entry in reversed(history):  # Show newest first
            st.markdown(f"**Zeitstempel**: {entry['timestamp']}")
            st.markdown(f"**Typ**: {entry['type'].capitalize()}")
            if entry["filename"]:
                st.markdown(f"**Dateiname**: {entry['filename']}")
            if entry["type"] == "text":
                st.markdown("**Eingabe**:")
                st.text_area("Text", entry["input"], height=100, disabled=True, key=f"text_{entry['timestamp']}")
            elif entry["type"] == "image":
                st.markdown("**Eingabe**:")
                st.image(base64.b64decode(entry["input"]), caption="Hochgeladenes Bild", use_column_width=True)
            elif entry["type"] == "pdf":
                st.markdown("**Eingabe**:")
                st.text_area("Extrahierter Text", entry["input"], height=100, disabled=True, key=f"pdf_{entry['timestamp']}")
            st.markdown("**Ergebnis**:")
            st.text_area("Analyse", entry["output"], height=100, disabled=True, key=f"output_{entry['timestamp']}")
            st.markdown("---")
    else:
        st.info("Keine Analysen in der Historie vorhanden.")