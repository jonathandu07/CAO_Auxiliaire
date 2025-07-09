# pages\page_moteur_stirling.py
import tkinter as tk
from styles import COULEURS, bouton_flat
from pages.page_piston_stirling import PagePistonStirling
from pages.page_cylindre_stirling import PageCylindreStirling
from pages.page_vilebrequin_stirling import PageVilebrequinStirling

# À créer :
from pages.page_bielle_stirling import PageBielleStirling
from pages.page_volant_stirling import PageVolantStirling
from pages.page_embase_stirling import PageEmbaseStirling
from pages.page_visserie_stirling import PageVisserieStirling
from pages.page_arbre_stirling import PageArbreStirling

from pages.page_accueil import PageAccueil

DONNEES = [
    ("Puissance souhaitée (W)", "puissance"),
    ("Température chaude (°C)", "t_chaude"),
    ("Température froide (°C)", "t_froide"),
    ("Pression moyenne (bar)", "pression"),
    ("Diamètre du cylindre (mm)", "d_cyl"),
]

def default_vals():
    return {
        "puissance": 1000,
        "t_chaude": 650,
        "t_froide": 40,
        "pression": 20,
        "d_cyl": 70,
        "gaz": "Air",
    }

class PageMoteurStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller
        self.vars = {k: tk.StringVar() for _, k in DONNEES}
        self.editing_key = tk.StringVar(value="puissance")

        # Formulaire principal
        form = tk.Frame(self, bg=COULEURS["fond"])
        form.pack(pady=20, padx=30, side="left", anchor="n")

        tk.Label(form, text="Entrer une seule donnée :", font=("Segoe UI", 14, "bold"),
                 bg=COULEURS["fond"], fg=COULEURS["primaire"]).pack(pady=(0,12))

        self.entries = {}
        for label, cle in DONNEES:
            row = tk.Frame(form, bg=COULEURS["fond"])
            row.pack(fill="x", pady=2)
            radio = tk.Radiobutton(
                row, variable=self.editing_key, value=cle, bg=COULEURS["fond"],
                command=self.on_editing_change
            )
            radio.pack(side="left")
            tk.Label(row, text=label, bg=COULEURS["fond"], width=24, anchor="w").pack(side="left")
            entry = tk.Entry(row, textvariable=self.vars[cle], width=8, font=("Segoe UI", 11))
            entry.pack(side="left", padx=6)
            self.entries[cle] = entry

        # Gaz
        gaz_zone = tk.Frame(form, bg=COULEURS["fond"])
        gaz_zone.pack(pady=(10,0))
        tk.Label(gaz_zone, text="Gaz :", bg=COULEURS["fond"]).pack(side="left")
        self.gaz_var = tk.StringVar(value="Air")
        tk.OptionMenu(gaz_zone, self.gaz_var, "Air", "Hélium", "Hydrogène", "Azote").pack(side="left", padx=4)

        bouton_flat(form, "Valider", self.calculer_auto).pack(pady=10)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(PageAccueil)).pack(pady=2)

        # Résultats
        self.resultat = tk.Label(self, text="", bg=COULEURS["fond"], font=("Consolas", 11), justify="left")
        self.resultat.pack(padx=32, side="left", anchor="n")

        # Sous-pages : pièces principales + visserie
        souspage_zone = tk.Frame(self, bg=COULEURS["fond"])
        souspage_zone.pack(padx=30, pady=20, side="left", anchor="n")
        bouton_flat(souspage_zone, "Détail Piston", lambda: self.goto_piece(PagePistonStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Détail Cylindre", lambda: self.goto_piece(PageCylindreStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Détail Vilebrequin", lambda: self.goto_piece(PageVilebrequinStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Détail Bielle", lambda: self.goto_piece(PageBielleStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Détail Volant", lambda: self.goto_piece(PageVolantStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Détail Arbre principal", lambda: self.goto_piece(PageArbreStirling)).pack(pady=2, fill="x")  # <--- AJOUTÉ ICI !
        bouton_flat(souspage_zone, "Support / Embase", lambda: self.goto_piece(PageEmbaseStirling)).pack(pady=2, fill="x")
        bouton_flat(souspage_zone, "Visserie & Assemblage", lambda: self.goto_piece(PageVisserieStirling)).pack(pady=2, fill="x")

        self.init_data()
        self.on_editing_change()  # Appliquer la config d'édition initiale

    def init_data(self):
        vals = self.controller.memo_moteur_stirling if self.controller.memo_moteur_stirling else default_vals()
        for _, cle in DONNEES:
            self.vars[cle].set(str(vals.get(cle, "")))
        self.gaz_var.set(vals.get("gaz", "Air"))

    def on_editing_change(self):
        editing = self.editing_key.get()
        for cle, entry in self.entries.items():
            entry.config(state="normal" if cle == editing else "readonly")

    def calculer_auto(self):
        try:
            editing_cle = self.editing_key.get()
            input_val = float(self.vars[editing_cle].get().replace(",", "."))
            vals = default_vals()
            vals.update(self.controller.memo_moteur_stirling)
            vals[editing_cle] = input_val
            vals["gaz"] = self.gaz_var.get()

            # Calculs croisés à affiner selon ta logique
            if editing_cle == "puissance":
                pass
            elif editing_cle == "d_cyl":
                vals["puissance"] = round(float(vals["d_cyl"]) ** 2 / 5)
            elif editing_cle == "t_chaude":
                vals["puissance"] = round(1000 * (1 + (float(vals["t_chaude"]) - 650) / 1000))

            for cle in self.vars:
                self.vars[cle].set(str(vals[cle]))
            self.gaz_var.set(vals["gaz"])
            self.controller.memo_moteur_stirling = vals

            self.on_editing_change()
            self.resultat.config(text="\n".join(f"{k} : {v}" for k, v in vals.items()))
        except Exception as e:
            self.resultat.config(text=f"Erreur : {e}")

    def goto_piece(self, page):
        self.calculer_auto()
        self.controller.afficher_page(page)
