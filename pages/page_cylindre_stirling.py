# pages\page_cylindre_stirling.py

import tkinter as tk
import numpy as np
from styles import COULEURS, bouton_flat
from materiaux import MATERIAUX

class PageCylindreStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement du cylindre Stirling", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)

        # Récupération automatique depuis la mémoire centrale moteur (champ de base + sécurité)
        self.d_cyl = self._champ(form, "Diamètre intérieur (mm)", 0)
        self.h_utile = self._champ(form, "Hauteur utile (mm)", 1)
        self.ep_cyl = self._champ(form, "Épaisseur cylindre (mm)", 2, default="4")
        self.t_chaude = self._champ(form, "Température max (°C)", 3)
        self.tol = self._champ(form, "Tolérance (µm)", 4, default="40")
        self.materiau = self._champ(form, "Matériau", 5, default="Inox 304L")

        bouton_flat(form, "Calculer le cylindre", self.calculer).pack(pady=10)
        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"], font=("Consolas", 10), justify="left", anchor="w")
        self.resultat.pack(pady=10, fill="x")

        self.canvas = None
        bouton_flat(self, "Retour", lambda: controller.afficher_page("PageMoteurStirling")).pack(pady=15)

        # Pré-remplir avec données moteur si dispo
        self.precharge_data()

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=10)
        return e

    def precharge_data(self):
        # Recharge depuis le moteur si dispo
        memo = self.controller.memo_moteur_stirling
        if memo:
            if "d_cyl" in memo: self.d_cyl.delete(0, tk.END); self.d_cyl.insert(0, memo["d_cyl"])
            if "t_chaude" in memo: self.t_chaude.delete(0, tk.END); self.t_chaude.insert(0, memo["t_chaude"])
            if "h_cyl_utile" in memo: self.h_utile.delete(0, tk.END); self.h_utile.insert(0, memo["h_cyl_utile"])

    def calculer(self):
        try:
            d = float(self.d_cyl.get())
            h = float(self.h_utile.get())
            ep = float(self.ep_cyl.get())
            tmax = float(self.t_chaude.get())
            tol = float(self.tol.get())
            mat = self.materiau.get() if hasattr(self.materiau, "get") else self.materiau.get()
            # Par défaut si champ non renseigné
            if not mat: mat = "Inox 304L"

            # Calculs de base
            d_ext = d + 2 * ep
            jeu_piston = 0.02 * d  # 2% du diamètre (ajustable)
            rugosite = "Ra ≤ 0.4 µm"
            usinage = "Alesage, honage final, polissage intérieur"
            mat_rec = mat

            # Estimation masse (inox 304 : 8.0 g/cm³)
            vol_mm3 = np.pi * ((d_ext/2)**2 - (d/2)**2) * h
            masse = vol_mm3 * 8.0e-3 / 1000  # en g

            # Résumé fabrication + conseils SolidWorks
            plan = (
                f"PLAN TECHNIQUE : CYLINDRE STIRLING\n"
                f"---------------------------------------------------\n"
                f"1. Ø intérieur (alésage) : {d:.2f} mm (tolérance -0/+{tol:.1f} µm)\n"
                f"2. Ø extérieur : {d_ext:.2f} mm\n"
                f"3. Épaisseur : {ep:.2f} mm (min 4 mm recommandé)\n"
                f"4. Hauteur utile : {h:.2f} mm\n"
                f"5. Température max service : {tmax:.1f} °C\n"
                f"6. Jeu piston/cylindre : {jeu_piston:.2f} mm\n"
                f"7. Rugosité intérieure : {rugosite}\n"
                f"8. Masse cylindre estimée : {masse:.1f} g\n"
                f"9. Matériau recommandé : {mat_rec}\n"
                f"\n"
                f"Instructions SolidWorks :\n"
                f"- Croquis extrudé sur {h:.2f} mm, Ø intérieur {d:.2f} mm.\n"
                f"- Ø extérieur {d_ext:.2f} mm (épaisseur {ep:.2f} mm).\n"
                f"- Appliquer la tolérance h7 (-0/+{tol:.1f} µm) sur l'alésage.\n"
                f"- Prévoir rainure(s) pour joints toriques si besoin.\n"
                f"\n"
                f"💡 Conseil : polir parfaitement l’alésage pour limiter usure piston.\n"
                f"⚠️ Utiliser inox réfractaire si >400°C.\n"
            )
            self.resultat.config(text=plan)
            self.afficher_schema(d, d_ext, h, ep)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, d_int, d_ext, h, ep):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        fig = Figure(figsize=(5, 2.5), dpi=100)
        ax = fig.add_subplot(111)

        # Coupe du cylindre (vue de côté)
        y0 = 0
        ax.add_patch(mpatches.Rectangle((0, y0), ep, h, color="#ccc", label="Paroi"))
        ax.add_patch(mpatches.Rectangle((ep, y0), d_int, h, color="#8ecae6", label="Alésage (gaz)"))
        ax.add_patch(mpatches.Rectangle((ep + d_int, y0), ep, h, color="#ccc"))

        # Cotes et repères
        ax.annotate(f"Ø int. {d_int:.1f} mm", xy=(ep + d_int/2, y0 + h + 2), ha="center", color="#1976d2")
        ax.annotate(f"Ø ext. {d_ext:.1f} mm", xy=(d_ext/2, y0 + h + 7), ha="center", color="#222")
        ax.annotate(f"Ép. {ep:.1f} mm", xy=(ep/2, y0 + h/2), ha="center", color="#333")
        ax.annotate(f"Hauteur {h:.1f} mm", xy=(d_ext + 2, h/2), va="center", color="#333", rotation=90)

        ax.set_xlim(0, d_ext + 12)
        ax.set_ylim(-5, h + 20)
        ax.axis("off")
        ax.set_title("Croquis industriel du cylindre – coupe longitudinale")
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=8)
