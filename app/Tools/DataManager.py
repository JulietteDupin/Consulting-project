from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QComboBox, QFormLayout
)
import os

class DataManager(QMainWindow):
    def __init__(self, image_directory, eating_habits_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des données")
        self.image_directory = image_directory
        self.eating_habits_file = eating_habits_file

        # Créer un widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Interface principale
        main_layout = QVBoxLayout()

        # Boutons pour naviguer entre les images
        self.prev_button = QPushButton("Supprimer les habitudes alimentaires des animaux")
        self.prev_button.clicked.connect(self.delete_eating_habits_file)
        main_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Supprimer les images non reconnues")
        self.next_button.clicked.connect(self.delete_unrecognised_images)
        main_layout.addWidget(self.next_button)
        
        central_widget.setLayout(main_layout)



    def delete_eating_habits_file(self):
        """Affiche l'image précédente."""
        os.remove(self.eating_habits_file)

    def delete_unrecognised_images(self):
        """Affiche l'image suivante."""
        for filename in os.listdir(self.image_directory):
            file_path = os.path.join(self.image_directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(filename, "is removed")