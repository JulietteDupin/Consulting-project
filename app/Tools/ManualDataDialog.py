from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton  # Pour les éléments de l'interface utilisateur
from PyQt5.QtCore import QDate  # Pour gérer la date

class ManualDataDialog(QDialog):
    """Fenêtre pour entrer manuellement les données de prise alimentaire"""
    def __init__(self, habits):
        super().__init__()
        self.habits = habits
        self.setWindowTitle("Ajouter Manuellement les Données Alimentaires")
        
        # Mise en place de l'interface
        layout = QFormLayout()
        
        self.count_input = QLineEdit(self)
        self.count_input.setPlaceholderText("Entrez le nombre de repas aujourd'hui")
        layout.addRow("Nombre de repas:", self.count_input)
        
        self.submit_btn = QPushButton("Soumettre", self)
        self.submit_btn.clicked.connect(self.submit_data)
        layout.addRow(self.submit_btn)
        
        self.setLayout(layout)

    def submit_data(self):
        """Soumettre les données et les enregistrer"""
        try:
            count = int(self.count_input.text())
            today = QDate.currentDate().toString("yyyy-MM-dd")
            self.habits.record_eating(today, count)
            self.accept()  # Fermer la fenêtre après soumission
        except ValueError:
            print("Erreur : Veuillez entrer un nombre valide.")
            self.count_input.clear()
