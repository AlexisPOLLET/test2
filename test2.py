import streamlit as st
import pandas as pd
try:
    import folium
    from streamlit_folium import folium_static
except ImportError:
    st.error("Les bibliothèques nécessaires ne sont pas correctement installées. Vérifiez le fichier requirements.txt.")
from streamlit_folium import folium_static
import plotly.express as px

# Titre de l'application
st.title("Analyse des Séismes en France")

# Étape 1 : Téléchargement du fichier CSV
uploaded_file = st.file_uploader("Téléchargez un fichier CSV contenant les données des séismes", type=["csv"])

if uploaded_file:
    # Étape 2 : Lecture du fichier CSV
    try:
        data = pd.read_csv(uploaded_file)
        st.success("Fichier chargé avec succès !")

        # Aperçu des données
        st.subheader("Aperçu des données :")
        st.write(data.head())

        # Statistiques descriptives
        st.subheader("Statistiques descriptives des données :")
        st.write(data.describe())

        # Filtrer les données pour la France
        data_france = data[data['state'] == 'France']

        # Étape 3 : Vérifications et calculs
        st.subheader("Statistiques des séismes en France")
        if data_france.empty:
            st.warning("Aucune donnée trouvée pour la France.")
        else:
            max_significance = data_france['significance'].max()
            min_significance = data_france['significance'].min()

            st.write(f"Significance maximale : {max_significance}")
            st.write(f"Significance minimale : {min_significance}")

            # Créer une carte centrée sur la France
            france_map = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

            # Filtrer selon la colonne 'significance'
            low_significance = data_france[data_france['significance'] < 50]
            medium_significance = data_france[(data_france['significance'] >= 50) & (data_france['significance'] < 150)]
            high_significance = data_france[data_france['significance'] >= 150]

            # Ajouter les couches pour chaque catégorie
            low_layer = folium.FeatureGroup(name="Significance < 50").add_to(france_map)
            for _, row in low_significance.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=2,
                    color='green',
                    fill=True,
                    fill_color='green',
                    fill_opacity=0.6
                ).add_to(low_layer)

            medium_layer = folium.FeatureGroup(name="Significance 50-150").add_to(france_map)
            for _, row in medium_significance.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color='orange',
                    fill=True,
                    fill_color='orange',
                    fill_opacity=0.6
                ).add_to(medium_layer)

            high_layer = folium.FeatureGroup(name="Significance >= 150").add_to(france_map)
            for _, row in high_significance.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=8,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.6
                ).add_to(high_layer)

            folium.LayerControl().add_to(france_map)

            # Afficher la carte avec Streamlit
            st.subheader("Carte des séismes en France :")
            folium_static(france_map)

            # Étape 4 : Frise chronologique des séismes
            st.subheader("Frise chronologique des séismes")

            # Assurez-vous que 'date' est au format datetime
            data_france['date'] = pd.to_datetime(data_france['date'], infer_datetime_format=True, errors='coerce')
            data_france['year'] = data_france['date'].dt.year

            # Compter le nombre de séismes par année
            seismes_par_annee = data_france.groupby('year').size().reset_index(name='nombre_seismes')

            # Créer la frise chronologique avec Plotly
            fig = px.bar(
                seismes_par_annee, 
                x='year', 
                y='nombre_seismes', 
                title='Nombre de Séismes par Année en France',
                labels={'year': 'Année', 'nombre_seismes': 'Nombre de Séismes'},
                template='plotly_dark'
            )

            # Afficher le graphique
            st.plotly_chart(fig)
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier : {e}")

