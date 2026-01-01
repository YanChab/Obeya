# Importer streamlit pour créer l'interface visuelle
import streamlit as st
# Utilisé pour échapper le texte dans les attributs HTML
from html import escape
# Importer datetime pour manipuler les dates
from datetime import datetime, timedelta
# Importer calendar pour les informations sur les calendriers
import calendar
# Importer pandas pour créer des DataFrames
import pandas as pd
# Importer TinyDB pour le stockage persistant des données
from tinydb import TinyDB, Query
import json
import os
# Importer locale pour forcer le format français
import locale

# Forcer la locale française pour les dates
try:
    # Essayer la locale française
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    try:
        # Alternative si fr_FR.UTF-8 n'est pas disponible
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except locale.Error:
        try:
            # Autre alternative pour certains systèmes
            locale.setlocale(locale.LC_TIME, 'French_France.1252')
        except locale.Error:
            # Si aucune locale française n'est disponible, continuer avec la locale par défaut
            pass

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

# Ajouter du CSS personnalisé adaptatif au thème du système d'exploitation
# Utilise les media queries CSS pour détecter automatiquement le thème
st.markdown("""
<style>
    /* ===== MODE CLAIR (par défaut) ===== */
    :root {
        --color-titles: #1f77b4;
        --color-border-title: #1f77b4;
        --color-subtitle-border: #e0e0e0;
        --color-metric-bg: #f0f2f6;
        --color-table-border: #ddd;
        --color-table-bg: white;
        --color-cell-bg: #f9f9f9;
        --color-project-bg: #0d3a14;
        --color-task-due-bg: #ff7f0e;
        --color-text-on-color: white;
        --color-table-text: inherit;
    }
    
    /* ===== MODE SOMBRE (détecté via prefers-color-scheme) ===== */
    @media (prefers-color-scheme: dark) {
        :root {
            --color-titles: #64b5f6;
            --color-border-title: #64b5f6;
            --color-subtitle-border: #444;
            --color-metric-bg: #2c3e50;
            --color-table-border: #555;
            --color-table-bg: #1e1e1e;
            --color-cell-bg: #2d2d2d;
            --color-project-bg: #0d3a14;
            --color-task-due-bg: #ff7f0e;
            --color-text-on-color: white;
            --color-table-text: #e0e0e0;
        }
    }
    
    /* Styling pour les titres principaux */
    h1 {
        text-align: center;
        color: var(--color-titles);
        padding: 20px;
        border-bottom: 3px solid var(--color-border-title);
    }
    
    /* Styling pour les sous-titres */
    h2 {
        color: var(--color-titles);
        margin-top: 30px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--color-subtitle-border);
    }
    
    /* Styling pour les métriques */
    [data-testid="metric-container"] {
        background-color: var(--color-metric-bg);
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

# Initialiser TinyDB pour la persistance des données
db_path = os.path.join(os.path.dirname(__file__), "db.json")
db = TinyDB(db_path)
projects_table = db.table("projects")

# Fonction pour charger les projets depuis la base de données
def load_projects_from_db():
    """Charge les projets depuis TinyDB et les reformate pour Streamlit"""
    projects_data = projects_table.all()
    projects = []
    for proj_data in projects_data:
        # Convertir les chaînes de date JSON en objets datetime
        proj = proj_data.copy()
        proj["start_date"] = datetime.fromisoformat(proj.get("start_date", datetime.now().isoformat()))
        proj["end_date"] = datetime.fromisoformat(proj.get("end_date", datetime.now().isoformat()))
        # Assurer que les tâches ont des dates au format datetime
        if "tasks" in proj and proj["tasks"]:
            for i, task in enumerate(proj["tasks"]):
                if isinstance(task.get("due_date"), str):
                    proj["tasks"][i] = task.copy()
                    proj["tasks"][i]["due_date"] = datetime.fromisoformat(task["due_date"])
        projects.append(proj)
    return projects

# Fonction pour sauvegarder les projets dans la base de données
def save_projects_to_db(projects):
    """Sauvegarde les projets dans TinyDB"""
    projects_table.truncate()  # Vider la table
    for proj in projects:
        # Convertir les dates en ISO format pour le stockage JSON
        proj_to_save = proj.copy()
        proj_to_save["start_date"] = proj["start_date"].isoformat()
        proj_to_save["end_date"] = proj["end_date"].isoformat()
        # Convertir les dates des tâches aussi
        if "tasks" in proj_to_save:
            for task in proj_to_save["tasks"]:
                if isinstance(task.get("due_date"), datetime):
                    task["due_date"] = task["due_date"].isoformat()
        projects_table.insert(proj_to_save)

# Gérer les projets via `st.session_state` pour permettre l'ajout dynamique
if "projects" not in st.session_state:
    # Charger depuis la base de données
    loaded_projects = load_projects_from_db()
    st.session_state.projects = loaded_projects if loaded_projects else []
    # Trier les projets par ordre alphabétique (A → Z) au démarrage
    st.session_state.projects.sort(key=lambda p: p["name"].lower())

# Fonction pour normaliser les dates des tâches
def ensure_task_dates_are_datetime(projects):
    """Vérifie et convertit les dates de tâches string en datetime"""
    for project in projects:
        if "tasks" in project and project["tasks"]:
            for task in project["tasks"]:
                if isinstance(task.get("due_date"), str):
                    task["due_date"] = datetime.fromisoformat(task["due_date"])
    return projects

# S'assurer que toutes les dates de tâches sont des datetime
st.session_state.projects = ensure_task_dates_are_datetime(st.session_state.projects)

# Fonction pour sauvegarder après modification
def sync_db():
    """Synchronise les projets en session avec la base de données"""
    save_projects_to_db(st.session_state.projects)


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

# Initialiser les filtres dans session_state s'ils n'existent pas
if "filtered_projects" not in st.session_state:
    st.session_state.filtered_projects = [p["name"] for p in st.session_state.projects]

if "filtered_categories" not in st.session_state:
    st.session_state.filtered_categories = ["Jalon", "Livrable", "Etude", "Prototype", "Map-Qual-Val", "Industrialisation"]

if "filtered_statuses" not in st.session_state:
    st.session_state.filtered_statuses = ["Pas démarré", "Dans les temps", "En retard", "Critique", "StandBy"]

# Utiliser la liste de projets depuis le session state
projects_full = st.session_state.projects

# Helper: importer des tâches depuis un fichier Excel
def parse_tasks_from_excel(uploaded_file, sheet_name="Model Tache"):
    """Lit un fichier Excel et retourne une liste de tâches normalisées.
    Colonnes attendues (en ordre): Nom, Catégorie, Date d'échéance, Progression.
    - Ignore la première ligne (entêtes) via pandas (header=0)
    - Si la catégorie n'est pas reconnue, utilise "Jalon"
    - Si la date n'est pas valide, utilise la date du jour
    - Si la progression n'est pas 0%/50%/100%, utilise 0%
    """
    allowed_categories = ["Jalon", "Livrable", "Etude", "Prototype", "Map-Qual-Val", "Industrialisation"]
    allowed_progress = ["0%", "50%", "100%"]

    try:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier Excel: {e}")
        return [], {"category": 0, "due_date": 0, "progress": 0}

    imported_tasks = []
    corrections = {"category": 0, "due_date": 0, "progress": 0}
    today = datetime.now()

    # Parcourir les lignes de données (pandas considère la première ligne comme en-tête)
    for _, row in df.iterrows():
        # Lecture des colonnes par position
        name = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
        if name == "" or name.lower() in ("nan", "none"):
            # Ignorer les lignes sans nom de tâche
            continue

        raw_category = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        category = raw_category if raw_category in allowed_categories else "Jalon"
        if category != raw_category:
            corrections["category"] += 1

        # Date d'échéance
        raw_due = row.iloc[2] if len(row) > 2 else None
        due_pd = pd.to_datetime(raw_due, errors="coerce")
        if pd.isna(due_pd):
            due_date = today
            corrections["due_date"] += 1
        else:
            # Convertir en datetime natif
            due_date = due_pd.to_pydatetime()

        # Progression - Convertir les valeurs numériques en texte avec %
        raw_progress = row.iloc[3] if (len(row) > 3 and pd.notna(row.iloc[3])) else ""
        
        # Si c'est un nombre (0, 0.5, 1) ou (0, 50, 100), convertir en texte avec %
        if isinstance(raw_progress, (int, float)):
            if raw_progress == 0 or raw_progress == 0.0:
                progress = "0%"
            elif raw_progress == 0.5 or raw_progress == 50:
                progress = "50%"
            elif raw_progress == 1 or raw_progress == 1.0 or raw_progress == 100:
                progress = "100%"
            else:
                # Valeur non reconnue, utiliser 0%
                progress = "0%"
                corrections["progress"] += 1
        else:
            # Si c'est déjà du texte, vérifier qu'il est dans les valeurs autorisées
            raw_progress_str = str(raw_progress).strip()
            progress = raw_progress_str if raw_progress_str in allowed_progress else "0%"
            if progress != raw_progress_str:
                corrections["progress"] += 1

        imported_tasks.append({
            "name": name,
            "category": category,
            "due_date": due_date,
            "progress": progress,
        })

    return imported_tasks, corrections

# Construire un tableau pour afficher le planning avec couleurs de fond
tableau_data = []
tableau_styles = []  # Stocker les styles pour chaque ligne
tableau_tooltips = []  # Stocker les tooltips pour chaque cellule

# Filtrer les projets selon la sélection stockée (projets et états)
projects = [p for p in projects_full if p["name"] in st.session_state.filtered_projects and p.get("status", "Pas démarré") in st.session_state.filtered_statuses]

for p in projects:
    # Ligne unique pour le projet (les tâches seront intégrées dans les cellules du projet)
    row = {"Projet/Tâche": f"📋 {p['name']}"}
    start_idx = date_to_period_index(p["start_date"], period_labels, period_starts, period_ends)
    end_idx = date_to_period_index(p["end_date"], period_labels, period_starts, period_ends)
    
    row_styles = ["project"]  # Style pour la colonne Projet/Tâche
    row_tooltips = [""]  # Tooltip vide pour la colonne Projet/Tâche
    project_tooltip = f"{p['name']} • fin {p['end_date'].strftime('%d/%m/%Y')}"
    tasks_per_period = [[] for _ in period_labels]  # Collecter les tâches par période pour le tooltip
    
    # Déterminer la classe CSS en fonction du statut du projet
    project_status = p.get("status", "Pas démarré")
    if project_status == "Pas démarré":
        status_class = "not_started"
    elif project_status == "En retard":
        status_class = "overdue"
    elif project_status == "Critique":
        status_class = "critical"
    elif project_status == "StandBy":
        status_class = "standby"
    else:  # "Dans les temps" or default
        status_class = "active"

    for idx, period in enumerate(period_labels):
        if idx >= start_idx and idx <= end_idx:
            row[period] = ""  # La couleur de fond suffit pour représenter la période active
            # Appliquer la classe CSS basée sur le statut du projet
            row_styles.append(status_class)
            row_tooltips.append(project_tooltip)
        else:
            row[period] = ""
            row_styles.append("inactive")
            row_tooltips.append("")

    # Ajouter les tâches directement dans la cellule de période du projet
    # (sauf les tâches en retard ou filtrées par catégorie)
    if "tasks" in p and len(p["tasks"]) > 0:
        for task in p["tasks"]:
            # Convertir la date de tâche si elle est en string
            due_date = task["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date)
            
            # Ne pas afficher les tâches en retard dans les colonnes
            if due_date < datetime.now():
                continue
            
            # Ne pas afficher les tâches terminées (100%)
            if task.get("progress", "0%") == "100%":
                continue
            
            # Filtrer par catégorie
            task_category = task.get("category", "Jalon")
            if task_category not in st.session_state.filtered_categories:
                continue
            
            due_idx = date_to_period_index(due_date, period_labels, period_starts, period_ends)
            target_period = period_labels[due_idx]
            task_progress = task.get("progress", "0%")
            task_category = task.get("category", "Jalon")
            
            # Créer le label avec icône et style différents selon la catégorie
            if task_category == "Jalon":
                # Utiliser un icône d'objectif pour les jalons et ajouter la classe CSS
                task_label = f"<span class='task_milestone'>🎯 {escape(task['name'])}</span>"
            elif task_category == "Livrable":
                # Utiliser une icône de document pour les livrables
                task_label = f"<span class='task_deliverable'>📄 {escape(task['name'])}</span>"
            elif task_category == "Etude":
                # Utiliser une icône de pile de livres pour les études
                task_label = f"<span class='task_study'>📚 {escape(task['name'])}</span>"
            elif task_category == "Prototype":
                # Utiliser une icône d'outils pour les prototypes
                task_label = f"<span class='task_prototype'>🔧 {escape(task['name'])}</span>"
            elif task_category == "Map-Qual-Val":
                # Utiliser une icône de tube à essai pour les tests
                task_label = f"<span class='task_mapqualval'>🧪 {escape(task['name'])}</span>"
            elif task_category == "Industrialisation":
                # Utiliser une icône d'usine pour l'industrialisation
                task_label = f"<span class='task_industrialisation'>🏭 {escape(task['name'])}</span>"
            else:
                # Icône losange pour les autres tâches
                task_label = f"◆ {escape(task['name'])}"

            existing = row.get(target_period, "")
            if existing.strip():
                row[target_period] = f"{existing}<br>{task_label}"
            else:
                row[target_period] = task_label

            tasks_per_period[due_idx].append(task)

    # Construire les tooltips finaux en combinant projet + tâches de la période
    for idx, period in enumerate(period_labels):
        if tasks_per_period[idx]:
            task_lines = [
                f"- {t['name']} (échéance {t['due_date'].strftime('%d/%m/%Y')}) [{t.get('progress', '0%')}]"
                for t in tasks_per_period[idx]
            ]
            tooltip_full = f"{project_tooltip}\nTâches:\n" + "\n".join(task_lines)
            row_tooltips[idx + 1] = tooltip_full
    tableau_data.append(row)
    tableau_styles.append(row_styles)
    tableau_tooltips.append(row_tooltips)

# Créer un DataFrame
df_tableau = pd.DataFrame(tableau_data)

# Générer le HTML du tableau avec styles personnalisés
st.subheader("Planning Gantt (Tableau)")

# CSS personnalisé pour le tableau (utilise les variables CSS du thème)
st.markdown("""
<style>
    table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        border: 1px solid var(--color-table-border);
        background-color: var(--color-table-bg);
    }
    th {
        padding: 8px;
        text-align: center;
        height: 30px;
        background-color: transparent;
        font-weight: bold;
        border-bottom: 2px solid var(--color-table-border);
        border-right: none;
        border-top: none;
        border-left: none;
        color: var(--color-table-text);
    }
    td {
        padding: 8px;
        text-align: center;
        height: 30px;
        border: none !important;
        background-color: var(--color-cell-bg);
        color: var(--color-table-text);
    }
    .row_label {
        text-align: left;
        font-weight: normal;
        border-right: 1px solid var(--color-table-border) !important;
    }
    .project_label {
        font-weight: bold;
    }
    .task_label {
        font-style: italic;
    }
    .active {
        background-color: var(--color-project-bg);
        color: var(--color-text-on-color);
    }
    .not_started {
        background-color: #424242;
        color: var(--color-text-on-color);
    }
    .overdue {
        background-color: #4a2f0c;
        color: var(--color-text-on-color);
    }
    .critical {
        background-color: #571208;
        color: var(--color-text-on-color);
    }
    .standby {
        background-color: #1e0636;
        color: var(--color-text-on-color);
    }
    .inactive {
        background-color: transparent;
    }
    .task_due {
        background-color: var(--color-task-due-bg);
        color: var(--color-text-on-color);
    }
    .task_milestone {
        color: #ff1744;
        font-weight: bold;
    }
    .task_deliverable {
        color: #ff9800;
        font-weight: bold;
    }
    .task_study {
        color: #66bb6a;
        font-weight: bold;
    }
    .task_prototype {
        color: #ffb366;
        font-weight: bold;
    }
    .task_mapqualval {
        color: #ce93d8;
        font-weight: bold;
    }
    .task_industrialisation {
        color: #64b5f6;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)
# Construire le HTML du tableau
html_table = '<table>'

# En-tête
html_table += '<tr><th style="text-align: left;">Projet/Tâche</th><th style="text-align: left;">En retard</th>'
for period in period_labels:
    html_table += f'<th style="font-size: 11px;">{period}</th>'
html_table += '</tr>'

# Date actuelle pour détecter les tâches en retard
today = datetime.now()

# Lignes de données
for row_idx, (_, row) in enumerate(df_tableau.iterrows()):
    html_table += '<tr>'
    # Première colonne (Projet/Tâche)
    project_name = row['Projet/Tâche']
    
    # Colonne projet/tâche
    if project_name.startswith('📋'):
        html_table += f'<td class="row_label project_label">{project_name}</td>'
    else:
        html_table += f'<td class="row_label task_label">{project_name}</td>'
    
    # Deuxième colonne (En retard) - afficher les tâches en retard du projet
    if project_name.startswith('📋'):
        # C'est un projet - chercher ses tâches en retard (filtrées par catégorie)
        project_full_name = project_name.replace('📋 ', '')
        current_project = next((p for p in st.session_state.projects if p["name"] == project_full_name), None)
        overdue_tasks = []
        if current_project and "tasks" in current_project:
            overdue_tasks = [
                t for t in current_project["tasks"] 
                if t["due_date"] < today 
                and t.get("category", "Jalon") in st.session_state.filtered_categories
                and t.get("progress", "0%") != "100%"
            ]
        
        if overdue_tasks:
            overdue_html = "<br>".join([f"⚠️ {escape(t['name'])}" for t in overdue_tasks])
            # Créer un tooltip avec les détails des tâches en retard
            tooltip_lines = [f"Tâches en retard pour {project_full_name}:"]
            tooltip_lines.extend([
                f"- {t['name']} (échéance {t['due_date'].strftime('%d/%m/%Y')}) [{t.get('progress', '0%')}]"
                for t in overdue_tasks
            ])
            tooltip_text = "\n".join(tooltip_lines)
            tooltip_attr = f' title="{escape(tooltip_text)}"'
            html_table += f'<td style="text-align: left; color: #d32f2f;"{tooltip_attr}>{overdue_html}</td>'
        else:
            html_table += '<td style="text-align: left;"></td>'
    else:
        html_table += '<td style="text-align: left;"></td>'
    
    # Colonnes de périodes
    for period in period_labels:
        style_class = tableau_styles[row_idx][period_labels.index(period) + 1]
        cell_content = row.get(period, "")
        tooltip_text = tableau_tooltips[row_idx][period_labels.index(period) + 1]
        tooltip_attr = f' title="{escape(tooltip_text)}"' if tooltip_text else ""
        html_table += f'<td class="{style_class}"{tooltip_attr}>{cell_content}</td>'
    
    html_table += '</tr>'

html_table += '</table>'

# Afficher le tableau HTML
st.markdown(html_table, unsafe_allow_html=True)

# Section d'édition de projet - accessible en cliquant sur un projet dans le tableau
st.markdown("---")
st.markdown("**✏️ Modifier un projet**")

if len(st.session_state.projects) > 0:
    filtered_projects = [p for p in st.session_state.projects if p["name"] in st.session_state.filtered_projects and p.get("status", "Pas démarré") in st.session_state.filtered_statuses]
    if len(filtered_projects) > 0:
        # Afficher les popovers pour chaque projet
        for project in filtered_projects:
            with st.popover(f"📋 {project['name']}", use_container_width=True):
                st.markdown(f"**Modifier : {project['name']}**")
                
                # Créer 2 colonnes : 1/3 pour les paramètres du projet, 2/3 pour les tâches
                col_params, col_tasks = st.columns([1, 2], gap="large")
                
                # ===== COLONNE 1 : PARAMÈTRES DU PROJET =====
                with col_params:
                    st.markdown("**Paramètres**")
                    
                    # Champs de modification
                    new_project_name = st.text_input(
                        "Nom",
                        value=project["name"],
                        key=f"edit_name_{project['name']}"
                    )
                    
                    new_start_period = st.selectbox(
                        "Début",
                        options=period_labels,
                        index=date_to_period_index(project["start_date"], period_labels, period_starts, period_ends),
                        key=f"edit_start_{project['name']}"
                    )
                    
                    new_end_period = st.selectbox(
                        "Fin",
                        options=period_labels,
                        index=date_to_period_index(project["end_date"], period_labels, period_starts, period_ends),
                        key=f"edit_end_{project['name']}"
                    )
                    
                    status_options = ["Pas démarré", "Dans les temps", "En retard", "Critique", "StandBy"]
                    current_status = project.get("status", "Pas démarré")
                    status_idx = status_options.index(current_status) if current_status in status_options else 0
                    new_status = st.selectbox(
                        "État du projet",
                        options=status_options,
                        index=status_idx,
                        key=f"edit_status_{project['name']}"
                    )
                    
                    col_save, col_delete = st.columns(2)
                    with col_save:
                        if st.button("💾 Sauvegarder", key=f"save_project_{project['name']}", use_container_width=True):
                            # Trouver l'index du projet
                            proj_idx = next(i for i, p in enumerate(st.session_state.projects) if p["name"] == project["name"])
                            
                            # Vérifier les dates
                            start_date = period_starts[period_labels.index(new_start_period)]
                            end_date = period_ends[period_labels.index(new_end_period)]
                            
                            if end_date < start_date:
                                st.error("La période de fin doit être après la période de début.")
                            else:
                                # Mettre à jour le projet
                                st.session_state.projects[proj_idx]["name"] = new_project_name.strip()
                                st.session_state.projects[proj_idx]["start_date"] = start_date
                                st.session_state.projects[proj_idx]["end_date"] = end_date
                                st.session_state.projects[proj_idx]["status"] = new_status
                                
                                # Trier les projets par ordre alphabétique
                                st.session_state.projects.sort(key=lambda p: p["name"].lower())
                                sync_db()  # Sauvegarder dans la DB
                                
                                st.success("Projet modifié.")
                                st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Supprimer", key=f"delete_project_{project['name']}", use_container_width=True):
                            proj_idx = next(i for i, p in enumerate(st.session_state.projects) if p["name"] == project["name"])
                            deleted_name = st.session_state.projects[proj_idx]["name"]
                            st.session_state.projects.pop(proj_idx)
                            
                            # Mettre à jour le filtre si le projet supprimé était sélectionné
                            if deleted_name in st.session_state.filtered_projects:
                                st.session_state.filtered_projects.remove(deleted_name)
                            
                            sync_db()  # Sauvegarder dans la DB
                            st.success(f"Projet supprimé.")
                            st.rerun()
                
                # ===== COLONNE 2 : GESTION DES TÂCHES =====
                with col_tasks:
                    st.markdown("**Tâches**")
                    
                    # Afficher les tâches existantes
                    proj_idx = next(i for i, p in enumerate(st.session_state.projects) if p["name"] == project["name"])
                    tasks = st.session_state.projects[proj_idx].get("tasks", [])
                    
                    # Affichage avec scrollable si beaucoup de tâches
                    if len(tasks) > 0:
                        task_container = st.container(border=True, height=250)
                        with task_container:
                            for task_idx, task in enumerate(tasks):
                                # Trouver l'index de la période actuelle
                                current_period_idx = date_to_period_index(task["due_date"], period_labels, period_starts, period_ends)
                                current_progress = task.get('progress', '0%')
                                progress_options = ["0%", "50%", "100%"]
                                progress_idx = progress_options.index(current_progress) if current_progress in progress_options else 0
                                
                                # Catégorie de la tâche
                                category_options = ["Jalon", "Livrable", "Etude", "Prototype", "Map-Qual-Val", "Industrialisation"]
                                current_category = task.get('category', 'Jalon')
                                category_idx = category_options.index(current_category) if current_category in category_options else 0
                                
                                # Tout sur une seule ligne avec colonnes
                                col_name, col_category, col_due, col_progress, col_save, col_delete = st.columns([2.5, 1.5, 1.5, 1.2, 0.4, 0.4])
                                
                                with col_name:
                                    task_name_edit = st.text_input(
                                        f"T{task_idx+1}",
                                        value=task['name'],
                                        key=f"edit_task_name_{project['name']}_{task_idx}",
                                        label_visibility="collapsed",
                                        placeholder="Nom de la tâche"
                                    )
                                
                                with col_category:
                                    task_category_edit = st.selectbox(
                                        "Catégorie",
                                        options=category_options,
                                        index=category_idx,
                                        key=f"edit_task_category_{project['name']}_{task_idx}",
                                        label_visibility="collapsed"
                                    )
                                
                                with col_due:
                                    task_due_date_edit = st.date_input(
                                        "Dateîchance",
                                        value=task["due_date"].date(),
                                        key=f"edit_task_due_{project['name']}_{task_idx}",
                                        label_visibility="collapsed"
                                    )
                                
                                with col_progress:
                                    task_progress_edit = st.selectbox(
                                        "État",
                                        options=progress_options,
                                        index=progress_idx,
                                        key=f"edit_task_progress_{project['name']}_{task_idx}",
                                        label_visibility="collapsed"
                                    )
                                
                                with col_save:
                                    if st.button("💾", key=f"save_task_{project['name']}_{task_idx}", use_container_width=True, help="Sauvegarder"):
                                        if task_name_edit.strip() == "":
                                            st.error("Nom requis.")
                                        else:
                                            # Mettre à jour la tâche avec la date choisie
                                            new_due_date = datetime.combine(task_due_date_edit, datetime.min.time())
                                            st.session_state.projects[proj_idx]["tasks"][task_idx] = {
                                                "name": task_name_edit.strip(),
                                                "due_date": new_due_date,
                                                "progress": task_progress_edit,
                                                "category": task_category_edit
                                            }
                                            sync_db()  # Sauvegarder dans la DB
                                            st.rerun()
                                
                                with col_delete:
                                    if st.button("🗑️", key=f"delete_task_{project['name']}_{task_idx}", use_container_width=True, help="Supprimer"):
                                        st.session_state.projects[proj_idx]["tasks"].pop(task_idx)
                                        sync_db()  # Sauvegarder dans la DB
                                        st.rerun()
                    else:
                        st.caption("Aucune tâche")
                    
                    st.divider()

                    # Bloc compact: deux lignes (création en haut, import en bas)
                    with st.container(border=True):
                        # Ligne 1: Création de tâche (Nom, Catégorie, Date, État, Ajouter)
                        task_name_col, task_cat_col, task_due_col, task_prog_col, task_add_col = st.columns([2.2, 1.2, 1.6, 1.2, 0.8])
                        
                        # Utiliser un compteur pour réinitialiser le champ Nom après chaque création
                        if "task_reset_count" not in st.session_state:
                            st.session_state.task_reset_count = {}
                        if project['name'] not in st.session_state.task_reset_count:
                            st.session_state.task_reset_count[project['name']] = 0
                        
                        with task_name_col:
                            task_name = st.text_input(
                                "Nom",
                                value="",
                                key=f"task_name_{project['name']}_{st.session_state.task_reset_count[project['name']]}",
                                label_visibility="collapsed",
                                placeholder="Nom"
                            )
                        with task_cat_col:
                            task_category = st.selectbox(
                                "Catégorie",
                                options=["Jalon", "Livrable", "Etude", "Prototype", "Map-Qual-Val", "Industrialisation"],
                                index=0,
                                key=f"task_category_{project['name']}",
                                label_visibility="collapsed"
                            )
                        with task_due_col:
                            task_due_date = st.date_input(
                                "Date",
                                value=(datetime.now() + timedelta(days=7)).date(),
                                key=f"task_due_{project['name']}",
                                label_visibility="collapsed"
                            )
                        with task_prog_col:
                            task_progress = st.selectbox(
                                "État",
                                options=["0%", "50%", "100%"],
                                index=0,
                                key=f"task_progress_{project['name']}",
                                label_visibility="collapsed"
                            )
                        with task_add_col:
                            if st.button("➕", key=f"add_task_{project['name']}", use_container_width=True, help="Ajouter"):
                                if task_name.strip() == "":
                                    st.error("Nom requis.")
                                else:
                                    due_date = datetime.combine(task_due_date, datetime.min.time())
                                    if "tasks" not in st.session_state.projects[proj_idx]:
                                        st.session_state.projects[proj_idx]["tasks"] = []
                                    st.session_state.projects[proj_idx]["tasks"].append({
                                        "name": task_name.strip(),
                                        "due_date": due_date,
                                        "progress": task_progress,
                                        "category": task_category
                                    })
                                    sync_db()  # Sauvegarder dans la DB
                                    # Incrémenter le compteur pour réinitialiser le champ Nom
                                    st.session_state.task_reset_count[project['name']] += 1
                                    st.success("Tâche créée !")
                                    st.rerun()

                        # Ligne 2: Import Excel (uploader + bouton)
                        up_col, import_col = st.columns([3.2, 0.8])
                        with up_col:
                            uploaded_file = st.file_uploader(
                                "Importer Excel (.xlsx)",
                                type=["xlsx"],
                                accept_multiple_files=False,
                                label_visibility="collapsed",
                                key=f"upload_excel_{project['name']}"
                            )
                        with import_col:
                            if st.button("📥", key=f"import_tasks_{project['name']}", use_container_width=True, help="Importer"):
                                if uploaded_file is None:
                                    st.error("Veuillez sélectionner un fichier Excel.")
                                else:
                                    new_tasks, corrections = parse_tasks_from_excel(uploaded_file, sheet_name="Model Tache")
                                    if len(new_tasks) == 0:
                                        st.warning("Aucune tâche importée.")
                                    else:
                                        if "tasks" not in st.session_state.projects[proj_idx]:
                                            st.session_state.projects[proj_idx]["tasks"] = []
                                        st.session_state.projects[proj_idx]["tasks"].extend(new_tasks)
                                        sync_db()  # Sauvegarder dans la DB
                                        st.success(f"{len(new_tasks)} importées.")
                                        st.rerun()

# Filtres à afficher (affichés sous le tableau)
st.markdown("---")
st.markdown("**Filtres**")

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    all_project_names = [p["name"] for p in projects_full]
    selected_project_names = st.multiselect(
        "Projets à afficher",
        options=all_project_names,
        default=st.session_state.filtered_projects,
        help="Sélectionne un ou plusieurs projets pour les afficher dans le tableau",
        key="filter_projects_selector"
    )

with col_filter2:
    all_categories = ["Jalon", "Livrable", "Etude", "Prototype", "Map-Qual-Val", "Industrialisation"]
    selected_categories = st.multiselect(
        "Catégories de tâches à afficher",
        options=all_categories,
        default=st.session_state.filtered_categories,
        help="Sélectionne une ou plusieurs catégories pour filtrer les tâches",
        key="filter_categories_selector"
    )

with col_filter3:
    all_statuses = ["Pas démarré", "Dans les temps", "En retard", "Critique", "StandBy"]
    selected_statuses = st.multiselect(
        "États des projets à afficher",
        options=all_statuses,
        default=st.session_state.filtered_statuses,
        help="Sélectionne un ou plusieurs états pour filtrer les projets",
        key="filter_statuses_selector"
    )

# Mettre à jour les filtres en session_state et rafraîchir
filter_changed = False
if selected_project_names != st.session_state.filtered_projects:
    st.session_state.filtered_projects = selected_project_names
    filter_changed = True
if selected_categories != st.session_state.filtered_categories:
    st.session_state.filtered_categories = selected_categories
    filter_changed = True
if selected_statuses != st.session_state.filtered_statuses:
    st.session_state.filtered_statuses = selected_statuses
    filter_changed = True
if filter_changed:
    st.rerun()

# Formulaire d'ajout direct affiché sous le tableau (un seul clic pour ajouter)
st.markdown("---")
col_a, col_b, col_c, col_d = st.columns([3,2,2,1])
with col_a:
    new_name = st.text_input("Nom du projet", value="")
with col_b:
    new_start_date = st.date_input("Date de début", value=datetime.now().date())
with col_c:
    new_end_date = st.date_input("Date de fin", value=(datetime.now() + timedelta(days=30)).date())
with col_d:
    if st.button("Ajouter"):
        # Convertir les dates en datetime
        start_datetime = datetime.combine(new_start_date, datetime.min.time())
        end_datetime = datetime.combine(new_end_date, datetime.min.time())
        if new_name.strip() == "":
            st.error("Le nom du projet est requis.")
        elif end_datetime < start_datetime:
            st.error("La date de fin doit être après la date de début.")
        else:
            st.session_state.projects.append({"name": new_name.strip(), "start_date": start_datetime, "end_date": end_datetime, "status": "Pas démarré", "tasks": []})
            # Trier les projets par ordre alphabétique (A → Z)
            st.session_state.projects.sort(key=lambda p: p["name"].lower())
            sync_db()  # Sauvegarder dans la DB
            # Ajouter le nouveau projet au filtre pour qu'il s'affiche
            st.session_state.filtered_projects.append(new_name.strip())
            st.success(f"Projet '{new_name.strip()}' ajouté.")
            # Forcer la réexécution du script pour mettre à jour le graphique immédiatement
            st.rerun()

# Section de gestion de la base de données
st.markdown("---")
st.markdown("### ⚙️ Gestion de la base de données")

with st.expander("🗑️ Supprimer toutes les données"):
    st.warning("⚠️ **Attention** : Cette action supprimera définitivement tous les projets et toutes les tâches de la base de données.")
    confirm_delete = st.checkbox("Je confirme vouloir supprimer toutes les données", key="confirm_db_delete")
    
    if st.button("🗑️ Effacer la base de données", type="primary", disabled=not confirm_delete):
        # Vider la session state
        st.session_state.projects = []
        st.session_state.filtered_projects = []
        # Supprimer la base de données
        projects_table.truncate()
        st.success("✅ Base de données effacée avec succès!")
        st.rerun()
