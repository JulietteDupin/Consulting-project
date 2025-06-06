import os
import json
from PyQt5.QtCore import QDate  # Assurez-vous que PyQt5 est installé

# Enregistre les habitudes alimentaires des animaux
import os
import json
from PyQt5.QtCore import QDateTime

class EatingHabits:
    def __init__(self, file_path="./datas/eating_habits.json"):
        """Initialise les habitudes alimentaires depuis un fichier JSON."""
        self.file_path = file_path
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.habits = json.load(f)
        else:
            self.habits = {}

    def record_eating(self, day, hour, count):
        """Enregistre le nombre de repas pour un jour donné et une heure spécifique."""
        if day not in self.habits:
            self.habits[day] = {}
        self.habits[day][hour] = count
        self.save()

    def save(self):
        """Sauvegarde les habitudes alimentaires dans un fichier."""
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.habits, f)
            #print("Les habitudes alimentaires ont été sauvegardées avec succès.")
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {str(e)}.")

    def get_average(self, animal=""):
        """
        Calcule la moyenne des repas depuis minuit jusqu'à l'heure actuelle pour les 7 derniers jours.
        Si un animal spécifique est donné, retourne la moyenne pour cet animal uniquement.
        """
        now = QDateTime.currentDateTime()
        current_hour = int(now.toString("h"))  # Heure actuelle
        today = now.toString("yyyy-MM-dd")
        
        # Récupérer les 7 derniers jours
        sorted_days = sorted(self.habits.keys())[-7:]
        
        # Accumuler les repas de minuit à l'heure actuelle
        total_meals = {}
        total_hours = 0
        for day in sorted_days:
            if day in self.habits:
                for hour in range(0, current_hour + 1):  # De minuit à l'heure actuelle
                    str_hour = str(hour)
                    if str_hour not in self.habits[day]:
                        continue  # Passer si l'heure n'est pas enregistrée
                    for recorded_animal, count in self.habits[day][str_hour].items():
                        if recorded_animal in total_meals:
                            total_meals[recorded_animal] += count
                        else:
                            total_meals[recorded_animal] = count
                    total_hours += 1
        
        # Calculer la moyenne
        if animal == "":
            # Retourner les moyennes pour tous les animaux
            for recorded_animal in total_meals:
                total_meals[recorded_animal] = total_meals[recorded_animal] / total_hours if total_hours > 0 else 0
            return total_meals
        else:
            # Retourner la moyenne pour l'animal spécifié
            if animal in total_meals:
                return total_meals[animal] / total_hours if total_hours > 0 else 0
            else:
                return 0  # Si l'animal n'est pas enregistré

    def check_for_change(self):
        """
        Vérifie si le comportement alimentaire actuel (de minuit à l'heure actuelle) est significativement
        inférieur à la moyenne (moins de 75% de la moyenne).
        """
        alert_for_animal = ""
        now = QDateTime.currentDateTime()
        current_hour = int(now.toString("h"))
        today = now.toString("yyyy-MM-dd")
    
        # Calcule la moyenne historique
        average = self.get_average()  # Dictionnaire avec les moyennes par animal
        #print("Average consumption:", average)
    
        # Calcule les repas actuels de minuit à l'heure actuelle
        current_meals = {}
        if today in self.habits:
            for hour in range(0, current_hour + 1):  # Parcourir de minuit à l'heure actuelle
                str_hour = str(hour)
                if str_hour in self.habits[today]:
                    for animal, count in self.habits[today][str_hour].items():
                        current_meals[animal] = current_meals.get(animal, 0) + count
    
        # Vérifie si les repas actuels sont en dessous de 75% de la moyenne
        alert = False
        for animal, current_count in current_meals.items():
            if animal in average:  # Vérifie si l'animal a une moyenne calculée
                if current_count < (average[animal] * 0.80):
                    #print(f"Alerte : consommation de {animal} en dessous de 90% de la moyenne.")
                    alert = True
                    alert_for_animal = animal
                if current_count > (average[animal] * 1.2):
                    #print(f"Alerte : consommation de {animal} au dessus de 110% de la moyenne.")
                    alert = True
                    alert_for_animal = animal
        return alert, animal
