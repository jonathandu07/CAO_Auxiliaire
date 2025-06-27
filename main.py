import tkinter as tk
import os
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Couleurs officielles (extraites de l'image)
COULEURS = {
    "fond": "#F4FEFE",         # Blanc-Lunaire
    "primaire": "#051440",     # Bleu-France
    "accent": "#FFC600",       # Jaune-Vatican
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
            PageAccueil, PageCalculs, PageMateriaux, PageParametres,
            PageMoteurStirling, PageDroneStructure, PageDronePropulsion,
            PageDroneIA, PageSimulationMission
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
            ("Simulation de mission", PageSimulationMission)
        ]

        for txt, page in boutons:
            b = bouton_flat(self, txt, lambda p=page: controller.afficher_page(p))
            b.pack(pady=5)


class PageCalculs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Calculs RDM", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        carte = carte_bento(self, "Exemple de module", "Calcul de moment fléchissant (à venir)")
        carte.pack(pady=20)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=20)

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
            ("Diamètre du cylindre (mm)", "d_cyl"),
            ("Course du piston (mm)", "course"),
            ("Longueur de la bielle (mm)", "bielle"),
            ("Volume chambre chaude (cm³)", "v_chaude"),
            ("Volume chambre froide (cm³)", "v_froide"),
            ("Température chaude (°C)", "t_chaude"),
            ("Température froide (°C)", "t_froide"),
            ("Fréquence de fonctionnement (Hz)", "freq"),
            ("Pression moyenne (bar)", "pression"),
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
        self.gaz_var = tk.StringVar()
        self.gaz_var.set("Air")
        menu = tk.OptionMenu(f_gaz, self.gaz_var, "Air", "Hélium", "Hydrogène", "Azote")
        menu.config(bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10), highlightthickness=0)
        f_gaz.pack(pady=5)

        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=30)


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
        tk.Label(self, text="Électronique & IA du drone (à venir)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 16)).pack(pady=30)

class PageSimulationMission(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Simulation de mission (à venir)", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 16)).pack(pady=30)



# ----- Lancement -----
app = AssistantCAO()
app.mainloop()
