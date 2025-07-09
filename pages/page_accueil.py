# pages\page_accueil.py
import tkinter as tk
import os
from PIL import Image, ImageTk
from styles import COULEURS, bouton_flat
from pages.page_calculs import PageCalculs
from pages.page_materiaux import PageMateriaux
from pages.page_parametres import PageParametres
# PAS D'IMPORT PageMoteurStirling ICI !
from pages.page_drone_structure import PageDroneStructure
from pages.page_drone_propulsion import PageDronePropulsion
from pages.page_drone_ia import PageDroneIA
from pages.page_simulation_mission import PageSimulationMission
from pages.page_boite_crabot import PageBoiteCrabot

class PageAccueil(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        # Logo
        logo_path = "JN-BWF.png"
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            image = image.resize((128, 128), Image.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(image)
            tk.Label(self, image=self.logo_image, bg=COULEURS["fond"]).pack(pady=(20, 10))

        # Titre
        tk.Label(self, text="Assistant de CAO", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        boutons = [
            ("Calculs RDM", PageCalculs),
            ("Matériaux", PageMateriaux),
            ("Paramètres", PageParametres),
            ("Conception moteur Stirling", "PageMoteurStirling"),  # on met une string !
            ("Structure du drone", PageDroneStructure),
            ("Propulsion du drone", PageDronePropulsion),
            ("Électronique & IA du drone", PageDroneIA),
            ("Simulation de mission", PageSimulationMission),
            ("Boîte à crabots automatique", PageBoiteCrabot),
        ]

        for txt, page in boutons:
            if page == "PageMoteurStirling":
                def show_stirling(p=page):
                    from pages.page_moteur_stirling import PageMoteurStirling
                    controller.afficher_page(PageMoteurStirling)
                b = bouton_flat(self, txt, show_stirling)
            else:
                b = bouton_flat(self, txt, lambda p=page: controller.afficher_page(p))
            b.pack(pady=5)
