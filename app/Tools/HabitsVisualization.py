from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import json


class HabitsVisualization(QMainWindow):
    def __init__(self, habits_file="./datas/eating_habits.json"):
        super().__init__()
        print("Initialisation de HabitsVisualization...")
        self.habits_file = habits_file

        # Charger les données
        try:
            self.data = self.load_habits()
            print(f"Données chargées : {self.data}")
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
        """Tracer les habitudes alimentaires sous forme de courbes pour un animal sélectionné."""
        plt.clf()  # Effacer le graphique précédent
        fig, ax = plt.subplots(figsize=(10, 6))

        # Préparer les données pour l'affichage
        for day, hours in self.data.items():
            # Trier les heures dans l'ordre croissant
            sorted_hours = sorted(hours.items(), key=lambda x: int(x[0]) if x[0].isdigit() else int(x[0].split(":")[0]))

            hours_list = []  # Liste des heures pour ce jour
            meals_list = []  # Liste des repas pour ce jour

            for hour, birds in sorted_hours:
                # Calculer le nombre de repas pour l'animal sélectionné
                meals = birds.get(selected_animal, 0)  # Nombre de repas pour l'animal
                hours_list.append(int(hour))  # Ajouter l'heure convertie en entier
                meals_list.append(meals)  # Ajouter le nombre de repas

            # Tracer une ligne pour ce jour
            ax.plot(hours_list, meals_list, marker='o', label=f"Jour {day}")

        # Définir les étiquettes et le titre
        ax.set_title(f"Habitudes Alimentaires pour {selected_animal}")
        ax.set_xlabel("Heures")
        ax.set_ylabel("Nombre de repas")
        ax.legend(title="Jours")  # Ajouter une légende avec un titre
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
