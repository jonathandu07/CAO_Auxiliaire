import tkinter as tk
import numpy as np
from styles import COULEURS, bouton_flat
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DENSITES_MATERIAUX = {
    "alu": 2.800,
    "aluminium": 2.800,
    "graphite": 1.900,
    "acier": 7.850,
}

class PagePistonStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        # En-tête sur 2 colonnes
        titre = tk.Label(self, text="Conception piston Stirling (galette)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold"))
        titre.grid(row=0, column=0, columnspan=2, pady=(18,2), sticky="w")
        descr = ("Ce calculateur estime toutes les côtes d’un piston galette pour moteur Stirling mono-cylindre.\n"
                 "⚙️ Entrez les données de base. Le plan détaillé + schéma sont générés pour la CAO.")
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)
        ).grid(row=1, column=0, columnspan=2, sticky="w")

        # Partie gauche : Formulaire + Plan
        cadre_gauche = tk.Frame(self, bg=COULEURS["fond"])
        cadre_gauche.grid(row=2, column=0, sticky="nw", padx=(8,30), pady=10)
        self.champs = {}
        donnees = [
            ("Diamètre du cylindre (mm)", "d_cyl"),
            ("Hauteur utile du cylindre (mm)", "h_cyl_utile"),
            ("Nombre de joints", "nb_joints"),
            ("Température chaude max (°C)", "t_chaude"),
            ("Matériau du piston", "materiau_piston")
        ]
        for label, cle in donnees:
            f = tk.Frame(cadre_gauche, bg=COULEURS["fond"])
            tk.Label(f, text=label, font=("Segoe UI", 10), width=28, anchor="w",
                     bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left")
            entry = tk.Entry(f, width=14, font=("Segoe UI", 10))
            entry.pack(side="right")
            f.pack(pady=2, anchor="w")
            self.champs[cle] = entry

        self.prefill_from_moteur()
        self.resultat = tk.Label(cadre_gauche, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left", anchor="nw")
        self.resultat.pack(pady=10, anchor="w")

        boutons_zone = tk.Frame(cadre_gauche, bg=COULEURS["fond"])
        boutons_zone.pack(anchor="w", pady=(5,0))
        bouton_flat(boutons_zone, "Générer le plan technique", self.calculer_piston).pack(side="left", padx=4)
        bouton_flat(boutons_zone, "Retour", self.retour_page_moteur).pack(side="left", padx=4)

        # Partie droite : Schéma matplotlib (Canvas)
        self.cadre_schema = tk.Frame(self, bg=COULEURS["fond"])
        self.cadre_schema.grid(row=2, column=1, sticky="ne", padx=(0,16), pady=15)
        self.canvas = None

        # Pour un affichage plus propre sur grands écrans
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def prefill_from_moteur(self):
        moteur = getattr(self.controller, "memo_moteur_stirling", {})
        if moteur.get("d_cyl"):
            self.champs["d_cyl"].delete(0, tk.END)
            self.champs["d_cyl"].insert(0, str(moteur["d_cyl"]))
        if moteur.get("t_chaude"):
            self.champs["t_chaude"].delete(0, tk.END)
            self.champs["t_chaude"].insert(0, str(moteur["t_chaude"]))
        if not self.champs["materiau_piston"].get():
            self.champs["materiau_piston"].insert(0, "Alu 2017A / 6082 / Graphite")
        if not self.champs["nb_joints"].get():
            self.champs["nb_joints"].insert(0, "2")

    def retour_page_moteur(self):
        from pages.page_moteur_stirling import PageMoteurStirling
        self.controller.afficher_page(PageMoteurStirling)

    def calculer_piston(self):
        try:
            moteur = getattr(self.controller, "memo_moteur_stirling", {})
            d_cyl = self._get_float("d_cyl", moteur.get("d_cyl", 70))
            h_cyl_utile = self._get_float("h_cyl_utile", 0.75 * d_cyl)
            nb_joints = self._get_int("nb_joints", 2)
            t_chaude = self._get_float("t_chaude", moteur.get("t_chaude", 650))
            mat_piston = self.champs["materiau_piston"].get().strip() or "Aluminium 2017A"
            jeu_lateral = max(round(0.0004 * d_cyl + 0.02, 4), 0.03)
            d_piston = round(d_cyl - 2 * jeu_lateral, 3)
            epaisseur_piston = round(max(0.165 * d_cyl, 7), 3)
            epaisseur_fond = round(0.12 * d_cyl, 3)
            largeur_rainure = 2.40
            profondeur_rainure = 1.60
            decalage_rainure = 2.00

            surface_piston = round(np.pi * (d_piston / 2) ** 2, 3)
            volume_piston = round(surface_piston * epaisseur_piston, 3)
            mat_key = "alu"
            for key in DENSITES_MATERIAUX:
                if key in mat_piston.lower():
                    mat_key = key
                    break
            densite = DENSITES_MATERIAUX.get(mat_key, 2.8)
            masse_piston = volume_piston * densite / 1000
            if "graphite" in mat_piston.lower():
                temp_max = 300
            elif "alu" in mat_piston.lower() or "aluminium" in mat_piston.lower():
                temp_max = 200
            elif "acier" in mat_piston.lower():
                temp_max = 500
            else:
                temp_max = 200

            plan = (
                f"PLAN TECHNIQUE : PISTON GALETTE STIRLING\n"
                f"--------------------------------------------------\n"
                f"1. Forme : Cylindre (galette), arrêtes légèrement chanfreinées\n"
                f"2. Ø extérieur piston (Øp) : {d_piston:.3f} mm (Tol. H8)\n"
                f"3. Épaisseur totale piston : {epaisseur_piston:.3f} mm\n"
                f"4. Épaisseur fond (côté froid) : {epaisseur_fond:.3f} mm\n"
                f"5. Nombre de joints : {nb_joints}\n"
                f"6. Rainure(s) joint : {nb_joints} x (largeur {largeur_rainure:.2f} mm × profondeur {profondeur_rainure:.2f} mm),\n"
                f"     décalée(s) de {decalage_rainure:.2f} mm du bord, symétriques\n"
                f"7. Matière : {mat_piston} (densité réelle {densite:.3f} g/cm³)\n"
                f"8. Jeu latéral cylindre/piston : {jeu_lateral:.4f} mm\n"
                f"9. Surface (piston) : {surface_piston:.3f} mm²\n"
                f"10. Volume (piston) : {volume_piston:.3f} mm³\n"
                f"11. Masse estimée : {masse_piston:.3f} g\n"
                f"12. Température max piston : {temp_max} °C\n"
                f"\n"
                f"Instructions CAO/SolidWorks :\n"
                f"- Faire un disque Ø {d_piston:.3f} mm, extrusion {epaisseur_piston:.3f} mm\n"
                f"- Ajouter un fond épaisseur {epaisseur_fond:.3f} mm (côté froid)\n"
                f"- Rainures pour {nb_joints} joints toriques : largeur {largeur_rainure:.2f} mm, profondeur {profondeur_rainure:.2f} mm, décalage {decalage_rainure:.2f} mm\n"
                f"- Chanfrein 0.5 mm sur toutes arrêtes vives\n"
                f"- Tolérances H8/g6, à ajuster selon usinage\n"
                f"\n"
                f"💡 Contrôler le jeu piston/cylindre, tester le coulissement à sec avant montage définitif.\n"
            )
            self.resultat.config(text=plan)
            self.generer_schema_piston(d_piston, epaisseur_piston, epaisseur_fond, nb_joints, largeur_rainure, profondeur_rainure, decalage_rainure)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def generer_schema_piston(self, d_piston, epaisseur_piston, epaisseur_fond, nb_joints, largeur_rainure, profondeur_rainure, decalage_rainure):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        from matplotlib.patches import Rectangle

        fig = Figure(figsize=(5.5, 6), dpi=110)
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')

        x0, y0 = 20, 30
        # Piston corps
        ax.add_patch(Rectangle((x0, y0), epaisseur_piston, d_piston, color="#e4e4e4", ec="#222", lw=2))
        # Fond
        ax.add_patch(Rectangle((x0, y0), epaisseur_fond, d_piston, color="#bbbbbb", ec="#222", lw=2))
        # Rainures
        espace_total = d_piston - 2 * decalage_rainure
        if nb_joints > 1:
            espace_entre_rainures = espace_total / (nb_joints - 1)
        else:
            espace_entre_rainures = 0
        for i in range(nb_joints):
            y_rainure = y0 + decalage_rainure + i * espace_entre_rainures - largeur_rainure / 2
            ax.add_patch(Rectangle((x0 + epaisseur_piston - profondeur_rainure, y_rainure),
                                   profondeur_rainure, largeur_rainure, color="#9ad0fc", ec="#1976d2", lw=1.2))
        # Cotes/annotations plus visibles
        ax.annotate(f"{epaisseur_piston:.1f} mm", xy=(x0 + epaisseur_piston/2, y0 + d_piston + 16), ha="center", fontsize=13, color="#111", fontweight="bold")
        ax.annotate(f"{d_piston:.1f} mm", xy=(x0 + epaisseur_piston + 12, y0 + d_piston/2), rotation=90, va="center", fontsize=13, color="#1976d2", fontweight="bold")
        ax.annotate("Rainure joint", xy=(x0 + epaisseur_piston - profondeur_rainure/2, y0 + d_piston/2),
                    xytext=(x0 + epaisseur_piston + 42, y0 + d_piston/2),
                    arrowprops=dict(arrowstyle="->", color="#1976d2", lw=2), color="#1976d2", fontsize=12)

        ax.axis("off")
        ax.set_xlim(0, x0 + epaisseur_piston + 90)
        ax.set_ylim(0, y0 + d_piston + 50)
        ax.set_title("Mise en plan simplifiée du piston (coupe longitudinale)", fontsize=14, pad=14)

        self.canvas = FigureCanvasTkAgg(fig, master=self.cadre_schema)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True)

    def _get_float(self, key, default):
        val = self.champs[key].get()
        try:
            return float(val)
        except Exception:
            return float(default)

    def _get_int(self, key, default):
        val = self.champs[key].get()
        try:
            return int(val)
        except Exception:
            return int(default)
