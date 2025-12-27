# Importer le module datetime pour manipuler les dates et les semaines
from datetime import datetime, timedelta
# Importer le module calendar pour obtenir les informations sur les calendriers
import calendar

# Définir la date d'aujourd'hui
date_debut = datetime.now()

# Afficher le titre du planning
print("=" * 80)
print(f"PLANNING OBEYA - À partir du {date_debut.strftime('%d/%m/%Y')}")
print("=" * 80)
print()

# ============================================================================
# PARTIE 1: AFFICHER LES 12 PROCHAINES SEMAINES
# ============================================================================
print("📅 LES 12 PROCHAINES SEMAINES")
print("-" * 80)

# Initialiser un compteur pour les semaines
compteur_semaine = 0

# Boucle pour afficher chaque semaine des 12 prochaines semaines
for i in range(12):
    # Calculer la date de début de la semaine courante
    date_semaine_debut = date_debut + timedelta(weeks=i)
    # Calculer la date de fin de la semaine (7 jours après le début)
    date_semaine_fin = date_semaine_debut + timedelta(days=6)
    # Incrémenter le compteur de semaine
    compteur_semaine += 1
    
    # Afficher le numéro de la semaine et la plage de dates
    print(f"Semaine {compteur_semaine:2d} : {date_semaine_debut.strftime('%d/%m/%Y')} - {date_semaine_fin.strftime('%d/%m/%Y')} | {date_semaine_debut.strftime('%A')} au {date_semaine_fin.strftime('%A')}")

# Ajouter une ligne vide pour la séparation
print()

# ============================================================================
# PARTIE 2: AFFICHER LES 6 MOIS SUIVANTS À PARTIR DE LA 12ème SEMAINE
# ============================================================================
print("📊 LES 6 MOIS SUIVANTS (À partir de la semaine 13)")
print("-" * 80)

# Calculer la date de début pour les 6 mois (après la 12ème semaine)
date_mois_debut = date_debut + timedelta(weeks=12)

# Initialiser un compteur pour les mois
compteur_mois = 0

# Boucle pour afficher chaque mois des 6 prochains mois
for i in range(6):
    # Initialiser le jour du mois à 1
    jour = 1
    # Initialiser le mois courant et l'année courante en fonction du nombre de mois écoulés
    mois = (date_mois_debut.month + i - 1) % 12 + 1
    # Calculer l'année en ajoutant le nombre d'années complètes au mois courant
    annee = date_mois_debut.year + (date_mois_debut.month + i - 1) // 12
    # Incrémenter le compteur de mois
    compteur_mois += 1
    
    # Obtenir le nombre de jours dans le mois courant
    nombre_jours_mois = calendar.monthrange(annee, mois)[1]
    # Créer la date de début du mois
    date_mois_debut_courant = datetime(annee, mois, 1)
    # Créer la date de fin du mois
    date_mois_fin = datetime(annee, mois, nombre_jours_mois)
    
    # Obtenir le nom du mois en français
    noms_mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    # Obtenir le nom du mois actuel
    nom_mois = noms_mois[mois - 1]
    
    # Afficher le mois avec sa plage de dates
    print(f"Mois {compteur_mois:2d} : {nom_mois:10s} {annee} | {date_mois_debut_courant.strftime('%d/%m/%Y')} - {date_mois_fin.strftime('%d/%m/%Y')} | ({nombre_jours_mois} jours)")

# Ajouter une ligne vide pour la séparation
print()

# ============================================================================
# AFFICHER UN RÉSUMÉ DU PLANNING
# ============================================================================
print("=" * 80)
# Calculer la date de fin totale (fin de la 6ème mois)
date_fin_total = date_debut + timedelta(weeks=12) + timedelta(days=180)
# Afficher le résumé avec les dates de début et fin
print(f"Résumé : {compteur_semaine} semaines + {compteur_mois} mois | Du {date_debut.strftime('%d/%m/%Y')} au {date_fin_total.strftime('%d/%m/%Y')}")
print("=" * 80)
