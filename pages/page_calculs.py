# pages\page_calculs.py
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

class PageCalculs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Calculs RDM", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        # Convertisseur kg -> N et kN
        convert_frame = tk.Frame(self, bg=COULEURS["fond"])
        tk.Label(convert_frame, text="Masse (kg) :", bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=0, column=0)
        self.kg_var = tk.StringVar()
        tk.Entry(convert_frame, textvariable=self.kg_var).grid(row=0, column=1)
        self.convert_result = tk.Label(convert_frame, text="", bg=COULEURS["fond"], fg=COULEURS["accent"])
        self.convert_result.grid(row=1, columnspan=2)
        tk.Button(convert_frame, text="Convertir", command=self.convertir_masse).grid(row=0, column=2, padx=5)
        convert_frame.pack(pady=10)

        # Sélection du matériau
        tk.Label(self, text="Matériau :", bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
        self.materiau_var = tk.StringVar(value="Acier")
        tk.OptionMenu(self, self.materiau_var, *MATERIAUX.keys()).pack()

        # Tolérance de sécurité
        tk.Label(self, text="Tolérance (%) :", bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
        self.tolerance_var = tk.StringVar(value="20")
        tk.Entry(self, textvariable=self.tolerance_var).pack()

        # Saisie des paramètres communs
        self.champs_liste = [
            ("Section (mm²)", "section"),
            ("Longueur (mm)", "longueur"),
            ("Force appliquée (N)", "force"),
            ("Moment appliqué (Nm)", "moment"),
            ("Couple appliqué (Nm)", "couple"),
            ("Module d’inertie (mm⁴)", "inertie")
        ]
        self.entrees = {}
        for label, cle in self.champs_liste:
            tk.Label(self, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
            entree = tk.Entry(self)
            entree.pack()
            self.entrees[cle] = entree

        self.resultat_label = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"])
        self.resultat_label.pack(pady=10)

        bouton_flat(self, "Calculer les contraintes", self.calculer).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def convertir_masse(self):
        try:
            masse = float(self.kg_var.get())
            newton = masse * 9.81
            kn = newton / 1000
            self.convert_result.config(text=f"{newton:.2f} N | {kn:.3f} kN")
        except:
            self.convert_result.config(text="Entrée invalide")

    def calculer(self):
        try:
            tol = float(self.tolerance_var.get() or "20") / 100
            mat_selectionne = self.materiau_var.get()
            prop = MATERIAUX[mat_selectionne]
            E = prop["E"]
            Re = prop["Re"]

            # Récupère tout ce qui a été saisi
            vals = {k: self.entrees[k].get().strip() for _, k in self.champs_liste}
            log_auto = []

            # 1) Déduction force à partir de la masse si champ force vide et masse renseignée
            masse_kg = self.kg_var.get().strip()
            if (not vals["force"] or float(vals["force"]) == 0) and masse_kg:
                force_val = float(masse_kg) * 9.81
                vals["force"] = f"{force_val:.3f}"
                self.entrees["force"].delete(0, tk.END)
                self.entrees["force"].insert(0, vals["force"])
                log_auto.append(f"Force déduite de la masse : {vals['force']} N")

            # 2) Section automatique si section manquante mais force présente
            if (not vals["section"] or float(vals["section"]) == 0) and vals["force"]:
                section_val = (float(vals["force"]) / ((1 - tol) * Re)) * 1e6  # mm²
                vals["section"] = f"{section_val:.1f}"
                self.entrees["section"].delete(0, tk.END)
                self.entrees["section"].insert(0, vals["section"])
                log_auto.append(f"Section calculée à partir de la force : {vals['section']} mm²")

            # 3) Force admissible si section saisie mais pas de force
            if (not vals["force"] or float(vals["force"]) == 0) and vals["section"]:
                force_max = (float(vals["section"]) / 1e6) * ((1 - tol) * Re)
                vals["force"] = f"{force_max:.1f}"
                self.entrees["force"].delete(0, tk.END)
                self.entrees["force"].insert(0, vals["force"])
                log_auto.append(f"Force max admissible recalculée : {vals['force']} N")

            # 4) Pour flexion, torsion, flambement : utilise valeurs si présentes sinon 0
            try:    L = float(vals["longueur"]) / 1000 if vals["longueur"] else 1
            except: L = 1
            try:    M = float(vals["moment"]) if vals["moment"] else 0
            except: M = 0
            try:    T = float(vals["couple"]) if vals["couple"] else 0
            except: T = 0
            try:    I = float(vals["inertie"]) / 1e12 if vals["inertie"] else 1e-4
            except: I = 1e-4

            # 5) Contraintes
            A = float(vals["section"]) / 1e6 if vals["section"] else 1e-6
            F = float(vals["force"]) if vals["force"] else 0

            sigma_traction = F / A if A else 0
            sigma_flexion = M * (L / 2) / I if I else 0
            tau_torsion = T * (L / 2) / I if I else 0
            flambement = (np.pi ** 2 * E * I) / (L ** 2) if I else 0

            # 6) Recherche meilleur matériau
            meilleurs = []
            for nom, props in MATERIAUX.items():
                Re_mat = props["Re"]
                if Re_mat == 0: continue
                A_calc = (F / ((1 - tol) * Re_mat)) * 1e6 if F else 0
                meilleurs.append((nom, A_calc))
            meilleurs = [t for t in meilleurs if t[1] > 0]
            meilleurs.sort(key=lambda x: x[1])
            meilleur_mat, meilleure_section = (meilleurs[0] if meilleurs else ("-", 0))

            resultat = ""
            if log_auto:
                resultat += "Données déduites automatiquement :\n- " + "\n- ".join(log_auto) + "\n\n"
            resultat += f"""
Contrainte de traction : {sigma_traction:.2f} Pa
Contrainte de flexion : {sigma_flexion:.2f} Pa
Contrainte de torsion : {tau_torsion:.2f} Pa
Charge critique de flambement : {flambement:.2f} N
Résistance limite du matériau : {Re:.2f} Pa

📐 Section requise avec {mat_selectionne} : {vals['section']} mm² (tolérance {tol*100:.0f}%)
"""
            if meilleur_mat != "-":
                resultat += f"\n✅ Meilleur matériau : {meilleur_mat}\n👉 Section minimale requise : {meilleure_section:.2f} mm²\n"

            self.resultat_label.config(text=resultat.strip())
        except Exception as e:
            self.resultat_label.config(text=f"Erreur : {str(e)}")