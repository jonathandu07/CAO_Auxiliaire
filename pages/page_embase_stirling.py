# pages\page_embase_stirling.py

# pages/page_embase_stirling.py

import tkinter as tk
from styles import COULEURS, bouton_flat
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageEmbaseStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement de l'embase/support du moteur Stirling",
                 bg=COULEURS["fond"], fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")
        ).pack(pady=18)

        descr = (
            "Cette page calcule les dimensions typiques et la disposition d'une embase pour un Stirling mono-cylindre, "
            "permettant de supporter le moteur, absorber les vibrations et assurer un ancrage robuste.\n"
            "L'embase doit offrir stabilité, rigidité, et permettre l'assemblage avec la visserie adaptée."
        )
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=12)

        self.largeur = self._champ(form, "Largeur emb. (mm)", 0, default="180")
        self.longueur = self._champ(form, "Longueur emb. (mm)", 1, default="260")
        self.epaisseur = self._champ(form, "Épaisseur plaque (mm)", 2, default="10")
        self.nb_trous = self._champ(form, "Nb trous fixation", 3, default="4")
        self.diam_trou = self._champ(form, "Diamètre trous (mm)", 4, default="10")
        self.mat_embase = self._champ(form, "Matériau", 5, default="Alu 5083 ou Acier S235")

        bouton_flat(form, "Calculer l'embase", self.calculer_embase).grid(row=6, columnspan=2, pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(self.controller.frames.keys()[0])).grid(row=7, columnspan=2, pady=4)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left")
        self.resultat.pack(pady=10)
        self.canvas = None

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=28, anchor="w").grid(row=row, column=0, padx=7, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=14)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=7)
        return e

    def calculer_embase(self):
        try:
            largeur = float(self.largeur.get())
            longueur = float(self.longueur.get())
            epaisseur = float(self.epaisseur.get())
            nb_trous = int(self.nb_trous.get())
            diam_trou = float(self.diam_trou.get())
            mat = self.mat_embase.get().strip() or "Alu 5083"

            # Masse estimée
            masse = largeur * longueur * epaisseur * 2.7e-3 / 1000 if "alu" in mat.lower() else largeur * longueur * epaisseur * 7.85e-3 / 1000

            # Visserie recommandée (M8 pour 10 mm, rondelles larges)
            visserie = f"{nb_trous}x Vis CHC M8x{int(epaisseur*1.2)} (classe 8.8) + rondelles larges Ø10, écrous Nylstop"

            # Plan technique/résumé
            plan = (
                f"- Dimensions extérieures : {longueur:.0f} x {largeur:.0f} mm\n"
                f"- Épaisseur plaque : {epaisseur:.1f} mm\n"
                f"- {nb_trous} trous Ø{diam_trou:.1f} mm, répartis aux angles et centre\n"
                f"- Matériau : {mat}\n"
                f"- Masse estimée : {masse:.1f} kg\n"
                f"- Visserie recommandée : {visserie}\n"
                f"- Tolérance générale : ±0,2 mm sur les cotes, trous H13"
            )

            conseils = (
                "✅ Conseil : Prévoir des inserts filetés si l’embase est en aluminium. "
                "Percer des lumières oblongues pour ajustage du moteur. "
                "Peindre ou anodiser la plaque pour résistance à la corrosion. "
                "Si moteur >1kW ou vibrations importantes, renforcer par deux longerons soudés dessous."
            )

            self.resultat.config(text=f"""
🦾 **Plan technique – Embase/support moteur Stirling**\n
{plan}

{conseils}
""")
            self.afficher_schema(longueur, largeur, epaisseur, nb_trous, diam_trou)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, longueur, largeur, epaisseur, nb_trous, diam_trou):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        fig = Figure(figsize=(6, 2.6), dpi=100)
        ax = fig.add_subplot(111)

        # Contour principal
        rect = mpatches.Rectangle((0, 0), longueur, largeur, color="#b6cef2", alpha=0.7)
        ax.add_patch(rect)

        # Trous de fixation aux coins et au centre
        positions = [
            (10, 10), (longueur-10, 10), (10, largeur-10), (longueur-10, largeur-10)
        ]
        if nb_trous > 4:
            positions.append((longueur/2, largeur/2))
        for x, y in positions[:nb_trous]:
            ax.add_patch(mpatches.Circle((x, y), diam_trou/2, color="#ef767a", alpha=0.8))

        ax.set_xlim(-10, longueur+10)
        ax.set_ylim(-10, largeur+10)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title("Croquis technique – Embase (vue de dessus)")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)
