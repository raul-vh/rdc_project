import os
from dotenv import load_dotenv
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import duckdb
import plotly.express as px
import random
import string

def connect_to_google_docs():
    """
    Connect to google docs sheet with survey results using duckdb.
    Returns dataframe.
    """
    load_dotenv()
    url = os.getenv('GOOGLESHEETS_URL')
    try:
        df = duckdb.sql(
            f"SELECT * FROM read_csv_auto('{url}',ignore_errors=1)").df()
        df = df.drop(labels=['Timestamp', 'Naam', 'E-mail', '[FRD Response ID] DO NOT REMOVE'], axis=1)
    except Exception as exeption:
        print(str(exeption))
    return df

def compute_score_password_usage(df):
    """
    Computes a password usage score based on the first four questions:
    Raakt u wel eens wachtwoorden kwijt?
    Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?
    Gebruikt u een password manager?
    Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)
    """
    points_value_map_1 = {
        'Ja': 0,
        'Nee': 1
    }
    points_value_map_2 = {
        'Ja': 1,
        'Nee': 0,
        'Ik gebruik de password manager in mij browser.': 0.5
    }
    columns_1 = ['Raakt u wel eens wachtwoorden kwijt?',
               'Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?']
    columns_2 = ['Gebruikt u een password manager?',
               'Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)']
    for index in df.index:
        score = 0
        for column in columns_1:
            score += points_value_map_1[df.loc[index][column]]
        for column in columns_2:
            score += points_value_map_2[df.loc[index][column]]
        df.loc[index, 'Score'] = score
    return df

def header():
    """
    Prints header section and description of page
    """
    st.set_page_config(page_title="Onderzoek wachtwoordgebruik en digitale veiligheid", page_icon=":bar_chart:", layout="wide")
    st.header("Wachtwoordgebruik en digitale veiligheid")
    st.write("Welkom op deze informatieve website over wachtwoordgebruik en digitale veiligheid. Wij hopen dat jij met deze kennis en tips jouw digitale veiligheid een boost geeft. \n\n Met vriendelijke groeten, \n\nMike Rumping, John-Anthony Loefstop, Nick Baggerman, Raúl van Harmelen")
    return

def descriptives_survey(df):
    """
    Prints descriptive statistics for the survey resonses:
    Age, Gender, Working status, Life status
    """
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        nbins = df['Leeftijd'].max() - df['Leeftijd'].min()
        fig1 = px.histogram(df,
                        x="Leeftijd",
                        nbins=int(2 * nbins),
                        title="Leeftijdsverdeling van respondenten")
        fig1.update_xaxes(range=[df['Leeftijd'].min(), df['Leeftijd'].max()])
        fig1.update_layout(bargap=0.2)
        st.plotly_chart(fig1, use_container_width=True, theme="streamlit")

        fig3 = px.histogram(df,
                            x="Welke van de volgende categorieën omschrijft het beste uw arbeidssituatie?",
                            title="Arbeidssituatie van respondenten")
        st.plotly_chart(fig3, use_container_width=True, theme="streamlit")
    with col2:
        fig2 = px.pie(df, names="Geslacht", values="Score", title="Geslachtverdeling van respondenten")
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, use_container_width=True, theme="streamlit")

        fig4 = px.histogram(df,
                            x="Welke van de volgende categorieën omschrijft het beste uw levensituatie?",
                            title="Levensituatie van respondenten")
        st.plotly_chart(fig4, use_container_width=True, theme="streamlit")
    return

def vis_oplossingen_sterke_ww(df):
    """
    Prints pie chart for the columns:
    Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?
    Raakt u wel eens wachtwoorden kwijt?
    """
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        pie_chart(df, "Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?")
    with col2:
        pie_chart(df, "Raakt u wel eens wachtwoorden kwijt?")
    return

def vis_oplossingen_pm(df):
    """
    Prints pie chart for the columns:
    Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?
    Raakt u wel eens wachtwoorden kwijt?
    """
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        pie_chart(df, "Gebruikt u een password manager?")
    with col2:
        color_order = ['Ja', 'Ik gebruik de password manager in mij browser.', 'Nee']
        fig1 = px.histogram(df, x="Hoe groot is het probleem van het managen van wachtwoorden voor u, ten opzichte van het grootste probleem in uw leven?", 
                    color="Gebruikt u een password manager?",
                    histfunc="count",
                    color_discrete_sequence=['#dc143c','#cd5c5c', '#ffa07a'],
                    category_orders={"Gebruikt u een password manager?": color_order})

        fig1.update_xaxes(range=[1, 10])
        fig1.update_layout(title_text='Maken mensen die wachtwoorden als probleem zien gebruik van een Password Manager?')
        fig1.update_xaxes(title_text='Groote probleem van het managen van wachtwoorden. (Op schaal van 1 tot 10)')
        fig1.update_yaxes(title_text='Aantal respondenten')
        fig1.update_layout(bargap=0.2)

        st.plotly_chart(fig1, use_container_width=True, theme="streamlit")
    return

def pie_chart(df, column_name, container_with = True):
    """
    Prints pie chart for specific column name
    """
    fig = px.pie(df, names=column_name, values="Score", title=column_name)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    if container_with == True:
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    else:
        st.plotly_chart(fig, theme="streamlit")
    return

def histogram(df, column_name):
    """
    Prints histogram for specific column name
    """
    fig = px.histogram(df, x=column_name, title=column_name, nbins=10, text_auto=True)
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
    return

def password_generator(length):
    """
    Generates a random password
    """
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation

    password = ""
    for x in range(length):
        password += random.choice(uppercase_letters + lowercase_letters + digits + symbols)

    return password

def password_crack_time_checker(password):
    """
    Checks password crack time and returns crack time in seconds.
    Based on the new Nvidia RTX 4090 GPU.
    https://www.tomshardware.com/news/rtx-4090-password-cracking-comparison
    7.6196 * 10^15 guesses a second with a standard hashing algorithm.
    """
    uppercase = [any([1 if c in string.ascii_uppercase else 0 for c in password]), len(string.ascii_uppercase)]
    lowercase = [any([1 if c in string.ascii_lowercase else 0 for c in password]), len(string.ascii_lowercase)]
    digits = [any([1 if c in string.digits else 0 for c in password]), len(string.digits)]
    symbols = [any([1 if c in string.punctuation else 0 for c in password]), len(string.punctuation)]

    length = len(password)

    unique_characters = 0
    if uppercase[0] == 1:
        unique_characters += uppercase[1]
    if lowercase[0] == 1:
        unique_characters += lowercase[1]
    if digits[0] == 1:
        unique_characters += digits[1]
    if symbols[0] == 1:
        unique_characters += symbols[1]

    password_strength = unique_characters ** length
    time_s = password_strength / (2.116558 * 10**12)
    return f"Seconden: {time_s:.2f}, Minuten: {time_s / 60:.2f}, Uren: {time_s / 3600:.2f}, Dagen: {time_s / 3600 / 24:.2f}"

if __name__ == "__main__":
    df = connect_to_google_docs()
    df = compute_score_password_usage(df)
    header()

    # --- HORIZONTAL MENU ---
    selected = option_menu(
        menu_title=None,
        options=["Inleiding", "Bedreigingen", "Oplossingen", "Best practices"],
        icons=["play-fill", "exclamation-triangle", "", "check2-circle"], #speedometer2
        default_index=0,
        orientation="horizontal",
    )
    if selected == "Inleiding":
        with open('text/inleiding.md', 'r') as inleiding:
            st.markdown(inleiding.read())
        st.write(
            f"""
            Om deze vraag te beantwoorden gaan we eerst in op de bedreigingen die er zijn.
            Vervolgens dragen we een aantal mogelijke oplossingen aan.
            We eindigen met de best practicies rondom wachtwoordgebruik die mensen kunnen toepassen.
            Om deze best practices te onderbouwen en om beter te begrijpen welke normen en waarden ten grondslag liggen aan het gedrag van mensen, 
            hebben wij een enquête gemaakt die is ingevuld door {df.index.size} participanten.
            Deze enquête bevat vragen over wachtwoordgebruik, beveiliging van wachtwoorden en persoonlijke meningen over dit onderwerp.
            \n\n
            Laten we beginnen met wat beschrijvende statestiek van deze resultaten.
            \n\n
            ## Beschrijvende statestiek van de enquêteresultaten
            """
        )
        descriptives_survey(df)
    elif selected == "Bedreigingen":
        with open('text/bedreigingen1.md', 'r') as bedreigingen1:
            st.markdown(bedreigingen1.read())
        st.markdown("## Hoe wachtwoorden worden opgeslagen? \n\n Een wachtwoord is feitelijk niets anders dan een combinatie van een gebruikersnaam en een hash. Als je het juiste wachtwoord invoert, krijg je toegang, anders niet.")
        opgeslagen_ww = pd.DataFrame({
            "Username": ["Alice", "Bob"],
            "Password hash": ["5f4dcc3b5aa765d61d8327deb882cf99", "482c811da5d5b4bc6d497ffa98491e38"]})
        st.write(opgeslagen_ww)
        with open('text/bedreigingen2.md', 'r') as bedreigingen2:
            st.markdown(bedreigingen2.read())
        st.markdown("## Als een database gehackt wordt.")
        fig1 = px.pie(df, names="Bent u ooit bewust geworden van een datalek waarbij uw gegevens zijn vrijgegeven?", values="Score", title="Bent u ooit bewust geworden van een datalek waarbij uw gegevens zijn vrijgegeven?")
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, theme="streamlit")
        with open('text/bedreigingen3.md', 'r') as bedreigingen3:
            st.markdown(bedreigingen3.read())
        fig2 = px.pie(df, names="Bent u wel eens gehackt?", values="Score", title="Bent u wel eens gehackt?")
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, theme="streamlit")

        
    elif selected == "Oplossingen":
        st.markdown("# De oplossingen")
        st.markdown("## Gebruik sterke wachtwoorden.")
        with open('text/oplossingen1.md', 'r') as oplossingen1:
            st.markdown(oplossingen1.read())
        st.write(
            """
            #### Check hier hoe snel uw wachtwoord gekraakt kan worden met brute forcing \n\n
            Gebasserd op snelheden van een enkele Nvidia RTX 4090 GPU (videokaart) die voor ongeveer 2000 euro te koop is (Pires, 2022). \n\n
            Dit is een videokaart die wordt gebruikt om games te spelen. \n\n
            De meeste hackers zullen waarschijnlijk nog geadvanceerde GPU's gebruiken!
            """)
        wachtwoord = st.text_input("Vul hier het te testen wachtwoord in:" )
        st.write("**Zo snel wordt dit wachtwoord gekraakt in.**",password_crack_time_checker(wachtwoord))
        
        st.markdown("## Hoe onthoud je sterke wachtwoorden?")
        vis_oplossingen_sterke_ww(df)
        with open('text/oplossingen2.md', 'r') as oplossingen2:
            st.markdown(oplossingen2.read())
        vis_oplossingen_pm(df)
        
        with open('text/oplossingen3.md', 'r') as oplossingen3:
            st.markdown(oplossingen3.read())
        pie_chart(df, "Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)", False)

    elif selected == "Best practices":
        st.markdown("# Best practices")
        with open("text/best_practices1.md", 'r') as best_practices1:
            st.markdown(best_practices1.read())

        st.markdown("#### Random password generator")
        st.write("Genereert willekeurige wachtwoorden met hoofdletters, kleine letters, cijfers en symbolen.")
        length = st.slider("Lengte van wachtwoord")
        st.write("**Uw willekeurig gegenereerde wachtwoord is:**", f"{password_generator(length)}")
        with open("text/best_practices2.md", 'r') as best_practices2:
            st.markdown(best_practices2.read())

        histogram(df, "Hoe groot is het probleem van het managen van wachtwoorden voor u, ten opzichte van het grootste probleem in uw leven?")
        histogram(df, "In hoeverre maak u zich zorgen om uw digitale veiligheid/privacy?")
        histogram(df, "Stelling: Ik heb niks te verbergen.\n\nIn hoeverre bent u het eens met de stelling?")
        histogram(df, "Hoe belangrijk vind u het om de controle te hebben over wie toegang heeft tot uw persoonlijke informatie online?")
        histogram(df, "Zou u bereid zijn om extra stappen te nemen, zoals het gebruik van encryptietools, om uw digitale privacy te waarborgen?")
        histogram(df, "Hoe belangrijk vind u het om te weten hoe bedrijven en organisaties omgaan met uw persoonlijke gegevens?")

    with open('text/bronnen.md', 'r') as bronnen:
        st.markdown(bronnen.read())
    