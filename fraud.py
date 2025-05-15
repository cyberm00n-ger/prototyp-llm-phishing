import streamlit as st
import openai
from openai import OpenAI
import os

# Set up OpenAI API key (replace with your own key or use environment variable)
openai_api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
client = OpenAI(api_key=openai_api_key)

# Function to analyze text for fraud/phishing
def detect_fraud(text):
    try:
        prompt = f"""
        Analyze the following text for signs of phishing or fraud. Provide:
        1. A probability score (0-100%) indicating the likelihood of fraud.
        2. A brief explanation of the findings.
        Focus on common phishing indicators like urgent language, suspicious links, requests for personal information, or impersonation.

        Text: "{text}"

        Response format:
        Probability: X%
        Explanation: [Your explanation here]
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in detecting phishing and fraud in text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

# Streamlit app
st.title("Betrugserkennung (Phishing & Co.)")
st.write("Geben Sie den Text (z. B. eine E-Mail oder Nachricht) ein, um ihn auf Phishing oder Betrug zu überprüfen.")

# Text input
user_input = st.text_area("Text hier eingeben:", height=200)

# Button to analyze
if st.button("Text analysieren"):
    if user_input.strip():
        with st.spinner("Analysiere Text..."):
            result = detect_fraud(user_input)
            st.subheader("Ergebnis")
            st.write(result)
    else:
        st.error("Bitte geben Sie einen Text ein.")