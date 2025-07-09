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
from styles import COULEURS, bouton_flat

class PageMoteurStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        # --------- CONTAINER 2 COLONNES ---------
        container = tk.Frame(self, bg=COULEURS["fond"])
        container.pack(fill="both", expand=True, padx=40, pady=10)
        container.grid_columnconfigure(0, weight=2)
        container.grid_columnconfigure(1, weight=1)

        # --------- COLONNE GAUCHE : Formulaire + Résultats ---------
        left_col = tk.Frame(container, bg=COULEURS["fond"])
        left_col.grid(row=0, column=0, sticky="nw")

        tk.Label(left_col, text="Conception du moteur Stirling",
                 bg=COULEURS["fond"], fg=COULEURS["primaire"],
                 font=("Segoe UI", 22, "bold")).pack(pady=(22, 10))

        # Formulaire
        form_zone = tk.Frame(left_col, bg=COULEURS["fond"])
        form_zone.pack(pady=(0, 8))

        self.champs = {}
        donnees = [
            ("Puissance souhaitée (W)", "puissance"),
            ("Température chaude (°C)", "t_chaude"),
            ("Température froide (°C)", "t_froide"),
            ("Pression moyenne (bar)", "pression"),
            ("Diamètre du cylindre (mm)", "d_cyl"),
            ("Nombre de joints piston", "nb_joints"),
            ("Rendement génératrice (%)", "rendement_gen"),
            ("Rendement mécanique (%)", "rendement_mec"),
            ("Rendement moteur Stirling (%)", "rendement_stirling"),
        ]
        for i, (label, cle) in enumerate(donnees):
            l = tk.Label(form_zone, text=label, font=("Segoe UI", 11), width=28, anchor="w",
                         bg=COULEURS["fond"], fg=COULEURS["texte"])
            l.grid(row=i, column=0, sticky="w", padx=6, pady=5)
            entry = tk.Entry(form_zone, width=12, font=("Segoe UI", 11))
            if "rendement" in cle:
                entry.insert(0, {"rendement_gen": "90", "rendement_mec": "80", "rendement_stirling": "35"}.get(cle, ""))
            if cle == "nb_joints":
                entry.insert(0, "2")
            form_default = {"puissance": "1000", "t_chaude": "650", "t_froide": "40", "pression": "20", "d_cyl": ""}
            if cle in form_default:
                entry.insert(0, form_default[cle])
            self.champs[cle] = entry
            entry.grid(row=i, column=1, padx=6, pady=5)

        # Gaz
        f_gaz = tk.Frame(form_zone, bg=COULEURS["fond"])
        tk.Label(f_gaz, text="Gaz utilisé", font=("Segoe UI", 11), width=25, anchor="w",
                 bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left", padx=6)
        self.gaz_var = tk.StringVar(value="Air")
        menu = tk.OptionMenu(f_gaz, self.gaz_var, "Air", "Hélium", "Hydrogène", "Azote")
        menu.config(bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 11), highlightthickness=0)
        menu.pack(side="left", padx=4)
        f_gaz.grid(row=len(donnees), column=0, columnspan=2, sticky="w", pady=8)

        # Boutons
        btns = tk.Frame(left_col, bg=COULEURS["fond"])
        btns.pack(pady=(5, 18))
        bouton_flat(btns, "Calculer le moteur", self.calculer).pack(side="left", padx=14)
        bouton_flat(btns, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(side="left", padx=14)

        # Résultats
        self.card_resultat = tk.Frame(left_col, bg="#f4f7fb", bd=1, relief="solid")
        self.card_resultat.pack(pady=(0, 8), padx=0, fill="x", expand=True)
        self.resultat = tk.Label(self.card_resultat, text="", bg="#f4f7fb", fg=COULEURS["accent"],
                                 font=("Consolas", 11), justify="left", anchor="w")
        self.resultat.pack(padx=16, pady=12, fill="both")

        # --------- COLONNE DROITE : SCHEMA ---------
        self.schema_zone = tk.Frame(container, bg=COULEURS["fond"])
        self.schema_zone.grid(row=0, column=1, sticky="ne", padx=20)
        self.canvas = None

    def _materiau_recommande(self, T_chaude):
        if T_chaude < 200:
            return "Acier S235 ou C45 (usage standard, bonne usinabilité)"
        elif T_chaude < 400:
            return "Acier allié ou fonte GS (meilleure résistance à la chaleur)"
        elif T_chaude < 650:
            return "Acier inox 304/316L ou fonte GS (usage courant moteurs Stirling)"
        elif T_chaude < 900:
            return "Inox réfractaire (310S/253MA), Inconel 600, ou acier réfractaire"
        else:
            return "Inconel 718 / Superalliages Ni-Cr (usage très haute température, applications spéciales)"

    def calculer(self):
        try:
            # 1. Lecture des champs et valeurs par défaut
            def getval(champ, typ=float, defval=None):
                txt = self.champs[champ].get().strip()
                if txt: return typ(txt)
                if defval is not None: return defval
                raise ValueError(f"Champ manquant : {champ}")

            W = getval("puissance", float, 1000)
            T_hot_C = getval("t_chaude", float, 650)
            T_hot = T_hot_C + 273.15
            T_cold_C = getval("t_froide", float, 40)
            T_cold = T_cold_C + 273.15
            P_bar = getval("pression", float, 20)
            d_cyl_user = getval("d_cyl", float, None)
            nb_joints = getval("nb_joints", int, 2)
            gaz = self.gaz_var.get()
            rendement_gen = getval("rendement_gen", float, 90) / 100
            rendement_mec = getval("rendement_mec", float, 80) / 100
            rendement_stirling = getval("rendement_stirling", float, 35) / 100

            # -- 1. Calcul thermodynamique --
            delta_T = T_hot - T_cold
            eta_carnot = delta_T / T_hot
            eta_total = eta_carnot * rendement_stirling

            if eta_total < 0.01:
                raise ValueError("Différence de température trop faible pour calculer un moteur réaliste.")

            Qth_necessaire = W / (eta_total * rendement_mec * rendement_gen)

            # -- 2. Géométrie réaliste (course typique 1.2x diamètre) --
            ratio_course = 1.2
            if d_cyl_user and d_cyl_user > 0:
                d_cyl = d_cyl_user
            else:
                # Estimation initiale si vide (pour éviter infini)
                d_cyl = 70  # mm
            course = ratio_course * d_cyl
            A_cyl = np.pi * (d_cyl / 2) ** 2  # mm²
            V_balayage = A_cyl * course * 1e-9  # m³

            # -- 3. Fréquence de rotation (dépend vitesse piston max, 2.2m/s) --
            V_piston_max = 2.2
            freq_max = V_piston_max / (2 * course / 1000)
            freq = min(freq_max, 8)  # 8 Hz max (typiquement de 1 à 8 Hz)
            rpm = freq * 60

            # -- 4. Volume balayé par cycle, puissance réellement possible
            P_Pa = P_bar * 1e5
            puissance_possible = (
                P_Pa * V_balayage * delta_T / T_hot *
                eta_total * freq * rendement_mec * rendement_gen
            )
            # On ne dépasse jamais la puissance cible
            P_elec = min(W, puissance_possible)

            # -- 5. Couple, production annuelle
            P_mec = P_elec / (rendement_gen * rendement_mec) if (rendement_gen * rendement_mec) > 0 else 0
            couple = P_mec / (2 * np.pi * freq) if freq > 0 else 0
            production_annuelle = P_elec * 24 * 365 / 1000  # kWh/an

            # -- 6. Dimensions annexes --
            e_piston = max(0.20 * d_cyl, 10)
            e_joint = 2.5
            zone_morte = 0.08 * course
            jeu_fonctionnement = 0.018 * course
            h_cyl_utile = course
            h_cyl_total = (
                h_cyl_utile + e_piston + nb_joints * e_joint +
                2 * zone_morte + jeu_fonctionnement
            )
            vilebrequin = course / 2

            materiau = self._materiau_recommande(T_hot_C)
            etat_surface = "Ra ≤ 0.4 µm"
            roulement = "Roulement à billes étanche, acier inox ou céramique"

            self.resultat.config(text=f"""
🔧 Résultats réalistes pour {W:.0f} W (gaz : {gaz}) :
Temp. chaude : {T_hot_C:.0f} °C | Temp. froide : {T_cold_C:.0f} °C | Pression : {P_bar:.1f} bar
Rendement Carnot : {eta_carnot*100:.1f} % | Rendement réel moteur : {rendement_stirling*100:.1f} %
Rendement mécanique : {rendement_mec*100:.1f} % | Génératrice : {rendement_gen*100:.1f} %
Puissance thermique à fournir : {Qth_necessaire:.1f} W

-- Géométrie --
Volume total balayé : {V_balayage*1e6:.2f} cm³ (à {freq:.2f} Hz)
Ø cylindre : {d_cyl:.2f} mm | Course piston : {course:.2f} mm (ratio : {ratio_course:.2f})
Hauteur utile : {h_cyl_utile:.2f} mm | Hauteur totale : {h_cyl_total:.2f} mm
Longueur vilebrequin : {vilebrequin:.2f} mm

-- Dynamique --
Vitesse piston max : {V_piston_max:.2f} m/s | Fréquence réelle : {freq:.2f} Hz
Vitesse de rotation : {rpm:.0f} tr/min | Couple vilebrequin : {couple:.2f} Nm

-- Production réelle --
Puissance électrique nette : {P_elec:.1f} W
Production annuelle continue : {production_annuelle:.1f} kWh/an

🛠️ État de surface : {etat_surface}
⚙️ Type de roulement : {roulement}
🧱 Matériau recommandé (cylindre) : {materiau}
""")

            # Schéma technique à jour
            self.afficher_schema(d_cyl, h_cyl_utile, e_piston, nb_joints, e_joint,
                                zone_morte, jeu_fonctionnement, h_cyl_total)

        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")

    def afficher_schema(self, d_cyl, h_utile, e_piston, nb_joints, e_joint,
                       zone_morte, jeu, h_cyl_total):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        import matplotlib.patches as mpatches

        fig = Figure(figsize=(5.5, 2.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.set_title("Coupe longitudinale du cylindre", fontsize=12)

        y = 0
        legend_handles = []

        # Zone morte bas
        zb = mpatches.Rectangle((0, y), d_cyl, zone_morte, color=COULEURS["bordure"], label="Zone morte (bas)")
        ax.add_patch(zb)
        legend_handles.append(zb)
        y += zone_morte

        # Volume utile gaz
        vg = mpatches.Rectangle((0, y), d_cyl, h_utile, color=COULEURS["hover"], label="Volume utile gaz")
        ax.add_patch(vg)
        legend_handles.append(vg)
        y += h_utile

        # Galette/piston
        ps = mpatches.Rectangle((0, y), d_cyl, e_piston, color=COULEURS["accent"], label="Galette/piston")
        ax.add_patch(ps)
        legend_handles.append(ps)
        y += e_piston

        # Joints piston
        for i in range(nb_joints):
            jt = mpatches.Rectangle((0, y), d_cyl, e_joint, color="#ffbe76", label="Joint" if i == 0 else "")
            ax.add_patch(jt)
            if i == 0:
                legend_handles.append(jt)
            y += e_joint

        # Zone morte haut
        zh = mpatches.Rectangle((0, y), d_cyl, zone_morte, color="#d6d6d6", label="Zone morte (haut)")
        ax.add_patch(zh)
        legend_handles.append(zh)
        y += zone_morte

        # Jeu
        j = mpatches.Rectangle((0, y), d_cyl, jeu, color="#ececec", label="Jeu (usinage)")
        ax.add_patch(j)
        legend_handles.append(j)
        y += jeu

        # Contour du cylindre
        ax.plot([0, 0, d_cyl, d_cyl, 0], [0, h_cyl_total, h_cyl_total, 0, 0], color="#222", lw=2, label="Cylindre")

        # Réglage axes
        ax.set_xlim(-0.08*d_cyl, d_cyl*1.12)
        ax.set_ylim(-0.02*h_cyl_total, y*1.04)
        ax.axis("off")

        # Légende à droite
        handles = [h for h in legend_handles if h.get_label()]
        labels = [h.get_label() for h in handles]
        ax.legend(handles, labels, loc="upper right", bbox_to_anchor=(1.22, 1.08), fontsize=9, frameon=True)

        self.canvas = FigureCanvasTkAgg(fig, master=self.schema_zone)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)