import tkinter as tk
import os
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from mpl_toolkits.basemap import Basemap
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from materiaux import MATERIAUX
import math
import pandas as pd

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
        self.geometry("900x600")
        self.configure(bg=COULEURS["fond"])
        self.frames = {}

        container = tk.Frame(self, bg=COULEURS["fond"])
        container.pack(fill="both", expand=True)

        for F in (
            PageAccueil,
            PageCalculs,
            PageMateriaux,
            PageParametres,
            PageMoteurStirling,
            PageDroneStructure,
            PageDronePropulsion,
            PageDroneIA,
            PageSimulationMission,
            PageBoiteCrabot
        ):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.afficher_page(PageAccueil)

    def afficher_page(self, page_class):
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
            ("Boîte à crabots automatique", PageBoiteCrabot)
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

        tk.Label(self, text="Conception du moteur Stirling", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        self.champs = {}
        donnees = [
            ("Puissance souhaitée (W)", "puissance"),
            ("Température chaude (°C)", "t_chaude"),
            ("Température froide (°C)", "t_froide"),
            ("Pression moyenne (bar)", "pression"),
            ("Fréquence de fonctionnement (Hz)", "freq")
        ]
        for label, cle in donnees:
            f = tk.Frame(self, bg=COULEURS["fond"])
            tk.Label(f, text=label, font=("Segoe UI", 10), width=30, anchor="w",
                     bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left")
            entry = tk.Entry(f, width=15, font=("Segoe UI", 10))
            entry.pack(side="right")
            f.pack(pady=5)
            self.champs[cle] = entry

        # Choix du gaz
        f_gaz = tk.Frame(self, bg=COULEURS["fond"])
        tk.Label(f_gaz, text="Gaz utilisé", font=("Segoe UI", 10), width=30, anchor="w",
                 bg=COULEURS["fond"], fg=COULEURS["texte"]).pack(side="left")
        self.gaz_var = tk.StringVar(value="Air")
        menu = tk.OptionMenu(f_gaz, self.gaz_var, "Air", "Hélium", "Hydrogène", "Azote")
        menu.config(bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10), highlightthickness=0)
        menu.pack(side="right")
        f_gaz.pack(pady=5)

        # Résultat
        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                 font=("Segoe UI", 10), justify="left")
        self.resultat.pack(pady=10)

        # Boutons
        bouton_flat(self, "Calculer le moteur", self.calculer).pack(pady=10)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def calculer(self):
        try:
            # Valeurs par défaut ingénieur
            defval = {
                "puissance": 1000,      # W
                "t_chaude": 650,        # °C
                "t_froide": 40,         # °C
                "pression": 20,         # bar
                "freq": 30              # Hz
            }
            # Récupère ou complète les champs
            def getval(champ):
                txt = self.champs[champ].get()
                return float(txt) if txt else defval[champ]

            W = getval("puissance")
            T_hot = getval("t_chaude") + 273.15
            T_cold = getval("t_froide") + 273.15
            P_bar = getval("pression")
            f = getval("freq")
            gaz = self.gaz_var.get()

            rendement = 0.35  # réaliste (35% du rendement de Carnot)
            delta_T = T_hot - T_cold
            eta_carnot = delta_T / T_hot
            eta_total = eta_carnot * rendement

            # Protection contre les divisions par zéro (ex : T_hot == T_cold)
            if eta_total < 0.01:
                raise ValueError("Différence de température trop faible pour calculer un moteur réaliste.")

            energie_cycle = W / (f * eta_total)
            P_Pa = P_bar * 1e5
            V_tot = energie_cycle / (P_Pa * delta_T / T_hot)  # m³

            # Calcul des dimensions caractéristiques (exemple type)
            d_cyl = (4 * V_tot * 1e6 / (np.pi * 30)) ** (1 / 3)     # mm
            h_cyl = 1.2 * d_cyl
            course = h_cyl / 2
            vilebrequin = course / 2
            couple = W / (2 * np.pi * f)
            rpm = f * 60

            etat_surface = "Ra ≤ 0.4 µm"
            roulement = "Roulement à billes étanche, acier inox ou céramique"

            auto_txt = []
            for champ, val in defval.items():
                if not self.champs[champ].get():
                    auto_txt.append(f"{champ.replace('_',' ').capitalize()} → {val}")

            txtauto = ""
            if auto_txt:
                txtauto = "Valeurs complétées automatiquement : " + ", ".join(auto_txt) + "\n"

            self.resultat.config(text=f"""{txtauto}
🔧 Résultats pour {W:.0f} W avec gaz = {gaz} :
- Volume total : {V_tot*1e6:.2f} cm³
- Diamètre du cylindre : {d_cyl:.2f} mm
- Hauteur du cylindre : {h_cyl:.2f} mm
- Course du piston : {course:.2f} mm
- Longueur du vilebrequin : {vilebrequin:.2f} mm
- Couple attendu : {couple:.2f} Nm
- Vitesse de rotation : {rpm:.0f} tr/min

🛠️ État de surface : {etat_surface}
⚙️ Type de roulement : {roulement}
""")
        except Exception as e:
            self.resultat.config(text=f"Erreur : {str(e)}")





class PageDroneStructure(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])

        tk.Label(self, text="Profil de l’aile du drone", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)

        form_frame = tk.Frame(self, bg=COULEURS["fond"])
        form_frame.pack()

        self.longueur_entry = self._champ(form_frame, "Longueur de l’aile (m)", 0)
        self.hauteur_entry = self._champ(form_frame, "Hauteur maximale (m)", 1)

        bouton_flat(self, "Afficher le profil", self.afficher_profil).pack(pady=15)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

        self.canvas = None

    def _champ(self, parent, label, row):
        l = tk.Label(parent, text=label, bg=COULEURS["fond"], fg=COULEURS["texte"],
                     font=("Segoe UI", 10))
        l.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        e = tk.Entry(parent, font=("Segoe UI", 10), width=10)
        e.grid(row=row, column=1, padx=10)
        return e

    def afficher_profil(self):
        try:
            L = float(self.longueur_entry.get())
            H = float(self.hauteur_entry.get())
        except ValueError:
            return

        # Génération d’un profil type NACA simplifié (cambrure max = H/L)
        x = np.linspace(0, 1, 200)
        m = H / L  # cambrure relative
        t = 0.12   # épaisseur relative fixe

        yt = 5 * t * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
        yc = np.where(x < 0.5, m * x / 0.5, m * (1 - x) / 0.5)
        xu, yu = x - yt*np.sin(0), yc + yt*np.cos(0)
        xl, yl = x + yt*np.sin(0), yc - yt*np.cos(0)

        fig = Figure(figsize=(5, 2), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(xu*L, yu*L, label="Extrados")
        ax.plot(xl*L, yl*L, label="Intrados")
        ax.axis("equal")
        ax.set_title("Profil d’aile généré")
        ax.set_xlabel("Longueur (m)")
        ax.set_ylabel("Hauteur (m)")
        ax.grid(True)

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

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

        bouton_flat(self, "Calculer", self.calculer).pack(pady=15)

        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"],
                                 fg=COULEURS["texte"], font=("Segoe UI", 11), justify="left")
        self.resultat.pack(pady=10)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=10)

    def calculer(self):
        try:
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
            z2 = z1 * (1 + i * 0.2)  # rapport progressif
            r = z2 / z1
            v_out = v_in / r
            rapports.append(f"Rapport {i} : {r:.2f}")
            vitesses.append(f"Vitesse sortie {i} : {v_out:.1f} tr/min")

        entraxe = m * (20 + 40) / 2 / 1000  # mm en m
        resultats = "\n".join(rapports + vitesses)
        resultats += f"\n\nDiamètre d’arbre : {d} mm"
        resultats += f"\nModule choisi : {m} mm"
        resultats += f"\nEntraxe estimé : {entraxe:.3f} m"

        self.resultat.config(text=resultats)

# ----- Lancement -----
app = AssistantCAO()
app.mainloop()
