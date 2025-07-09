# pages/page_moteur_stirling.py

import tkinter as tk
import numpy as np
from styles import COULEURS, bouton_flat
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from pages.page_piston_stirling import PagePistonStirling
from pages.page_cylindre_stirling import PageCylindreStirling
from pages.page_vilebrequin_stirling import PageVilebrequinStirling
from pages.page_bielle_stirling import PageBielleStirling
from pages.page_volant_stirling import PageVolantStirling
from pages.page_embase_stirling import PageEmbaseStirling
from pages.page_visserie_stirling import PageVisserieStirling
from pages.page_arbre_stirling import PageArbreStirling
from pages.page_accueil import PageAccueil

PI = np.pi
R = 8.314  # Constante gaz parfait

def borned(val, vmin, vmax):
    """Contrainte une valeur entre vmin et vmax"""
    return max(vmin, min(val, vmax))

def recommandation_n_cyl(puissance):
    """Renvoie un nombre réaliste de cylindres selon la puissance"""
    if puissance < 200:
        return 1
    elif puissance < 1000:
        return 2
    elif puissance < 4000:
        return 4
    elif puissance < 12000:
        return 6
    elif puissance < 25000:
        return 8
    elif puissance < 70000:
        return 12
    elif puissance < 150000:
        return 16
    return 24

def pression_recommandee(puissance, n_cyl):
    """Valeur indicative de pression maximale selon la puissance (plus la puissance est grande, plus la pression doit augmenter)"""
    if puissance < 300:
        return 10
    elif puissance < 1000:
        return 15
    elif puissance < 5000:
        return 20
    elif puissance < 20000:
        return 28
    elif puissance < 70000:
        return 38
    return 55

def rpm_recommandee(puissance):
    """Valeur indicative de régime maximal selon puissance"""
    if puissance < 1000:
        return 1600
    elif puissance < 5000:
        return 1500
    elif puissance < 20000:
        return 1400
    elif puissance < 50000:
        return 1200
    elif puissance < 120000:
        return 950
    return 700

def temperature_chaude_reco():
    """Valeur industrielle standard en °C pour moteur robuste avec air ou hélium (hors haute techno)"""
    return 650

def temperature_froide_reco():
    return 40

def sanitize_inputs(P_tot, n_cyl, P_bar, rpm, T_chaud, T_froide):
    """Corrige dynamiquement les entrées irréalistes"""
    rec_n_cyl = recommandation_n_cyl(P_tot)
    n_cyl = int(borned(n_cyl, 1, 32))
    if n_cyl > 2 * rec_n_cyl:
        n_cyl = rec_n_cyl

    # Corrige la pression service en bar
    rec_P_bar = pression_recommandee(P_tot, n_cyl)
    P_bar = borned(P_bar, 6, rec_P_bar * 1.2)
    if abs(P_bar - rec_P_bar) > rec_P_bar * 0.5:
        P_bar = rec_P_bar

    # Corrige régime cible
    rec_rpm = rpm_recommandee(P_tot)
    rpm = borned(rpm, 400, rec_rpm * 1.25)
    if rpm > rec_rpm * 1.15:
        rpm = rec_rpm

    # Températures réalistes
    T_chaud = borned(T_chaud, 450, 800)
    T_froide = borned(T_froide, -20, 90)
    if T_chaud < T_froide + 100:
        T_chaud = T_froide + 120

    # Retourne les valeurs corrigées
    return float(P_tot), int(n_cyl), float(P_bar), float(rpm), float(T_chaud), float(T_froide)

class PageMoteurStirling(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COULEURS["fond"])
        self.controller = controller

        tk.Label(self, text="Conception moteur Stirling universel", bg=COULEURS["fond"],
                 fg=COULEURS["primaire"], font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(16,4))
        descr = (
            "Ce module dimensionne un moteur Stirling industriel à partir de la puissance. "
            "Les autres paramètres (cylindres, pression, régime, cotes, etc.) sont recalculés pour rester réalistes et fiables."
        )
        tk.Label(self, text=descr, bg=COULEURS["fond"], fg=COULEURS["texte"], font=("Segoe UI", 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=20)

        form = tk.Frame(self, bg=COULEURS["fond"])
        form.grid(row=2, column=0, sticky="nw", padx=(18,30), pady=(12,10))
        self.fields = {}
        champs = [
            ("Puissance totale (W)", "puissance", "15000"),
            ("Nombre de cylindres", "n_cyl", "8"),
            ("Pression service (bar)", "pression", "20"),
            ("Régime cible (tr/min)", "rpm", "1400"),
            ("Température chaude (°C)", "t_chaude", "650"),
            ("Température froide (°C)", "t_froide", "40"),
        ]
        for i, (lbl, key, default) in enumerate(champs):
            tk.Label(form, text=lbl, font=("Segoe UI", 11), bg=COULEURS["fond"], fg=COULEURS["texte"]).grid(row=i, column=0, sticky="w")
            ent = tk.Entry(form, width=10, font=("Segoe UI", 11))
            ent.insert(0, default)
            ent.grid(row=i, column=1, padx=7)
            self.fields[key] = ent

        bouton_flat(form, "Calculer le plan moteur", self.calculer).grid(row=len(champs), column=0, columnspan=2, pady=14)
        bouton_flat(form, "Retour", lambda: controller.afficher_page(PageAccueil)).grid(row=len(champs)+1, column=0, columnspan=2, pady=6)

        self.plan_texte = tk.Label(self, text="", bg=COULEURS["fond"], fg=COULEURS["accent"],
                                   font=("Consolas", 10), justify="left", anchor="nw")
        self.plan_texte.grid(row=3, column=0, sticky="nw", pady=10)

        souspage_zone = tk.Frame(self, bg=COULEURS["fond"])
        souspage_zone.grid(row=4, column=0, sticky="nw", padx=16, pady=(6,10))
        bouton_flat(souspage_zone, "Détail Piston", lambda: self.goto_piece(PagePistonStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Détail Cylindre", lambda: self.goto_piece(PageCylindreStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Détail Vilebrequin", lambda: self.goto_piece(PageVilebrequinStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Détail Bielle", lambda: self.goto_piece(PageBielleStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Détail Volant", lambda: self.goto_piece(PageVolantStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Détail Arbre", lambda: self.goto_piece(PageArbreStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Support / Embase", lambda: self.goto_piece(PageEmbaseStirling)).pack(side="left", padx=4)
        bouton_flat(souspage_zone, "Visserie", lambda: self.goto_piece(PageVisserieStirling)).pack(side="left", padx=4)

        self.cadre_schema = tk.Frame(self, bg=COULEURS["fond"])
        self.cadre_schema.grid(row=2, column=1, rowspan=4, sticky="ne", padx=(0,10), pady=10)
        self.canvas = None

    def calculer(self):
        try:
            # Récupère et corrige toutes les entrées incohérentes
            P_tot = abs(float(self.fields["puissance"].get()))
            n_cyl = abs(int(self.fields["n_cyl"].get()))
            P_bar = abs(float(self.fields["pression"].get()))
            rpm = abs(float(self.fields["rpm"].get()))
            T_chaud = abs(float(self.fields["t_chaude"].get()))
            T_froide = abs(float(self.fields["t_froide"].get()))

            # Correction intelligente et couplée de toutes les entrées
            P_tot, n_cyl, P_bar, rpm, T_chaud, T_froide = sanitize_inputs(P_tot, n_cyl, P_bar, rpm, T_chaud, T_froide)

            # ---- CALCULS ----
            f = rpm / 60
            rendement = 0.22
            P = P_bar * 1e5
            P_cyl = P_tot / n_cyl

            # Calcul du volume balayé/cylindre (respecte les contraintes d'usure piston)
            v_piston_max = 1.8
            d_cyl, course, v_piston, V_balayé = 45, 45, 10, 0
            correction_ok = False
            for _ in range(15):
                V_balayé = P_cyl / (P * f * rendement)
                d_cyl = (4 * V_balayé / (PI * 0.85))**(1/3)
                course = 0.85 * d_cyl
                v_piston = 2 * course * f / 1000
                if v_piston > v_piston_max:
                    course *= 0.96
                else:
                    correction_ok = True
                    break
            V_balayé_cm3 = V_balayé * 1e6

            S_piston = PI/4 * (d_cyl/1000)**2
            F_piston_max = P * S_piston
            effort_maneton = F_piston_max / np.cos(np.radians(17))
            C_nom = P_cyl / (2 * PI * f)
            tau_adm = 160e6
            d_vilebrequin = ((16 * C_nom) / (PI * tau_adm))**(1/3) * 1000
            masse_air = (P * V_balayé / (R * (T_chaud + 273.15))) * 29

            warnings = []
            if not correction_ok:
                warnings.append("⚠️ Limite de vitesse piston atteinte, dimensions réduites automatiquement.")

            if T_chaud < T_froide + 100:
                warnings.append("⚠️ T° chaude augmentée pour assurer un fonctionnement efficace.")

            plan = (
                f"PLAN MOTEUR STIRLING MULTICYLINDRE – CALCULS INDUSTRIELS\n"
                f"-------------------------------------------------------\n"
                f"Puissance totale : {P_tot:.0f} W – Cylindres : {n_cyl}\n"
                f"Pression service corrigée : {P_bar:.1f} bar\n"
                f"T° Chaude corrigée : {T_chaud:.1f} °C | T° froide corrigée : {T_froide:.1f} °C\n"
                f"Régime corrigé : {rpm:.0f} tr/min | Rendement estimé : {rendement*100:.1f}%\n"
                f"Puissance/cylindre : {P_cyl:.1f} W\n"
                f"Volume balayé/cylindre : {V_balayé_cm3:.1f} cm³\n"
                f"Diamètre cylindre : {d_cyl:.3f} mm | Course piston : {course:.3f} mm\n"
                f"Vitesse linéaire piston : {v_piston:.3f} m/s (max : 1.8 m/s)\n"
                f"Couple/cylindre : {C_nom:.2f} Nm\n"
                f"Effort piston max : {F_piston_max:.1f} N | Effort maneton : {effort_maneton:.1f} N\n"
                f"Diamètre min maneton vilebrequin : {d_vilebrequin:.2f} mm\n"
                f"Masse air/cycle/cylindre : {masse_air:.2f} g\n"
                f"\nNOMENCLATURE (par cylindre) :\n"
                f"- Cylindre Ø {d_cyl:.3f} mm, course {course:.3f} mm\n"
                f"- Piston galette épaisseur {round(0.16*d_cyl,2)} mm\n"
                f"- Bielle L = {round(2.3*course,2)} mm\n"
                f"- Vilebrequin Ø {d_vilebrequin:.2f} mm (maneton)\n"
                f"- Refroidissement, embases, visserie : à détailler selon conception\n"
                f"\n{' '.join(warnings)}\n"
            )
            self.plan_texte.config(text=plan)
            # Pour les autres modules
            self.controller.memo_moteur_stirling = {
                "puissance": P_tot, "n_cyl": n_cyl, "pression": P_bar,
                "rpm": rpm, "t_chaude": T_chaud, "t_froide": T_froide,
                "d_cyl": d_cyl, "course": course, "P_cyl": P_cyl
            }
            self.afficher_schema(n_cyl, d_cyl, course)
        except Exception as e:
            self.plan_texte.config(text=f"Erreur : {str(e)}")

    def afficher_schema(self, n_cyl, d_cyl, course):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        fig = Figure(figsize=(min(13, n_cyl*1.6), 3.8), dpi=110)
        ax = fig.add_subplot(111)
        ecart = 1.4 * d_cyl
        for i in range(n_cyl):
            x = 1 + i * ecart
            ax.add_patch(Rectangle((x, 1), course, d_cyl, fc="#dde3f8", ec="#111", lw=2, zorder=1))
            ep_piston = 0.16 * d_cyl
            ax.add_patch(Rectangle((x+course-ep_piston, 1), ep_piston, d_cyl, fc="#f7d6c1", ec="#a36b19", lw=2, zorder=2))
            ax.text(x + course/2, 1 + d_cyl + 5, f"Cyl {i+1}", ha="center", fontsize=10, color="#175")
        ax.axis("off")
        ax.set_xlim(0, 1 + n_cyl * ecart)
        ax.set_ylim(0, 1 + d_cyl + 30)
        ax.set_title(f"Implantation {n_cyl} cyl. – vue coupe", fontsize=13)
        self.canvas = FigureCanvasTkAgg(fig, master=self.cadre_schema)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True)

    def goto_piece(self, page):
        self.calculer()
        self.controller.afficher_page(page)
