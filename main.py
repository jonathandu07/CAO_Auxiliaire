import tkinter as tk

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

        for F in (PageAccueil, PageCalculs, PageMateriaux, PageParametres):
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
            self.logo_image = tk.PhotoImage(file=logo_path)
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
        carte = carte_bento(self, "Acier", "E = 210 GPa\nLimite élastique = 235 MPa")
        carte.pack(pady=20)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=20)

class PageParametres(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        tk.Label(self, text="Paramètres", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).pack(pady=20)
        carte = carte_bento(self, "Unités", "Longueur : mm\nForce : N\nModule : MPa")
        carte.pack(pady=20)
        bouton_flat(self, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=20)

# ----- Lancement -----
app = AssistantCAO()
app.mainloop()
