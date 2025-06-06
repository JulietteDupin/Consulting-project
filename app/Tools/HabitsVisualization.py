from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import json
import numpy as np

class HabitsVisualization(QMainWindow):
    def __init__(self, habits_file="./datas/eating_habits.json"):
        super().__init__()
        print("Initialisation de HabitsVisualization...")
        self.habits_file = habits_file

        # Charger les données
        try:
            self.data = self.load_habits()
            #print(f"Données chargées : {self.data}")
        except Exception as e:
            print(f"Erreur : {e}")
            self.data = {}

        # Initialiser les animaux dynamiquement
        self.animals = self.extract_animals(self.data)
        print(f"Animaux extraits : {self.animals}")

        # Créer le layout
        layout = QVBoxLayout()

        # Ajouter le graphique
        self.canvas = FigureCanvas(plt.figure(figsize=(10, 6)))  # Figure pour pyplot
        layout.addWidget(self.canvas)
        print("Canvas initialisé.")

        # Ajouter une combobox pour sélectionner l'animal
        self.animal_combobox = QComboBox()
        self.animal_combobox.addItems(self.animals)
        self.animal_combobox.currentIndexChanged.connect(self.update_graph)
        layout.addWidget(self.animal_combobox)
        print("ComboBox pour les animaux ajoutée.")

        self.plot_habits(self.animals[0])  # Initialiser avec un animal par défaut

        # Ajouter un bouton pour actualiser les données
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        print("Bouton d'actualisation ajouté.")

        # Configuration de la fenêtre principale
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        print("HabitsVisualization configurée.")

    def load_habits(self):
        """Charger les données à partir du fichier JSON."""
        try:
            if os.path.exists(self.habits_file):
                with open(self.habits_file, "r") as f:
                    return json.load(f)
            else:
                print(f"Le chemin n'existe pas : {self.habits_file}")
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement des habitudes : {e}")
            return {}

    def extract_animals(self, data):
        """Extraire dynamiquement les animaux présents dans les données."""
        animals = set()
        # Parcourir les jours et les heures pour extraire les animaux
        for day, hours in data.items():
            for hour, birds in hours.items():
                for animal in birds.keys():
                    animals.add(animal)  # Ajouter l'animal à l'ensemble
        return sorted(list(animals))  # Retourner une liste triée d'animaux


    def plot_habits(self, selected_animal):
        """Tracer les habitudes alimentaires sous forme de courbe moyenne par heure."""
        plt.clf()  # Effacer le graphique précédent
        fig, ax = plt.subplots(figsize=(10, 6))
    
        # Dictionnaire pour stocker la somme et le nombre d'observations par heure
        hourly_sums = {}
        hourly_counts = {}
    
        # Parcourir toutes les données
        for day, hours in self.data.items():
            for hour, birds in hours.items():
                hour_int = int(hour)  # Convertir en entier
                meals = birds.get(selected_animal, 0)
    
                # Ajouter les repas à la somme et incrémenter le nombre d'observations
                if hour_int not in hourly_sums:
                    hourly_sums[hour_int] = 0
                    hourly_counts[hour_int] = 0
                hourly_sums[hour_int] += meals
                hourly_counts[hour_int] += 1
    
        # Trier les heures pour éviter les allers-retours
        hours_list = sorted(hourly_sums.keys())  # Liste des heures triées (ex: [1, 9, 10, 11, 14, 15, 20, 21, 22])
        meal_averages = [hourly_sums[h] / hourly_counts[h] for h in hours_list]
    
        # Tracer la courbe moyenne
        ax.plot(hours_list, meal_averages, marker='o', linestyle='-', color='b', label="Moyenne par heure")
    
        # Définir les étiquettes et le titre
        ax.set_title(f"Moyenne des repas par heure - {selected_animal}")
        ax.set_xlabel("Heure de la journée")
        ax.set_ylabel("Nombre moyen de repas")
        ax.set_xticks(np.arange(0, 24, 1))  # Afficher chaque heure sur l'axe X
        ax.set_xlim(0, 23)  # Assurer une plage fixe de 0h à 23h pour éviter un mauvais affichage
        ax.legend()
    
        self.canvas.figure = fig  # Assigner la figure au canvas
        self.canvas.draw()

    def refresh_data(self):
        """Rafraîchir les données et le graphique."""
        self.data = self.load_habits()
        selected_animal = self.animal_combobox.currentText()  # Récupérer l'animal sélectionné
        self.plot_habits(selected_animal)

    def update_graph(self):
        """Mettre à jour le graphique en fonction de l'animal sélectionné."""
        selected_animal = self.animal_combobox.currentText()  # Récupérer l'animal sélectionné
        self.plot_habits(selected_animal)
