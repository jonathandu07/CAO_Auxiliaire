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