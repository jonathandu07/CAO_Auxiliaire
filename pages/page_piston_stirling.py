import tkinter as tk
import numpy as np
from styles import COULEURS, bouton_flat

class PagePistonStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Conception piston Stirling (galette)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        descr = ("Ce calculateur estime toutes les côtes d’un piston galette pour moteur Stirling mono-cylindre.\n"
                 "⚙️ Entrer les données de base. Le plan détaillé est généré pour CAO.")
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).pack()

        self.champs = {}
        donnees = [
            ("Diamètre du cylindre (mm)", "d_cyl"),
            ("Hauteur utile du cylindre (mm)", "h_cyl_utile"),
            ("Nombre de joints", "nb_joints"),
            ("Température chaude max (°C)", "t_chaude"),
            ("Matériau du piston", "materiau_piston")
        ]
        for label, cle in donnees:
            f = tk.Frame(self, bg=COULEURS["fond"])
            tk.Label(f, text=label, font=("Segoe UI", 10), width=30, anchor="w",
                     bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left")
            entry = tk.Entry(f, width=15, font=("Segoe UI", 10))
            entry.pack(side="right")
            f.pack(pady=5)
            self.champs[cle] = entry

        # Valeur par défaut pour le matériau
        self.champs["materiau_piston"].insert(0, "Alu 2017A / 6082 / Graphite")

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left", anchor="w")
        self.resultat.pack(pady=10, fill="x")

        bouton_flat(self, "Générer le plan technique", self.calculer_piston).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def calculer_piston(self):
        try:
            # -- Lecture des champs --
            d_cyl = float(self.champs["d_cyl"].get())
            h_cyl_utile = float(self.champs["h_cyl_utile"].get())
            nb_joints = int(self.champs["nb_joints"].get()) if self.champs["nb_joints"].get() else 2
            t_chaude = float(self.champs["t_chaude"].get()) if self.champs["t_chaude"].get() else 650
            mat_piston = self.champs["materiau_piston"].get().strip() or "Aluminium 2017A"

            # -- Calculs principaux --
            jeu_lateral = max(0.03 * d_cyl, 0.03)  # Jeu latéral min 0.03 mm
            d_piston = d_cyl - 2 * jeu_lateral
            epaisseur_piston = max(0.16 * d_cyl, 8)
            epaisseur_fond = 0.12 * d_cyl
            profondeur_rainure = 1.6      # mm
            largeur_rainure = 2.4         # mm
            surface_piston = np.pi * (d_piston / 2) ** 2  # mm²
            masse_piston = (surface_piston * epaisseur_piston * 2.8e-3) / 1000  # g

            # Température max selon matériau
            if "graphite" in mat_piston.lower():
                temp_max = 300
            elif "alu" in mat_piston.lower() or "aluminium" in mat_piston.lower():
                temp_max = 200
            elif "acier" in mat_piston.lower():
                temp_max = 500
            else:
                temp_max = 200

            # Texte du plan pour SolidWorks
            plan = (
                f"PLAN TECHNIQUE : PISTON GALETTE STIRLING\n"
                f"--------------------------------------------------\n"
                f"1. Forme : Cylindre (galette), arrêtes légèrement chanfreinées\n"
                f"2. Ø extérieur piston (Øp) : {d_piston:.2f} mm (Tol. H8)\n"
                f"3. Épaisseur totale piston : {epaisseur_piston:.2f} mm\n"
                f"4. Épaisseur fond (côté froid) : {epaisseur_fond:.2f} mm\n"
                f"5. Nombre de joints : {nb_joints}\n"
                f"6. Rainure(s) joint : {nb_joints} x (largeur {largeur_rainure:.1f} mm × profondeur {profondeur_rainure:.1f} mm),\n"
                f"     décalée(s) de 2 mm du bord, symétriques\n"
                f"7. Matière : {mat_piston}\n"
                f"8. Jeu latéral avec cylindre : {jeu_lateral:.2f} mm (Haut. piston < hauteur utile cylindre)\n"
                f"9. Surface : poli-miroir, rugosité Ra ≤ 0.4 µm\n"
                f"10. Masse estimée : {masse_piston:.1f} g\n"
                f"11. Température max piston : {temp_max} °C\n"
                f"\n"
                f"Pour SolidWorks :\n"
                f"- Croquis :\n"
                f"   . Faire un disque Ø {d_piston:.2f} mm, extrusion {epaisseur_piston:.2f} mm\n"
                f"   . Perçage central si axe de guidage (à ajuster selon conception)\n"
                f"   . Ajouter les rainures pour joints sur le côté latéral\n"
                f"   . Chanfrein de 0.5 mm sur toutes les arrêtes vives\n"
                f"- Tolérances à ajuster selon ajustement H7/g6 ou ton process d’usinage.\n"
                f"\n"
                f"Recommandé : contrôler le jeu piston/cylindre, tester le coulissement à sec AVANT assemblage définitif.\n"
            )

            self.resultat.config(text=plan)
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")
