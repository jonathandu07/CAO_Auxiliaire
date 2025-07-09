# pages/page_vilebrequin_stirling.py
import tkinter as tk
import numpy as np
from styles import COULEURS, bouton_flat
from materiaux import MATERIAUX
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pages.page_accueil import PageAccueil

class PageVilebrequinStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement du vilebrequin", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)

        # Lecture des données moteur
        moteur = getattr(self.controller, "memo_moteur_stirling", {}) or {}
        P_tot = moteur.get("puissance", 1000)
        n_cyl = moteur.get("n_cyl", 1)
        rpm = moteur.get("rpm", 900)
        couple_nom = (P_tot / n_cyl) / (2 * np.pi * (rpm/60)) if n_cyl else 10
        L_defaut = max(80, 2.7 * moteur.get("course", 30)) if "course" in moteur else 80

        self.champs = {}
        items = [
            ("Nombre de cylindres", "n_cyl", str(n_cyl)),
            ("Puissance transmise (W)", "puissance", str(P_tot)),
            ("Couple transmis par cyl. (Nm)", "couple", f"{couple_nom:.2f}"),
            ("Vitesse de rotation (tr/min)", "vitesse", str(rpm)),
            ("Longueur entre paliers (mm)", "longueur", f"{L_defaut:.2f}"),
            ("Rayon excentrique (mm)", "rayon_manivelle", f"{moteur.get('course', 20)/2:.2f}"),
            ("Largeur maneton (mm)", "largeur_maneton", "18"),
            ("Tolérance sécurité (%)", "tol", "20"),
        ]
        for i, (label, key, default) in enumerate(items):
            tk.Label(form, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                     font=("Segoe UI", 10), width=32, anchor="w").grid(row=i, column=0, padx=10, pady=5)
            ent = tk.Entry(form, font=("Segoe UI", 10), width=15)
            ent.insert(0, default)
            ent.grid(row=i, column=1, padx=10)
            self.champs[key] = ent

        tk.Label(form, text="Matériau", bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=len(items), column=0, sticky="w", padx=10, pady=5)
        self.mat_var = tk.StringVar(value="Acier S355")
        tk.OptionMenu(form, self.mat_var, *MATERIAUX.keys()).grid(row=len(items), column=1, padx=10)

        bouton_flat(form, "Calculer vilebrequin", self.calculer).grid(row=len(items)+1, columnspan=2, pady=10)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Consolas", 10), justify="left", anchor="w")
        self.resultat.pack(pady=10, fill="x")

        self.canvas = None
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=15)

    def calculer(self):
        try:
            n_cyl = int(self.champs["n_cyl"].get())
            W = float(self.champs["puissance"].get())
            N = float(self.champs["vitesse"].get())
            C = float(self.champs["couple"].get())
            L = float(self.champs["longueur"].get())
            r = float(self.champs["rayon_manivelle"].get())
            b = float(self.champs["largeur_maneton"].get())
            tol = float(self.champs["tol"].get()) / 100
            mat = self.mat_var.get()
            mat_props = MATERIAUX.get(mat)
            if mat_props is None:
                raise ValueError(f"Matériau '{mat}' introuvable dans la base.")

            Re = float(mat_props["Re"]) * 1e6 if "Re" in mat_props else 250e6  # MPa -> Pa

            # Calcul très précis : charge maxi sur le maneton
            couple_tot = C * n_cyl  # couple total pour tous les cylindres
            Re_adm = (1-tol) * Re
            tau_adm = 0.6 * Re_adm

            # Diamètre min du maneton sous torsion + flexion combinée
            d_m = ((16 * couple_tot) / (np.pi * tau_adm))**(1/3) * 1000  # mm
            d_m = max(d_m, 12)  # Sécu mini

            # Diamètre des paliers
            d_p = d_m * 1.15

            largeur_palier = 0.9 * b
            largeur_bras = 0.65 * b
            espace_bras_maneton = 0.22 * b

            # Vitesse de rotation en rad/s pour calcul dynamique
            omega = 2 * np.pi * (N/60)
            effort_radial = couple_tot / r if r > 0 else 0

            plan = (
                f"PLAN TECHNIQUE : VILEBREQUIN STIRLING MULTICYLINDRE\n"
                f"---------------------------------------------------\n"
                f"Nombre de cylindres : {n_cyl}\n"
                f"Puissance transmise totale : {W:.1f} W\n"
                f"Couple transmis total : {couple_tot:.2f} Nm\n"
                f"Vitesse de rotation : {N:.1f} tr/min\n"
                f"1. Longueur entre paliers (L) : {L:.1f} mm\n"
                f"2. Diamètre maneton (Øm) : {d_m:.2f} mm (Tol. h7)\n"
                f"3. Largeur maneton : {b:.1f} mm\n"
                f"4. Diamètre paliers (Øp) : {d_p:.2f} mm (Tol. h7)\n"
                f"5. Largeur palier : {largeur_palier:.2f} mm\n"
                f"6. Bras de manivelle : {largeur_bras:.2f} mm chacun\n"
                f"7. Rayon excentrique (manivelle) : {r:.2f} mm\n"
                f"8. Espace entre bras/maneton : {espace_bras_maneton:.2f} mm\n"
                f"9. Matériau recommandé : {mat}\n"
                f"10. Résistance admissible τ : {tau_adm/1e6:.0f} MPa (Sécurité {tol*100:.0f}%)\n"
                f"11. Effort radial max : {effort_radial:.2f} N\n"
                f"\n"
                f"Instructions CAO/SolidWorks :\n"
                f"- Axe principal (Øp), extrusion sur toute la longueur.\n"
                f"- Bras de manivelle : extrusion largeur {largeur_bras:.2f} mm, reliés au maneton.\n"
                f"- Maneton excentré (Øm, b): centre à r = {r:.2f} mm de l’axe principal.\n"
                f"- Palier gauche et droit (Øp), largeur {largeur_palier:.2f} mm.\n"
                f"- Tous les axes et arrondis, tolérance h7 pour montage sur roulements.\n"
                f"💡 Astuce : prévoir un congé de rayon 2 mm à la jonction bras/maneton.\n"
                f"⚠️ Vérifier l’équilibrage dynamique avant usinage.\n"
            )

            self.resultat.config(text=plan)
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
        fig = Figure(figsize=(8.5, 2.6), dpi=110)
        ax = fig.add_subplot(111)

        largeur_palier = 0.9 * b
        largeur_bras = 0.65 * b
        largeur_maneton = b
        espace_bras_maneton = 0.22 * b

        # Placement sur l'axe X
        x0 = 0
        x1 = x0 + largeur_palier
        x2 = x1 + largeur_bras
        x3 = x2 + espace_bras_maneton
        x4 = x3 + largeur_maneton
        x5 = x4 + espace_bras_maneton
        x6 = x5 + largeur_bras
        x7 = x6 + largeur_palier

        y = 1.0

        # Palier gauche/droite
        ax.add_patch(mpatches.Rectangle((x0, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier gauche"))
        ax.add_patch(mpatches.Rectangle((x6, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier droit"))
        # Bras de manivelle
        ax.add_patch(mpatches.Rectangle((x1, y - d_p/2), largeur_bras, d_p, color="#aaaaaa", label="Bras"))
        ax.add_patch(mpatches.Rectangle((x5, y - d_p/2), largeur_bras, d_p, color="#aaaaaa"))
        # Maneton
        ax.add_patch(mpatches.Rectangle((x3, y + r - d_m/2), largeur_maneton, d_m, color="#ef767a", label="Maneton excentré"))

        ax.plot([x0, x7], [y, y], color="k", lw=2, linestyle="--", zorder=3)
        x_centre_maneton = x3 + largeur_maneton / 2
        ax.plot([x_centre_maneton, x_centre_maneton], [y, y + r], color="#222", lw=2, linestyle="-")
        ax.plot([x3, x4], [y + r, y + r], color="#a33", lw=2, linestyle=":")

        ax.text(x1 + largeur_bras/2, y + d_p/2 + 3, "Bras de manivelle", ha="center", color="#555")
        ax.text(x3 + largeur_maneton/2, y + r + d_m/2 + 2, "Maneton (excentré)", ha="center", color="#a33")
        ax.text(x0 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")
        ax.text(x6 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")

        ax.set_xlim(x0 - 10, x7 + 10)
        ax.set_ylim(y - d_p, y + d_p * 2)
        ax.axis("off")
        ax.set_title("Croquis industriel du vilebrequin – vue de dessus")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=8)
