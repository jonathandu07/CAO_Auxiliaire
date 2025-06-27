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

# Couleurs officielles (extraites de l'image)
COULEURS = {
    "fond": "#F4FEFE",         # Blanc-Lunaire
    "primaire": "#051440",     # Bleu-France
    "accent": "#0A0B0A",       # Jaune-Vatican
    "texte": "#1E1E1E",        # Noir-Figma
    "bouton": "#303030",       # Anthracite
    "hover": "#3E5349",        # Natural-Green (pour effet hover)
    "bordure": "#D9D9D9",      # Gris Figma
}

# ----- Fonctions de style -----
def carte_bento(parent, titre, contenu):
    frame = tk.Frame(parent, bg=COULEURS["fond"], bd=2, relief="groove", highlightthickness=0)
    titre_label = tk.Label(frame, text=titre, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 14, "bold"))
    contenu_label = tk.Label(frame, text=contenu, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10))
    titre_label.pack(pady=(10, 0))
    contenu_label.pack(pady=(5, 10))
    return frame

def bouton_flat(parent, texte, commande):
    return tk.Button(
        parent, text=texte,
        command=commande,
        bg=COULEURS["bouton"], fg=COULEURS["fond"],
        activebackground=COULEURS["hover"],
        relief="flat", bd=0,
        font=("Segoe UI", 11),
        padx=15, pady=8
    )

# ----- Structure multi-pages -----
class AssistantCAO(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistant de CAO")
        # ---- Met en plein écran natif ----
        self.attributes('-fullscreen', True)
        # ---- Si tu veux une touche pour quitter le plein écran (ex: F11) ----
        self.bind("<F11>", lambda e: self.attributes('-fullscreen', not self.attributes('-fullscreen')))
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False))

        self.configure(bg=COULEURS["fond"])
        self.frames = {}
        self.memo_moteur_stirling = {}

        container = tk.Frame(self, bg=COULEURS["fond"])
        container.pack(fill="both", expand=True)

        for F in (
            PageAccueil,
            PageCalculs,
            PageMateriaux,
            PageParametres,
            PageMoteurStirling,
            PagePistonStirling,
            PageDroneStructure,
            PageDronePropulsion,
            PageDroneIA,
            PageSimulationMission,
            PageBoiteCrabot,
            PageVilebrequin,
        ):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.afficher_page(PageAccueil)

    def afficher_page(self, page_class):
        """Affiche la page demandée (classe) et masque les autres"""
        frame = self.frames[page_class]
        frame.tkraise()



# ----- Pages -----
class PageAccueil(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        # Logo de ta boîte (au-dessus du titre)
        logo_path = "JN-BWF.png"  # 🖼️ remplace par le chemin exact
        if os.path.exists(logo_path):
            image = Image.open(logo_path)
            image = image.resize((128, 128), Image.LANCZOS)  # ou 64x64 selon le rendu souhaité
            self.logo_image = ImageTk.PhotoImage(image)
            tk.Label(self, image=self.logo_image, bg=COULEURS["fond"]).pack(pady=(20, 10))

        # Titre de l'application
        tk.Label(self, text="Assistant de CAO", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        # Boutons uniquement en texte
        boutons = [
            ("Calculs RDM", PageCalculs),
            ("Matériaux", PageMateriaux),
            ("Paramètres", PageParametres),
            ("Conception moteur Stirling", PageMoteurStirling),
            ("Structure du drone", PageDroneStructure),
            ("Propulsion du drone", PageDronePropulsion),
            ("Électronique & IA du drone", PageDroneIA),
            ("Simulation de mission", PageSimulationMission),
            ("Boîte à crabots automatique", PageBoiteCrabot),
            ("Conception piston Stirling (galette)", PagePistonStirling),
            ("Dimensionnement vilebrequin", PageVilebrequin),
        ]

        for txt, page in boutons:
            b = bouton_flat(self, txt, lambda p=page: controller.afficher_page(p))
            b.pack(pady=5)


class PageCalculs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Calculs RDM", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        # Convertisseur kg -> N et kN
        convert_frame = tk.Frame(self, bg=COULEURS["fond"])
        tk.Label(convert_frame, text="Masse (kg) :", bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=0, column=0)
        self.kg_var = tk.StringVar()
        tk.Entry(convert_frame, textvariable=self.kg_var).grid(row=0, column=1)
        self.convert_result = tk.Label(convert_frame, text="", bg=COULEURS["fond"], fg=COULEURS["accent"])
        self.convert_result.grid(row=1, columnspan=2)
        tk.Button(convert_frame, text="Convertir", command=self.convertir_masse).grid(row=0, column=2, padx=5)
        convert_frame.pack(pady=10)

        # Sélection du matériau
        tk.Label(self, text="Matériau :", bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
        self.materiau_var = tk.StringVar(value="Acier")
        tk.OptionMenu(self, self.materiau_var, *MATERIAUX.keys()).pack()

        # Tolérance de sécurité
        tk.Label(self, text="Tolérance (%) :", bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
        self.tolerance_var = tk.StringVar(value="20")
        tk.Entry(self, textvariable=self.tolerance_var).pack()

        # Saisie des paramètres communs
        self.champs_liste = [
            ("Section (mm²)", "section"),
            ("Longueur (mm)", "longueur"),
            ("Force appliquée (N)", "force"),
            ("Moment appliqué (Nm)", "moment"),
            ("Couple appliqué (Nm)", "couple"),
            ("Module d’inertie (mm⁴)", "inertie")
        ]
        self.entrees = {}
        for label, cle in self.champs_liste:
            tk.Label(self, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"]).pack()
            entree = tk.Entry(self)
            entree.pack()
            self.entrees[cle] = entree

        self.resultat_label = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"])
        self.resultat_label.pack(pady=10)

        bouton_flat(self, "Calculer les contraintes", self.calculer).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def convertir_masse(self):
        try:
            masse = float(self.kg_var.get())
            newton = masse * 9.81
            kn = newton / 1000
            self.convert_result.config(text=f"{newton:.2f} N | {kn:.3f} kN")
        except:
            self.convert_result.config(text="Entrée invalide")

    def calculer(self):
        try:
            tol = float(self.tolerance_var.get() or "20") / 100
            mat_selectionne = self.materiau_var.get()
            prop = MATERIAUX[mat_selectionne]
            E = prop["E"]
            Re = prop["Re"]

            # Récupère tout ce qui a été saisi
            vals = {k: self.entrees[k].get().strip() for _, k in self.champs_liste}
            log_auto = []

            # 1) Déduction force à partir de la masse si champ force vide et masse renseignée
            masse_kg = self.kg_var.get().strip()
            if (not vals["force"] or float(vals["force"]) == 0) and masse_kg:
                force_val = float(masse_kg) * 9.81
                vals["force"] = f"{force_val:.3f}"
                self.entrees["force"].delete(0, tk.END)
                self.entrees["force"].insert(0, vals["force"])
                log_auto.append(f"Force déduite de la masse : {vals['force']} N")

            # 2) Section automatique si section manquante mais force présente
            if (not vals["section"] or float(vals["section"]) == 0) and vals["force"]:
                section_val = (float(vals["force"]) / ((1 - tol) * Re)) * 1e6  # mm²
                vals["section"] = f"{section_val:.1f}"
                self.entrees["section"].delete(0, tk.END)
                self.entrees["section"].insert(0, vals["section"])
                log_auto.append(f"Section calculée à partir de la force : {vals['section']} mm²")

            # 3) Force admissible si section saisie mais pas de force
            if (not vals["force"] or float(vals["force"]) == 0) and vals["section"]:
                force_max = (float(vals["section"]) / 1e6) * ((1 - tol) * Re)
                vals["force"] = f"{force_max:.1f}"
                self.entrees["force"].delete(0, tk.END)
                self.entrees["force"].insert(0, vals["force"])
                log_auto.append(f"Force max admissible recalculée : {vals['force']} N")

            # 4) Pour flexion, torsion, flambement : utilise valeurs si présentes sinon 0
            try:    L = float(vals["longueur"]) / 1000 if vals["longueur"] else 1
            except: L = 1
            try:    M = float(vals["moment"]) if vals["moment"] else 0
            except: M = 0
            try:    T = float(vals["couple"]) if vals["couple"] else 0
            except: T = 0
            try:    I = float(vals["inertie"]) / 1e12 if vals["inertie"] else 1e-4
            except: I = 1e-4

            # 5) Contraintes
            A = float(vals["section"]) / 1e6 if vals["section"] else 1e-6
            F = float(vals["force"]) if vals["force"] else 0

            sigma_traction = F / A if A else 0
            sigma_flexion = M * (L / 2) / I if I else 0
            tau_torsion = T * (L / 2) / I if I else 0
            flambement = (np.pi ** 2 * E * I) / (L ** 2) if I else 0

            # 6) Recherche meilleur matériau
            meilleurs = []
            for nom, props in MATERIAUX.items():
                Re_mat = props["Re"]
                if Re_mat == 0: continue
                A_calc = (F / ((1 - tol) * Re_mat)) * 1e6 if F else 0
                meilleurs.append((nom, A_calc))
            meilleurs = [t for t in meilleurs if t[1] > 0]
            meilleurs.sort(key=lambda x: x[1])
            meilleur_mat, meilleure_section = (meilleurs[0] if meilleurs else ("-", 0))

            resultat = ""
            if log_auto:
                resultat += "Données déduites automatiquement :\n- " + "\n- ".join(log_auto) + "\n\n"
            resultat += f"""
Contrainte de traction : {sigma_traction:.2f} Pa
Contrainte de flexion : {sigma_flexion:.2f} Pa
Contrainte de torsion : {tau_torsion:.2f} Pa
Charge critique de flambement : {flambement:.2f} N
Résistance limite du matériau : {Re:.2f} Pa

📐 Section requise avec {mat_selectionne} : {vals['section']} mm² (tolérance {tol*100:.0f}%)
"""
            if meilleur_mat != "-":
                resultat += f"\n✅ Meilleur matériau : {meilleur_mat}\n👉 Section minimale requise : {meilleure_section:.2f} mm²\n"

            self.resultat_label.config(text=resultat.strip())
        except Exception as e:
            self.resultat_label.config(text=f"Erreur : {str(e)}")


class PageMateriaux(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Base de données matériaux", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        # Liste des matériaux clés
        materiaux = [
            ("Acier S235", "E = 210 GPa\nRe = 235 MPa\nρ = 7.85 g/cm³"),
            ("Acier Inox 304", "E = 193 GPa\nRe = 215 MPa\nρ = 8.0 g/cm³"),
            ("Aluminium 6061-T6", "E = 69 GPa\nRe = 276 MPa\nρ = 2.70 g/cm³"),
            ("Titane Grade 5", "E = 114 GPa\nRe = 880 MPa\nρ = 4.43 g/cm³"),
            ("ABS", "E = 2.1 GPa\nRe ≈ 40 MPa\nρ = 1.04 g/cm³"),
            ("Nylon (PA)", "E = 2.5 GPa\nRe ≈ 70 MPa\nρ = 1.15 g/cm³"),
            ("PEEK", "E = 3.6 GPa\nRe = 100 MPa\nρ = 1.3 g/cm³"),
            ("Bakelite", "E ≈ 3.5 GPa\nRe ≈ 60 MPa\nρ = 1.3 g/cm³"),
            ("Carbone époxy", "E = 70–135 GPa\nRe = 600+ MPa\nρ = 1.5 g/cm³"),
            ("Cuivre", "E = 110 GPa\nRe = 70 MPa\nρ = 8.96 g/cm³")
        ]

        for nom, specs in materiaux:
            carte = carte_bento(self, nom, specs)
            carte.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=20)


class PageParametres(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Paramètres", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        carte = carte_bento(self, "Unités", "Longueur : mm\nForce : N\nModule : MPa")
        carte.pack(pady=20)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=20)



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
        zb = mpatches.Rectangle((0, y), d_cyl, zone_morte, color="#d6d6d6", label="Zone morte (bas)")
        ax.add_patch(zb)
        legend_handles.append(zb)
        y += zone_morte

        # Volume utile gaz
        vg = mpatches.Rectangle((0, y), d_cyl, h_utile, color="#b9edc8", label="Volume utile gaz")
        ax.add_patch(vg)
        legend_handles.append(vg)
        y += h_utile

        # Galette/piston
        ps = mpatches.Rectangle((0, y), d_cyl, e_piston, color="#ffe37a", label="Galette/piston")
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




class PageDroneStructure(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Profil de l’aile du drone", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.longueur_entry = self._champ(form_frame, "Longueur de la corde (mm)", 0)
        self.hauteur_entry = self._champ(form_frame, "Épaisseur max (mm)", 1)
        self.camber_entry = self._champ(form_frame, "Cambrure max (%)", 2, default="2.0")
        self.camberpos_entry = self._champ(form_frame, "Position cambrure max (%)", 3, default="40")

        bouton_flat(self, "Afficher le profil", self.afficher_profil).pack(pady=15)
        bouton_flat(self, "Exporter CSV SolidWorks", self.exporter_csv).pack(pady=5)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

        self.canvas = None
        self.coord_label = tk.Label(self, text="", bg=COULEURS["fond"], fg="#333333", font=("Consolas", 8))
        self.coord_label.pack()

        self.last_coords = None

    def _champ(self, parent, label, row, default=""):
        l = tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10))
        l.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=10)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=10)
        return e

    def afficher_profil(self):
        try:
            # Tout en millimètres
            L = float(self.longueur_entry.get())      # corde en mm
            H = float(self.hauteur_entry.get())       # épaisseur max en mm
            camber = float(self.camber_entry.get()) / 100
            camber_pos = float(self.camberpos_entry.get()) / 100
        except ValueError:
            self._show_error("Saisies invalides.")
            return

        t = H / L   # épaisseur relative (ex : 120/1000 = 0.12)
        n = 200     # nombre de points du profil

        x = np.linspace(0, L, n)      # mm
        xt = x / L                    # de 0 à 1 (adimensionné)

        yt = 5 * t * (
            0.2969 * np.sqrt(xt) -
            0.1260 * xt -
            0.3516 * xt ** 2 +
            0.2843 * xt ** 3 -
            0.1015 * xt ** 4
        ) * L     # => mm

        # Courbe de cambrure (toujours en mm)
        yc = np.where(
            x < camber_pos * L,
            camber / (camber_pos ** 2) * (2 * camber_pos * x / L - (x / L) ** 2) * L,
            camber / ((1 - camber_pos) ** 2) * ((1 - 2 * camber_pos) + 2 * camber_pos * x / L - (x / L) ** 2) * L
        )

        dyc_dx = np.where(
            x < camber_pos * L,
            2 * camber / (camber_pos ** 2) * (camber_pos - x / L),
            2 * camber / ((1 - camber_pos) ** 2) * (camber_pos - x / L)
        )
        theta = np.arctan(dyc_dx)

        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)

        # Pour SolidWorks : on veut le contour complet (extrados puis intrados à l'envers)
        X = np.concatenate([xu, xl[::-1]])
        Y = np.concatenate([yu, yl[::-1]])
        coords = np.vstack([X, Y]).T

        # Affichage du profil (en mm)
        fig = Figure(figsize=(7, 2.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(xu, yu, label="Extrados", color='blue')
        ax.plot(xl, yl, label="Intrados", color='red')
        ax.fill_between(xu, yu, yl, where=(yu > yl), color='lightblue', alpha=0.3)
        ax.set_title(f"Profil NACA optimisé - Corde={L:.1f}mm, Ép.={H:.1f}mm, Cambrure={camber*100:.1f}%")
        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.axis("equal")
        ax.legend()
        ax.grid(True)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

        # Affiche les 10 premiers points pour contrôle
        text = "x (mm)\ty (mm)\n" + "\n".join([f"{X[i]:.2f}\t{Y[i]:.2f}" for i in range(0, len(X), max(1, len(X)//10))])
        self.coord_label.config(text=text)

        self.last_coords = coords

    def exporter_csv(self):
        if self.last_coords is None:
            self._show_error("Aucun profil généré !")
            return

        import tkinter.filedialog as fd
        path = fd.asksaveasfilename(title="Exporter profil pour SolidWorks",
                                    defaultextension=".csv",
                                    filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
        if not path:
            return
        # Export en millimètres (X,Y)
        np.savetxt(path, self.last_coords, delimiter=",", header="X (mm),Y (mm)", comments='', fmt="%.4f")
        self._show_error(f"Profil exporté avec succès : {path}")

    def _show_error(self, msg):
        error_popup = tk.Toplevel(self)
        error_popup.title("Info")
        tk.Label(error_popup, text=msg, fg="red").pack(padx=20, pady=10)
        bouton_flat(error_popup, "OK", error_popup.destroy).pack(pady=5)


class PageDronePropulsion(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Calcul de propulsion du drone", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.poids_entry = self._champ(form_frame, "Poids du drone (kg)", 0)
        self.autonomie_entry = self._champ(form_frame, "Autonomie visée (min)", 1)

        bouton_flat(self, "Calculer", self.calculer_propulsion).pack(pady=15)

        self.resultat_label = tk.Label(self, text="", bg=COULEURS["fond"],
                                       fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat_label.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def _champ(self, parent, label, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.grid(row=row, column=1, padx=10)
        return e

    def calculer_propulsion(self):
        try:
            masse = float(self.poids_entry.get())  # en kg
            autonomie = float(self.autonomie_entry.get()) / 60  # min → h
        except ValueError:
            self.resultat_label.config(text="Entrées invalides.")
            return

        g = 9.81  # m/s²
        rendement = 0.7
        puissance_w = (masse * g * 5) / rendement  # estimation 5 m/s montée verticale
        energie_wh = puissance_w * autonomie
        tension_v = 22.2  # batterie LiPo 6S standard
        courant_a = energie_wh / tension_v

        self.resultat_label.config(text=f"""
Puissance moteur nécessaire : {puissance_w:.0f} W
Capacité minimale batterie : {energie_wh:.0f} Wh
Courant requis (à {tension_v} V) : {courant_a:.1f} A
""")


class PageDroneIA(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Calcul d’ajustement ISO", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.diametre_entry = self._champ(form_frame, "Diamètre nominal (mm)", 0)
        self.alésage_var = tk.StringVar(value="H7")
        self.arbre_var = tk.StringVar(value="g6")

        # Menus déroulants
        self._menu(form_frame, "Tolérance de l’alésage", self.alésage_var, ["H7", "H8", "H6"], 1)
        self._menu(form_frame, "Tolérance de l’arbre", self.arbre_var, ["g6", "f7", "k6", "m6"], 2)

        bouton_flat(self, "Calculer", self.calculer_ajustement).pack(pady=15)

        self.resultat_label = tk.Label(self, text="", bg=COULEURS["fond"],
                                       fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat_label.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def _champ(self, parent, label, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.grid(row=row, column=1, padx=10)
        return e

    def _menu(self, parent, label, variable, options, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        tk.OptionMenu(parent, variable, *options).grid(row=row, column=1, padx=10)

    def calculer_ajustement(self):
        # Valeurs typiques d'écart pour un diamètre nominal entre 10 et 50 mm
        ISO_TOLERANCES = {
            "H7": (0, +21),
            "H8": (0, +33),
            "H6": (0, +13),
            "g6": (-14, -4),
            "f7": (-20, -6),
            "k6": (+2, +10),
            "m6": (+8, +20)
        }

        try:
            d = float(self.diametre_entry.get())
        except ValueError:
            self.resultat_label.config(text="Diamètre invalide.")
            return

        ales_min, ales_max = ISO_TOLERANCES[self.alésage_var.get()]
        arb_min, arb_max = ISO_TOLERANCES[self.arbre_var.get()]

        # Jeu en microns → mm
        jeu_min = (ales_min - arb_max) / 1000
        jeu_max = (ales_max - arb_min) / 1000

        if jeu_max < 0:
            ajustement = "Serré"
        elif jeu_min > 0:
            ajustement = "Libre"
        else:
            ajustement = "Incertain / glissant"

        self.resultat_label.config(text=f"""
Jeu minimal : {jeu_min:.3f} mm
Jeu maximal : {jeu_max:.3f} mm
Type d’ajustement : {ajustement}
""")


class PageSimulationMission(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Simulation de mission", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.batt_entry = self._champ(form_frame, "Capacité batterie (Wh)", 0)
        self.puiss_entry = self._champ(form_frame, "Puissance de propulsion (W)", 1)
        self.vit_entry = self._champ(form_frame, "Vitesse de croisière (km/h)", 2)

        # Mode aller simple / aller-retour
        self.mode_var = tk.StringVar()
        self.mode_var.set("aller-retour")
        tk.OptionMenu(form_frame, self.mode_var, "aller", "aller-retour").grid(row=3, column=1, pady=10)

        bouton_flat(self, "Simuler", self.simuler).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

        self.canvas = None

    def _champ(self, parent, label, row):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.grid(row=row, column=1, padx=10)
        return e

    def simuler(self):
        try:
            batt = float(self.batt_entry.get())     # Wh
            puiss = float(self.puiss_entry.get())   # W
            vitesse = float(self.vit_entry.get())   # km/h
        except ValueError:
            return

        if self.mode_var.get() == "aller-retour":
            autonomie_h = batt / puiss / 2
        else:
            autonomie_h = batt / puiss

        distance_km = autonomie_h * vitesse

        # Carte avec Basemap centrée sur Chabeuil
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        m = Basemap(projection='mill', resolution='l',
                    llcrnrlat=-60, urcrnrlat=80,
                    llcrnrlon=-180, urcrnrlon=180, ax=ax)
        m.drawcoastlines()
        m.drawcountries()
        m.drawmapboundary(fill_color='lightblue')
        m.fillcontinents(color='beige', lake_color='lightblue')

        # Coordonnées de Chabeuil (ou autre base)
        base_lat, base_lon = 44.933, 5.033
        x0, y0 = m(base_lon, base_lat)
        m.plot(x0, y0, 'ro', markersize=5)

        # Tracer un cercle de rayon d’action
        circle_lats, circle_lons = self._trace_circle(base_lat, base_lon, distance_km)
        x, y = m(circle_lons, circle_lats)
        m.plot(x, y, 'r-', linewidth=1.5)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.canvas = FigureCanvasTkAgg(fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

    def _trace_circle(self, lat, lon, rayon_km, points=360):
        R = 6371.0
        lat_rad = np.radians(lat)
        lon_rad = np.radians(lon)
        d = rayon_km / R

        angles = np.linspace(0, 2*np.pi, points)
        lat_circle = np.arcsin(np.sin(lat_rad)*np.cos(d) +
                               np.cos(lat_rad)*np.sin(d)*np.cos(angles))
        lon_circle = lon_rad + np.arctan2(np.sin(angles)*np.sin(d)*np.cos(lat_rad),
                                          np.cos(d)-np.sin(lat_rad)*np.sin(lat_circle))
        return np.degrees(lat_circle), np.degrees(lon_circle)


class PageBoiteCrabot(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Conception boîte à crabots automatique", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        self.champs = {}
        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack()

        parametres = [
            ("Vitesse d’entrée (tr/min)", "v_in"),
            ("Nombre de rapports", "nb_rapports"),
            ("Diamètre de l’arbre (mm)", "d_arbre"),
            ("Module des engrenages (mm)", "module"),
        ]

        for i, (label, cle) in enumerate(parametres):
            tk.Label(form, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                     font=("Segoe UI", 10), width=30, anchor="w").grid(row=i, column=0, padx=10, pady=5)
            entry = tk.Entry(form, font=("Segoe UI", 10), width=15)
            entry.grid(row=i, column=1, padx=10)
            self.champs[cle] = entry

        bouton_flat(self, "Charger depuis moteur Stirling", self.charger_depuis_stirling).pack(pady=5)
        bouton_flat(self, "Calculer", self.calculer).pack(pady=15)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"],
                                 fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def charger_depuis_stirling(self):
        """Pré-remplit les champs avec les valeurs du moteur Stirling s'ils existent."""
        data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}

        if data:
            if data.get("rpm"):
                self.champs["v_in"].delete(0, tk.END)
                self.champs["v_in"].insert(0, f"{data['rpm']:.0f}")
            if data.get("vilebrequin"):
                self.champs["d_arbre"].delete(0, tk.END)
                self.champs["d_arbre"].insert(0, f"{data['vilebrequin']:.2f}")
            # Tu peux aussi pré-remplir "module" si tu le veux (par défaut à 2)
            self.champs["module"].delete(0, tk.END)
            self.champs["module"].insert(0, "2.0")
            # Nb rapports : valeur par défaut 4
            self.champs["nb_rapports"].delete(0, tk.END)
            self.champs["nb_rapports"].insert(0, "4")
            self.resultat.config(text="Valeurs importées du moteur Stirling.")
        else:
            self.resultat.config(text="Aucune donnée moteur Stirling disponible.")

    def calculer(self):
        # Déduction intelligente :
        try:
            v_in = self.champs["v_in"].get()
            n = self.champs["nb_rapports"].get()
            d = self.champs["d_arbre"].get()
            m = self.champs["module"].get()

            # Remplissage automatique si possible
            if not v_in:
                data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}
                v_in = data.get("rpm", 1500)
                self.champs["v_in"].insert(0, str(int(v_in)))
            if not n:
                n = 4
                self.champs["nb_rapports"].insert(0, "4")
            if not d:
                data = self.controller.memo_moteur_stirling if hasattr(self.controller, "memo_moteur_stirling") else {}
                d = data.get("vilebrequin", 20)
                self.champs["d_arbre"].insert(0, f"{float(d):.2f}")
            if not m:
                m = 2.0
                self.champs["module"].insert(0, "2.0")

            v_in = float(self.champs["v_in"].get())
            n = int(self.champs["nb_rapports"].get())
            d = float(self.champs["d_arbre"].get())
            m = float(self.champs["module"].get())

        except ValueError:
            self.resultat.config(text="⚠️ Vérifie les entrées.")
            return

        rapports = []
        vitesses = []
        for i in range(1, n + 1):
            z1 = 20
            z2 = int(z1 * (1 + i * 0.25))  # rapport progressif, un peu plus étagé
            r = z2 / z1
            v_out = v_in / r
            rapports.append(f"Rapport {i} : {z1} / {z2} = {r:.2f}")
            vitesses.append(f"Vitesse sortie {i} : {v_out:.1f} tr/min")

        entraxe = m * (20 + z2) / 2 / 1000  # mm en m
        resultats = "Données déduites automatiquement si besoin.\n\n"
        resultats += "\n".join(rapports + vitesses)
        resultats += f"\n\nDiamètre d’arbre : {d} mm"
        resultats += f"\nModule choisi : {m} mm"
        resultats += f"\nEntraxe estimé : {entraxe:.3f} m"

        self.resultat.config(text=resultats)

        

class PagePistonStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Conception piston Stirling (galette)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        descr = ("Ce calculateur estime toutes les côtes d’un piston galette pour moteur Stirling mono-cylindre.\n"
                 "⚙️ Utilise la même architecture que la page moteur : entre les mêmes données de base.")
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

        # Valeurs par défaut pour le matériau du piston
        self.champs["materiau_piston"].insert(0, "Alu 2017A / 6082 / Graphite")

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Segoe UI", 10), justify="left")
        self.resultat.pack(pady=10)

        bouton_flat(self, "Calculer le piston", self.calculer_piston).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def calculer_piston(self):
        try:
            # --- Lecture et valeurs standard ---
            d_cyl = float(self.champs["d_cyl"].get())
            h_cyl_utile = float(self.champs["h_cyl_utile"].get())
            nb_joints = int(self.champs["nb_joints"].get()) if self.champs["nb_joints"].get() else 2
            t_chaude = float(self.champs["t_chaude"].get()) if self.champs["t_chaude"].get() else 650
            mat_piston = self.champs["materiau_piston"].get().strip() or "Aluminium 2017A"

            # Cotes typiques pour piston galette :
            jeu_lateral = 0.03 * d_cyl    # Jeu latéral entre piston et cylindre (3% du Ø, min 0.03 mm)
            epaisseur_piston = max(0.16 * d_cyl, 8)  # Galette (16% du Ø mini 8mm)
            profondeur_rainure = 1.6      # mm (rainure à joint torique)
            largeur_rainure = 2.4         # mm (joint Viton standard)
            epaisseur_fond = 0.12 * d_cyl # Fond de la galette (12% du Ø)
            surface_piston = np.pi * (d_cyl / 2) ** 2  # mm²

            masse_piston = (surface_piston * epaisseur_piston * 2.8e-3) / 1000  # Aluminium, densité ≈ 2.8g/cm³

            # Température max selon matériau
            if "graphite" in mat_piston.lower():
                temp_max = 300  # °C (auto-lubrifiant)
            elif "alu" in mat_piston.lower() or "aluminium" in mat_piston.lower():
                temp_max = 200
            elif "acier" in mat_piston.lower():
                temp_max = 500
            else:
                temp_max = 200

            # Résumé fabrication
            consignes = (
                f"- Ø galette : {d_cyl - 2*jeu_lateral:.2f} mm (jeu de {jeu_lateral:.2f} mm)\n"
                f"- Épaisseur galette : {epaisseur_piston:.2f} mm\n"
                f"- Fond galette : {epaisseur_fond:.2f} mm\n"
                f"- Nombre de joints : {nb_joints} (rainure {largeur_rainure:.1f} × {profondeur_rainure:.1f} mm)\n"
                f"- Masse piston estimée : {masse_piston:.1f} g\n"
                f"- Température max piston : {temp_max} °C\n"
            )

            # Recommandations
            remarque = (
                f"✅ Conseil : Piston galette à faible jeu (auto-lubrifiant si graphite).\n"
                "Préférer un alliage Alu 2017A, 6082, ou graphite dense (faible usure). "
                "Rainure pour joint Viton ou PTFE renforcé. "
                "Adapter la longueur du piston selon la course max (laisser 8 à 15 mm de sécurité pour la butée à pleine course)."
            )

            self.resultat.config(text=f"""
🔩 **Piston galette pour Stirling**\n
{consignes}
Matériau conseillé : {mat_piston}
{remarque}
""")
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")


class PageVilebrequin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Dimensionnement du vilebrequin", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=10)

        self.puissance = self._champ(form, "Puissance transmise (W)", 0)
        self.vitesse = self._champ(form, "Vitesse de rotation (tr/min)", 1)
        self.couple = self._champ(form, "Couple transmis (Nm)", 2)
        self.longueur = self._champ(form, "Longueur entre paliers (mm)", 3, default="80")
        self.rayon_manivelle = self._champ(form, "Rayon excentrique (mm)", 4, default="20")
        self.largeur_maneton = self._champ(form, "Largeur maneton (mm)", 5, default="18")
        self.tol = self._champ(form, "Tolérance sécurité (%)", 6, default="20")

        tk.Label(form, text="Matériau", bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=7, column=0, sticky="w", padx=10, pady=5)
        self.mat_var = tk.StringVar(value="Acier S235")
        tk.OptionMenu(form, self.mat_var, *MATERIAUX.keys()).grid(row=7, column=1, padx=10)

        bouton_flat(self, "Calculer vilebrequin", self.calculer).pack(pady=10)
        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"], font=("Consolas", 10), justify="left")
        self.resultat.pack(pady=10)

        self.canvas = None
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=15)

    def _champ(self, parent, label, row, default=""):
        tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                 font=("Segoe UI", 10), width=30, anchor="w").grid(row=row, column=0, padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=15)
        e.insert(0, default)
        e.grid(row=row, column=1, padx=10)
        return e

    def calculer(self):
        try:
            W = float(self.puissance.get()) if self.puissance.get() else None
            N = float(self.vitesse.get()) if self.vitesse.get() else None
            C = float(self.couple.get()) if self.couple.get() else None
            L = float(self.longueur.get())
            r = float(self.rayon_manivelle.get())
            b = float(self.largeur_maneton.get())
            tol = float(self.tol.get()) / 100
            mat = self.mat_var.get()

            mat_props = MATERIAUX.get(mat)
            if mat_props is None:
                raise ValueError(f"Matériau '{mat}' introuvable dans la base.")

            Re = float(mat_props["Re"]) * 1e6 if "Re" in mat_props else 250e6  # MPa -> Pa

            # Si couple absent, calcule à partir de puissance & vitesse
            if not C:
                if W is not None and N is not None:
                    C = W / (2 * np.pi * (N/60))
                else:
                    raise ValueError("Donne au moins la puissance+vitesse ou le couple transmis.")

            Re_adm = (1-tol) * Re
            tau_adm = 0.6 * Re_adm

            # Diamètre min du maneton sous torsion et flexion combinée
            d_m = ((16 * C) / (np.pi * tau_adm))**(1/3) * 1000  # mm

            # Diamètre des paliers généralement > maneton
            d_p = d_m * 1.15

            self.resultat.config(text=f"""
🧮 Calcul vilebrequin :
- Couple transmis = {C:.2f} Nm | L = {L:.0f} mm | Rayon excentrique = {r:.1f} mm
- Résistance admissible τ = {tau_adm/1e6:.0f} MPa (sécurité {tol*100:.0f}%)
- **Ø maneton mini recommandé** : {d_m:.1f} mm
- **Ø paliers recommandé** : {d_p:.1f} mm
- Largeur maneton : {b:.1f} mm
""")
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
        fig = Figure(figsize=(8, 2), dpi=100)
        ax = fig.add_subplot(111)

        # --- Dimensions des éléments principaux ---
        largeur_palier = 16      # mm (ajustable)
        largeur_bras = 12        # mm
        largeur_maneton = b      # mm (entrée utilisateur)
        espace_bras_maneton = 4  # mm pour visibilité

        # Placement sur l'axe X (gauche à droite)
        x0 = 0
        x1 = x0 + largeur_palier
        x2 = x1 + largeur_bras
        x3 = x2 + espace_bras_maneton
        x4 = x3 + largeur_maneton
        x5 = x4 + espace_bras_maneton
        x6 = x5 + largeur_bras
        x7 = x6 + largeur_palier

        # Centre du maneton (excentré de r)
        y = 1.0

        # Paliers gauche/droite
        ax.add_patch(mpatches.Rectangle((x0, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier gauche"))
        ax.add_patch(mpatches.Rectangle((x6, y - d_p/2), largeur_palier, d_p, color="#b6cef2", label="Palier droit"))

        # Bras de manivelle
        ax.add_patch(mpatches.Rectangle((x1, y - d_p/2), largeur_bras, d_p, color="#aaaaaa", label="Bras"))
        ax.add_patch(mpatches.Rectangle((x5, y - d_p/2), largeur_bras, d_p, color="#aaaaaa"))

        # Maneton (excentré en Y de +r)
        ax.add_patch(mpatches.Rectangle((x3, y + r - d_m/2), largeur_maneton, d_m, color="#ef767a", label="Maneton excentré"))

        # Axe principal
        ax.plot([x0, x7], [y, y], color="k", lw=2, linestyle="--", zorder=3)

        # Axe du maneton (excentré)
        x_centre_maneton = x3 + largeur_maneton / 2
        ax.plot([x_centre_maneton, x_centre_maneton], [y, y + r], color="#222", lw=2, linestyle="-")
        ax.plot([x3, x4], [y + r, y + r], color="#a33", lw=2, linestyle=":")

        # Légendes
        ax.text(x1 + largeur_bras/2, y + d_p/2 + 3, "Bras de manivelle", ha="center", color="#555")
        ax.text(x3 + largeur_maneton/2, y + r + d_m/2 + 2, "Maneton (excentré)", ha="center", color="#a33")
        ax.text(x0 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")
        ax.text(x6 + largeur_palier/2, y + d_p/2 + 2, "Palier", ha="center", color="#334")

        # Ajuste la vue
        ax.set_xlim(x0 - 10, x7 + 10)
        ax.set_ylim(y - d_p, y + d_p * 2)
        ax.axis("off")
        ax.set_title("Croquis industriel du vilebrequin – vue de dessus")

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=5)


class PageDimensionnementStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        # --------- FORMULAIRE ---------
        left_col = tk.Frame(self, bg=COULEURS["fond"])
        left_col.pack(side="left", fill="both", expand=True, padx=32, pady=18)

        tk.Label(left_col, text="Dimensionnement moteur Stirling – Outil ultime",
                 bg=COULEURS["fond"], fg=COULEURS["primaire"],
                 font=("Segoe UI", 21, "bold")).pack(pady=(12, 10))

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
            l.grid(row=i, column=0, sticky="w", padx=6, pady=5)
            if cle == "gaz":
                var = tk.StringVar(value=default)
                menu = tk.OptionMenu(left_col, var, "Air", "Hélium", "Hydrogène", "Azote")
                menu.config(bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 11), highlightthickness=0)
                menu.grid(row=i, column=1, padx=6, pady=5)
                self.champs[cle] = var
            else:
                entry = tk.Entry(left_col, width=13, font=("Segoe UI", 11))
                if default:
                    entry.insert(0, default)
                entry.grid(row=i, column=1, padx=6, pady=5)
                self.champs[cle] = entry

        # Boutons
        btns = tk.Frame(left_col, bg=COULEURS["fond"])
        btns.grid(row=len(donnees), column=0, columnspan=2, pady=(10, 20))
        bouton_flat(btns, "Calculer", self.calculer).pack(side="left", padx=14)
        bouton_flat(btns, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(side="left", padx=14)

        # Résultats
        self.resultat = tk.Label(left_col, text="", bg="#f4f7fb", fg=COULEURS["accent"],
                                 font=("Consolas", 11), justify="left", anchor="w", width=64)
        self.resultat.grid(row=len(donnees)+1, column=0, columnspan=2, sticky="w", padx=2, pady=(2, 8))

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


# ----- Lancement -----
app = AssistantCAO()
app.mainloop()
