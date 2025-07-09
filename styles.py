# styles.py

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
    "fond": "#F4FEFE",         # Blanc-Lunaire (fond général)
    "primaire": "#051440",     # Bleu-France (titre principal, éléments forts)
    "accent": "#0A0B0A",        # Jaune-Vatican (élément accent, surlignage)
    "texte": "#1E1E1E",        # Noir-Figma (texte principal)
    "bouton": "#303030",       # Anthracite (boutons principaux)
    "hover": "#3E5349",        # Natural-Green (survol bouton, hover)
    "bordure": "#D9D9D9",      # Gris Figma (bordures, séparateurs)
    # Bonus si besoin pour variantes secondaires :
    "rouge": "#EC1920",        # Rouge-France
    "jaune_blé": "#E8D630",    # Jaune-Blé (pour warnings)
    "bleu_web": "#091226",     # Bleu-France-Web
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