# main.py
import tkinter as tk
from styles import COULEURS, bouton_flat  # widgets/couleurs personnalisés

# --- Import de toutes les pages (à adapter si tu ajoutes de nouvelles pages) ---
from pages.page_calculs import PageCalculs
from pages.page_materiaux import PageMateriaux
from pages.page_parametres import PageParametres
from pages.page_moteur_stirling import PageMoteurStirling
from pages.page_piston_stirling import PagePistonStirling
from pages.page_drone_structure import PageDroneStructure
from pages.page_drone_propulsion import PageDronePropulsion
from pages.page_drone_ia import PageDroneIA
from pages.page_simulation_mission import PageSimulationMission
from pages.page_boite_crabot import PageBoiteCrabot
from pages.page_vilebrequin_stirling import PageVilebrequinStirling
from pages.page_dimensionnement_stirling import PageDimensionnementStirling
from pages.page_accueil import PageAccueil

# ----------------- Application principale avec structure multi-pages -----------------
class AssistantCAO(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistant de CAO")
        self.attributes('-fullscreen', True)
        self.bind("<F11>", lambda e: self.attributes('-fullscreen', not self.attributes('-fullscreen')))
        self.bind("<Escape>", lambda e: self.attributes('-fullscreen', False))

        self.configure(bg=COULEURS["fond"])

        # Mémoire partagée pour les pages (ex : données moteur, paramètres globaux…)
        self.frames = {}
        self.memo_moteur_stirling = {}

        container = tk.Frame(self, bg=COULEURS["fond"])
        container.pack(fill="both", expand=True)

        # --- Instanciation et enregistrement de chaque page ---
        pages = (
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
            PageVilebrequinStirling,
            PageDimensionnementStirling,
        )

        for PageClass in pages:
            frame = PageClass(parent=container, controller=self)
            self.frames[PageClass] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.afficher_page(PageAccueil)

    def afficher_page(self, page_class):
        """Affiche la page demandée (par classe)"""
        frame = self.frames[page_class]
        frame.tkraise()

# --- Lancement de l’application ---
if __name__ == "__main__":
    app = AssistantCAO()
    app.mainloop()
