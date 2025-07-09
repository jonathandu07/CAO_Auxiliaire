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

class PageVilebrequin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement du vilebrequin", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)

        self.puissance = self._champ(form, "Puissance transmise (W)", 0)
        self.vitesse = self._champ(form, "Vitesse de rotation (tr/min)", 1)
        self.couple = self._champ(form, "Couple transmis (Nm)", 2)
        self.longueur = self._champ(form, "Longueur entre paliers (mm)", 3, default="80")
        self.rayon_manivelle = self._champ(form, "Rayon excentrique (mm)", 4, default="20")
        self.largeur_maneton = self._champ(form, "Largeur maneton (mm)", 5, default="18")
        self.tol = self._champ(form, "Tolérance sécurité (%)", 6, default="20")

        tk.Label(form, text="Matériau", bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.mat_var = tk.StringVar(value="Acier S235")
        tk.OptionMenu(form, self.mat_var, *MATERIAUX.keys()).grid(row=7, column=1, padx=10)

        bouton_flat(self, "Calculer vilebrequin", self.calculer).pack(pady=10)
        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"], font=("Consolas", 10), justify="left")
        self.resultat.pack(pady=10)

        self.canvas = None
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=15)

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=10)
        return e

    def calculer(self):
        try:
            W = float(self.puissance.get()) if self.puissance.get() else None
            N = float(self.vitesse.get()) if self.vitesse.get() else None
            C = float(self.couple.get()) if self.couple.get() else None
            L = float(self.longueur.get())
            r = float(self.rayon_manivelle.get())
            b = float(self.largeur_maneton.get())
            tol = float(self.tol.get()) / 100
            mat = self.mat_var.get()

            mat_props = MATERIAUX.get(mat)
            if mat_props is None:
                raise ValueError(f"Matériau '{mat}' introuvable dans la base.")

            Re = float(mat_props["Re"]) * 1e6 if "Re" in mat_props else 250e6  # MPa -> Pa

            # Si couple absent, calcule à partir de puissance & vitesse
            if not C:
                if W is not None and N is not None:
                    C = W / (2 * np.pi * (N/60))
                else:
                    raise ValueError("Donne au moins la puissance+vitesse ou le couple transmis.")

            Re_adm = (1-tol) * Re
            tau_adm = 0.6 * Re_adm

            # Diamètre min du maneton sous torsion et flexion combinée
            d_m = ((16 * C) / (np.pi * tau_adm))**(1/3) * 1000  # mm

            # Diamètre des paliers généralement > maneton
            d_p = d_m * 1.15

            self.resultat.config(text=f"""
🧮 Calcul vilebrequin :
- Couple transmis = {C:.2f} Nm | L = {L:.0f} mm | Rayon excentrique = {r:.1f} mm
- Résistance admissible τ = {tau_adm/1e6:.0f} MPa (sécurité {tol*100:.0f}%)
- **Ø maneton mini recommandé** : {d_m:.1f} mm
- **Ø paliers recommandé** : {d_p:.1f} mm
- Largeur maneton : {b:.1f} mm
""")
            self.afficher_schema(d_p, d_m, L, r, b)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, d_p, d_m, L, r, b):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        fig = Figure(figsize=(8, 2), dpi=100)
        ax = fig.add_subplot(111)

        # --- Dimensions des éléments principaux ---
        largeur_palier = 16      # mm (ajustable)
        largeur_bras = 12        # mm
        largeur_maneton = b      # mm (entrée utilisateur)
        espace_bras_maneton = 4  # mm pour visibilité

        # Placement sur l'axe X (gauche à droite)
        x0 = 0
        x1 = x0 + largeur_palier
        x2 = x1 + largeur_bras
        x3 = x2 + espace_bras_maneton
        x4 = x3 + largeur_maneton
        x5 = x4 + espace_bras_maneton
        x6 = x5 + largeur_bras
        x7 = x6 + largeur_palier

        # Centre du maneton (excentré de r)
        y = 1.0

        # Paliers gauche/droite
        ax.add_patch(mpatches.Rectangle((x0, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier gauche"))
        ax.add_patch(mpatches.Rectangle((x6, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier droit"))

        # Bras de manivelle
        ax.add_patch(mpatches.Rectangle((x1, y - d_p/2), largeur_bras, d_p, color="#aaaaaa", label="Bras"))
        ax.add_patch(mpatches.Rectangle((x5, y - d_p/2), largeur_bras, d_p, color="#aaaaaa"))

        # Maneton (excentré en Y de +r)
        ax.add_patch(mpatches.Rectangle((x3, y + r - d_m/2), largeur_maneton, d_m, color="#ef767a", label="Maneton excentré"))

        # Axe principal
        ax.plot([x0, x7], [y, y], color="k", lw=2, linestyle="--", zorder=3)

        # Axe du maneton (excentré)
        x_centre_maneton = x3 + largeur_maneton / 2
        ax.plot([x_centre_maneton, x_centre_maneton], [y, y + r], color="#222", lw=2, linestyle="-")
        ax.plot([x3, x4], [y + r, y + r], color="#a33", lw=2, linestyle=":")

        # Légendes
        ax.text(x1 + largeur_bras/2, y + d_p/2 + 3, "Bras de manivelle", ha="center", color="#555")
        ax.text(x3 + largeur_maneton/2, y + r + d_m/2 + 2, "Maneton (excentré)", ha="center", color="#a33")
        ax.text(x0 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")
        ax.text(x6 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")

        # Ajuste la vue
        ax.set_xlim(x0 - 10, x7 + 10)
        ax.set_ylim(y - d_p, y + d_p * 2)
        ax.axis("off")
        ax.set_title("Croquis industriel du vilebrequin – vue de dessus")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)