# pages\page_visserie_stirling.py

# pages/page_visserie_stirling.py

import tkinter as tk
from styles import COULEURS, bouton_flat
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PageVisserieStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Visserie & Assemblage moteur Stirling",
                 bg=COULEURS["fond"], fg=COULEURS["primaire"],
                 font=("Segoe UI", 18, "bold")).pack(pady=18)

        desc = (
            "Cette page donne les recommandations détaillées de visserie pour l’assemblage de chaque pièce\n"
            "du moteur Stirling : cylindre, embase, couvercles, volant, et les liaisons bielle/vilebrequin.\n"
            "Sélection automatique des classes d’acier, diamètres et longueurs, avec couple de serrage conseillé."
        )
        tk.Label(self, text=desc, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        # Entrées principales (peuvent venir du memo_moteur_stirling)
        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)
        self.d_cyl = self._champ(form, "Diamètre cylindre (mm)", 0)
        self.ep_plaques = self._champ(form, "Épaisseur plaques (mm)", 1, default="10")
        self.n_trous_embase = self._champ(form, "Nb vis embase", 2, default="4")
        self.n_trous_cyl = self._champ(form, "Nb vis couvercle cylindre", 3, default="6")
        self.n_trous_volant = self._champ(form, "Nb vis volant", 4, default="4")

        bouton_flat(form, "Calculer la visserie", self.calculer_visserie).grid(row=6, columnspan=2, pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(list(controller.frames.keys())[0])).grid(row=7, columnspan=2, pady=4)

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
        if memo.get("d_cyl"):
            self.d_cyl.delete(0, tk.END)
            self.d_cyl.insert(0, str(memo["d_cyl"]))

    def calculer_visserie(self):
        try:
            d_cyl = float(self.d_cyl.get())
            ep = float(self.ep_plaques.get())
            n_emb = int(self.n_trous_embase.get())
            n_cyl = int(self.n_trous_cyl.get())
            n_volant = int(self.n_trous_volant.get())

            # --- Sélection automatique des visseries optimales ---
            # Hypothèses :
            # - Embase/plaque : effort max ≈ 20kN par vis (grosse marge)
            # - Couvercle cylindre : pression + serrage thermique
            # - Volant : inertie, sollicitation dynamique
            # - Tous filetages sur alu/acier, utilisation de rondelles larges/écrous Nylstop

            # Dimensionnement typique selon Ø cylindre
            if d_cyl <= 45:
                vis_emb = "M6x25"
                vis_cyl = "M5x18"
                vis_volant = "M5x16"
            elif d_cyl <= 80:
                vis_emb = "M8x35"
                vis_cyl = "M6x25"
                vis_volant = "M6x20"
            else:
                vis_emb = "M10x40"
                vis_cyl = "M8x30"
                vis_volant = "M8x25"

            # Recommandation acier 8.8 (standard industriel)
            classe = "8.8 (acier trempé)"
            couple_M8 = 25  # Nm (à affiner selon cas)
            couple_M10 = 49  # Nm
            couple_M6 = 10
            couple_M5 = 5

            # Conseils
            plan_tech = (
                f"🪛 **Plan visserie pour assemblage moteur Stirling**\n\n"
                f"- Embase : {n_emb} x Vis CHC {vis_emb} – Acier {classe}, rondelles Ø large, écrou Nylstop\n"
                f"  (Serrer à {couple_M8 if 'M8' in vis_emb else (couple_M10 if 'M10' in vis_emb else couple_M6)} Nm)\n"
                f"- Couvercle cylindre : {n_cyl} x Vis {vis_cyl} – Acier {classe}, rondelle élastique\n"
                f"  (Serrer à {couple_M6 if 'M6' in vis_cyl else (couple_M8 if 'M8' in vis_cyl else couple_M5)} Nm)\n"
                f"- Volant : {n_volant} x Vis {vis_volant} – Acier {classe}, frein-filet conseillé\n"
                f"  (Serrer à {couple_M6 if 'M6' in vis_volant else (couple_M8 if 'M8' in vis_volant else couple_M5)} Nm)\n"
                f"- Liaison bielle/maneton : 1 ou 2 vis M6 (8.8), frein filet fort, écrou Nylstop\n"
                f"- Tolérance perçage : H13 (jeu standard), prévoir alésage si montage précis.\n\n"
                f"**Conseils industriels** :\n"
                f"• Toujours utiliser des rondelles larges sur l’alu, et des écrous Nylstop.\n"
                f"• Prévoir du frein filet Loctite 243 sur tous les filetages soumis aux vibrations.\n"
                f"• Vérifier le serrage après 1er cycle thermique (rodage)."
            )

            self.resultat.config(text=plan_tech)
            self.afficher_schema(d_cyl, ep, n_emb, n_cyl, n_volant, vis_emb, vis_cyl, vis_volant)

        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def afficher_schema(self, d_cyl, ep, n_emb, n_cyl, n_volant, vis_emb, vis_cyl, vis_volant):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        from matplotlib.patches import Rectangle, Circle

        fig = Figure(figsize=(6, 2.2), dpi=100)
        ax = fig.add_subplot(111)
        # Simple croquis schématique : embase, cylindre, volant, et points de vis
        # Embase = grande plaque
        ax.add_patch(Rectangle((0, 0), 180, 60, edgecolor="#222", facecolor="#b9e1f5", lw=2, label="Embase"))
        # Points de vis embase (n_emb)
        f
