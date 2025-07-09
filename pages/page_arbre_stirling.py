# pages/page_arbre_stirling.py

import tkinter as tk
from styles import COULEURS, bouton_flat
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageArbreStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement de l’arbre principal du Stirling", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=18)

        descr = (
            "Cette page calcule les dimensions principales de l'arbre de sortie du moteur Stirling :\n"
            "résistance à la torsion, choix de l’acier, tolérance ajustée selon l’assemblage (palier, volant, poulie, etc.)."
        )
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=12)

        self.couple = self._champ(form, "Couple transmis (Nm)", 0)
        self.L_arbre = self._champ(form, "Longueur arbre (mm)", 1, default="110")
        self.tol = self._champ(form, "Tolérance sécurité (%)", 2, default="20")
        self.mat_arbre = self._champ(form, "Matériau (ex: 42CrMo4 ou S355)", 3, default="Acier 42CrMo4")

        bouton_flat(form, "Calculer l’arbre", self.calculer_arbre).grid(row=8, columnspan=2, pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(controller.frames.keys()[0])).grid(row=9, columnspan=2, pady=4)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left")
        self.resultat.pack(pady=10)
        self.canvas = None

        self.prefill_from_memo()

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=32, anchor="w").grid(row=row, column=0, padx=7, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=14)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=7)
        return e

    def prefill_from_memo(self):
        memo = getattr(self.controller, "memo_moteur_stirling", {})
        if memo.get("puissance") and memo.get("d_cyl"):
            P = float(memo["puissance"])
            d_cyl = float(memo["d_cyl"])
            # Estimation couple typique pour démarrage
            C = P / (2 * np.pi * 400 / 60)  # à 400 tr/min par défaut
            self.couple.delete(0, tk.END)
            self.couple.insert(0, f"{C:.2f}")

    def calculer_arbre(self):
        try:
            C = float(self.couple.get())
            L = float(self.L_arbre.get())
            tol = float(self.tol.get()) / 100
            mat = self.mat_arbre.get().strip() or "Acier 42CrMo4"

            # Résistance admissible (Pa) pour acier courants
            if "42crmo4" in mat.lower():
                Re = 900e6
            elif "355" in mat.lower():
                Re = 355e6
            else:
                Re = 600e6  # Valeur prudente

            tau_adm = 0.5 * (1 - tol) * Re

            # Ø arbre mini sous torsion (formule EN 10277-2)
            d_arbre = ((16 * C) / (np.pi * tau_adm)) ** (1/3) * 1000  # mm

            # Conseil : choisir un diamètre commercial standard (arrondi)
            diam_std = min([x for x in [15, 18, 20, 22, 25, 30, 35, 40] if x >= d_arbre], default=round(d_arbre+2))

            # Usinage/assemblage
            tolerance_arbre = "h6" if diam_std < 40 else "h7"
            conseil_montage = (
                "Prévoir un ajustement glissant ou serré selon montage : "
                f"queue d'arbre {tolerance_arbre}, rainure de clavette pour volant/poulie si nécessaire."
            )

            plan_tech = (
                f"- Couple à transmettre : {C:.2f} Nm\n"
                f"- Longueur arbre : {L:.0f} mm\n"
                f"- Matériau conseillé : {mat} (Re={Re/1e6:.0f} MPa)\n"
                f"- Diamètre mini calculé : {d_arbre:.2f} mm\n"
                f"- Ø nominal recommandé : {diam_std:.1f} mm (tolérance {tolerance_arbre})\n"
                f"- Finition : surface usinée Ra ≤ 1.6 µm, congés aux épaulements"
            )

            self.resultat.config(text=f"""
🛠️ **Plan technique arbre moteur Stirling**\n
{plan_tech}
{conseil_montage}
- Percer taraudage M8 sur extrémité pour extraction, filetage si fixation directe d’un volant.
- Graissage conseillé pour montage dans les paliers (bague bronze ou roulement à billes).
""")
            self.afficher_schema(diam_std, L)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, d, L):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        fig = Figure(figsize=(6, 1.2), dpi=100)
        ax = fig.add_subplot(111)
        y0 = 0.7
        # Arbre (vue de côté)
        ax.add_patch(mpatches.Rectangle((0, y0 - d/200), L, d/100, color="#bbb", label="Arbre"))
        # Côtes
        ax.annotate(f"{L:.0f} mm", xy=(L/2, y0 + d/80), xytext=(L/2, y0 + d/30),
                    ha="center", arrowprops=dict(arrowstyle="<->"))
        ax.annotate(f"Ø {d:.1f} mm", xy=(L + 8, y0), xytext=(L + 14, y0),
                    ha="left", va="center")
        ax.set_xlim(-10, L + 40)
        ax.set_ylim(y0 - 0.2, y0 + 0.3)
        ax.axis("off")
        ax.set_title("Croquis technique arbre (vue latérale)")
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)
