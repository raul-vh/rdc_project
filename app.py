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
        st.plotly_chart(fig1, theme="streamlit")

        fig3 = px.histogram(df,
                            x="Welke van de volgende categorieën omschrijft het beste uw arbeidssituatie?",
                            title="Arbeidssituatie van respondenten")
        st.plotly_chart(fig3, theme="streamlit")
    with col2:
        fig2 = px.pie(df, names="Geslacht", values="Score", title="Geslachtverdeling van respondenten")
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, theme="streamlit")

        fig4 = px.histogram(df,
                            x="Welke van de volgende categorieën omschrijft het beste uw levensituatie?",
                            title="Levensituatie van respondenten")
        st.plotly_chart(fig4, theme="streamlit")
    return

def pie_chart(df, column_name):
    """
    Prints pie chart for specific column name
    """
    fig = px.pie(df, names=column_name, values="Score", title=column_name)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, theme="streamlit")
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
        options=["Inleiding", "De bedreigingen", "De oplossingen", "Best practices"],
        icons=["play-fill", "exclamation-triangle", "", "check2-circle"], #speedometer2
        default_index=0,
        orientation="horizontal",
    )
    if selected == "Inleiding":
        st.header("Inleiding")
        st.write("- Text van empirisch voorbeeld.\n\n- Introductie onderzoek en enquete.")
        descriptives_survey(df)
    elif selected == "De bedreigingen":
        st.header("De bedreigingen")
        st.markdown("### Hoe wachtwoorden worden opgeslagen?")
        opgeslagen_ww = pd.DataFrame({
            "Username": ["Alice", "Bob"],
            "Password hash": ["5f4dcc3b5aa765d61d8327deb882cf99", "482c811da5d5b4bc6d497ffa98491e38"]})
        st.write(opgeslagen_ww)
        st.markdown("### Als een database gehackt wordt.")
        fig1 = px.pie(df, names="Bent u ooit bewust geworden van een datalek waarbij uw gegevens zijn vrijgegeven?", values="Score", title="Bent u ooit bewust geworden van een datalek waarbij uw gegevens zijn vrijgegeven?")
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, theme="streamlit")
        st.markdown("### Bruteforcing")
        fig2 = px.pie(df, names="Bent u wel eens gehackt?", values="Score", title="Bent u wel eens gehackt?")
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig2, theme="streamlit")
    elif selected == "De oplossingen":
        st.header("De oplossingen")
        st.markdown("### Wat maakt een wachtwoord sterk?")
        pie_chart(df, "Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?")

        st.write("**Check hier hoe snel uw wachtwoord gekraakt kan worden.** \n\n Gebasserd op snelheden van een enkele Nvidia RTX 4090 GPU die voor ongeveer 2000 euro te koop is.")
        wachtwoord = st.text_input("Vul hier het te testen wachtwoord in:" )
        st.write("**Zo snel wordt dit wachtwoord gekraakt in.**",password_crack_time_checker(wachtwoord))
        st.markdown("### Hoe onthoud je sterke wachtwoorden?")
        pie_chart(df, "Raakt u wel eens wachtwoorden kwijt?")
        st.write("Text over de oplossing: Passwordt manager")
        pie_chart(df, "Gebruikt u een password manager?")
        st.markdown("### Wat als mijn wachwoord dan toch gehackt wordt? --> 2FA")
        st.write("- iets dat je weet (wachtwoord)\n\n- iets dat je bezit(security key, telefoon met OTP)\n\n- iets dat je eigen is(vingerafdruk, gezichtsherkenning)")
        pie_chart(df, "Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)")

    elif selected == "Best practices":
        st.header("Best practices")
        st.markdown("### Veiligheid vs Gebruiksgemak")
        st.markdown("### Normen en waarden")
        st.write("Nothing to hide, but everything to protect. \n\n Bewustwording")
        st.markdown("### Opsomming van de best practices")
        st.write("- PM \n\n - 2FA \n\n - wachtwoorden regelmatig veranderen \n\n - nog toevoegen")
        st.markdown("### Random password generator")
        st.write("Genereert willekeurige wachtwoorden met hoofdletters, kleine letters, cijfers en symbolen.")
        length = st.slider("Lengte van wachtwoord")
        st.write("**Uw willekeurig gegenereerde wachtwoord is:**", f"{password_generator(length)}")
