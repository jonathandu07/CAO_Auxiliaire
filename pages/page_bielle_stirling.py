# pages\page_bielle_stirling.py

import tkinter as tk
from styles import COULEURS, bouton_flat
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageBielleStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement de la bielle du Stirling", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=18)

        descr = (
            "Cette page calcule les dimensions principales d'une bielle pour un moteur Stirling mono-cylindre,\n"
            "en tenant compte du diamètre du cylindre, du rayon du vilebrequin et des efforts transmis."
        )
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        # Entrées principales (pré-remplies si possible depuis le memo)
        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=12)

        self.d_cyl = self._champ(form, "Diamètre cylindre (mm)", 0)
        self.rayon_manivelle = self._champ(form, "Rayon excentrique vilebrequin (mm)", 1)
        self.f_max = self._champ(form, "Effort max (N)", 2)
        self.L_bielle = self._champ(form, "Longueur totale bielle (mm)", 3)
        self.d_tete_piston = self._champ(form, "Diamètre œil côté piston (mm)", 4)
        self.d_tete_vilebrequin = self._champ(form, "Diamètre œil côté maneton (mm)", 5)
        self.mat_bielle = self._champ(form, "Matériau (ex: Acier 42CrMo4)", 6, default="Acier 42CrMo4")

        bouton_flat(form, "Calculer la bielle", self.calculer_bielle).grid(row=8, columnspan=2, pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(self.controller.frames.keys()[0])).grid(row=9, columnspan=2, pady=4)

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
        # Suggère des valeurs réalistes si dispo
        if memo.get("d_cyl"):
            self.d_cyl.delete(0, tk.END)
            self.d_cyl.insert(0, str(memo["d_cyl"]))
        # Rayon manivelle par défaut : 0.6 x diamètre cylindre (ratio à ajuster)
        if memo.get("d_cyl") and not self.rayon_manivelle.get():
            self.rayon_manivelle.insert(0, f"{float(memo['d_cyl'])/2*0.6:.1f}")
        # Longueur bielle par défaut : 3 x rayon manivelle
        if self.rayon_manivelle.get() and not self.L_bielle.get():
            self.L_bielle.insert(0, f"{float(self.rayon_manivelle.get())*3:.1f}")
        # Diamètres d’œil
        if memo.get("d_cyl"):
            d_cyl = float(memo["d_cyl"])
            self.d_tete_piston.insert(0, f"{max(0.35*d_cyl, 10):.1f}")
            self.d_tete_vilebrequin.insert(0, f"{max(0.3*d_cyl, 8):.1f}")
        # Effort max : pression x surface piston
        if memo.get("pression") and memo.get("d_cyl"):
            P = float(memo["pression"])*1e5  # bar -> Pa
            A = np.pi * (float(memo["d_cyl"])/2/1000)**2
            self.f_max.insert(0, f"{P*A:.1f}")

    def calculer_bielle(self):
        try:
            d_cyl = float(self.d_cyl.get())
            r = float(self.rayon_manivelle.get())
            F_max = float(self.f_max.get())
            L = float(self.L_bielle.get())
            d_t_pist = float(self.d_tete_piston.get())
            d_t_vil = float(self.d_tete_vilebrequin.get())
            mat = self.mat_bielle.get().strip() or "Acier 42CrMo4"

            # Calculs section mini, largeur, épaisseur
            # Hypothèse : sollicitation en traction/compression
            sigma_adm = 380e6  # Pa (42CrMo4)
            section_min = F_max / (0.5 * sigma_adm) * 1.5  # sécurité x1.5, coeff 0.5 si section rectangulaire ajourée

            largeur_bielle = max(0.22*d_cyl, 8)  # typique 20-25% du Ø cylindre
            epaisseur_bielle = max(section_min / largeur_bielle, 4)  # mini 4mm

            # Conseils SolidWorks / usinage
            plan_tech = (
                f"- Longueur axe à axe : {L:.2f} mm\n"
                f"- Largeur bielle : {largeur_bielle:.2f} mm\n"
                f"- Épaisseur bielle : {epaisseur_bielle:.2f} mm\n"
                f"- Diamètre œil piston : {d_t_pist:.2f} mm (roulement/bague bronze/axe)\n"
                f"- Diamètre œil maneton : {d_t_vil:.2f} mm\n"
                f"- Entraxe œil : {L:.2f} mm\n"
                f"- Matière : {mat}\n"
                f"- Rainure graissage et chanfrein d'ébauche conseillés.\n"
                f"- Usiner les têtes d'œil pour circlips ou bagues de maintien."
            )

            # Masse (approximative)
            volume_bielle = largeur_bielle * epaisseur_bielle * L  # mm³
            masse_bielle = volume_bielle * 7.85e-3 / 1000  # acier

            conseils = (
                "✅ Conseil : Prévoir rayons généreux pour éviter les amorces de rupture. "
                "Utiliser une bielle ajourée pour réduire la masse, contrôler l'équilibrage dynamique.\n"
                "Prévoir une visserie M6 ou M8 (8.8) pour la fixation de la tête de bielle si démontable."
            )

            self.resultat.config(text=f"""
🔩 **Plan technique bielle moteur Stirling**\n
{plan_tech}
Masse estimée : {masse_bielle:.1f} g

{conseils}
""")
            self.afficher_schema(L, largeur_bielle, epaisseur_bielle, d_t_pist, d_t_vil)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, L, largeur, epaisseur, d_t_pist, d_t_vil):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        import matplotlib.patches as mpatches
        fig = Figure(figsize=(7, 1.8), dpi=100)
        ax = fig.add_subplot(111)
        y0 = 0.8

        # Œil piston
        ax.add_patch(mpatches.Circle((0, y0), d_t_pist/20, color="#b6cef2", label="Œil piston"))
        # Corps bielle
        ax.add_patch(mpatches.Rectangle((0, y0-epaisseur/30), L, epaisseur/15, color="#aaaaaa", label="Corps bielle"))
        # Œil maneton
        ax.add_patch(mpatches.Circle((L, y0), d_t_vil/20, color="#ef767a", label="Œil maneton"))

        ax.text(0, y0+0.19, "Œil piston", ha="center", color="#345")
        ax.text(L/2, y0-0.17, "Corps bielle", ha="center", color="#555")
        ax.text(L, y0+0.19, "Œil maneton", ha="center", color="#a33")

        # Cotes
        ax.annotate(f"{L:.1f} mm", xy=(L/2, y0+0.13), xytext=(L/2, y0+0.25),
                    ha="center", arrowprops=dict(arrowstyle="<->"))
        ax.set_xlim(-L*0.15, L*1.15)
        ax.set_ylim(y0-0.4, y0+0.45)
        ax.axis("off")
        ax.set_title("Croquis technique bielle (vue de dessus)")
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)
