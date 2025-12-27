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

# Gérer les projets via `st.session_state` pour permettre l'ajout dynamique
if "projects" not in st.session_state:
    # Projets par défaut, avec dates absolues
    initial_date = datetime.now()
    st.session_state.projects = [
        {"name": "Projet Alpha", "start_date": initial_date + timedelta(days=0), "end_date": initial_date + timedelta(days=20), "tasks": []},
        {"name": "Projet Beta",  "start_date": initial_date + timedelta(days=14), "end_date": initial_date + timedelta(days=70), "tasks": []},
        {"name": "Projet Gamma", "start_date": initial_date + timedelta(days=35), "end_date": initial_date + timedelta(days=119), "tasks": []},
    ]
    # Trier les projets par ordre alphabétique (A → Z) au démarrage
    st.session_state.projects.sort(key=lambda p: p["name"].lower())

# Fonction pour convertir une date absolue en indice de période
def date_to_period_index(date, period_labels, period_starts, period_ends):
    """Retourne l'indice de la période qui contient la date donnée"""
    for idx in range(len(period_labels)):
        if period_starts[idx] <= date <= period_ends[idx]:
            return idx
    # Si la date n'est pas dans les périodes, retourner l'indice le plus proche
    if date < period_starts[0]:
        return 0
    else:
        return len(period_labels) - 1

# Utiliser la liste de projets depuis le session state
projects = st.session_state.projects

# Construire un tableau pour afficher le planning
# Créer les données du tableau
tableau_data = []

for p in projects:
    # Ajouter le projet lui-même
    row = {"Projet/Tâche": f"📋 {p['name']}"}
    start_idx = date_to_period_index(p["start_date"], period_labels, period_starts, period_ends)
    end_idx = date_to_period_index(p["end_date"], period_labels, period_starts, period_ends)
    for idx, period in enumerate(period_labels):
        if idx >= start_idx and idx <= end_idx:
            row[period] = "█"
        else:
            row[period] = ""
    tableau_data.append(row)
    
    # Ajouter les tâches du projet (toujours affichées)
    if "tasks" in p and len(p["tasks"]) > 0:
        for task in p["tasks"]:
            task_row = {"Projet/Tâche": f"  ↳ {task['name']}"}
            due_idx = date_to_period_index(task["due_date"], period_labels, period_starts, period_ends)
            for idx, period in enumerate(period_labels):
                if idx == due_idx:
                    task_row[period] = "◆"  # Diamant pour marquer la date d'échéance
                else:
                    task_row[period] = ""
            tableau_data.append(task_row)

# Créer un DataFrame
df_tableau = pd.DataFrame(tableau_data)

# Afficher le tableau avec mise en forme (lecture seule, sans index numérique)
# La colonne "Projet/Tâche" devient l'index
st.subheader("Planning Gantt (Tableau)")
st.table(df_tableau.set_index('Projet/Tâche'))

# Formulaire d'ajout direct affiché sous le tableau (un seul clic pour ajouter)
st.markdown("---")
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
        # convertir labels en dates absolues
        start_date = period_starts[period_labels.index(new_start)]
        end_date = period_ends[period_labels.index(new_end)]
        if new_name.strip() == "":
            st.error("Le nom du projet est requis.")
        elif end_date < start_date:
            st.error("La période de fin doit être après la période de début.")
        else:
            st.session_state.projects.append({"name": new_name.strip(), "start_date": start_date, "end_date": end_date, "tasks": []})
            # Trier les projets par ordre alphabétique (A → Z)
            st.session_state.projects.sort(key=lambda p: p["name"].lower())
            st.success(f"Projet '{new_name.strip()}' ajouté.")
            # Forcer la réexécution du script pour mettre à jour le graphique immédiatement
            st.rerun()

# Section de modification de projets
st.markdown("---")
st.subheader("Modifier un projet")
if len(st.session_state.projects) > 0:
    # Sélecteur pour choisir le projet à modifier
    project_names_list = [p["name"] for p in st.session_state.projects]
    selected_project_name = st.selectbox("Sélectionner un projet à modifier", project_names_list)
    
    # Trouver le projet sélectionné
    selected_project_idx = next(i for i, p in enumerate(st.session_state.projects) if p["name"] == selected_project_name)
    selected_project = st.session_state.projects[selected_project_idx]
    
    # Afficher les tâches existantes
    st.markdown("**Tâches existantes**")
    tasks = selected_project.get("tasks", [])
    if len(tasks) > 0:
        for i, task in enumerate(tasks):
            col_t1, col_t2, col_t3 = st.columns([2, 2, 1])
            with col_t1:
                st.write(f"📌 {task['name']}")
            with col_t2:
                # Trouver le label de la période correspondant à la date de fin
                period_idx = date_to_period_index(task["due_date"], period_labels, period_starts, period_ends)
                due_period = period_labels[period_idx] if period_idx < len(period_labels) else "N/A"
                st.write(f"À faire avant: {due_period}")
            with col_t3:
                if st.button("Supprimer", key=f"delete_task_{selected_project_idx}_{i}"):
                    st.session_state.projects[selected_project_idx]["tasks"].pop(i)
                    st.success(f"Tâche '{task['name']}' supprimée.")
                    st.rerun()
    else:
        st.info("Aucune tâche pour ce projet.")
    
    # Formulaire d'ajout de tâche
    st.markdown("**Ajouter une tâche**")
    col_ta1, col_ta2, col_ta3 = st.columns([2, 2, 1])
    with col_ta1:
        task_name = st.text_input("Nom de la tâche", value="", key=f"task_name_{selected_project_idx}")
    with col_ta2:
        task_due = st.selectbox("À faire avant", period_labels, index=0, key=f"task_due_{selected_project_idx}")
    with col_ta3:
        if st.button("Ajouter tâche", key=f"add_task_{selected_project_idx}"):
            if task_name.strip() == "":
                st.error("Le nom de la tâche est requis.")
            else:
                due_date = period_ends[period_labels.index(task_due)]
                if "tasks" not in st.session_state.projects[selected_project_idx]:
                    st.session_state.projects[selected_project_idx]["tasks"] = []
                st.session_state.projects[selected_project_idx]["tasks"].append({
                    "name": task_name.strip(),
                    "due_date": due_date
                })
                st.success(f"Tâche '{task_name.strip()}' ajoutée au projet.")
                st.rerun()
else:
    st.info("Aucun projet à modifier. Créez un projet d'abord.")

# Fin de la vue Gantt
