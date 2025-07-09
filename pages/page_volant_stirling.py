# pages\page_volant_stirling.py

# pages/page_volant_stirling.py

import tkinter as tk
from styles import COULEURS, bouton_flat
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

MATERIAUX_VOLANT = [
    {"nom": "Acier S235", "Re": 235, "densite": 7.85, "usage": "standard, masse élevée"},
    {"nom": "Fonte GGG40", "Re": 400, "densite": 7.1, "usage": "inertie, anti-vibratoire"},
    {"nom": "Alu 2017A", "Re": 380, "densite": 2.8, "usage": "léger, petits moteurs"},
]

def mat_volant_optimal(M_cible):
    # On privilégie fonte/acier si masse élevée nécessaire, alu sinon
    if M_cible > 1:
        return MATERIAUX_VOLANT[1]  # Fonte
    else:
        return MATERIAUX_VOLANT[0]  # Acier

class PageVolantStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement du volant d’inertie Stirling", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=16)
        tk.Label(self, text=(
            "Cette page calcule les cotes et la masse d’un volant pour le moteur Stirling,\n"
            "à partir du régime, du couple et de la régularité visée."
        ), bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)

        self.P = self._champ(form, "Puissance moteur (W)", 0)
        self.N = self._champ(form, "Régime cible (tr/min)", 1, "300")
        self.C = self._champ(form, "Couple max moteur (Nm)", 2)
        self.delta = self._champ(form, "Ondulation max (Δω/ω, ex: 0.04)", 3, "0.04")
        self.D = self._champ(form, "Diamètre max dispo (mm)", 4, "200")
        self.e = self._champ(form, "Épaisseur cible (mm)", 5, "18")
        self.tol = self._champ(form, "Tolérance sécurité (%)", 6, "20")

        bouton_flat(form, "Calculer volant", self.calculer).grid(row=8, columnspan=2, pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(list(self.controller.frames.keys())[0])).grid(row=9, columnspan=2, pady=4)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left")
        self.resultat.pack(pady=10)
        self.canvas = None

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=7, pady=4)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=14)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=7)
        return e

    def calculer(self):
        try:
            P = float(self.P.get())
            N = float(self.N.get())
            C = float(self.C.get()) if self.C.get() else P / (2*np.pi*(N/60))
            delta = float(self.delta.get())
            D_max = float(self.D.get())
            e = float(self.e.get())
            tol = float(self.tol.get()) / 100

            omega = 2*np.pi*N/60  # rad/s
            # Énergie cinétique cible = énergie fournie par cycle, corrigée du facteur d’ondulation
            E_cycle = C * 2 * np.pi
            J_min = E_cycle / (omega * delta) * (1 + tol)
            # On suppose un disque plein, J = (1/2) M R^2
            R = D_max / 2 / 1000  # en m
            M = J_min / (0.5 * R**2)
            mat = mat_volant_optimal(M)
            masse_volant = M
            inertie = 0.5 * M * (R**2)
            sigma_max = (3 * M * (omega**2) * R**2) / (8 * np.pi * e / 1000 * (R**3))

            plan = (
                f"- Ø volant : {D_max:.1f} mm\n"
                f"- Largeur/épaisseur : {e:.1f} mm\n"
                f"- Masse cible : {masse_volant:.2f} kg\n"
                f"- Inertie (J) : {inertie:.2f} kg·m²\n"
                f"- Régime : {N:.0f} tr/min\n"
                f"- Matériau recommandé : {mat['nom']} (Re={mat['Re']} MPa, ρ={mat['densite']} g/cm³)\n"
                f"- Tension max estimée (centre) : {sigma_max/1e6:.1f} MPa (tolérance {tol*100:.0f}%)\n"
                "- Moyeu alésé H7, rainure de clavette ou vis de pression.\n"
                "- Fixation sur vilebrequin par clavette, vis M6/M8 (min 8.8).\n"
                "- Usiner équilibrage dynamique, filetage taraudé possible pour extracteur."
            )
            conseils = (
                "✅ Conseil : Si masse trop élevée, réduire D ou utiliser volant à rayons/moyeu évidé.\n"
                "Surface de contact avec la courroie (si besoin) : usinée, Ra ≤ 1.6 µm.\n"
                "Vérifier le balourd avant montage."
            )

            self.resultat.config(text=f"""
🔩 **Plan technique volant moteur Stirling**\n
{plan}
{conseils}
""")
            self.afficher_schema(D_max, e, masse_volant)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, D, e, masse):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        fig = Figure(figsize=(4.6, 2), dpi=100)
        ax = fig.add_subplot(111)
        # Volant vu de côté (rectangle)
        ax.add_patch(mpatches.Rectangle((0.7, 0.8), D/60, e/15, color="#cccccc", label="Volant d'inertie"))
        ax.text(0.7 + D/120, 0.8 + e/30 + 0.08, f"Ø {D:.0f} mm", ha="center", color="#333")
        ax.text(0.7 + D/130, 0.8 - 0.09, f"e {e:.0f} mm", ha="center", color="#333")
        ax.set_xlim(0.5, 0.7 + D/55)
        ax.set_ylim(0.7, 1.3)
        ax.axis("off")
        ax.set_title(f"Croquis technique volant (vue de côté, masse ≈ {masse:.2f} kg)")
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)
