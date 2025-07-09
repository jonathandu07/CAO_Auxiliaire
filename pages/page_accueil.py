import tkinter as tk
import os
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from mpl_toolkits.basemap import Basemap
from materiaux import MATERIAUX
import math
import pandas as pd
import matplotlib.pyplot as plt

class PageAccueil(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        # Logo de ta boîte (au-dessus du titre)
        logo_path = "JN-BWF.png"  # 🖼️ remplace par le chemin exact
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            image = image.resize((128, 128), Image.LANCZOS)  # ou 64x64 selon le rendu souhaité
            self.logo_image = ImageTk.PhotoImage(image)
            tk.Label(self, image=self.logo_image, bg=COULEURS["fond"]).pack(pady=(20, 10))

        # Titre de l'application
        tk.Label(self, text="Assistant de CAO", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        # Boutons uniquement en texte
        boutons = [
            ("Calculs RDM", PageCalculs),
            ("Matériaux", PageMateriaux),
            ("Paramètres", PageParametres),
            ("Conception moteur Stirling", PageMoteurStirling),
            ("Structure du drone", PageDroneStructure),
            ("Propulsion du drone", PageDronePropulsion),
            ("Électronique & IA du drone", PageDroneIA),
            ("Simulation de mission", PageSimulationMission),
            ("Boîte à crabots automatique", PageBoiteCrabot),
            ("Conception piston Stirling (galette)", PagePistonStirling),
            ("Dimensionnement vilebrequin", PageVilebrequin),
            ("Dimensionnement moteur Stirling", PageDimensionnementStirling),
        ]

        for txt, page in boutons:
            b = bouton_flat(self, txt, lambda p=page: controller.afficher_page(p))
            b.pack(pady=5)
