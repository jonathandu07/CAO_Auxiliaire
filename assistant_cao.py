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
            PageDimensionnementStirling,
        ):
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.afficher_page(PageAccueil)

    def afficher_page(self, page_class):
        """Affiche la page demandée (classe) et masque les autres"""
        frame = self.frames[page_class]
        frame.tkraise()