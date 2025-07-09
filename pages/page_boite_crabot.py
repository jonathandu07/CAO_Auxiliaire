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

class PageBoiteCrabot(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Conception boîte à crabots automatique", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        self.champs = {}
        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack()

        parametres = [
            ("Vitesse d’entrée (tr/min)", "v_in"),
            ("Nombre de rapports", "nb_rapports"),
            ("Diamètre de l’arbre (mm)", "d_arbre"),
            ("Module des engrenages (mm)", "module"),
        ]

        for i, (label, cle) in enumerate(parametres):
            tk.Label(form, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                     font=("Segoe UI", 10), width=30, anchor="w").grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(form, font=("Segoe UI", 10), width=15)
            entry.grid(row=i, column=1, padx=10)
            self.champs[cle] = entry

        bouton_flat(self, "Charger depuis moteur Stirling", self.charger_depuis_stirling).pack(pady=5)
        bouton_flat(self, "Calculer", self.calculer).pack(pady=15)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"],
                                 fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def charger_depuis_stirling(self):
        """Pré-remplit les champs avec les valeurs du moteur Stirling s'ils existent."""
        data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}

        if data:
            if data.get("rpm"):
                self.champs["v_in"].delete(0, tk.END)
                self.champs["v_in"].insert(0, f"{data['rpm']:.0f}")
            if data.get("vilebrequin"):
                self.champs["d_arbre"].delete(0, tk.END)
                self.champs["d_arbre"].insert(0, f"{data['vilebrequin']:.2f}")
            # Tu peux aussi pré-remplir "module" si tu le veux (par défaut à 2)
            self.champs["module"].delete(0, tk.END)
            self.champs["module"].insert(0, "2.0")
            # Nb rapports : valeur par défaut 4
            self.champs["nb_rapports"].delete(0, tk.END)
            self.champs["nb_rapports"].insert(0, "4")
            self.resultat.config(text="Valeurs importées du moteur Stirling.")
        else:
            self.resultat.config(text="Aucune donnée moteur Stirling disponible.")

    def calculer(self):
        # Déduction intelligente :
        try:
            v_in = self.champs["v_in"].get()
            n = self.champs["nb_rapports"].get()
            d = self.champs["d_arbre"].get()
            m = self.champs["module"].get()

            # Remplissage automatique si possible
            if not v_in:
                data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}
                v_in = data.get("rpm", 1500)
                self.champs["v_in"].insert(0, str(int(v_in)))
            if not n:
                n = 4
                self.champs["nb_rapports"].insert(0, "4")
            if not d:
                data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}
                d = data.get("vilebrequin", 20)
                self.champs["d_arbre"].insert(0, f"{float(d):.2f}")
            if not m:
                m = 2.0
                self.champs["module"].insert(0, "2.0")

            v_in = float(self.champs["v_in"].get())
            n = int(self.champs["nb_rapports"].get())
            d = float(self.champs["d_arbre"].get())
            m = float(self.champs["module"].get())

        except ValueError:
            self.resultat.config(text="⚠️ Vérifie les entrées.")
            return

        rapports = []
        vitesses = []
        for i in range(1, n + 1):
            z1 = 20
            z2 = int(z1 * (1 + i * 0.25))  # rapport progressif, un peu plus étagé
            r = z2 / z1
            v_out = v_in / r
            rapports.append(f"Rapport {i} : {z1} / {z2} = {r:.2f}")
            vitesses.append(f"Vitesse sortie {i} : {v_out:.1f} tr/min")

        entraxe = m * (20 + z2) / 2 / 1000  # mm en m
        resultats = "Données déduites automatiquement si besoin.\n\n"
        resultats += "\n".join(rapports + vitesses)
        resultats += f"\n\nDiamètre d’arbre : {d} mm"
        resultats += f"\nModule choisi : {m} mm"
        resultats += f"\nEntraxe estimé : {entraxe:.3f} m"

        self.resultat.config(text=resultats)