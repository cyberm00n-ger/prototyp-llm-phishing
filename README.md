# prototyp-llm-phishing

Fraud Detection App

A Streamlit-based web application for detecting phishing and fraud in text, images, and PDF documents using the OpenAI API. This app analyzes user-uploaded content to identify suspicious patterns, such as urgent language, fake links, or impersonation, and provides a fraud probability score with explanations.

Features





Text Analysis: Analyze emails, messages, or other text for phishing indicators using OpenAI's gpt-4o-mini model.



Photo Analysis: Detect fraud in screenshots (e.g., fake websites or emails) using OpenAI's gpt-4o vision model.



PDF Analysis: Extract text from PDFs and analyze it for fraud using PyPDF2 and gpt-4o-mini.



Secure API Key Storage: Store your OpenAI API key securely with encryption using the cryptography library.



User-Friendly Interface: Built with Streamlit, featuring tabs for each analysis type and a settings page for API key management.



Deployable on Streamlit Cloud: Easily host the app for public or private use.