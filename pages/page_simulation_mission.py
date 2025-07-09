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