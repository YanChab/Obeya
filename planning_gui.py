# Importer streamlit pour créer l'interface visuelle
import streamlit as st
# Importer datetime pour manipuler les dates
from datetime import datetime, timedelta
# Importer calendar pour les informations sur les calendriers
import calendar
# Importer pandas pour créer des DataFrames
import pandas as pd

# Configurer la page Streamlit avec le titre et l'icône
st.set_page_config(
    # Définir le titre de la page
    page_title="Planning Obeya",
    # Définir l'icône de la page
    page_icon="📅",
    # Définir la mise en page comme wide
    layout="wide",
    # Définir le mode initial du thème en sombre
    initial_sidebar_state="expanded"
)

# Ajouter du CSS personnalisé pour un style professionnel moderne
st.markdown("""
<style>
    /* Styling pour les titres principaux */
    h1 {
        text-align: center;
        color: #1f77b4;
        padding: 20px;
        border-bottom: 3px solid #1f77b4;
    }
    
    /* Styling pour les sous-titres */
    h2 {
        color: #1f77b4;
        margin-top: 30px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
    }
    
    /* Styling pour les métriques */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Afficher le titre principal
st.title("📅 Planning Obeya")

# Obtenir la date d'aujourd'hui
date_debut = datetime.now()

# Afficher la date actuelle
col1, col2, col3 = st.columns(3)
with col1:
    # Afficher la métrique de la date actuelle
    st.metric("📌 Date d'aujourd'hui", date_debut.strftime('%d/%m/%Y'))
with col2:
    # Afficher le jour de la semaine
    st.metric("📆 Jour", date_debut.strftime('%A'))
with col3:
    # Afficher le jour du mois
    st.metric("🗓️ Semaine de l'année", f"Semaine {date_debut.isocalendar()[1]}")

# Ajouter une ligne de séparation
st.divider()

# ============================================================================
# SECTION 1: LES 12 PROCHAINES SEMAINES
# ============================================================================

# Afficher le titre de la section des 12 semaines
st.header("📅 Les 12 prochaines semaines")

# Créer une liste pour stocker les données des semaines
donnees_semaines = []

# Boucle pour générer les données de chaque semaine
for i in range(12):
    # Calculer la date de début de la semaine courante
    date_semaine_debut = date_debut + timedelta(weeks=i)
    # Calculer la date de fin de la semaine
    date_semaine_fin = date_semaine_debut + timedelta(days=6)
    
    # Ajouter les données de la semaine dans la liste
    donnees_semaines.append({
        # Ajouter le numéro de la semaine
        "Semaine": f"S{i+1:02d}",
        # Ajouter la date de début
        "Date de début": date_semaine_debut.strftime('%d/%m/%Y'),
        # Ajouter la date de fin
        "Date de fin": date_semaine_fin.strftime('%d/%m/%Y'),
        # Ajouter le jour de début
        "Jour début": date_semaine_debut.strftime('%A'),
        # Ajouter le jour de fin
        "Jour fin": date_semaine_fin.strftime('%A')
    })

# Créer un DataFrame avec les données des semaines
df_semaines = pd.DataFrame(donnees_semaines)

# Afficher le tableau des semaines
st.dataframe(
    # Utiliser le DataFrame créé
    df_semaines,
    # Utiliser la largeur complète de la colonne
    use_container_width=True,
    # Cacher l'index des lignes
    hide_index=True
)

# Afficher un résumé des semaines
st.info(f"✅ **{len(df_semaines)} semaines** planifiées du {date_debut.strftime('%d/%m/%Y')} au {(date_debut + timedelta(weeks=11, days=6)).strftime('%d/%m/%Y')}")

# Ajouter une ligne de séparation
st.divider()

# ============================================================================
# SECTION 2: LES 6 MOIS SUIVANTS
# ============================================================================

# Afficher le titre de la section des 6 mois
st.header("📊 Les 6 mois suivants")

# Créer une liste pour stocker les données des mois
donnees_mois = []

# Calculer la date de début pour les 6 mois (après la 12ème semaine)
date_mois_debut = date_debut + timedelta(weeks=12)

# Boucle pour générer les données de chaque mois
for i in range(6):
    # Calculer le mois courant
    mois = (date_mois_debut.month + i - 1) % 12 + 1
    # Calculer l'année courante
    annee = date_mois_debut.year + (date_mois_debut.month + i - 1) // 12
    
    # Obtenir le nombre de jours dans le mois
    nombre_jours_mois = calendar.monthrange(annee, mois)[1]
    
    # Obtenir les noms des mois en français
    noms_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    # Obtenir le nom du mois actuel
    nom_mois = noms_mois[mois - 1]
    
    # Créer la date de début du mois
    date_debut_mois = datetime(annee, mois, 1)
    # Créer la date de fin du mois
    date_fin_mois = datetime(annee, mois, nombre_jours_mois)
    
    # Ajouter les données du mois dans la liste
    donnees_mois.append({
        # Ajouter le numéro du mois
        "Mois": f"M{i+1:02d}",
        # Ajouter le nom du mois
        "Nom": nom_mois,
        # Ajouter l'année
        "Année": annee,
        # Ajouter la date de début
        "Date de début": date_debut_mois.strftime('%d/%m/%Y'),
        # Ajouter la date de fin
        "Date de fin": date_fin_mois.strftime('%d/%m/%Y'),
        # Ajouter le nombre de jours
        "Jours": nombre_jours_mois
    })

# Créer un DataFrame avec les données des mois
df_mois = pd.DataFrame(donnees_mois)

# Afficher le tableau des mois
st.dataframe(
    # Utiliser le DataFrame créé
    df_mois,
    # Utiliser la largeur complète de la colonne
    use_container_width=True,
    # Cacher l'index des lignes
    hide_index=True
)

# Afficher un résumé des mois
dernier_mois = donnees_mois[-1]
# Afficher les mois avec les dates de début et fin
st.info(f"✅ **{len(df_mois)} mois** planifiés du {dernier_mois['Date de début']} au {dernier_mois['Date de fin']}")

# Ajouter une ligne de séparation
st.divider()

# ============================================================================
# SECTION 3: RÉSUMÉ GLOBAL
# ============================================================================

# Afficher le titre du résumé
st.header("📈 Résumé du planning")

# Créer 4 colonnes pour afficher les métriques principales
col1, col2, col3, col4 = st.columns(4)

# Afficher la métrique du nombre de semaines
with col1:
    # Afficher le nombre total de semaines
    st.metric("📅 Semaines", "12")

# Afficher la métrique du nombre de mois
with col2:
    # Afficher le nombre total de mois
    st.metric("📊 Mois", "6")

# Afficher la métrique de la date de fin
with col3:
    # Calculer la date de fin totale
    date_fin_totale = date_debut + timedelta(weeks=12, days=180)
    # Afficher la date de fin
    st.metric("🏁 Date de fin", date_fin_totale.strftime('%d/%m/%Y'))

# Afficher la métrique du nombre de jours total
with col4:
    # Calculer le nombre total de jours
    nombre_jours_total = (date_fin_totale - date_debut).days
    # Afficher le nombre total de jours
    st.metric("⏱️ Jours total", f"{nombre_jours_total}")

# Afficher un message de succès
st.success("✅ Planning créé avec succès !")
