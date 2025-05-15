# app.py
import streamlit as st
import pandas as pd
import altair as alt

st.title("Absatzanalyse in Sekunden")

uploaded = st.file_uploader("CSV hochladen")
if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df.head())

    produkt = st.selectbox("Produkt wählen", df["Produkt"].unique())
    monat   = st.slider("Monat", 1, 12, 1)

    gefiltert = df[(df["Produkt"] == produkt) & (df["Monat"] <= monat)]

    chart = alt.Chart(gefiltert).mark_area().encode(
        x="Monat", y="Umsatz", tooltip=["Monat","Umsatz"]
    )
    st.altair_chart(chart, use_container_width=True)

    st.download_button("CSV herunterladen", gefiltert.to_csv(index=False), "report.csv")