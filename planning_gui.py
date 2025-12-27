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

# ============================================================================
# SECTION: DIAGRAMME DE GANTT COMBINÉ (SEM => MOIS)
# ============================================================================

# Importer plotly pour générer le diagramme de Gantt
import plotly.express as px

# Construire la liste des tâches pour le Gantt
tasks = []

# Ajouter les 12 semaines en tant que tâches
for i, s in enumerate(donnees_semaines):
    # Calculer les dates de début et fin réelles en datetime
    start = datetime.strptime(s["Date de début"], "%d/%m/%Y")
    end = datetime.strptime(s["Date de fin"], "%d/%m/%Y") + timedelta(days=1)  # rendre la fin inclusive
    # Construire le label de la tâche
    label = f"{s['Semaine']} ({start.strftime('%d/%m')})"
    # Ajouter la tâche avec le type 'Semaine' et un ordre pour conserver la séquence
    tasks.append({"Task": label, "Start": start, "Finish": end, "Type": "Semaine", "Order": i})

# Calculer la date de début pour les mois (après la 12ème semaine)
date_mois_debut = date_debut + timedelta(weeks=12)

# Générer les 6 mois et les ajouter après les semaines
for i in range(6):
    mois = (date_mois_debut.month + i - 1) % 12 + 1
    annee = date_mois_debut.year + (date_mois_debut.month + i - 1) // 12
    nombre_jours_mois = calendar.monthrange(annee, mois)[1]
    start = datetime(annee, mois, 1)
    end = datetime(annee, mois, nombre_jours_mois) + timedelta(days=1)
    noms_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    nom_mois = noms_mois[mois - 1]
    label = f"{nom_mois} {annee}"
    tasks.append({"Task": label, "Start": start, "Finish": end, "Type": "Mois", "Order": 12 + i})

# Créer un DataFrame pour le Gantt
df_gantt = pd.DataFrame(tasks)

# Définir l'ordre des tâches pour que les semaines apparaissent en premier puis les mois
ordre_taches = df_gantt.sort_values("Order")["Task"].tolist()


# Construire des colonnes catégorielles : 12 semaines puis 6 mois
period_labels = df_gantt.sort_values("Order")["Task"].tolist()  # ordre des colonnes
period_types = df_gantt.sort_values("Order")["Type"].tolist()
period_starts = df_gantt.sort_values("Order")["Start"].tolist()
period_ends = df_gantt.sort_values("Order")["Finish"].tolist()

import plotly.graph_objects as go

# Préparer les couleurs
color_map = {"Semaine": "#1f77b4", "Mois": "#ff7f0e"}
colors = [color_map.get(t, "#888888") for t in period_types]

# Créer une figure avec des colonnes verticales (chaque colonne représente une période)
fig = go.Figure()

# Ajouter une barre par période (hauteur fixe) pour représenter la colonne
fig.add_trace(go.Bar(
    x=period_labels,
    y=[1] * len(period_labels),
    marker_color=colors,
    hoverinfo='text',
    text=[f"{lbl}<br>{start.strftime('%d/%m/%Y')} → {(end - timedelta(days=1)).strftime('%d/%m/%Y')}" for lbl, start, end in zip(period_labels, period_starts, period_ends)],
    hovertemplate="%{text}<extra></extra>",
))

# Style : enlever axes y inutiles et rendre lisible
fig.update_yaxes(visible=False)
fig.update_layout(
    barmode='stack',
    showlegend=False,
    title="Planning — 12 semaines puis 6 mois (colonnes)",
    xaxis_title="Périodes",
    margin=dict(l=40, r=20, t=60, b=120),
)

# Rotation des labels x pour lisibilité
fig.update_xaxes(tickangle= -45)

# Afficher le graphique dans Streamlit
st.plotly_chart(fig, use_container_width=True)

# Fin de la vue Gantt (le résumé demandé a été supprimé)
