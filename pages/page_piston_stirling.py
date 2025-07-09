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

class PagePistonStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Conception piston Stirling (galette)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        descr = ("Ce calculateur estime toutes les côtes d’un piston galette pour moteur Stirling mono-cylindre.\n"
                 "⚙️ Utilise la même architecture que la page moteur : entre les mêmes données de base.")
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        self.champs = {}
        donnees = [
            ("Diamètre du cylindre (mm)", "d_cyl"),
            ("Hauteur utile du cylindre (mm)", "h_cyl_utile"),
            ("Nombre de joints", "nb_joints"),
            ("Température chaude max (°C)", "t_chaude"),
            ("Matériau du piston", "materiau_piston")
        ]
        for label, cle in donnees:
            f = tk.Frame(self, bg=COULEURS["fond"])
            tk.Label(f, text=label, font=("Segoe UI", 10), width=30, anchor="w",
                     bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left")
            entry = tk.Entry(f, width=15, font=("Segoe UI", 10))
            entry.pack(side="right")
            f.pack(pady=5)
            self.champs[cle] = entry

        # Valeurs par défaut pour le matériau du piston
        self.champs["materiau_piston"].insert(0, "Alu 2017A / 6082 / Graphite")

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Segoe UI", 10), justify="left")
        self.resultat.pack(pady=10)

        bouton_flat(self, "Calculer le piston", self.calculer_piston).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def calculer_piston(self):
        try:
            # --- Lecture et valeurs standard ---
            d_cyl = float(self.champs["d_cyl"].get())
            h_cyl_utile = float(self.champs["h_cyl_utile"].get())
            nb_joints = int(self.champs["nb_joints"].get()) if self.champs["nb_joints"].get() else 2
            t_chaude = float(self.champs["t_chaude"].get()) if self.champs["t_chaude"].get() else 650
            mat_piston = self.champs["materiau_piston"].get().strip() or "Aluminium 2017A"

            # Cotes typiques pour piston galette :
            jeu_lateral = 0.03 * d_cyl    # Jeu latéral entre piston et cylindre (3% du Ø, min 0.03 mm)
            epaisseur_piston = max(0.16 * d_cyl, 8)  # Galette (16% du Ø mini 8mm)
            profondeur_rainure = 1.6      # mm (rainure à joint torique)
            largeur_rainure = 2.4         # mm (joint Viton standard)
            epaisseur_fond = 0.12 * d_cyl # Fond de la galette (12% du Ø)
            surface_piston = np.pi * (d_cyl / 2) ** 2  # mm²

            masse_piston = (surface_piston * epaisseur_piston * 2.8e-3) / 1000  # Aluminium, densité ≈ 2.8g/cm³

            # Température max selon matériau
            if "graphite" in mat_piston.lower():
                temp_max = 300  # °C (auto-lubrifiant)
            elif "alu" in mat_piston.lower() or "aluminium" in mat_piston.lower():
                temp_max = 200
            elif "acier" in mat_piston.lower():
                temp_max = 500
            else:
                temp_max = 200

            # Résumé fabrication
            consignes = (
                f"- Ø galette : {d_cyl - 2*jeu_lateral:.2f} mm (jeu de {jeu_lateral:.2f} mm)\n"
                f"- Épaisseur galette : {epaisseur_piston:.2f} mm\n"
                f"- Fond galette : {epaisseur_fond:.2f} mm\n"
                f"- Nombre de joints : {nb_joints} (rainure {largeur_rainure:.1f} × {profondeur_rainure:.1f} mm)\n"
                f"- Masse piston estimée : {masse_piston:.1f} g\n"
                f"- Température max piston : {temp_max} °C\n"
            )

            # Recommandations
            remarque = (
                f"✅ Conseil : Piston galette à faible jeu (auto-lubrifiant si graphite).\n"
                "Préférer un alliage Alu 2017A, 6082, ou graphite dense (faible usure). "
                "Rainure pour joint Viton ou PTFE renforcé. "
                "Adapter la longueur du piston selon la course max (laisser 8 à 15 mm de sécurité pour la butée à pleine course)."
            )

            self.resultat.config(text=f"""
🔩 **Piston galette pour Stirling**\n
{consignes}
Matériau conseillé : {mat_piston}
{remarque}
""")
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
