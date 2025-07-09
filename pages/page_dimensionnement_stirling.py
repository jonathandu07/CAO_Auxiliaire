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

class PageDimensionnementStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        # --------- FORMULAIRE ---------
        left_col = tk.Frame(self, bg=COULEURS["fond"])
        left_col.grid(row=0, column=0, sticky="nsew", padx=32, pady=18)

        titre = tk.Label(left_col, text="Dimensionnement moteur Stirling – Outil ultime",
                         bg=COULEURS["fond"], fg=COULEURS["primaire"],
                         font=("Segoe UI", 21, "bold"))
        titre.grid(row=0, column=0, columnspan=2, pady=(12, 10))

        # Données d'entrée
        self.champs = {}
        donnees = [
            ("Température chaude (°C)", "t_chaude", "650"),
            ("Température froide (°C)", "t_froide", "40"),
            ("Pression travail (bar)", "pression", "20"),
            ("Diamètre cylindre (mm)", "d_cyl", ""),  # Laisse vide pour auto-calc
            ("Course piston (mm)", "course", ""),
            ("Fréquence (Hz)", "freq", ""),
            ("Type de gaz", "gaz", "Air"),
            ("Rendement moteur (%)", "rendement_moteur", "35"),
            ("Rendement mécanique (%)", "rendement_mec", "80"),
            ("Rendement génératrice (%)", "rendement_gen", "90"),
            ("Nombre de cylindres", "nb_cyl", "1"),
        ]
        for i, (label, cle, default) in enumerate(donnees):
            l = tk.Label(left_col, text=label, font=("Segoe UI", 11), width=26, anchor="w",
                         bg=COULEURS["fond"], fg=COULEURS["texte"])
            l.grid(row=i+1, column=0, sticky="w", padx=6, pady=5)
            if cle == "gaz":
                var = tk.StringVar(value=default)
                menu = tk.OptionMenu(left_col, var, "Air", "Hélium", "Hydrogène", "Azote")
                menu.config(bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 11), highlightthickness=0)
                menu.grid(row=i+1, column=1, padx=6, pady=5)
                self.champs[cle] = var
            else:
                entry = tk.Entry(left_col, width=13, font=("Segoe UI", 11))
                if default:
                    entry.insert(0, default)
                entry.grid(row=i+1, column=1, padx=6, pady=5)
                self.champs[cle] = entry

        # Boutons
        btns = tk.Frame(left_col, bg=COULEURS["fond"])
        btns.grid(row=len(donnees)+2, column=0, columnspan=2, pady=(10, 20))
        bouton_flat(btns, "Calculer", self.calculer).pack(side="left", padx=14)
        bouton_flat(btns, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(side="left", padx=14)

        # Résultats
        self.resultat = tk.Label(left_col, text="", bg="#f4f7fb", fg=COULEURS["accent"],
                                 font=("Consolas", 11), justify="left", anchor="w", width=64)
        self.resultat.grid(row=len(donnees)+3, column=0, columnspan=2, sticky="w", padx=2, pady=(2, 8))

    def calculer(self):
        try:
            def safe_float(key, default=None):
                txt = self.champs[key].get().strip()
                return float(txt) if txt else default

            # 1. Entrées utilisateur
            T_hot_C    = safe_float("t_chaude", 650)
            T_cold_C   = safe_float("t_froide", 40)
            T_hot      = T_hot_C + 273.15
            T_cold     = T_cold_C + 273.15
            P_bar      = safe_float("pression", 20)
            d_cyl      = safe_float("d_cyl", None)
            course     = safe_float("course", None)
            freq       = safe_float("freq", None)
            gaz        = self.champs["gaz"].get()
            rendement_moteur = safe_float("rendement_moteur", 35) / 100
            rendement_mec    = safe_float("rendement_mec", 80) / 100
            rendement_gen    = safe_float("rendement_gen", 90) / 100
            nb_cyl = int(self.champs["nb_cyl"].get() or 1)

            eta_carnot = 1 - (T_cold / T_hot)
            eta_reel   = eta_carnot * rendement_moteur * rendement_mec * rendement_gen

            # AUTO-DIMENSIONNEMENT si d_cyl ou course ou freq manquant
            d_cyl_auto = False
            course_auto = False
            freq_auto = False

            # On cible une vitesse moyenne piston de 2,5 m/s max (classique pour Stirling robuste)
            V_piston_max = 2.5  # m/s

            # Si tout est manquant, cible 1000 W (pratique)
            P_bar_val = P_bar if P_bar is not None else 20
            W_cible = 1000

            # 1. Si d_cyl ou course est manquant → on choisit d'abord course/d_cyl = 1,2 (ratio classique)
            if d_cyl is None and course is None:
                d_cyl = 70
                d_cyl_auto = True
                course = 1.2 * d_cyl
                course_auto = True
            elif d_cyl is None:
                course = course
                d_cyl = course / 1.2
                d_cyl_auto = True
            elif course is None:
                d_cyl = d_cyl
                course = 1.2 * d_cyl
                course_auto = True

            # 2. Calcul volume balayé V (m3)
            V = np.pi * (d_cyl/2)**2 * course * 1e-9 * nb_cyl

            # 3. Si fréquence manquante, déduire pour respecter V_piston_max
            # Vitesse piston moyenne = 2 * course * freq (en m/s)
            if freq is None:
                freq = V_piston_max / (2 * (course / 1000)) if course > 0 else 5
                freq_auto = True

            rpm = freq * 60
            P_Pa = P_bar_val * 1e5

            # Puissance théorique simplifiée
            P_th = P_Pa * V * freq * eta_carnot * rendement_moteur  # W

            # Puissance nette électrique
            P_elec = P_th * rendement_mec * rendement_gen

            # Couple arbre (N.m)
            P_mec = P_elec / rendement_gen if rendement_gen > 0 else 0
            N = freq  # tr/s
            couple = P_mec / (2 * np.pi * N) if N > 0 else 0

            # Dimension arbre (acier, sécurité 60MPa)
            tau_adm = 60e6  # Pa
            d_arbre = ((16 * abs(couple)) / (np.pi * tau_adm)) ** (1/3) * 1000  # mm
            l_arbre = 1.6 * d_arbre  # mm

            # Indiquer quelles valeurs ont été auto-déduites
            auto = []
            if d_cyl_auto: auto.append("diamètre cylindre")
            if course_auto: auto.append("course piston")
            if freq_auto: auto.append("fréquence")

            txtauto = ""
            if auto:
                txtauto = "Valeurs complétées automatiquement : " + ", ".join(auto) + "\n"

            self.resultat.config(text=f"""{txtauto}
🌡️ Entrées : Tₕ={T_hot_C:.1f} °C, T𝒇={T_cold_C:.1f} °C, P={P_bar_val:.1f} bar, d={d_cyl:.1f} mm, course={course:.1f} mm, f={freq:.2f} Hz, gaz={gaz}
🔄 Cylindres : {nb_cyl}

⏩ Rendement Carnot : {eta_carnot*100:.1f} %
⏩ Rendement global réel : {eta_reel*100:.2f} %

🛠️ Volume balayé : {V*1e6:.2f} cm³
🛞 Tours/minute : {rpm:.0f}
⚡️ Puissance nette électrique : {P_elec:.1f} W
⛓️ Couple arbre : {couple:.2f} Nm

🧱 Dimension mini arbre : Ø {d_arbre:.2f} mm × {l_arbre:.2f} mm
""")

        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")