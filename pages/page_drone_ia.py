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
from styles import COULEURS, bouton_flat

class PageDroneIA(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Calcul d’ajustement ISO", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.diametre_entry = self._champ(form_frame, "Diamètre nominal (mm)", 0)
        self.alésage_var = tk.StringVar(value="H7")
        self.arbre_var = tk.StringVar(value="g6")

        # Menus déroulants
        self._menu(form_frame, "Tolérance de l’alésage", self.alésage_var, ["H7", "H8", "H6"], 1)
        self._menu(form_frame, "Tolérance de l’arbre", self.arbre_var, ["g6", "f7", "k6", "m6"], 2)

        bouton_flat(self, "Calculer", self.calculer_ajustement).pack(pady=15)

        self.resultat_label = tk.Label(self, text="", bg=COULEURS["fond"],
                                       fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat_label.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def _champ(self, parent, label, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.grid(row=row, column=1, padx=10)
        return e

    def _menu(self, parent, label, variable, options, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        tk.OptionMenu(parent, variable, *options).grid(row=row, column=1, padx=10)

    def calculer_ajustement(self):
        # Valeurs typiques d'écart pour un diamètre nominal entre 10 et 50 mm
        ISO_TOLERANCES = {
            "H7": (0, +21),
            "H8": (0, +33),
            "H6": (0, +13),
            "g6": (-14, -4),
            "f7": (-20, -6),
            "k6": (+2, +10),
            "m6": (+8, +20)
        }

        try:
            d = float(self.diametre_entry.get())
        except ValueError:
            self.resultat_label.config(text="Diamètre invalide.")
            return

        ales_min, ales_max = ISO_TOLERANCES[self.alésage_var.get()]
        arb_min, arb_max = ISO_TOLERANCES[self.arbre_var.get()]

        # Jeu en microns → mm
        jeu_min = (ales_min - arb_max) / 1000
        jeu_max = (ales_max - arb_min) / 1000

        if jeu_max < 0:
            ajustement = "Serré"
        elif jeu_min > 0:
            ajustement = "Libre"
        else:
            ajustement = "Incertain / glissant"

        self.resultat_label.config(text=f"""
Jeu minimal : {jeu_min:.3f} mm
Jeu maximal : {jeu_max:.3f} mm
Type d’ajustement : {ajustement}
""")