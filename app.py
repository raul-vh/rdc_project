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
    points_value_map = {
        'Ja': 1,
        'Nee': 0,
        'Ik gebruik de password manager in mij browser.': 0.5
    }
    columns = ['Raakt u wel eens wachtwoorden kwijt?',
               'Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?',
               'Gebruikt u een password manager?',
               'Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)']
    for index in df.index:
        score = 0
        for column in columns:
            score += points_value_map[df.loc[index][column]]
        df.loc[index, 'Score'] = score
    return df

if __name__ == "__main__":
    df = connect_to_google_docs()
    st.set_page_config(page_title="Onderzoek wachtwoordgebruik en digitale veiligheid", page_icon=":bar_chart:", layout="wide")
    st.header("Onderzoek wachtwoordgebruik en digitale veiligheid")
    st.write(df)
    df = compute_score_password_usage(df)
    st.write(df)

    color_order = ['Ja', 'Ik gebruik de password manager in mij browser.', 'Nee']
    fig1 = px.histogram(df, x="Hoe groot is het probleem van het managen van wachtwoorden voor u, ten opzichte van het grootste probleem in uw leven?", 
                   color="Gebruikt u een password manager?",
                   histfunc="count",
                   color_discrete_sequence=['#dc143c','#cd5c5c', '#ffa07a'],
                   category_orders={"Gebruikt u een password manager?": color_order})

    fig1.update_xaxes(range=[1, 10])
    fig1.update_layout(title_text='Groote probleem wachtwoorden en Password Manager Gebruik')
    fig1.update_xaxes(title_text='Hoe groot het probleem van het managen van wachtwoorden voor individu is. (Op schaal van 1 tot 10)')
    fig1.update_yaxes(title_text='Aantal respondenten')

    st.plotly_chart(fig1, theme="streamlit")

    grouped = df.groupby(['Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)', 'Bent u wel eens gehackt?']).size().reset_index(name='count')

    # Calculate percentages hacked for each 2FA group
    grouped['percent_hacked'] = grouped.groupby('Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)')[['count']].transform(lambda x: x/x.sum()*100)

    # Create bar chart 
    fig2 = px.bar(grouped, x='Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)', y='percent_hacked', color='Bent u wel eens gehackt?',
                color_discrete_map={True: '#dc143c', False: '#ffa07a'},
                labels={'Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)': 'Gebruik 2FA', 
                        'percent_hacked': '% Hacked'},
                title='Percentage gehackte mensen bij 2FA gebruik.')

    fig2.update_yaxes(range=[0,100])
    fig2.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    st.plotly_chart(fig2, theme="streamlit")

    plot_df = df.groupby(['Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)', 
                     'Bent u wel eens gehackt?'])['Leeftijd'].count().reset_index(name='Count')

    # Create plot 
    fig3 = px.bar(plot_df, x='Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)', 
             y='Count', color='Bent u wel eens gehackt?', barmode='group',
             color_discrete_map={True: '#d14343', False: '#ffa07a'},
             labels={'Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)': 'Gebruik 2FA',
                    'Count': 'Aantal respondenten'},
             title='2FA Gebruik en gehackt worden.')

    fig3.update_xaxes(type='category')
    st.plotly_chart(fig3, theme="streamlit")

    fig4 = px.scatter(df,  
                 x="In hoeverre maak u zich zorgen om uw digitale veiligheid/privacy?",
                 y="Zou u bereid zijn om extra stappen te nemen, zoals het gebruik van encryptietools, om uw digitale privacy te waarborgen?",
                 labels={'In hoeverre maak u zich zorgen om uw digitale veiligheid/privacy?':'Bezorgdheid over digitale privacy',
                         'Zou u bereid zijn om extra stappen te nemen, zoals het gebruik van encryptietools, om uw digitale privacy te waarborgen?':'Bereidheid om extra stappen te nemen voor privacy'},
                title='Relatie tussen bezorgdheid over privacy en bereidheid om encryptie te gebruiken')

    st.plotly_chart(fig4, theme="streamlit")

    fig5 = px.scatter(df,  
                 x="In hoeverre maak u zich zorgen om uw digitale veiligheid/privacy?",
                 y="Stelling: Ik heb niks te verbergen.\n\nIn hoeverre bent u het eens met de stelling?",
                 labels={'In hoeverre maak u zich zorgen om uw digitale veiligheid/privacy?':'Bezorgdheid over digitale privacy',
                         'Stelling: Ik heb niks te verbergen.\n\nIn hoeverre bent u het eens met de stelling?':'Ik heb niks te verbergen.'},
                title='Relatie tussen bezorgdheid over privacy en stelling: Ik heb niks te verbergen.')

    st.plotly_chart(fig5, theme="streamlit")

    st.write("**Creert een score van 0 tot 4 gebasseerd op de eerste vier vragen**\n\n Raakt u wel eens wachtwoorden kwijt?\n\n Heeft u vergelijkbare wachtwoorden die u op meerdere plekken gebruikt?\n\n Gebruikt u een password manager?\n\n Gebruikt u tweestapsverificatie naast uw wachtwoord? (Bijvoorbeeld: SMS, OTP, security key, vingerafdruk)")
    fig6 = px.scatter(df,  
                 x="Leeftijd",
                 y="Score",
                 labels={'Leeftijd':'Leefdtijd',
                         'Score':'Score wachtwoordgebruik.'},
                title='Relatie tussen leeftijd en wachtwoordgebruik')

    st.plotly_chart(fig6, theme="streamlit")
    # st.header("Structuur van dit digitaal instrument.")
    # st.write("**Inleiding:** Empirische beschrijving van het voorbeeld.")
    # st.write("**De bedreigingen:** Welke bedreigingen zijn er? Hoe goed zijn mensen nu beveiligd tegen deze?")
    # st.write("**De oplossingen:** Welke oplossingen zijn er? Waarom zijn ze nodig? *Hier bespreken we wat de effecten zijn op de veiligheid*")
    # st.write("**Welke oplossing past bij mij?** *Hier gaan we proberen te verklaren waarom mensen bepaald gedrag vertonen. De schaal van veiligheid vs gebruiksgemak.*")
    # st.write("**Nadenken over hoe de visualisaties de tekst ondersteunen.** Dus welke visualisaties en hoe ze eruit zien.")
    # st.write("**Het programmeren zelf**")