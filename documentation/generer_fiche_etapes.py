# -*- coding: utf-8 -*-
"""Fiche de conduite A4 paysage : une ligne par etape (lancer / montrer / dire / attendu).

Sortie : Fiche_conduite_etapes.docx (+ PDF via Word, voir la commande passee a l'agent).
"""
import pathlib

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RACINE = pathlib.Path(r"C:\LaSalle\Automne2026\TechWeek_Atelier_Agent_IA")
SORTIE = RACINE / "Fiche_conduite_etapes.docx"

BLEU = RGBColor(0x0B, 0x12, 0x20)
CYAN = RGBColor(0x0E, 0x74, 0x90)
GRIS = RGBColor(0x55, 0x60, 0x70)

LIGNES = [
    ("1", "Le cerveau seul", "python etape1.py",
     "Une réponse en 3 s, en français, avec du code JSX.",
     "« Il répond en trois secondes. Il n'a lu aucun de vos documents. »",
     "Quelle est la date de l'examen du cours 420-TT4-AS ?",
     "Refus poli, trois conseils, puis du code hors sujet. Aucune source."),
    ("2", "La matière", "python etape2.py",
     "« useState » répond ; « useReducer » est refusé net.",
     "« Le prompt est de la politesse. Le code, c'est la police. »",
     "Explique useReducer.",
     "Refus immédiat, 0 appel : la garde bloque avant le modèle."),
    ("3", "Les mains", "python etape3.py",
     "La ligne [outil] lire_cours() apparaît avant la réponse.",
     "« Un agent, ce n'est pas un modèle qui sait tout : c'est un modèle qui peut demander. »",
     "Que dit le cours sur useState ?",
     "Le modèle demande, Python lit, le modèle rédige."),
    ("4", "Le visage", "python etape4.py",
     "La page s'ouvre sur 127.0.0.1:3000.",
     "« Coupez le wifi : la page marche encore. Rien ne sort de la machine. »",
     "Une question, wifi coupé.",
     "Même réponse. Aucun réseau, aucune clé."),
    ("5", "Le contrôle", "python etape5_web.py",
     "Quiz de 2 questions, score détaillé.",
     "« Qui a corrigé ? Python. Combien d'appels au modèle ? Zéro. »",
     "Répondre volontairement faux à la question 1.",
     "« 1:A=NON->B » : la bonne réponse est affichée."),
    ("6", "La bibliothèque", "python etape6_web.py",
     "Un snippet + la pastille banque_react.py:usereducer.",
     "« Demandez le code : la réponse existe avant le modèle. »",
     "donne le code usereducer",
     "Code figé + pastille. 0 appel au modèle."),
    ("7", "La mémoire documentaire", "python etape6_web_doc.py",
     "Une date juste + le nom du fichier du calendrier.",
     "« Le calendrier n'est pas dans le prompt : il est lu à la question. »",
     "Quand le cours 420-TT4-AS ?",
     "Réponse instantanée, 0 appel, pastille du calendrier."),
    ("8", "Le tri et la preuve", "python etape8.py --demo",
     "5 questions, 4 chemins, 2 appels au modèle (6 questions si le livre est indexé).",
     "« Comptez avec moi : deux appels sur cinq. Le reste, c'est du Python. »",
     "La batterie se joue seule, puis « Que dit le livre sur Redux et les reducers ? ».",
     "Batterie : Tailwind → .docx ; date → 0 ; useReducer → .docx ; code → banque ; tarte → refus.\n→ Livre : fullstack-react p.565, vérifiable dans le PDF."),
    ("9", "La mesure", "python etape9_tokens.py",
     "Trois comptes de tokens, côte à côte.",
     "« Vos notes ne rentrent pas. Ce n'est pas un bug : c'est la raison d'être du RAG. »",
     "(pas de question : on mesure)",
     "8 192 tokens ≈ 30 000 caractères ; le corpus en fait 68 000."),
    ("10", "L'ouverture", "python etape10_ressources.py",
     "La liste des livres présents + les 5 sites.",
     "« Ouvrez le livre à la page 565 : la citation est vraie. C'est ça, une preuve. »",
     "Que dit le livre sur Redux et les reducers ?",
     "fullstack-react p.565, vérifiable dans le PDF."),
]

PHRASES = [
    "Le modèle propose, Python décide.",
    "Pas de source, pas de réponse.",
    "Le prompt est de la politesse ; le code, c'est la police.",
    "Un agent sans preuve est un moteur à vraisemblance.",
    "L'enseignant garde la note, le programme et la parole.",
]


def ombre(cellule, couleur="F1F5F9"):
    tcPr = cellule._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), couleur)
    tcPr.append(shd)


def cadre(tableau):
    tbl = tableau._tbl
    bordures = OxmlElement("w:tblBorders")
    for cote in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement("w:%s" % cote)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "C7D2E0")
        bordures.append(el)
    tbl.tblPr.append(bordures)


def main():
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = Cm(29.7), Cm(21.0)
    for cote in ("top_margin", "bottom_margin"):
        setattr(section, cote, Cm(1.2))
    for cote in ("left_margin", "right_margin"):
        setattr(section, cote, Cm(1.4))

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(9)
    style.paragraph_format.space_after = Pt(2)

    titre = doc.add_paragraph()
    r = titre.add_run("Fiche de conduite — les 10 étapes")
    r.font.size = Pt(19)
    r.font.bold = True
    r.font.color.rgb = BLEU

    sous = doc.add_paragraph()
    r = sous.add_run("Atelier TechWeek · Collège LaSalle · 2 h · 127.0.0.1 uniquement · aucun PDF dans le dépôt")
    r.font.size = Pt(9.5)
    r.font.color.rgb = GRIS
    r.font.italic = True

    intro = doc.add_paragraph()
    r = intro.add_run(
        "Règle unique : une démo ratée ne se débogue pas en direct plus de 60 s. "
        "On dit « je garde ça pour la fin », on ouvre app_final.py, on continue.")
    r.font.size = Pt(9.5)

    tableau = doc.add_table(rows=1, cols=6)
    tableau.alignment = WD_TABLE_ALIGNMENT.CENTER
    cadre(tableau)
    entetes = ["#", "Étape", "Lancer (dossier mon_agent_react)", "Ce que je montre",
               "Ce que je dis", "Question posée → réaction attendue"]
    largeurs = [Cm(0.9), Cm(3.5), Cm(4.6), Cm(4.6), Cm(6.9), Cm(6.4)]
    for i, (cellule, texte_) in enumerate(zip(tableau.rows[0].cells, entetes)):
        cellule.width = largeurs[i]
        ombre(cellule, "0B1220")
        p = cellule.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(texte_)
        run.font.size = Pt(9)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for j, ligne in enumerate(LIGNES):
        # les deux derniers champs (question posee / reaction attendue) tiennent dans une seule colonne
        ligne = ligne[:5] + (ligne[5] + "\n→ " + ligne[6],)
        cellules = tableau.add_row().cells
        for i, valeur in enumerate(ligne):
            cellules[i].width = largeurs[i]
            if j % 2 == 1:
                ombre(cellules[i], "F7FAFC")
            p = cellules[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)
            run = p.add_run(valeur)
            run.font.size = Pt(8.6)
            if i == 0:
                run.font.bold = True
                run.font.color.rgb = CYAN
            if i == 2:
                run.font.name = "Consolas"
                run.font.size = Pt(8.3)

    # ---------------------------------------------------------- page 2
    doc.add_page_break()
    h = doc.add_paragraph()
    r = h.add_run("Les cinq phrases à répéter")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BLEU
    for phrase in PHRASES:
        p = doc.add_paragraph(phrase, style="List Number")
        p.runs[0].font.size = Pt(10.5)

    h = doc.add_paragraph()
    r = h.add_run("Ordre de coupe (décidé à froid)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BLEU

    t2 = doc.add_table(rows=1, cols=3)
    cadre(t2)
    for cellule, texte_ in zip(t2.rows[0].cells, ["Priorité", "Étapes", "Pourquoi"]):
        ombre(cellule, "0B1220")
        run = cellule.paragraphs[0].add_run(texte_)
        run.font.bold = True
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for prio, etapes, pourquoi in [
        ("Bloquant (35 min)", "1 · 3 · 8", "Sans elles, il n'y a pas de démonstration, seulement des fonctionnalités."),
        ("Cœur (46 min)", "2 · 4 · 6 · 7 · 10", "Ce sont les preuves que le public peut vérifier lui-même."),
        ("Variable (17 min)", "5 · 9", "Remplaçables par une phrase si le temps manque : 9 → 3 min (tokens)."),
    ]:
        cellules = t2.add_row().cells
        for i, valeur in enumerate((prio, etapes, pourquoi)):
            run = cellules[i].paragraphs[0].add_run(valeur)
            run.font.size = Pt(9)
            if i == 0:
                run.font.bold = True

    h = doc.add_paragraph()
    r = h.add_run("Si ça casse")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BLEU
    for cas, geste in [
        ("Ollama ne répond pas", "Lancer l'application Ollama, puis « ollama list ». Modèle absent : ollama pull llama3.2:latest."),
        ("Port 3000 occupé", "Fermer l'ancien python (ou redémarrer le terminal), puis relancer."),
        ("Page blanche", "Vérifier que le terminal affiche « Ouvrez http://127.0.0.1:3000 » ; utiliser 127.0.0.1, jamais localhost."),
        ("Une étape échoue", "60 s maximum. Sinon : « je garde ça pour la fin », puis app_final.py qui contient la même logique."),
        ("Question imprévue du public", "La poser à l'agent en direct : c'est le meilleur test, et le refus est une réponse."),
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(cas + " — ")
        run.font.bold = True
        run.font.size = Pt(9.5)
        run2 = p.add_run(geste)
        run2.font.size = Pt(9.5)

    h = doc.add_paragraph()
    r = h.add_run("Après les dix étapes : les versions ultimate (3 min, sans lancer)")
    r.font.size = Pt(14)
    r.font.bold = True
    r.font.color.rgb = BLEU
    doc.add_paragraph(
        "app_rag_pro.py (recherche sémantique, SentenceTransformer) → app_ia_final.py (+ OCR, voix) → "
        "app_ultimate_ia_*.py (+ mémoire, Socrate, RAG PRO, quiz) → app_ultimate_ia_production.py "
        "(+ login, logs_pedagogie.json, tableau de bord /admin, langue détectée)."
    ).runs[0].font.size = Pt(9.5)
    doc.add_paragraph(
        "Ne pas les lancer en direct : torch + sentence-transformers + easyocr ≈ 2 Go, et un premier "
        "lancement qui télécharge des modèles. Aujourd'hui easyocr n'est pas installé : le mode image est "
        "désactivé au démarrage, le reste tourne. Montrer le code et une capture de /admin."
    ).runs[0].font.size = Pt(9.5)

    doc.save(SORTIE)
    print("OK ->", SORTIE)


if __name__ == "__main__":
    main()
