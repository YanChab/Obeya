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

# Réafficher le titre principal
st.title("📅 Planning Obeya")

# Obtenir la date d'aujourd'hui par défaut
initial_date = datetime.now()

# Ajout d'un sélecteur de date pour définir la date de début du Gantt
# Le sélecteur est placé 'à côté' de la date et de la semaine
cols = st.columns(3)
# Sélecteur de date (menu) dans la colonne du milieu
selected_date = cols[2].date_input("Date de début du Gantt", value=initial_date.date())

# Convertir la date sélectionnée en datetime pour les calculs
date_debut = datetime.combine(selected_date, datetime.min.time())

# Afficher la date et la semaine en petit (le jour est retiré)
cols[0].markdown(f"<div style='font-size:13px'>📌 <strong>Date d\'aujourd\'hui</strong><br><span style='font-size:16px'>{date_debut.strftime('%d/%m/%Y')}</span></div>", unsafe_allow_html=True)
cols[1].markdown(f"<div style='font-size:13px'>🗓️ <strong>Semaine</strong><br><span style='font-size:16px'>Semaine {date_debut.isocalendar()[1]}</span></div>", unsafe_allow_html=True)

# Ajouter une ligne de séparation
st.divider()

# ============================================================================
# SECTION 1: LES 12 PROCHAINES SEMAINES (header supprimé pour affichage épuré)
# ============================================================================

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
    # Construire le label de la tâche : utiliser le numéro ISO de la semaine
    week_num = start.isocalendar()[1]
    label = f"S{week_num:02d} ({start.strftime('%d/%m')})"
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

# Construire un subplot avec 2 lignes : en haut les titres/colonnes, en bas les lignes de projets
from plotly.subplots import make_subplots

# Gérer les projets via `st.session_state` pour permettre l'ajout dynamique
if "projects" not in st.session_state:
    # Projets par défaut, triés alphabétiquement
    st.session_state.projects = [
        {"name": "Projet Alpha", "start": 0, "end": 3},
        {"name": "Projet Beta",  "start": 2, "end": 10},
        {"name": "Projet Gamma", "start": 5, "end": 17},
    ]
    # Trier les projets par ordre alphabétique inverse (Z → A) au démarrage
    st.session_state.projects.sort(key=lambda p: p["name"].lower(), reverse=True)

# Utiliser la liste de projets depuis le session state
projects = st.session_state.projects

# Pour l'affichage, les projets sont déjà triés alphabétiquement en session state
projects_display = projects

# Construire la matrice projet x période (0/1) à partir des projets triés
project_names = [p["name"] for p in projects_display]
z = []
for p in projects_display:
    row = [1 if (idx >= p["start"] and idx <= p["end"]) else 0 for idx in range(len(period_labels))]
    z.append(row)

# Construire une seule heatmap : colonnes en haut (axe X) et projets en lignes
fig = go.Figure()

# Heatmap des projets (1 = actif)
heat = go.Heatmap(
    z=z,
    x=period_labels,
    y=project_names,
    colorscale=[[0, 'rgba(255,255,255,0)'], [1, '#2ca02c']],
    showscale=False,
    hovertemplate="Projet: %{y}<br>Période: %{x}<extra></extra>",
)
fig.add_trace(heat)

# Placer les labels de l'axe X au-dessus
fig.update_xaxes(side='top', tickangle=-45)

# Ajuster le style et la taille
fig.update_layout(
    height=420,
    margin=dict(l=40, r=20, t=60, b=80),
    # Pas de titre du diagramme (affichage épuré)
)

# Afficher la figure dans Streamlit
st.plotly_chart(fig, use_container_width=True)

# Formulaire d'ajout direct affiché sous le Gantt (un seul clic pour ajouter)
st.markdown("---")
st.subheader("Ajouter un projet")
# Champs simples : nom, début, fin
col_a, col_b, col_c, col_d = st.columns([3,2,2,1])
with col_a:
    new_name = st.text_input("Nom du projet", value="")
with col_b:
    new_start = st.selectbox("Période de début", period_labels, index=0)
with col_c:
    new_end = st.selectbox("Période de fin", period_labels, index=min(3, len(period_labels)-1))
with col_d:
    if st.button("Ajouter"):
        # convertir labels en indices
        si = period_labels.index(new_start)
        ei = period_labels.index(new_end)
        if new_name.strip() == "":
            st.error("Le nom du projet est requis.")
        elif ei < si:
            st.error("La période de fin doit être après la période de début.")
        else:
            st.session_state.projects.append({"name": new_name.strip(), "start": si, "end": ei})
            # Trier les projets par ordre alphabétique inverse (Z → A)
            st.session_state.projects.sort(key=lambda p: p["name"].lower(), reverse=True)
            st.success(f"Projet '{new_name.strip()}' ajouté.")
            # Forcer la réexécution du script pour mettre à jour le graphique immédiatement
            st.rerun()

# Fin de la vue Gantt
