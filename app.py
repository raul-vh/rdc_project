import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import duckdb
import plotly.express as px

load_dotenv()
url = os.getenv('GOOGLESHEETS_URL')

def connect_to_google_docs():
    """
    Connect to google docs sheet with survey results using duckdb.
    Returns dataframe.
    """
    try:
        df = duckdb.sql(
            f"SELECT * FROM read_csv_auto('{url}')").df()
    except Exception as exeption:
        print(str(exeption))
    return df

if __name__ == "__main__":
    df = connect_to_google_docs()
    st.set_page_config(page_title="Onderzoek wachtwoordgebruik en digitale veiligheid", page_icon=":bar_chart:", layout="wide")
    st.write(df)
    st.header("Structuur van dit digitaal instrument.")
    st.write("**Inleiding:** Empirische beschrijving van het voorbeeld.")
    st.write("**De bedreigingen:** Welke bedreigingen zijn er? Hoe goed zijn mensen nu beveiligd tegen deze?")
    st.write("**De oplossingen:** Welke oplossingen zijn er? Waarom zijn ze nodig? *Hier bespreken we wat de effecten zijn op de veiligheid*")
    st.write("**Welke oplossing past bij mij?** *Hier gaan we proberen te verklaren waarom mensen bepaald gedrag vertonen. De schaal van veiligheid vs gebruiksgemak.*")
