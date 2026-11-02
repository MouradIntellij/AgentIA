# -*- coding: utf-8 -*-
"""Genere le conducteur Word de l'atelier TechWeek (aucun code Python dans le document).

Sortie : Conducteur_Atelier_Agent_IA_2h.docx
Usage  : python generer_conducteur.py
"""
import pathlib
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from _outils_docx import (
    nouveau_document, entete_pied, para, riche, h1, h2, h3, puces, bloc,
    encadre, tableau, fiche_etape, sommaire, saut_page, shade_cell,
    table_borders, cell_margins, ENCRE, BLEU, BLEU_CLAIR, VERT, VERT_CLAIR,
    AMBRE, AMBRE_CLAIR, ROUGE, ROUGE_CLAIR, GRIS, GRIS_CLAIR, GRIS_BORD, BLANC,
)

SORTIE = pathlib.Path(__file__).resolve().parent / "Conducteur_Atelier_Agent_IA_2h.docx"


# ================================================================== COUVERTURE
def couverture(doc):
    p = para(doc, "TECHWEEK  ·  COLLÈGE LASALLE  ·  AUTOMNE 2026", 9, True, BLEU, avant=40, apres=6)
    p = para(doc, "Conducteur d'atelier", 30, True, ENCRE, avant=0, apres=0, interligne=1.0)
    p = para(doc, "Construire un agent IA", 30, True, ENCRE, apres=0, interligne=1.0)
    p = para(doc, "pédagogique local", 30, True, BLEU, apres=10, interligne=1.0)
    p = para(doc, "10 étapes, 3 extensions, 2 heures, aucune clé API", 14, False, GRIS, apres=4)
    p = para(doc, "De la première réponse du modèle au TP qui se débloque tout seul", 11, False, GRIS,
             italique=True, apres=18)

    t = doc.add_table(rows=1, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    table_borders(t, "E2E8F0", 4)
    cell_margins(t, 140, 140, 90, 90)
    cases = [("10", "étapes numérotées,\nune commande par étape"),
             ("6", "démonstrations de contrôle\nprêtes à montrer"),
             ("0", "compte, clé API\nou port ouvert")]
    for i, (gros, petit) in enumerate(cases):
        c = t.rows[0].cells[i]
        c.width = Cm(5.4)
        shade_cell(c, GRIS_CLAIR)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(gros)
        r.font.size = Pt(26)
        r.bold = True
        r.font.color.rgb = RGBColor.from_string(BLEU)
        p2 = c.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(0)
        r = p2.add_run(petit)
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor.from_string(GRIS)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(26)

    encadre(doc, "Ce document ne contient aucun code Python",
            "Vous avez déjà la solution complète dans les fichiers etape1.py à etape10_ressources.py, "
            "app_final.py, app_tp.py et app_maths.py. Ce conducteur donne autre chose : le sens de chaque "
            "étape, la commande exacte, le résultat attendu, le lien avec la suite, et la réponse à "
            "l'objection « on devrait pouvoir poser n'importe quelle question ». L'étape 8, qui manquait, "
            "est fournie à part dans etape8.py.", VERT, VERT_CLAIR, 10)

    p = para(doc, "Version du 1er novembre 2026  ·  à utiliser pendant la séance, pas à lire avant",
             8.5, False, GRIS, italique=True, avant=6)


# ================================================================== MODE D'EMPLOI
def mode_emploi(doc):
    h1(doc, None, "Mode d'emploi", "Trois lectures possibles du même document")

    para(doc, "Ce conducteur est un outil de pilotage. Il ne remplace pas les fichiers de l'atelier : "
              "il dit quoi faire, dans quel ordre, ce qu'on doit voir, et pourquoi c'est là.")

    tableau(doc,
            ["Moment", "Ce que vous lisez", "Ce que vous faites"],
            [["**J-7**", "Sections « Le pitch et l'exploit », « La carte du parcours », « Avant de commencer », annexe D", "Installer, tester le hors-ligne, préparer la clé USB."],
             ["**Pendant**", "Section « Les dix étapes » et « Le conducteur 2 h »", "Vous suivez la colonne « commande », vous montrez la colonne « attendu »."],
             ["**Après**", "Sections « On devrait pouvoir poser n'importe quelle question », « Les démonstrations de contrôle », « Dépannage express »", "Vous répondez aux objections, vous rejouez les démonstrations, vous dépannez."]],
            [2.4, 6.2, 8.0])

    h2(doc, "Les cinq rubriques, toujours dans le même ordre")
    puces(doc, [
        ("COMMANDE", "ce que vous tapez, tel quel, dans le dossier mon_agent_react."),
        ("RÉSULTAT ATTENDU", "ce que la console ou le navigateur doit afficher. Si ce n'est pas ça, allez à la section « Dépannage »."),
        ("POURQUOI", "l'utilité réelle de l'étape pour l'agent. C'est ce que vous dites à voix haute."),
        ("LIEN", "ce que l'étape suivante ajoute, et ce qui casserait sans celle-ci."),
        ("PIÈGE / CONTRÔLE", "l'erreur classique, et la question à poser aux étudiants pour vérifier qu'ils ont compris."),
    ])

    encadre(doc, "La seule phrase à retenir",
            "Prompt = politesse, Code = police. Le modèle propose des mots ; Python décide de ce qui est vrai, "
            "note, daté, corrigé ou débloqué. Tout le reste du document découle de cette phrase.", AMBRE, AMBRE_CLAIR, 10.5)

    h2(doc, "Ce dont vous avez besoin")
    tableau(doc,
            ["Élément", "Version / taille", "Rôle", "Où"],
            [["Python", "3.10 ou plus", "Exécute l'agent, le serveur, les outils", "python.org (cocher Add to PATH)"],
             ["Ollama", "application de bureau", "Fait tourner le modèle en local", "ollama.com/download"],
             ["llama3.2", "2 Go, version latest", "Le modèle de langage de tout l'atelier", "ollama pull llama3.2:latest"],
             ["mon_agent_react", "le dossier de l'atelier", "Contient les scripts, cours/, Tps/, static/", "votre clé USB ou le dépôt"],
             ["Bibliothèques", "requests, pypdf, transformers", "Réseau local, lecture PDF, tokens", "installer.bat"]],
            [2.8, 4.0, 5.4, 4.4])

    h2(doc, "Trois conventions de ce document")
    puces(doc, [
        "Toutes les adresses sont en 127.0.0.1, jamais localhost : c'est la même machine, sans détour DNS.",
        "Les commandes se tapent dans le dossier mon_agent_react. Si vous êtes ailleurs, faites d'abord cd mon_agent_react.",
        "Les blocs « résultat attendu » sont des extraits réels, pas des illustrations. Les accents peuvent s'afficher bizarrement dans PowerShell : les fichiers, eux, sont corrects.",
    ])


# ================================================================== CHAPITRE 1
def chapitre_pitch(doc):
    h1(doc, None, "Le pitch et l'exploit", "Ce qu'on construit, ce que ce n'est pas, et pourquoi c'est difficile")

    h2(doc, "En soixante secondes")
    para(doc, "Nous allons construire, sur un ordinateur portable et sans internet, un agent qui répond "
              "aux questions d'un cours React, explique le code des étudiants, corrige leurs erreurs, "
              "fait passer un quiz, et les guide dans un TP sans jamais leur donner la solution.")
    para(doc, "Il ne prononce pas une seule réponse qui ne vienne d'un document que nous lui avons fourni. "
              "À chaque réponse, il affiche le fichier qui l'a nourri. Quand la réponse n'est pas dans "
              "le cours, il refuse — et ce refus est instantané, gratuit, et vérifiable.")
    riche(doc, [("Ce n'est pas ", {"taille": 10.5}),
                ("un chatbot de plus", {"bold": True, "taille": 10.5}),
                (". C'est un agent documentaire : un modèle de langage qui ne peut parler que de ce qu'on lui a donné à lire.",
                 {"taille": 10.5})])

    h2(doc, "L'exploit, en une image : trois verrous et un rédacteur")
    tableau(doc,
            ["Pièce", "Qui la tient", "Ce qu'elle empêche"],
            [["**La garde**", "Python, avant le modèle", "Répondre à une question absente du cours (0 appel, 0 invention)."],
             ["**Le tri (RAG)**", "Python, entre les documents et le modèle", "Envoyer tout le cours — ou tout un livre — au modèle et noyer la vraie réponse."],
             ["**Les pastilles de source**", "Python, après la lecture", "Dire « selon le cours » sans fichier derrière."],
             ["**La rédaction**", "Le modèle", "Rien : il reformule ce que Python lui a apporté. C'est le seul rôle qui reste."]],
            [3.6, 5.4, 7.6])

    para(doc, "L'exploit n'est donc pas que le modèle parle. Un modèle parle déjà, tout seul, et il invente. "
              "L'exploit est qu'il parle ", apres=5)
    p = doc.paragraphs[-1]
    r = p.add_run("sans pouvoir mentir sur ce qui compte")
    r.bold = True
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor.from_string(ROUGE)
    r = p.add_run(" : une date, une note, un extrait de code, une étape de TP.")
    r.font.size = Pt(10.5)

    h2(doc, "Ce que l'agent sait faire, et ce qu'il ne sait pas")
    tableau(doc,
            ["Capacité", "Comment", "Preuve montrable"],
            [["Répondre sur le cours", "Lit les DOCX/PDF de cours/, trie les passages utiles, rédige", "Pastille avec le nom du fichier"],
             ["Donner une date, un horaire, un prof", "Expression régulière sur le calendrier, zéro modèle", "Ligne « Enseignant : … » + source"],
             ["Donner un snippet React", "Banque de 22 codes validés par le professeur", "Pastille banque_react.py:clé"],
             ["Corriger du code", "Analyse du code, motifs React, exécution en bac à sable, puis explication", "Liste de faits + « EXPLICATION IA »"],
             ["Noter un quiz", "Questions et réponses dans Python", "Score 1/2 avec le détail"],
             ["Guider un TP", "Plan extrait du PDF, vérificateur de code, seuil 0,6", "Étape débloquée, ligne dans progres.csv"],
             ["Répondre à tout", "—", "Il refuse : c'est le contrat, pas une panne"]],
            [4.6, 7.2, 4.8])


# ================================================================== CHAPITRE 2
def chapitre_carte(doc):
    h1(doc, None, "La carte du parcours", "Ce que chaque étape ajoute, et ce qui casserait sans elle")

    para(doc, "Lisez ce tableau de gauche à droite : chaque ligne transforme l'agent construit à la ligne "
              "précédente. La colonne « ce que ça change pour l'utilisateur » est celle que vous commentez "
              "à voix haute ; la colonne « commande » est celle que les étudiants tapent.")

    tableau(doc,
            ["#", "Étape", "Fichier", "Ce que ça ajoute", "Ce que ça change pour l'utilisateur", "Min"],
            [["1", "Le cerveau", "etape1.py", "Un modèle local qui parle", "Il répond, mais invente", "8"],
             ["2", "La matière", "etape2.py", "cours/react.txt + garde", "Il répond juste ou refuse", "10"],
             ["3", "Les mains", "etape3.py", "Outil lire_cours, boucle ReAct", "Il lit le cours au lieu de s'en souvenir", "12"],
             ["4", "Le visage", "etape4.py", "Serveur web local", "On le montre dans un navigateur", "8"],
             ["5", "Le contrôle", "etape5_web.py", "Quiz corrigé par Python", "Il peut interroger sans inventer", "10"],
             ["6", "La bibliothèque de code", "etape6_web.py", "22 snippets + correcteur", "Il donne du code validé et explique les fautes", "12"],
             ["7", "La mémoire documentaire", "etape6_web_doc.py", "Lecture DOCX/PDF réelle", "Il lit vos vrais documents", "10"],
             ["8", "Le tri et la preuve", "etape8.py", "Routage Python + RAG + pastilles", "Il montre pourquoi il répond", "15"],
             ["9", "La mesure", "etape9_tokens.py, etape9c_eval.py", "Tokens et évaluation verrouillée", "On comprend ses limites, on mesure", "7"],
             ["10", "L'ouverture", "etape10_ressources.py", "Livre entier indexé + sites + cache", "Il cite une page de livre et la doc officielle", "6"]],
            [0.8, 3.5, 4.2, 4.2, 5.4, 1.0], taille=8.3)

    h2(doc, "La règle des trois couches")
    tableau(doc,
            ["Couche", "Rôle", "Exemples dans l'atelier", "Si elle disparaît"],
            [["**Le modèle**", "Mettre en mots", "llama3.2, reformulation, explication, indices", "Plus de langage naturel : l'agent redevient un script"],
             ["**Python**", "Décider et vérifier", "garde, tri, calendrier, quiz, AST, seuil de déblocage", "Le modèle invente, et rien n'est vérifiable"],
             ["**Les documents**", "Dire la vérité", "cours/, Tps/, banque_react.py, cache web", "Le modèle parle de mémoire : plus de preuve"]],
            [3.0, 3.6, 6.4, 3.6])

    para(doc, "Les étapes 1 à 4 installent les couches une par une. Les étapes 5 à 7 branchent les "
              "documents. L'étape 8 les fait travailler ensemble. Les étapes 9 et 10 mesurent et élargissent, "
              "sans jamais retirer un verrou.")

    h2(doc, "Le chemin complet, en une ligne")
    bloc(doc, "De la question à la preuve",
         "question → Python choisit le chemin → (banque | calendrier | garde | RAG)\n"
         "         → si RAG : notes de cours/ + index du livre → tri des passages → modèle rédige\n"
         "         → Python extrait les sources (fichier, page) → réponse + preuve",
         BLEU, BLEU_CLAIR, 9)

    encadre(doc, "Le point de bascule",
            "Tant que l'agent ne fait que répondre, c'est une démonstration. À partir de l'étape 5, il "
            "corrige ; à partir de l'étape 8, il prouve ; à partir de l'extension 11, il refuse de faire "
            "le TP à la place de l'étudiant. C'est là qu'il devient pédagogique.", VERT, VERT_CLAIR, 10)

    h2(doc, "Trois durées possibles")
    tableau(doc,
            ["Format", "Étapes gardées", "Ce qu'on sacrifie", "Public"],
            [["**90 minutes**", "1, 2, 3, 8 + les démonstrations de la section « Les démonstrations de contrôle »", "5, 6, 9, 10 et extensions", "Découverte, enseignants pressés"],
             ["**2 heures (défaut)**", "Les 10 étapes, 8 en démonstration guidée", "Le TP complet (extension 11 montrée)", "Étudiants et enseignants"],
             ["**3 heures**", "Les 10 étapes + app_tp.py en autonomie", "Rien", "Atelier pratique avec TP"]],
            [3.0, 6.0, 5.0, 4.6])

    h2(doc, "Pourquoi 10 étapes, et pas un seul fichier")
    para(doc, "Parce que chaque étape ajoute une pièce qu'on peut montrer seule. Si vous donnez app_final.py "
              "d'emblée, les étudiants voient une application qui marche ; ils ne voient pas pourquoi elle "
              "marche. Les dix étapes rendent chaque décision visible : le modèle seul, la matière, les mains, "
              "le visage, le contrôle, la bibliothèque, le tri, la mesure, l'ouverture.")

    encadre(doc, "À dire à la fin, mot pour mot",
            "1. Le modèle ne lit pas vos documents : Python lit, trie et lui apporte les passages.\n"
            "2. Le modèle propose, Python décide : notes, horaires et code viennent de fichiers.\n"
            "3. Un agent qui répond à tout sans source est un moteur à vraisemblance, pas un agent de cours.",
            VERT, VERT_CLAIR, 10.5)


# ================================================================== CHAPITRE 3
def chapitre_avant(doc):
    h1(doc, None, "Avant de commencer", "Trente minutes de préparation qui sauvent les deux heures")

    h2(doc, "L'installation, une seule fois, avec du wifi")
    bloc(doc, "Dans le dossier mon_agent_react",
         "cd mon_agent_react\n"
         "installer.bat\n"
         "ollama list\n"
         "python -c \"import requests, pypdf, transformers; print('libs OK')\"",
         ENCRE, GRIS_CLAIR, 9)
    bloc(doc, "Résultat attendu",
         "NAME                  ID              SIZE      MODIFIED\n"
         "llama3.2:latest       a80c4f17acd5    2.0 GB    ...\n"
         "\n"
         "libs OK",
         VERT, VERT_CLAIR, 8.8)
    para(doc, "installer.bat vérifie Python, installe les trois bibliothèques et télécharge le modèle. "
              "Il ne s'installe qu'une fois. Le jour de l'atelier, il n'y a plus rien à télécharger : "
              "c'est tout l'intérêt du local.")

    h2(doc, "Les quatre vérifications du jour J")
    tableau(doc,
            ["Vérification", "Comment", "Attendu"],
            [["Le moteur tourne", "ollama list", "llama3.2:latest apparaît"],
             ["Les bibliothèques sont là", "python -c \"import requests, pypdf, transformers; print('libs OK')\"", "libs OK"],
             ["L'interface est hors-ligne", "Couper le wifi, lancer python app_final.py", "La page reste stylée (CSS local)"],
             ["Aucun serveur fantôme", "Gestionnaire des tâches, ou taskkill /F /IM python.exe", "Aucun python.exe ne traîne"]],
            [4.2, 7.4, 5.0])

    h2(doc, "Les trois dossiers qui comptent")
    tableau(doc,
            ["Dossier", "Ce qu'on y met", "Qui le lit"],
            [["cours/", "react.txt, vos DOCX, vos PDF, livres/ et cache_web/", "lire_cours() dans les étapes 2 à 8"],
             ["Tps/", "le PDF du TP, plan_tp.json, fiche_A.json, progres.csv", "app_tp.py (extension 11)"],
             ["static/", "app.css (9 Ko) et mathjax-tex-svg.js (2 Mo)", "les trois applications web, sans CDN"]],
            [3.2, 8.2, 5.2])

    h2(doc, "Les cinq choses qu'on ne fait jamais")
    puces(doc, [
        ("Relancer ollama serve", "s'il tourne déjà : l'erreur « bind » est normale, le service est déjà là."),
        ("Écouter sur 0.0.0.0", "les applications restent en 127.0.0.1. Pour montrer à distance, on utilise un tunnel sortant."),
        ("Utiliser localhost", "dans les scripts et les démonstrations : 127.0.0.1 évite les détours IPv6 et proxy."),
        ("Déposer un PDF pirate", "cours/livres/ accueille votre PDF légal ou un extrait libre de droits, rien d'autre."),
        ("Compresser .venv", "817 Mo : utilisez les archives déjà préparées, ou robocopy sans .venv."),
    ])

    h2(doc, "Le test de cinq minutes, avant les étudiants")
    para(doc, "Lancez l'agent complet, posez les quatre questions de la section « Les démonstrations de "
              "contrôle », vérifiez que les pastilles s'affichent. Si les quatre passent, l'atelier peut "
              "commencer. Si une seule échoue, vous savez exactement où chercher : section « Dépannage ».")
    bloc(doc, "Le test express",
         "python app_final.py\n"
         "-> ouvrir http://127.0.0.1:3000\n"
         "-> « Que dit la matiere sur Tailwind ? »      (attend : une reponse + pastille .docx)\n"
         "-> « Quand le cours 420-TT4-AS ? »           (attend : lundi 08h-12h, Mourad Sehboub)\n"
         "-> « donne le code usereducer »              (attend : snippet de la banque)\n"
         "-> « Explique useReducer ? »                 (attend : une reponse + pastille .docx)",
         BLEU, BLEU_CLAIR, 8.8)

    h2(doc, "Le plan B, dès maintenant")
    encadre(doc, "Si une étape casse pendant la séance",
            "Ne réparez pas devant le groupe. Basculez sur app_final.py (l'agent complet, BUILD v10) et "
            "rejouez les démonstrations de la section « Les démonstrations de contrôle ». L'atelier survit "
            "à une étape ratée ; il ne survit pas à dix minutes de débogage silencieux.", ROUGE, ROUGE_CLAIR, 10)

    h2(doc, "Si le test express échoue, où aller")
    tableau(doc,
            ["Ce que vous voyez", "Cause probable", "Où regarder"],
            [["Le moteur ne répond pas", "Ollama est arrêté ou occupé", "Dépannage : « Connection refused »"],
             ["Aucune pastille sous la réponse", "Le fichier n'est pas reconnu comme une source", "Vérifier son nom et son extension dans cours/"],
             ["Le calendrier donne une autre date", "Le PDF ou le DOCX du calendrier manque", "Le remettre dans cours/, relancer"],
             ["Le snippet n'apparaît pas", "La clé n'existe pas dans banque_react.py", "Poser la question « donne le code … » avec le bon nom"]],
            [6.0, 5.6, 5.0], taille=8.6)


# ================================================================== GABARIT D'ÉTAPE
def etape(doc, numero, titre, sous_titre, fichier, duree, mode, sortie,
          but, faits, commande, attendu, pourquoi, apporte, suivante,
          piege, controle, plan_b=None, couleur_attendu=VERT):
    h1(doc, None, f"Étape {numero} · {titre}", sous_titre, nouvelle_page=False)
    fiche_etape(doc, fichier, duree, mode, sortie)

    para(doc, but, 10.5, apres=7)

    h3(doc, "Ce que vous faites")
    puces(doc, faits)

    bloc(doc, "Commande", commande, ENCRE, GRIS_CLAIR, 9)
    bloc(doc, "Résultat attendu", attendu, couleur_attendu,
         VERT_CLAIR if couleur_attendu == VERT else GRIS_CLAIR, 8.6)

    encadre(doc, "Pourquoi cette étape compte", pourquoi, BLEU, BLEU_CLAIR, 10)

    h3(doc, "Le lien avec les autres étapes")
    riche(doc, [("Ce que cette étape rend possible : ", {"bold": True, "color": BLEU}), (apporte, {})], 10, apres=3)
    riche(doc, [("Ce que la suivante ajoute : ", {"bold": True, "color": VERT}), (suivante, {})], 10, apres=7)

    encadre(doc, "Piège", piege, AMBRE, AMBRE_CLAIR, 9.8)
    encadre(doc, "Question de contrôle", controle, VERT, VERT_CLAIR, 9.8)
    if plan_b:
        riche(doc, [("Si ça rate : ", {"bold": True, "color": ROUGE}), (plan_b, {"italic": True})], 9.2, apres=4)


# ================================================================== ÉTAPES 1-5
def etapes_1_5(doc):
    h1(doc, None, "Les dix étapes", "Une commande, un résultat attendu, une raison d'être")

    para(doc, "Chaque étape suit le même gabarit. Les étudiants tapent la commande ; vous lisez à voix "
              "haute l'encadré « pourquoi » et la question de contrôle. Si le résultat attendu n'apparaît "
              "pas, ne corrigez pas le code : passez au plan B en bas de l'étape, puis à la section "
              "« Dépannage ».")

    # ---------------------------------------------------------------- 1
    etape(doc, 1, "Le cerveau seul", "Un modèle local qui parle — et qui invente",
          "etape1.py", "8 min", "Console", "Réponse en 2 à 8 s",
          "Entendre le moteur. Un modèle de langage tourne sur le portable, sans internet. C'est la voix "
          "de l'agent. C'est aussi la démonstration de ce qu'il ne faut pas faire : répondre de mémoire.",
          ["Se placer dans mon_agent_react.",
           "Poser une question facile : « Explique useState ».",
           "Poser deux questions pièges : l'horaire du cours 420-TT4-AS, puis le nom de l'enseignant.",
           "Noter les réponses au tableau : elles sont fluides, plausibles, et fausses."],
          "python etape1.py",
          "Question React [defaut: Explique useState avec exemple simple] : Explique useState\n"
          "\n"
          "--- reponse ---\n"
          "\n"
          "useState est un hook React qui permet de garder un etat...\n"
          "(sortie variable, 2 a 8 s)\n"
          "\n"
          "Question React [defaut: Explique useState avec exemple simple] : Quand a lieu le cours 420-TT4-AS ?\n"
          "\n"
          "--- reponse ---\n"
          "\n"
          "Le cours a lieu le mardi de 13 h a 16 h avec M. Dupont.\n"
          "(plausible — et faux : ce n'est pas votre calendrier)",
          "C'est la couche « modèle » : sans elle, pas de reformulation, pas d'explication, pas d'indice. "
          "Mais seule, elle répond avec sa mémoire statistique. Elle ne sait pas ce qu'elle ne sait pas, "
          "et elle ne dit jamais « je n'ai pas cette information ». C'est exactement le problème que "
          "les neuf étapes suivantes vont encadrer.",
          "Un agent qui parle et qu'on peut montrer en dix secondes.",
          "La matière : le modèle perd sa mémoire et gagne un classeur de 515 caractères.",
          "Confondre fluidité et vérité. La réponse la plus convaincante de la séance est souvent la plus fausse. "
          "Le modèle ne signale pas son incertitude : c'est à Python de le faire.",
          "« D'où vient l'horaire qu'il vient de donner ? » Réponse attendue : de nulle part. Aucun fichier n'a été lu.",
          "Ollama ne répond pas → lancer Ollama, puis vérifier avec ollama list. Modèle absent → ollama pull llama3.2:latest.")

    # ---------------------------------------------------------------- 2
    etape(doc, 2, "La matière", "Un classeur fini, et un portier qui refuse le reste",
          "etape2.py", "10 min", "Console", "Réponse juste ou refus",
          "Remplacer la mémoire par un document. Le cours React tient dans 515 caractères ; le modèle ne "
          "répond plus que là-dessus. Une garde Python refuse les questions dont aucun mot n'apparaît dans "
          "le cours, sans même appeler le modèle.",
          ["Ouvrir cours/react.txt et montrer les quatre notions : useState, useEffect, Props, Composant.",
           "Lancer le script, poser « Explique useState » : la réponse est juste.",
           "Poser « Explique useReducer » : le refus est immédiat, sans appel au modèle.",
           "Faire remarquer le compteur : « Cours charge : 515 caracteres »."],
          "python etape2.py",
          "Cours charge : 515 caracteres depuis cours\\react.txt\n"
          "\n"
          "Question React (vide=quitter) : Explique useState\n"
          "\n"
          "--- reponse ---\n"
          "\n"
          "useState garde une valeur qui fait re-afficher le composant...\n"
          "\n"
          "Question React (vide=quitter) : Explique useReducer\n"
          "\n"
          "--- reponse ---\n"
          "\n"
          "Hors-matiere - voir manuel. (bloque par garde Python, 0 appel LLM)",
          "La matière devient finie, donc vérifiable. Le refus est une fonctionnalité : zéro appel, zéro "
          "coût, zéro invention, réponse instantanée. C'est la première fois de la séance qu'un étudiant "
          "voit un agent qui admet ne pas savoir — et c'est cela qui rend l'agent crédible.",
          "La règle « la réponse doit venir du cours » et le premier verrou.",
          "Les mains : le classeur devient un outil que le modèle peut demander, au lieu d'être collé dans son prompt.",
          "La garde est un filtre grossier : un seul mot présent par hasard suffit à laisser passer une question. "
          "Elle complète le tri des passages, elle ne le remplace pas. Ne lui demandez pas d'être intelligente ; "
          "demandez-lui d'être prévisible.",
          "« Pourquoi refuse-t-il useReducer alors que llama3.2 sait très bien l'expliquer ? » Réponse attendue : "
          "parce que ce chapitre n'est pas dans le cours, et qu'on préfère un refus à une réponse invérifiable.",
          "La garde refuse une question légitime ? Ajoutez le document ou le chapitre, pas une exception dans le code.")

    # ---------------------------------------------------------------- 3
    etape(doc, 3, "Les mains", "Le modèle ne lit pas le disque : il demande, Python exécute",
          "etape3.py", "12 min", "Console", "Ligne [outil] + réponse",
          "Séparer celui qui parle de celui qui lit. Le modèle émet une demande d'outil ; Python ouvre le "
          "fichier et renvoie le texte ; le modèle rédige à partir de ce texte. C'est la boucle ReAct, en "
          "cinq tours maximum.",
          ["Lancer le script et poser « Que dit le cours sur Props ? ».",
           "Faire observer la ligne [outil] lire_cours() : c'est Python qui a lu.",
           "Expliquer les trois temps : le modèle demande, Python exécute, le modèle rédige.",
           "Montrer le plafond de cinq tours : un agent doit pouvoir s'arrêter."],
          "python etape3.py",
          "Question React (vide=quitter) : Que dit le cours sur Props ?\n"
          "\n"
          "--- agent ---\n"
          "\n"
          "[outil] lire_cours()\n"
          "Props : donnees du parent vers enfant. Ex: <Bouton titre=\"Valider\" />.",
          "C'est la séparation des pouvoirs. Le modèle ne peut lire que ce que Python accepte de lui donner : "
          "on peut journaliser, limiter, remplacer l'outil, ou couper l'accès. Sans cette boucle, aucune "
          "pastille de source n'est possible : on ne peut pas prouver ce qu'on n'a pas tracé.",
          "Un agent auditable : chaque lecture passe par une fonction que vous contrôlez.",
          "Le visage : la même boucle, mais derrière un navigateur.",
          "llama3.2 écrit parfois l'appel d'outil en texte au lieu de tool_calls ; d'où le parse_secours. "
          "Autre erreur classique : renvoyer le résultat sans role=tool ni le même identifiant, ce qui fait boucler le modèle.",
          "« Qui a ouvert cours/react.txt ? » Réponse attendue : Python, pas le modèle. « Le modèle a-t-il vu tout "
          "le fichier ? » Non : seulement les 4 000 premiers caractères, et bientôt seulement les passages utiles.",
          "Si le modèle n'appelle jamais l'outil, vérifier que le champ tools est bien envoyé et que la température est à 0.")

    # ---------------------------------------------------------------- 4
    etape(doc, 4, "Le visage", "Un navigateur, zéro installation côté étudiant",
          "etape4.py", "8 min", "Navigateur", "Page servie en local",
          "Sortir de la console. Python sert une page HTML sur 127.0.0.1:3000 ; l'étudiant tape sa question "
          "dans un champ et lit la réponse. Rien à installer sur les postes : un navigateur suffit.",
          ["Lancer le script.", "Ouvrir http://127.0.0.1:3000 dans le navigateur.",
           "Poser une question sur Props et vérifier que la réponse s'affiche dans la page.",
           "Faire remarquer l'adresse : 127.0.0.1, donc uniquement cette machine."],
          "python etape4.py",
          "Ouvrez http://127.0.0.1:3000\n"
          "\n"
          "(page : « Agent React - TechWeek (local) », un champ, un bouton OK,\n"
          " puis la reponse dans un cadre gris)",
          "Une démonstration qu'on peut projeter, et une frontière de sécurité : le serveur écoute sur "
          "127.0.0.1, pas sur le réseau. On n'ouvre pas de port sur le routeur. Pour montrer à distance, "
          "on utilisera un tunnel sortant (extension 12), jamais une redirection de port.",
          "Le support de toutes les démonstrations suivantes : boutons, modes, pastilles.",
          "Le contrôle : des boutons qui déclenchent du code Python, pas des réponses du modèle.",
          "localhost n'est pas toujours 127.0.0.1 (IPv6, proxy d'entreprise). Un ancien python.exe peut garder "
          "le port 3000 : tuez-le avant de relancer. Et ne mettez jamais 0.0.0.0 « pour tester ».",
          "« Pourquoi un autre étudiant ne voit-il pas cette page ? » Réponse attendue : le serveur n'écoute "
          "que sur la boucle locale de cette machine.",
          "Port occupé → taskkill /F /IM python.exe, puis relancer. Page blanche → vérifier l'adresse exacte et le BUILD affiché en console.")

    # ---------------------------------------------------------------- 5
    etape(doc, 5, "Le contrôle", "Le premier geste que le modèle ne fait pas : noter",
          "etape5_web.py", "10 min", "Navigateur", "Score détaillé",
          "Ajouter un quiz dont les questions, les choix et la bonne réponse vivent dans Python. Le modèle "
          "n'écrit rien, ne corrige rien : il n'a même pas la clé. L'agent devient un outil de classe, pas "
          "un générateur de QCM.",
          ["Cliquer sur « Lancer Quiz » : deux questions tirées parmi quatre.",
           "Répondre volontairement faux à une question, puis cliquer sur « Corriger ».",
           "Lire le score détaillé : 1:B=OK 2:A=NON->B.",
           "Relancer le quiz : le tirage change, la correction reste exacte."],
          "python etape5_web.py",
          "Ouvrez http://127.0.0.1:3000\n"
          "\n"
          "(page : « Agent React - Etape 5 Web (local) », boutons Cours et Lancer Quiz)\n"
          "\n"
          "[outil] verifier_reponse() [Python]\n"
          "Score 1/2 - 1:B=OK 2:A=NON->B",
          "La note ne peut pas être inventée : elle est calculée par du code, deux fois de suite, avec le "
          "même résultat. Le modèle n'a aucun rôle. C'est reproductible, gratuit, instantané, et surtout "
          "explicable à un étudiant qui conteste sa note : on lui montre la ligne qui a produit le score.",
          "Le schéma « bouton → Python → réponse » que tout le reste réutilise.",
          "La bibliothèque de code : un autre bouton, un autre outil Python, la même logique.",
          "L'état du quiz vit en mémoire : deux onglets se marchent dessus. En classe, un binôme par navigateur, "
          "ou un Reset entre deux passages. Le quiz n'est pas une évaluation notée à distance.",
          "« Qui a corrigé ? » Réponse attendue : Python. « L'IA peut-elle donner la réponse si on la lui demande ? » "
          "Non : elle ne la possède pas.",
          "Si le score ne s'affiche pas, vérifier que le bouton Corriger est bien envoyé après le quiz, et qu'aucun pare-feu local ne bloque le POST.")

    # ---------------------------------------------------------------- 6
    etape(doc, 6, "La bibliothèque de code", "Le code vient du professeur, l'explication vient du modèle",
          "etape6_web.py", "12 min", "Navigateur", "Snippet + correction",
          "Deux régimes qui ne se mélangent jamais. Quand on demande du code, il sort d'une banque de "
          "22 snippets validés par le professeur. Quand on colle du code fautif, Python relève les faits "
          "(motifs React, analyse du code, exécution en bac à sable) et le modèle se contente de les expliquer.",
          ["Cliquer sur un bouton de snippet, ou taper « donne le code usereducer ».",
           "Coller un composant fautif : function carte(){ count=count+1; ... }.",
           "Lire d'abord la liste CORRECTION PYTHON, puis seulement EXPLICATION IA.",
           "Faire ajouter un snippet par un étudiant : une entrée dans la banque, et il est disponible."],
          "python etape6_web.py",
          "[outil] banque_exemples() -> useReducer (etats complexes)\n"
          "import { useReducer } from 'react';\n"
          "...\n"
          "\n"
          "[outil] corriger_code() [Python] + [IA explique]\n"
          "CORRECTION PYTHON (regles du cours) :\n"
          "- Ligne count= : interdit par le cours. Utilisez setCount(count+1).\n"
          "- Composant en minuscule : mettez majuscule ex: function Carte().\n"
          "- Erreur syntaxe ligne 1 : invalid syntax\n"
          "\n"
          "EXPLICATION IA (verrouillee sur faits) :\n"
          "Ta fonction doit s'appeler Carte et modifier l'etat avec setCount...",
          "Un snippet inventé compile parfois, mais il n'est pas dans votre progression : la banque garantit "
          "le niveau, le style et les notions déjà vues. Le correcteur, lui, ne demande pas au modèle de "
          "trouver les fautes : il les trouve, puis lui demande de les expliquer. C'est la première "
          "application complète de « Prompt = politesse, Code = police ».",
          "Une bibliothèque de code fiable et une correction qui ne dépend pas de l'humeur du modèle.",
          "La mémoire documentaire : les documents du cours remplacent le fichier texte écrit à la main.",
          "Python ne comprend pas le JSX : l'erreur « invalid syntax » sur un composant est attendue, elle "
          "signifie « ce n'est pas du Python », pas « votre React est faux ». Les vraies erreurs React sont "
          "les motifs (minuscule, count=). Ajouter un snippet mal nommé le rend introuvable.",
          "« Qui a écrit le code affiché ? » Réponse attendue : le professeur, dans banque_react.py. "
          "« Qui l'a expliqué ? » Le modèle, à partir des faits Python.",
          "Si le snippet n'apparaît pas, vérifier la clé dans banque_react.py et la question exacte (« donne le code … »).")

    # ---------------------------------------------------------------- 7
    etape(doc, 7, "La mémoire documentaire", "Vos vrais documents remplacent le fichier texte",
          "etape6_web_doc.py", "10 min", "Navigateur", "Réponse + nom du fichier",
          "Passer du .txt écrit à la main aux documents réels : le plan de cours, le calendrier, le guide "
          "React, les tendances technologiques. C'est le moment où l'agent devient le vôtre. Le RAG naît ici, "
          "par nécessité : quatre documents font près de 20 000 caractères, trop pour être envoyés à chaque "
          "question — et un livre entier ne rentre pas du tout.",
          ["Déposer un DOCX ou un PDF dans cours/ (le calendrier y est déjà).",
           "Relancer le script et poser une question sur un passage précis du document.",
           "Vérifier que la réponse cite le nom du fichier entre crochets.",
           "Déposer un PDF scanné : l'agent l'ignore et le dit, au lieu d'inventer."],
          "python etape6_web_doc.py",
          "BUILD porte3-calendrier v2 - Ouvrez http://127.0.0.1:3000\n"
          "\n"
          "(page : Agents React, champ de question, boutons Quiz et Corriger)\n"
          "\n"
          "[outil] lire_cours() [calendrier Python, 0 LLM]\n"
          "D'apres le calendrier :\n"
          "Cours : 420-TT4-AS\n"
          "Enseignant : Mourad Sehboub\n"
          "Horaires : Lundi 08h-12h (À distance)",
          "C'est le passage à l'échelle : l'agent lit des dizaines de pages sans qu'on réécrive son prompt. "
          "Il lit aussi les PDF, ce qui permet d'utiliser le calendrier officiel et le TP. Et il sait dire "
          "« ce PDF est une image, je ne peux pas le lire » : une limite avouée vaut mieux qu'une réponse inventée.",
          "Un agent qui parle de votre cours, avec vos mots et vos dates.",
          "Le tri et la preuve : parmi 20 000 caractères — et bientôt des centaines de pages — quels passages "
          "envoyer, et comment le prouver.",
          "Un PDF scanné est une image : sans OCR, il ne contient pas de texte. Un .doc renommé en .docx ne "
          "s'ouvre pas. Les notes de cours sont plafonnées : au-delà de 20 000 caractères, un PDF est indexé "
          "page par page au lieu d'être copié en entier (c'est l'objet de l'étape 8).",
          "« D'où vient la réponse ? » Réponse attendue : du fichier cité, pas de la mémoire du modèle.",
          "Si un document n'apparaît jamais, vérifier son extension réelle et sa taille ; réduire le corpus à l'essentiel.")

    # ---------------------------------------------------------------- 8
    etape(doc, 8, "Le tri et la preuve", "Python choisit le chemin, le modèle rédige, la source s'affiche",
          "etape8.py", "15 min", "Console", "5 questions, 4 chemins, 2 appels LLM",
          "Assembler les pièces. Avant d'appeler le modèle, Python classe la question : demande de code, "
          "date, hors-sujet, ou question documentaire. Puis il ne lui donne que les passages utiles. Enfin, "
          "il extrait les sources du texte qu'il a réellement envoyé — ce ne sont pas des remerciements, "
          "ce sont des preuves. Et si un livre volumineux est présent, Python l'a indexé page par page : "
          "la réponse peut citer « p.42 », pas seulement « le livre ».",
          ["Lancer la démonstration : cinq questions, quatre chemins différents (six questions et un "
           "chemin de plus si un livre est indexé).",
           "Compter les appels au modèle : deux sur cinq.",
           "Montrer les pastilles de source, et le mode dégradé quand Ollama est absent.",
           "Relancer en interactif et laisser un étudiant poser sa question."],
          "python etape8.py --demo\n"
          "python etape8.py",
          "etape8 v2 - hybride + RAG + livre indexe + preuves\n"
          "Matiere chargee : 19824 caracteres depuis cours/  |  Ollama : OK\n"
          "\n"
          "QUESTION : Que dit la matiere sur Tailwind ?\n"
          "[outil] lire_cours() / tri Python | chemin : RAG (Python trie, LLM redige) | 1 appel(s) LLM\n"
          "Selon le guide, Tailwind CSS propose des classes utilitaires...\n"
          "Sources consultees (preuve Python) : [Guide_complet_React_TypeScript_Tailwind.docx]\n"
          "\n"
          "QUESTION : Quand le cours 420-TT4-AS ?\n"
          "[outil] lire_cours() / tri Python | chemin : CALENDRIER (Python seul) | 0 appel(s) LLM\n"
          "Cours : 420-TT4-AS\n"
          "Enseignant : Mourad Sehboub\n"
          "Horaires : Lundi 08h-12h (À distance)\n"
          "Sources consultees (preuve Python) : [TendancesTechnologiques_420-TT4-AS.docx]  [Tendances...Calendrier...pdf]\n"
          "\n"
          "QUESTION : Explique useReducer ?\n"
          "[outil] lire_cours() / tri Python | chemin : RAG (Python trie, LLM redige) | 1 appel(s) LLM\n"
          "useReducer centralise les transitions d'etat complexes... [SOURCE ...docx]\n"
          "\n"
          "QUESTION : donne le code usereducer\n"
          "chemin : BANQUE (Python seul) | 0 appel(s) LLM\n"
          "Banque (validee par le prof) : useReducer (etats complexes)\n"
          "\n"
          "QUESTION : Quelle est la recette de la tarte aux pommes ?\n"
          "chemin : GARDE (Python seul) | 0 appel(s) LLM\n"
          "Hors-matiere - voir manuel.",
          "C'est le cœur de l'exploit, et il tient en cinq observations. 1) Le chemin est décidé par du code, "
          "donc il est prévisible et explicable. 2) Trois questions sur cinq ne coûtent aucun appel au modèle : "
          "elles sont instantanées et gratuites. 3) Les sources sont extraites du texte envoyé, pas déclarées "
          "par le modèle : une preuve, pas une politesse. 4) Le RAG n'envoie que 3 500 caractères au lieu de "
          "20 000 : la fenêtre de contexte est respectée — et cela restera vrai avec un livre de 500 pages. "
          "5) Ollama éteint, l'agent ne ment pas : il montre les passages et annonce le mode dégradé.",
          "Le produit complet : app_final.py n'est que cette étape, avec l'interface et tous les modes (BUILD v10).",
          "La mesure : pourquoi 3 500 caractères et pas tout le cours (tokens), et comment évaluer sans tricher.",
          "La garde est volontairement grossière : elle accepte dès qu'un mot important existe dans les "
          "documents ou dans le livre, même si la réponse exacte n'y est pas. Le tri par mots-clés peut "
          "choisir de mauvais passages sur une question abstraite : on améliore en ajoutant des documents, "
          "jamais en supprimant la preuve. Et on n'envoie jamais tout le corpus : même indexé, un livre de "
          "300 pages ne pèse que quatre ou cinq pages dans le contexte.",
          "« Combien de fois le modèle a-t-il été appelé pour cinq questions ? » Réponse attendue : deux. "
          "« Qui a produit les pastilles ? » Python, à partir du texte lu.",
          "etape8.py est une démonstration, pas le produit : si elle échoue, lancez app_final.py, qui contient la même logique.")

    h2(doc, "Le livre entier, page par page : l'index BM25")
    para(doc, "Un manuel React de 300 pages pèse environ 500 000 caractères, soit seize fois la fenêtre de "
              "8 192 tokens (≈ 30 000 caractères). On ne peut donc ni l'envoyer en entier, ni le couper aux "
              "6 000 premiers caractères : l'agent ne connaîtrait que la préface. La solution tient dans un "
              "fichier, index_livre.py, et en quatre gestes.")
    puces(doc, [
        ("Extraire", "pypdf lit le PDF page par page ; chaque morceau garde son numéro de page d'origine."),
        ("Découper", "morceaux d'environ 900 caractères, avec 150 caractères de recouvrement pour ne pas couper une idée en deux."),
        ("Noter", "BM25, un score classique qui récompense les mots rares de la question et pénalise les morceaux trop longs."),
        ("Envoyer", "seuls les quatre ou cinq meilleurs morceaux partent au modèle, chacun précédé de [=== SOURCE: React_livre p.42 ===]."),
    ])
    bloc(doc, "Ce que la console affiche (exemple avec un livre de 312 pages)",
         "Livre indexe : React_livre (312 pages) -> 1187 morceaux, recherche BM25 par page\n"
         "(le premier lancement extrait le PDF ; les suivants lisent le cache JSON)\n"
         "\n"
         "QUESTION : Que dit le livre sur useReducer et les etats complexes ?\n"
         "[outil] lire_cours() / tri Python | chemin : RAG (Python trie, LLM redige) | 1 appel(s) LLM\n"
         "Le livre presente useReducer comme le hook des transitions complexes...\n"
         "Sources consultees (preuve Python) : [React_livre p.42]  [React_livre p.43]",
         BLEU, BLEU_CLAIR, 8.8)
    para(doc, "Le modèle voit environ 2 000 caractères, comme avant. Mais la bibliothèque peut faire "
              "500 pages, et chaque citation porte un numéro vérifiable : on ouvre le livre à la page 42, "
              "et le passage y est. C'est la différence entre « le livre dit que » et une preuve.")
    tableau(doc,
            ["Situation", "Ce qui part au modèle", "Ce que l'utilisateur voit"],
            [["Question sur une notion du livre", "4 ou 5 pages, ~1 800 caractères", "La réponse + la pastille p.42"],
             ["Question sur une notion du cours", "Les notes de cours (~1 700 caractères)", "La réponse + le nom du .docx"],
             ["Question absente du cours et du livre", "rien : la garde refuse avant le modèle", "« Hors-matière », 0 appel, 0 invention"],
             ["Deuxième lancement", "le même index, relu depuis le cache JSON", "démarrage en quelques millisecondes"]],
            [6.0, 5.4, 5.2], taille=8.6)
    encadre(doc, "Pourquoi BM25 et pas des embeddings",
            "Une recherche par embeddings serait plus sémantique, mais elle ajoute un modèle à télécharger, "
            "du temps CPU et une dépendance de plus. BM25 tient en quelques dizaines de lignes de Python pur, "
            "s'indexe en une seconde et reste prévisible : en atelier, la preuve d'abord. Sa limite est "
            "réelle : si la question n'emploie aucun mot du livre, la bonne page peut être manquée. On "
            "reformule avec les mots du livre — ou on ajoute un chapitre.", AMBRE, AMBRE_CLAIR, 9.8)
    para(doc, "L'index ne change pas le contrat : il rend le livre citable. Le modèle ne reçoit jamais le "
              "PDF, seulement quatre pages, et Python affiche la page exacte. C'est le même principe que "
              "depuis l'étape 2, appliqué à une échelle plus grande.")

    # ---------------------------------------------------------------- 9
    etape(doc, 9, "La mesure", "Pourquoi on ne peut pas tout donner, et comment évaluer sans tricher",
          "etape9_tokens.py, etape9c_eval.py", "7 min", "Console", "Tokens + score CSV",
          "Comprendre la contrainte qui justifie tout le reste. Un modèle ne voit pas des caractères, il voit "
          "des tokens ; sa fenêtre est finie. Et mesurer ce que les étudiants ont compris avec un QCM dont "
          "les bonnes réponses sont verrouillées par Python.",
          ["Lancer la tokenisation sur trois phrases (du code, une question, une date).",
           "Faire le lien avec la limite de 8 192 tokens et la taille des passages de l'étape 8.",
           "Lancer l'évaluation, répondre aux questions, lire le score.",
           "Montrer le fichier resultats/eval.csv : une ligne par passage, pas une note inventée."],
          "python etape9_tokens.py\n"
          "python etape9c_eval.py",
          "'const [count, setCount] = useState(0);'\n"
          "  -> 13 tokens : [9979, 685, 9127, 11, 900, 12332, ...]...\n"
          "  -> decode : 'const [count, setCount] ='\n"
          "\n"
          "'Quand le cours TendancesTechnologiques ?'\n"
          "  -> 11 tokens : [4507, 392, 443, 1093, ...]...\n"
          "\n"
          "'Lundi 08h-12h avec Mourad Sehboub'\n"
          "  -> 16 tokens : [43, 917, 72, 8487, ...]...\n"
          "\n"
          "Lien atelier : NUM_CTX=8192 tokens max, vos 12000 car. cours sont tronques.\n"
          "D'ou passages_utiles().\n"
          "\n"
          "--- evaluation ---\n"
          "12 phrases candidates dans cours/\n"
          "\n"
          "1. [IA auteur] Pourquoi utilise-t-on useState dans un composant ?\n"
          "   A) ...   B) ...   C) ...\n"
          "Votre lettre : B\n"
          "OK   [SOURCE cours/ + IA]\n"
          "\n"
          "Score comprehension : 2/3 -> resultats/eval.csv\n"
          "(si Ollama est absent : « 1. [Python seul, IA indisponible] ... » puis [SOURCE cours/])",
          "Le RAG n'est pas une mode : c'est une conséquence arithmétique. Un cours de 12 000 caractères "
          "dépasse déjà la fenêtre confortable ; quatre documents la remplissent. Et un QCM généré par le "
          "modèle mais verrouillé par Python — la bonne réponse doit se retrouver dans le passage, les leurres "
          "doivent en différer — montre qu'on peut utiliser l'IA sans lui donner le pouvoir de noter.",
          "La justification chiffrée du tri, et un outil d'évaluation réutilisable pour n'importe quel cours.",
          "L'ouverture : un livre, des sites officiels, et un cache pour que la démonstration survive au wifi du collège.",
          "transformers télécharge le tokenizer gpt2 (environ 500 Ko) : à faire une fois, avec wifi, avant "
          "l'atelier. torch n'est nécessaire que pour l'option sentiment (etape9b), pas pour les tokens.",
          "« Pourquoi ne pas envoyer les quatre documents d'un coup ? » Réponse attendue : 8 192 tokens, "
          "et il faut encore de la place pour la réponse.",
          "Pas de wifi pour le tokenizer → l'étape 9 est optionnelle, passez à la 10.")

    # ---------------------------------------------------------------- 10
    etape(doc, 10, "L'ouverture", "Un livre entier, des sites officiels, et un cache pour le hors-ligne",
          "etape10_ressources.py", "6 min", "Console", "Liste livre + sites",
          "Élargir la bibliothèque sans casser le contrat. Un PDF légal dans cours/livres/, des sites de "
          "référence, et un cache local : la première visite télécharge, les suivantes lisent le cache. "
          "Et si le PDF est volumineux, il est indexé page par page (BM25) : le livre entier devient "
          "interrogeable, seules les pages utiles partent au modèle, et la preuve porte un numéro de page.",
          ["Lancer le script et lire la liste : livre attendu, chapitres reliés à la banque, sites.",
           "Déposer votre PDF légal dans cours/livres/, relancer, vérifier qu'il est détecté.",
           "Lancer app_final.py : la console annonce « Livre indexe : N pages -> M morceaux ».",
           "Poser une question sur une notion précise et vérifier la pastille « p.N ».",
           "Dans app_final.py, poser une question sur react.dev et observer la pastille (live) puis (cache).",
           "Rappeler la règle : aucun PDF pirate dans l'atelier."],
          "python etape10_ressources.py",
          "[Ressources React - livre + web]\n"
          "\n"
          "LIVRE : React - Apprendre pas a pas (dossier du prof)\n"
          "Fichier attendu : cours/livres/React_livre.pdf\n"
          "PDF presents : React_livre.pdf\n"
          "\n"
          "SITES POPULAIRES :\n"
          "  - React officiel - react.dev : https://react.dev",
          "L'agent peut désormais citer une page précise d'un livre et la documentation officielle, pas "
          "seulement vos notes. Un manuel de 300 pages ne rentre pas dans la fenêtre du modèle : il est "
          "indexé, et seules quatre ou cinq pages sont envoyées. Le cache, lui, rend la démonstration "
          "reproductible : si le wifi du collège tombe, ou si le CDN est bloqué, l'agent répond quand même "
          "avec ce qu'il a déjà lu.",
          "Une bibliothèque extensible : un livre entier, des sources web, et une trace (live) ou (cache) "
          "pour chacune.",
          "Les extensions : le même principe appliqué aux TP (app_tp.py), puis au partage et à l'exécutable.",
          "Un PDF scanné ne passe pas : sans OCR, il n'y a pas de texte à indexer. L'index BM25 est lexical : "
          "une question qui n'emploie aucun mot du livre peut manquer la bonne page — reformulez avec les "
          "mots du livre. Le cache web ne se rafraîchit que si vous supprimez le fichier correspondant dans "
          "cours/cache_web/. Et un site peut changer : la preuve dit (cache), pas « la vérité ».",
          "« Pourquoi la réponse dit-elle (cache) ? » Réponse attendue : la page a déjà été téléchargée lors "
          "d'une démonstration précédente.",
          "Le livre reste légal : votre exemplaire, un extrait libre de droits, ou la documentation officielle. "
          "Sans aucun livre, tout le reste de l'atelier fonctionne à l'identique.")


# ================================================================== EXTENSIONS
def chapitre_extensions(doc):
    h1(doc, None, "Les trois extensions", "Partager, faire travailler, livrer — si le temps le permet")

    para(doc, "Les dix étapes construisent l'agent. Les trois extensions montrent ce qu'on peut en faire "
              "en classe, à distance et sur une clé USB. Elles ne sont pas nécessaires pour comprendre "
              "l'exploit ; elles le rendent utilisable.")

    # ---------------------------------------------------------------- 11
    etape(doc, "11 (extension)", "L'agent pédagogue TP", "Il ne donne pas la solution : il débloque",
          "app_tp.py", "10 min (démo)", "Navigateur", "Port 3002",
          "Un agent qui lit le PDF du TP, n'en montre qu'une étape à la fois, donne un indice sans jamais "
          "donner la solution, et ne passe à l'étape suivante que si le code collé passe le vérificateur Python.",
          ["Lancer app_tp.py : il tourne à côté de app_final.py, sur le port 3002.",
           "Ouvrir la fiche de l'étape A : but, étapes A1 à A7, squelettes, question de contrôle.",
           "Coller un code incomplet : le déblocage est refusé, un indice apparaît.",
           "Coller un code qui passe le seuil : l'étape B se débloque, progres.csv s'allonge."],
          "python app_tp.py",
          "BUILD app-tp v4 (JS valide) - Ouvrez http://127.0.0.1:3002\n"
          "\n"
          "(page : plan A-E, fiche de l'etape courante)\n"
          "A. Configuration de A a Z         60 min\n"
          "B. Composer une interface         50 min\n"
          "C. Rendre l'application interactive  40 min\n"
          "D. Afficher les donnees d'une API 40 min\n"
          "E. Formulaire et deploiement      30 min",
          "C'est l'aboutissement pédagogique : le modèle ne fait pas le TP à la place de l'étudiant. "
          "Le seuil de 0,6 est dans Python ; les indices sont du texte court ; la décision de débloquer "
          "appartient au code. Un agent qui ferait le TP serait un anti-apprentissage : ici, il refuse "
          "activement de le faire.",
          "Un tuteur qui accompagne sans remplacer, et une trace de progression par binôme.",
          "Le partage : montrer cet agent à distance, sans ouvrir de port.",
          "L'état est partagé entre tous les visiteurs : un seul binôme à la fois si vous partagez. Les fiches "
          "sont des fichiers JSON éditables : le professeur garde la main sur le contenu. Et avant chaque "
          "démonstration, tuez les python.exe fantômes et vérifiez la ligne BUILD.",
          "« Qui décide de débloquer l'étape ? » Réponse attendue : Python, sur le code collé. « L'IA peut-elle "
          "donner la solution ? » Non : ses consignes l'en empêchent, et le vérificateur ne lit que le code.",
          "Port 3002 occupé → tuer l'ancien processus. Plan absent → vérifier Tps/plan_tp.json et Tps/fiche_A.json.")

    # ---------------------------------------------------------------- 12
    etape(doc, "12 (extension)", "Le lien public", "Un tunnel sortant, pas un port ouvert",
          "partager.py / partager.bat", "5 min", "Navigateur distant", "URL trycloudflare.com",
          "Montrer l'agent sur un autre ordinateur ou un téléphone, sans compte, sans clé API et sans toucher "
          "au routeur. Le PC ouvre un tunnel sortant vers Cloudflare ; le lien public est jetable et meurt "
          "avec la fenêtre.",
          ["Double-cliquer sur partager.bat (ou lancer python partager.py).",
           "Lire l'URL affichée : elle finit par ?k= une clé aléatoire.",
           "Ouvrir l'URL sans la clé : 403. Avec la clé : la page, puis un cookie.",
           "Fermer la fenêtre : le lien ne fonctionne plus (erreur 530)."],
          "partager.bat\n"
          "python partager.py 3002        (partage app_tp.py)\n"
          "python partager.py --sans-cle  (lien ouvert, deconseille)",
          "https://exemple-aleatoire.trycloudflare.com/?k=6hxJ5ZgS\n"
          "\n"
          "sans ?k=  -> 403 : cle d acces manquante.\n"
          "avec ?k=  -> 200 : la page de l'agent, puis cookie de session.",
          "C'est la réponse au « on ne peut pas montrer à distance » sans faire de trou de sécurité. Le PC "
          "se connecte vers l'extérieur en 443 ; Ollama reste en 11434, sur la boucle locale. Aucun compte, "
          "aucune clé API, aucun port ouvert sur le routeur.",
          "Une démonstration à distance en trente secondes, révocable en fermant la fenêtre.",
          "L'exécutable : livrer l'agent sur une clé USB, sans Python.",
          "L'état est partagé : tous les visiteurs voient le même quiz, le même TP, le même progres.csv. Le "
          "lien change à chaque lancement et le laptop doit rester allumé. DNS peut mettre 30 secondes ; "
          "cloudflared (52 Mo) est retéléchargé s'il manque.",
          "« Pourquoi n'y a-t-il pas de port ouvert sur le routeur ? » Réponse attendue : le tunnel part du PC "
          "vers l'extérieur ; rien n'entre directement.",
          "403 → il manque ?k=. DNS name does not exist → attendre 30 s. Le lien meurt → la fenêtre a été fermée.")

    # ---------------------------------------------------------------- 13
    etape(doc, "13 (extension)", "L'exécutable", "Une clé USB qui marche sans Python installé",
          "build_exe.bat, dist\\AgentReact", "10 min (hors séance)", "Windows", "AgentReact.exe",
          "Emballer l'application, les documents, le CSS et MathJax dans un dossier exécutable. L'étudiant "
          "double-clique, le navigateur s'ouvre ; seuls Ollama et le modèle restent à installer.",
          ["Lancer build_exe.bat sur la machine de préparation (avec wifi, une seule fois).",
           "Copier dist\\AgentReact, installer.bat et le lien ollama.com/download sur la clé USB.",
           "Sur un poste neuf : installer Ollama, puis lancer AgentReact.exe.",
           "Pour ajouter un document ou un livre, le déposer dans dist\\AgentReact\\_internal\\cours\\, puis relancer.",
           "Vérifier la ligne BUILD en console : c'est elle qui dit quelle version tourne."],
          "build_exe.bat\n"
          "dist\\AgentReact\\AgentReact.exe",
          "BUILD app-finale v10 (livre indexe BM25) - Ouvrez http://127.0.0.1:3000\n"
          "\n"
          "(le navigateur s'ouvre sur la page de l'agent)",
          "C'est la version « je n'ai pas le temps d'installer Python » : Python, les documents et les "
          "ressources sont embarqués. Ollama et llama3.2 restent à part, parce qu'un modèle de 2 Go ne se "
          "met pas dans un exécutable de cette taille — et parce qu'il doit tourner en service.",
          "Une livraison autonome, reproductible, pour les postes sans environnement de développement.",
          "Fin du parcours : vous avez l'agent, ses preuves, son tuteur de TP et sa version portable.",
          "On construit en --onedir, pas en --onefile : l'exe a besoin de son dossier _internal "
           "(cours/, static/, les fichiers Python). torch et transformers sont exclus : l'étape 9 n'est pas "
           "dans l'exe. Et l'exe ne "
          "contient évidemment pas Ollama.",
          "« Qu'est-ce qui n'est pas dans l'exe ? » Réponse attendue : Ollama et le modèle, qui s'installent à part.",
          "L'exe ne démarre pas → vérifier qu'il est bien dans son dossier, avec _internal à côté.")


# ================================================================== OBJECTION
def chapitre_objection(doc):
    h1(doc, None, "« On devrait pouvoir poser n'importe quelle question »",
        "La remarque des étudiants, prise au sérieux — et la réponse en trente secondes")

    riche(doc, [("C'est la question la plus utile de l'atelier. Elle mérite mieux qu'un slogan. "
                 "Elle révèle une confusion entre deux objets qui parlent de la même façon, et qui ne "
                 "promettent pas la même chose.", {})], 10.5, apres=7)

    h2(doc, "Ce que la phrase compare sans le dire")
    tableau(doc,
            ["", "Le chatbot général (étape 1)", "L'agent pédagogique (étape 8)"],
            [["Questions acceptées", "Toutes", "Toutes celles dont la réponse est dans les documents"],
             ["Source de la réponse", "Sa mémoire d'entraînement", "Un fichier, un passage, une ligne"],
             ["Vérifiable", "Non", "Oui, en cinq secondes"],
             ["Quand il ne sait pas", "Il invente, avec assurance", "Il refuse, ou il cite"],
             ["Peut noter un quiz", "Non", "Oui, le score est calculé"],
             ["Utile en cours", "Pour discuter", "Pour répondre, corriger, guider"],
             ["Coût d'une erreur", "Une phrase fausse", "Une note fausse, une date fausse"]],
            [3.6, 6.4, 6.4])

    para(doc, "Le premier est impressionnant. Le second est utilisable. L'atelier construit le second, "
              "mais commence par le premier : c'est l'étape 1, et c'est volontaire. On ne peut pas "
              "comprendre le contrat de l'agent si on n'a pas vu, en direct, le modèle inventer un horaire.")

    h2(doc, "Le contrat : trois conditions, aucune négociable")
    puces(doc, [
        ("La réponse est dans la matière", "documents de cours/, banque de code validée, calendrier, ou cache web. Pas dans la mémoire du modèle."),
        ("La question est reconnaissable", "au moins un mot important doit exister dans les documents. Sinon la garde refuse, et le dit."),
        ("L'agent peut dire « je ne sais pas »", "et ce refus est une réponse de première classe : instantané, gratuit, vérifiable."),
    ])
    para(doc, "Ces trois conditions ne limitent pas l'agent : elles le rendent citable. Un agent qui "
              "répond à tout sans source ne peut pas être utilisé pour une note, un horaire ou un extrait "
              "de code. Il peut seulement être utilisé pour discuter.")

    h2(doc, "La démonstration en quatre-vingt-dix secondes")
    para(doc, "C'est la batterie de questions à faire devant la classe, dans cet ordre. Elle est déjà "
              "scriptée dans etape8.py --demo ; vous pouvez aussi la jouer dans app_final.py. La ligne "
              "« livre » suppose un PDF indexé : sans livre, la batterie fait cinq questions et deux "
              "appels au modèle.")
    tableau(doc,
            ["Question", "Chemin", "LLM", "Preuve affichée", "Ce que ça prouve"],
            [["Que dit la matière sur Tailwind ?", "RAG", "1", "Le nom du .docx", "Il lit et il cite"],
             ["Quand le cours 420-TT4-AS ?", "Calendrier", "0", "Le fichier du calendrier", "La date ne sort pas du modèle"],
             ["Donne le code useReducer", "Banque", "0", "banque_react.py:usereducer", "Le code ne sort pas du modèle"],
             ["Explique useReducer ?", "RAG", "1", "Le nom du .docx", "Il lit au lieu de deviner"],
             ["Que dit le livre sur useReducer ?", "RAG livre", "1", "React_livre p.42", "Il cite une page précise"],
             ["Quelle est la recette de la tarte aux pommes ?", "Garde", "0", "aucune", "Le hors-sujet est instantané"]],
            [5.4, 2.4, 1.0, 4.0, 3.6], taille=8.3)

    encadre(doc, "La phrase à dire après la démonstration",
            "« Sur ces six questions, le modèle n'a été appelé que trois fois. Les trois autres réponses "
            "sortent du code et des fichiers : zéro invention, zéro attente. Ce n'est pas un chatbot plus "
            "faible : c'est un chatbot qui a des comptes à rendre. »", VERT, VERT_CLAIR, 10.5)

    h2(doc, "Les trois verrous, un seul rédacteur")
    tableau(doc,
            ["Verrou", "Ce qu'il bloque", "Où le voir"],
            [["La garde", "Une question dont aucun mot n'est dans le cours ni dans le livre", "etape2.py, etape8.py"],
             ["Le tri (RAG)", "L'envoi de tout le cours — ou de tout un livre — et la noyade du passage utile", "passages_utiles(), index_livre.py"],
             ["Les pastilles", "L'affirmation « selon le cours » sans fichier derrière", "extraire_sources(), app_final.py"]],
            [3.4, 8.2, 4.8])
    para(doc, "Le rédacteur, lui, n'a qu'un rôle : mettre en français ce que Python lui a apporté. C'est "
              "pour cela qu'on peut le remplacer par un autre modèle sans changer le contrat. Le jour où "
              "un modèle plus petit, plus rapide ou plus français arrive, on le branche : les verrous, eux, "
              "ne bougent pas.")

    h2(doc, "Ce que l'étudiant veut vraiment, et quoi répondre")
    tableau(doc,
            ["Ce qu'il dit", "Ce qu'il cherche", "Votre réponse"],
            [["« Je devrais pouvoir demander n'importe quoi »", "Tester les limites, comme avec ChatGPT", "« Tu peux : demande n'importe quoi sur le cours. Pour le reste, l'agent te dira qu'il ne sait pas — et c'est ce qui rend ses réponses fiables. »"],
             ["« Donne-moi la réponse du quiz »", "Contourner l'exercice", "« Il ne l'a pas : les réponses sont dans Python, pas dans le modèle. »"],
             ["« Il refuse ma question sur Docker, il est nul »", "Comprendre pourquoi", "« Normal : Docker n'est ni dans ton cours ni dans ton livre. Ajoute un document, relance, et il répondra. Le refus n'est pas une limite du modèle : c'est une limite de ta matière. »"],
             ["« Pourquoi pas ChatGPT ? »", "Comprendre l'intérêt du local", "« ChatGPT ne lit pas ton cours, ne cite pas tes fichiers, et ne peut pas être branché sur ta banque de code. Ici, tout est chez toi. »"]],
            [5.0, 4.4, 7.0], taille=8.5)

    h2(doc, "Élargir, sans casser le contrat")
    tableau(doc,
            ["Geste", "Effet", "Temps"],
            [["Ajouter un DOCX, un PDF ou un livre entier dans cours/", "De nouvelles questions deviennent légitimes ; un livre est indexé page par page", "1 min"],
             ["Ajouter un snippet dans banque_react.py", "Un nouveau « donne le code … » fonctionne", "2 min"],
             ["Ajouter un site dans le cache web", "Une source officielle devient citable", "5 min"],
             ["Ajuster les mots de la garde", "Moins de refus, plus de bruit : à faire avec mesure", "10 min"],
             ["Mesurer avec etape9c_eval.py", "Savoir ce qui est compris, pas seulement répondu", "10 min"]],
            [7.2, 7.4, 2.0])
    para(doc, "La bonne façon d'élargir n'est jamais de retirer un verrou. C'est d'ajouter de la matière, "
              "puis de vérifier que la preuve suit. Un agent qui accepte tout parce qu'on a supprimé la "
              "garde n'est pas plus utile : il est seulement plus difficile à contredire.")

    h2(doc, "Les limites, dites honnêtement")
    puces(doc, [
        ("PDF scannés", "sans OCR, ils ne contiennent pas de texte : l'agent l'annonce et les ignore."),
        ("Livre indexé, recherche lexicale", "un livre entier est indexé, mais BM25 rapproche des mots, pas des idées : une question sans aucun mot du livre peut manquer la bonne page."),
        ("Questions à plusieurs documents", "le tri par mots choisit des passages, il ne raisonne pas sur une chaîne de preuves."),
        ("Questions abstraites", "« quelle est la philosophie de React ? » peut trouver de mauvais passages : le tri est lexical, pas sémantique."),
        ("Langue et formulation", "une question très éloignée du vocabulaire du cours peut être refusée à tort."),
        ("Fenêtre de contexte", "8 192 tokens : au-delà, on ne peut pas tout envoyer, d'où le tri et l'index."),
        ("Garde grossière", "un mot présent par hasard suffit à laisser passer : elle réduit le bruit, elle ne prouve pas la pertinence."),
    ])
    para(doc, "Ces limites ne sont pas des défauts cachés : elles sont la raison d'être des étapes 8 et 9. "
              "Un agent qui prétendrait ne pas les avoir serait en train de vous vendre quelque chose.")

    h2(doc, "Et si la question est vraiment hors programme ?")
    para(doc, "Alors on change d'outil, pas de discours. L'étape 1 est là pour cela : elle répond à tout, "
              "avec sa mémoire, et elle ne prétend rien prouver. On peut l'utiliser pour une discussion "
              "ouverte, une explication générale, un brainstorming. On ne l'utilise pas pour une note, "
              "une date ou un extrait de code.")
    encadre(doc, "La distinction à garder en tête",
            "Un agent pour apprendre (ouvert, bavard, sans preuve) et un agent pour évaluer (fermé, cité, "
            "vérifiable). Les deux sont utiles. Les confondre est la seule vraie erreur.", AMBRE, AMBRE_CLAIR, 10)

    h2(doc, "La réponse en trente secondes")
    encadre(doc, "À réciter",
            "« L'agent ne sait pas tout : il sait ce qu'il a lu, et il vous montre où. Si vous voulez "
            "qu'il réponde à une nouvelle question, ajoutez le document — et il vous dira de quel passage "
            "vient la réponse. C'est moins impressionnant qu'un chatbot qui invente, mais c'est utilisable "
            "pour apprendre et pour noter. »", BLEU, BLEU_CLAIR, 10.5)


# ================================================================== DÉMONSTRATIONS
def chapitre_demos(doc):
    h1(doc, None, "Les démonstrations de contrôle", "Six preuves à montrer, et la phrase qui va avec")

    para(doc, "Une démonstration ne vaut que si elle peut échouer. Ces six-là sont choisies pour cela : "
              "chacune montre une décision prise par Python, ou une limite assumée par l'agent. Faites-en "
              "trois avant la pause, les trois autres après.")

    tableau(doc,
            ["#", "Démonstration", "Ce que vous faites", "Ce que ça prouve", "Min"],
            [["1", "Le modèle seul contre l'agent", "Poser le même horaire à etape1.py puis à app_final.py", "La différence, c'est le fichier, pas le modèle", "1"],
             ["2", "La garde et la banque", "« Explique useReducer ? », « Donne le code useReducer », puis une question hors sujet", "Même sujet, deux chemins ; le refus est instantané", "1"],
             ["3", "La correction", "Coller un composant fautif", "Python tranche, le modèle explique", "1"],
             ["4", "La panne", "Fermer Ollama, relancer app_final.py", "Le Python continue de fonctionner", "1,5"],
             ["5", "Le tunnel", "Ouvrir le lien sans puis avec ?k=", "403 puis 200, sans port ouvert", "2"],
             ["6", "Le TP verrouillé", "Coller un code incomplet dans app_tp.py", "L'IA ne fait pas le TP", "2"]],
            [0.7, 4.0, 5.6, 5.2, 1.0], taille=8.3)

    h2(doc, "1. Le modèle seul contre l'agent — la démonstration qui retourne la classe")
    para(doc, "C'est celle qui répond à l'objection avant même qu'elle soit posée. Elle prend une minute "
              "et elle est imparable, parce que c'est le même modèle, la même question, et deux résultats.")
    bloc(doc, "Le script, mot pour mot",
         "Etape 1 : « Quand a lieu le cours 420-TT4-AS ? »\n"
         "  -> le modele repond : mardi 13 h, avec M. Dupont.       (plausible, faux)\n"
         "\n"
         "Etape 8 / app_final : la meme question\n"
         "  -> chemin : CALENDRIER (Python seul), 0 appel LLM\n"
         "  -> Lundi 08h-12h, Mourad Sehboub\n"
         "  -> Sources : [TendancesTechnologiques_420-TT4-AS.docx] [Calendrier...pdf]",
         BLEU, BLEU_CLAIR, 8.8)
    para(doc, "Ce qu'il faut dire : « Le modèle n'a pas changé. Ce qui a changé, c'est qu'on ne lui demande "
              "plus de se souvenir : on lui donne le calendrier, et c'est Python qui lit la date. »")

    h2(doc, "2. La garde — le refus qui rassure")
    para(doc, "Poser « Explique useReducer ? » : l'agent lit le passage du guide et cite le .docx. Enchaîner "
              "avec « Donne le code useReducer » : la banque répond, avec le snippet validé. Même sujet, "
              "deux chemins, deux preuves. Puis poser « Quelle est la recette de la tarte aux pommes ? » : "
              "refus instantané, zéro appel au modèle.")
    para(doc, "Ce qu'il faut dire : « Il ne refuse pas parce qu'il est bête. Il refuse ce qui n'est ni dans "
              "le cours ni dans le livre indexé. Ajoutez le chapitre, relancez, et il répondra. »")

    h2(doc, "3. La correction — le modèle n'a pas le dernier mot")
    para(doc, "Coller un composant en minuscule avec count=count+1. Lire d'abord la liste CORRECTION PYTHON, "
              "puis seulement l'EXPLICATION IA. Insister sur l'ordre : les faits d'abord, la politesse ensuite.")
    para(doc, "Ce qu'il faut dire : « Si l'IA se trompe dans l'explication, la correction reste juste. "
              "C'est ça, la séparation des pouvoirs. »")

    h2(doc, "4. La panne — ce qui marche sans modèle")
    para(doc, "Fermer Ollama (quitter l'application), puis relancer app_final.py. Le quiz, la banque de "
              "codes, le calendrier et le TP continuent de fonctionner. Le mode Cours affiche les passages "
              "trouvés et annonce que l'IA est indisponible. Revenir ensuite au mode normal.")
    para(doc, "Ce qu'il faut dire : « Tout ce qui est vérifiable ne dépend pas du modèle. C'est pour cela "
              "qu'on peut l'utiliser en évaluation. »")

    h2(doc, "5. Le tunnel — la sécurité en une manipulation")
    para(doc, "Lancer partager.bat, ouvrir l'URL sans ?k= (403), puis avec (200). Fermer la fenêtre : le "
              "lien meurt. Rappeler qu'aucun port n'a été ouvert sur le routeur.")
    para(doc, "Ce qu'il faut dire : « Le PC se connecte vers l'extérieur. Rien n'entre directement. Et "
              "quand je ferme cette fenêtre, le lien public n'existe plus. »")

    h2(doc, "6. Le TP — l'agent qui refuse de faire le travail")
    para(doc, "Dans app_tp.py, coller un code incomplet : l'étape ne se débloque pas, un indice apparaît. "
              "Coller un code qui passe le seuil : l'étape suivante s'ouvre. Montrer progres.csv.")
    para(doc, "Ce qu'il faut dire : « L'IA ne peut pas vous donner la solution : elle ne décide même pas "
              "du déblocage. C'est le code qui vérifie. »")

    h2(doc, "Les quatre questions à poser à chaque pause")
    tableau(doc,
            ["Question", "Réponse attendue", "Si l'étudiant se trompe"],
            [["Qui a lu le document ?", "Python, via l'outil", "Revenir à la ligne [outil] de l'étape 3"],
             ["Qui a écrit la réponse ?", "Le modèle, à partir des passages", "Montrer le prompt système"],
             ["Qui a décidé de refuser ?", "Python, la garde", "Relancer etape8.py --demo"],
             ["Qui a corrigé le quiz ?", "Python", "Montrer le score et le code de correction"]],
            [6.0, 5.6, 5.0])

    encadre(doc, "La phrase de transition, à chaque fois",
            "« Ce n'est pas le modèle qui est intelligent, c'est le montage autour de lui. Et ce montage, "
            "vous venez de le construire. »", VERT, VERT_CLAIR, 10.5)


# ================================================================== CONDUCTEUR
def chapitre_runbook(doc):
    h1(doc, None, "Le conducteur 2 h", "Minute par minute, avec ce que vous dites")

    para(doc, "Les durées incluent la manipulation par les étudiants. Si un groupe est plus lent, coupez "
              "court aux étapes 9 et 10 : elles illustrent, elles ne conditionnent pas la compréhension. "
              "Ne coupez jamais l'étape 8 : c'est elle qui porte l'exploit.")

    tableau(doc,
            ["Min", "Ce que vous faites", "Ce que vous dites", "Étape"],
            [["0-5", "Accueil, vérification d'Ollama, ouverture du dossier", "« Aujourd'hui, on ne va pas utiliser une IA : on va la construire, et l'empêcher de mentir. »", "—"],
             ["5-13", "Étape 1, trois questions dont deux pièges", "« Retenez la réponse à l'horaire : elle est fausse. On va voir pourquoi. »", "1"],
             ["13-23", "Étape 2, le cours et le refus", "« Le refus est une fonctionnalité, pas un bug. »", "2"],
             ["23-35", "Étape 3, la boucle et la ligne [outil]", "« Le modèle ne lit pas le disque. C'est Python qui lit. »", "3"],
             ["35-43", "Étape 4, la page dans le navigateur", "« 127.0.0.1 : cette page n'existe que sur ce PC. »", "4"],
             ["43-53", "Étape 5, quiz et score détaillé", "« La note est calculée. L'IA n'a pas la clé. »", "5"],
             ["53-65", "Étape 6, banque et correction", "« Le code vient du prof, l'explication vient du modèle. »", "6"],
             ["65-75", "Étape 7, vos vrais documents", "« Maintenant il lit votre calendrier, pas le mien. »", "7"],
             ["75-90", "Étape 8, les cinq chemins et l'index du livre", "« Deux questions sur cinq ont besoin du modèle ; le livre, lui, est cité page par page. »", "8"],
             ["90-97", "Étape 9, tokens et évaluation", "« Voilà pourquoi on ne peut pas tout donner. »", "9"],
             ["97-103", "Étape 10, livre indexé et cache", "« Un livre de 300 pages tient dans l'agent : il cite la page. »", "10"],
             ["103-112", "Extension 11, le TP verrouillé (démo)", "« L'IA refuse de faire le TP à votre place. »", "11"],
             ["112-120", "Objection, trois phrases, synthèse", "« L'agent ne sait pas tout : il sait ce qu'il a lu, et il montre où. »", "—"]],
            [1.5, 6.2, 8.2, 1.2], taille=8.2)

    h2(doc, "Si vous êtes en retard")
    puces(doc, [
        "Sautez les étapes 9 et 10 : elles seront lues sur le document.",
        "Gardez 1, 2, 3, 8 et les démonstrations de la section précédente. C'est le squelette de l'argument.",
        "Ne sautez pas l'étape 2 : sans le refus, l'étape 8 n'a pas de sens.",
    ])
    h2(doc, "Si vous êtes en avance")
    puces(doc, [
        "Faites ajouter un document par un étudiant, puis reposez la question qui était refusée.",
        "Faites ajouter un snippet à la banque, puis demandez-le.",
        "Lancez app_tp.py en autonomie sur 15 minutes et circulez.",
    ])
    h2(doc, "Après la séance")
    tableau(doc,
            ["À faire", "Pourquoi"],
            [["Fermer les tunnels et tuer les python.exe", "Un lien public oublié reste ouvert"],
             ["Sauvegarder le dossier (sans .venv)", "5,8 Mo suffisent ; .venv fait 817 Mo"],
             ["Noter les questions restées sans réponse", "Elles deviennent les documents de la prochaine séance"],
             ["Relancer etape9c_eval.py", "Mesurer ce qui est compris, pas seulement ce qui a été montré"]],
            [7.4, 8.6])


# ================================================================== DÉPANNAGE
def chapitre_depannage(doc):
    h1(doc, None, "Dépannage express", "Les trois commandes de survie, puis les cas courants")

    bloc(doc, "À essayer dans cet ordre",
         "taskkill /F /IM python.exe     (tue les serveurs fantomes)\n"
         "ollama list                    (le moteur et le modele sont-ils la ?)\n"
         "python app_final.py            (relance l'agent complet, BUILD v10)",
         ROUGE, ROUGE_CLAIR, 9)

    tableau(doc,
            ["Symptôme", "Cause probable", "Ce que vous faites"],
            [["Connection refused", "Ollama n'est pas lancé", "Démarrer Ollama ; sinon ollama serve"],
             ["model not found", "llama3.2 absent", "ollama pull llama3.2:latest"],
             ["Le port 3000 est occupé", "Un ancien python.exe tourne", "taskkill /F /IM python.exe, puis relancer"],
             ["Page blanche", "Mauvaise adresse ou mauvais BUILD", "Ouvrir http://127.0.0.1:3000, vérifier la ligne BUILD en console"],
             ["Page sans style", "static/ absent ou CDN utilisé", "Vérifier static/app.css ; aucune page ne doit appeler un CDN"],
             ["Accents bizarres dans la console", "Encodage PowerShell", "set PYTHONIOENCODING=utf-8 ; les fichiers sont corrects"],
             ["403 sur le lien public", "Il manque ?k= ou le cookie a été effacé", "Rouvrir l'URL complète avec la clé"],
             ["DNS name does not exist", "Le tunnel vient de démarrer", "Attendre 30 secondes"],
             ["530 sur le lien public", "La fenêtre du tunnel est fermée", "Relancer partager.bat"],
             ["PDF ignoré", "PDF scanné (image)", "Utiliser un PDF texte, ou faire de l'OCR"],
             ["Le livre n'est jamais cité", "PDF sous 20 000 caractères, ou question sans mot du livre", "Vérifier la ligne « Livre indexe » au démarrage ; reformuler avec les mots du livre"],
             ["Premier démarrage lent avec un livre", "Extraction pypdf la première fois", "Attendre une fois ; le cache JSON accélère les lancements suivants"],
             ["DOCX illisible", "Fichier .doc renommé", "Enregistrer vraiment en .docx"],
             ["« Clique d'abord Lancer Quiz »", "État du quiz perdu", "Relancer le quiz, un binôme par navigateur"],
             ["Le TP ne débloque pas", "Code sous le seuil 0,6", "Lire l'indice, compléter, recoller"],
             ["ImportError transformers", "Conflit de versions", "pip install -r requirements.txt (le verrou huggingface-hub<2 est inclus)"],
             ["Première réponse très lente", "Le modèle se charge en mémoire", "Attendre 10 à 20 s, les suivantes sont rapides"],
             ["L'exe ne démarre pas", "Il a été déplacé hors de son dossier", "Garder dist\\AgentReact entier, avec son dossier _internal"]],
            [5.0, 5.2, 5.8], taille=8.3)

    encadre(doc, "La règle d'or du dépannage en séance",
            "Deux minutes maximum. Au-delà, vous basculez sur app_final.py et vous continuez. Un atelier "
            "qui avance avec une démo partielle vaut mieux qu'un atelier qui s'arrête sur un port occupé.", AMBRE, AMBRE_CLAIR, 10)


# ================================================================== ANNEXES
def chapitre_annexes(doc):
    h1(doc, None, "Annexes", "L'arborescence, toutes les commandes, le glossaire, la checklist")

    h2(doc, "A. L'arborescence de mon_agent_react")
    bloc(doc, "Les fichiers que vous manipulez",
         "mon_agent_react\\\n"
         "├─ etape1.py … etape10_ressources.py   les dix etapes (console ou web)\n"
         "├─ etape8.py                            l'etape manquante, reconstruite et testee\n"
         "├─ etape9b_sentiment.py, etape9c_eval.py  options de mesure\n"
         "├─ index_livre.py                       l'index BM25 d'un livre PDF, page par page\n"
         "├─ app_final.py                         l'agent complet, BUILD v10, port 3000\n"
         "├─ app_tp.py                            l'agent pedagogue, BUILD v4, port 3002\n"
         "├─ app_maths.py                         la demo maths, BUILD v3, port 3001\n"
         "├─ banque_react.py                      22 snippets valides par le prof\n"
         "├─ cours\\                               la matiere (txt, docx, pdf, livres\\, cache_web\\, cache_index\\)\n"
         "├─ Tps\\                                 le TP (PDF, plan_tp.json, fiche_A.json, progres.csv)\n"
         "├─ static\\                              app.css + mathjax-tex-svg.js (hors-ligne)\n"
         "├─ resultats\\                           eval.csv, lien_public.txt, tunnel.log\n"
         "├─ installer.bat, demarrer-agent.bat, partager.bat, build_exe.bat\n"
         "└─ requirements.txt",
         ENCRE, GRIS_CLAIR, 8.2)

    h2(doc, "B. Toutes les commandes, en une page")
    tableau(doc,
            ["Quand", "Commande", "Attendu"],
            [["Installation (une fois)", "installer.bat", "llama3.2 téléchargé, libs OK"],
             ["Vérifier le moteur", "ollama list", "llama3.2:latest"],
             ["Étape 1", "python etape1.py", "réponse, parfois fausse"],
             ["Étape 2", "python etape2.py", "515 caractères, refus hors-matière"],
             ["Étape 3", "python etape3.py", "[outil] lire_cours()"],
             ["Étape 4", "python etape4.py", "page sur 127.0.0.1:3000"],
             ["Étape 5", "python etape5_web.py", "quiz + score Python"],
             ["Étape 6", "python etape6_web.py", "banque + correction"],
             ["Étape 7", "python etape6_web_doc.py", "réponse citant un .docx"],
             ["Étape 8", "python etape8.py --demo", "5 chemins, 2 appels LLM"],
             ["Étape 9", "python etape9_tokens.py", "13, 11, 16 tokens"],
             ["Étape 9 (éval)", "python etape9c_eval.py", "score dans resultats/eval.csv"],
             ["Étape 10", "python etape10_ressources.py", "livre + sites"],
             ["Agent complet", "python app_final.py", "BUILD v10, port 3000"],
             ["TP", "python app_tp.py", "BUILD v4, port 3002"],
             ["Maths (option)", "python app_maths.py", "BUILD v3, port 3001"],
             ["Partager", "partager.bat", "URL trycloudflare avec ?k="],
             ["Partager le TP", "python partager.py 3002", "URL du TP"],
             ["Lien ouvert", "python partager.py --sans-cle", "déconseillé en classe"],
             ["Exe", "build_exe.bat", "dist\\AgentReact\\AgentReact.exe"],
             ["Nettoyage", "taskkill /F /IM python.exe", "plus de serveur fantôme"]],
            [4.4, 6.6, 5.0], taille=8.0)

    h2(doc, "C. Glossaire")
    tableau(doc,
            ["Terme", "Définition utile en atelier"],
            [["LLM", "Modèle de langage : un programme qui prédit la suite de mots. Il ne « sait » pas, il calcule une vraisemblance."],
             ["Token", "Morceau de mot (environ 4 caractères). Un modèle compte en tokens, pas en caractères."],
             ["Fenêtre de contexte", "Nombre maximal de tokens que le modèle peut lire en une fois (8 192 ici)."],
             ["Hallucination", "Réponse fluide et fausse, produite sans source. L'étape 1 la montre, l'étape 8 la bloque."],
             ["RAG", "Recherche dans des documents, puis envoi des passages utiles au modèle. Le modèle ne lit pas le disque."],
             ["Index (BM25)", "Table qui note chaque morceau d'un livre pour une question, sans modèle ni GPU. C'est ce qui rend un livre de 300 pages interrogeable."],
             ["Morceau (chunk)", "Extrait d'environ 900 caractères, étiqueté avec sa page : l'unité envoyée au modèle quand un livre est indexé."],
             ["Citation p.N", "Pastille qui donne la page exacte d'un livre indexé, vérifiable en ouvrant le PDF."],
             ["Garde", "Filtre Python qui refuse une question avant l'appel au modèle."],
             ["Pastille", "Étiquette de source affichée sous une réponse, extraite du texte réellement lu."],
             ["Tool-calling", "Le modèle demande une fonction ; Python l'exécute et renvoie le résultat."],
             ["ReAct", "Boucle raisonner → agir → observer, plafonnée ici à cinq tours."],
             ["AST", "Arbre syntaxique d'un code : permet de repérer des noms inconnus et des fautes de frappe."],
             ["Bac à sable", "Exécution d'un code étudiant dans un fichier temporaire, avec un délai maximal."],
             ["Tunnel", "Connexion sortante qui rend un serveur local accessible par une URL publique, sans ouvrir de port."],
             ["Cache", "Copie locale d'une page web, pour répondre sans wifi et prouver la source (cache)."],
             ["OCR", "Reconnaissance de texte sur une image : nécessaire pour les PDF scannés."]],
            [3.4, 12.6], taille=8.4)

    h2(doc, "D. Checklist J-7")
    tableau(doc,
            ["☐", "Vérification", "Critère"],
            [["☐", "Ollama installé et llama3.2 présent", "ollama list"],
             ["☐", "Bibliothèques installées", "python -c \"import requests, pypdf, transformers; print('OK')\""],
             ["☐", "Le tokenizer gpt2 est en cache", "python etape9_tokens.py affiche 13 tokens"],
             ["☐", "Les 10 étapes ont été lancées une fois", "aucune erreur bloquante"],
             ["☐", "app_final.py répond et affiche une pastille", "question Tailwind"],
             ["☐", "Un livre légal est dans cours/livres/ et la console annonce « Livre indexe »", "question sur une notion précise, pastille p.N"],
             ["☐", "Le calendrier donne la bonne date", "lundi 08h-12h, Mourad Sehboub"],
             ["☐", "La page est stylée sans wifi", "CSS local, pas de CDN"],
             ["☐", "app_tp.py ouvre sur 3002", "fiche A visible"],
             ["☐", "Le tunnel fonctionne", "403 sans clé, 200 avec"],
             ["☐", "La clé USB contient dist + installer.bat", "test sur un poste neuf"],
             ["☐", "Aucun python.exe fantôme", "taskkill avant la séance"],
             ["☐", "Le document est imprimé ou ouvert", "cette page suffit"]],
            [1.0, 9.0, 6.0])

    h2(doc, "E. Où est le code, et ce qui a changé")
    para(doc, "Ce document ne contient volontairement aucun code Python. La solution est dans les fichiers : "
              "etape1.py à etape10_ressources.py pour le parcours, app_final.py pour l'agent complet, "
              "app_tp.py pour le tuteur de TP, app_maths.py pour la démonstration de transfert, "
              "index_livre.py pour l'index du livre.")
    encadre(doc, "Cette version du 1er novembre 2026",
            "etape8.py a été reconstruit : il n'existait pas dans le dossier. Il reprend la logique de "
            "app_final.py (lecture des documents, tri des passages, extraction des sources, calendrier, "
            "banque) et l'expose en console avec cinq démonstrations. Il a été testé avec Ollama allumé, "
            "puis en mode dégradé sans Ollama. requirements.txt verrouille désormais huggingface-hub<2, "
            "sans quoi l'étape 9 ne démarre pas. Nouveauté : index_livre.py indexe un livre PDF entier "
            "(BM25, page par page) au lieu de le tronquer ; app_final.py et etape8.py l'utilisent, citent "
            "« p.N » et refusent toujours le hors-sujet.", VERT, VERT_CLAIR, 10)

    h2(doc, "F. La fiche à garder sous les yeux")
    bloc(doc, "Les six questions et les trois phrases",
         "1. Que dit la matiere sur Tailwind ?          -> RAG + pastille .docx\n"
         "2. Quand le cours 420-TT4-AS ?                -> calendrier, 0 LLM\n"
         "3. Donne le code useReducer                   -> banque, 0 LLM\n"
         "4. Explique useReducer ?                      -> RAG + pastille .docx\n"
         "5. Quelle est la recette de la tarte ?        -> garde, refus\n"
         "6. Que dit le livre sur useReducer ?          -> RAG livre, p.42 (si livre indexe)\n"
         "\n"
         "Le modele ne lit pas vos documents : Python lit, trie, apporte.\n"
         "Le modele propose, Python decide : notes, horaires, code viennent de fichiers.\n"
         "Un agent qui repond a tout sans source est un moteur a vraisemblance, pas un agent de cours.",
         BLEU, BLEU_CLAIR, 8.8)


# ================================================================== MAIN
def main():
    doc = nouveau_document()
    cp = doc.core_properties
    cp.title = "Conducteur d'atelier — Construire un agent IA pédagogique local"
    cp.subject = "TechWeek Collège LaSalle — 10 étapes, 2 heures, sans clé API"
    cp.author = "Atelier TechWeek — Collège LaSalle"
    cp.keywords = "agent IA, Ollama, RAG, pédagogie, React, TechWeek"
    cp.comments = ("Conducteur de séance. Ne contient aucun code Python : commandes, résultats attendus, "
                   "sens des étapes, objection « n'importe quelle question ».")

    entete_pied(doc, "Conducteur d'atelier · Agent IA pédagogique local",
                "TechWeek · Collège LaSalle · Automne 2026")

    couverture(doc)
    mode_emploi(doc)
    saut_page(doc)
    sommaire(doc)
    chapitre_pitch(doc)
    chapitre_carte(doc)
    chapitre_avant(doc)
    etapes_1_5(doc)
    chapitre_extensions(doc)
    chapitre_objection(doc)
    chapitre_demos(doc)
    chapitre_runbook(doc)
    chapitre_depannage(doc)
    chapitre_annexes(doc)

    doc.save(SORTIE)
    print(f"OK -> {SORTIE}")
    print(f"paragraphes : {len(doc.paragraphs)} | tableaux : {len(doc.tables)}")


if __name__ == "__main__":
    main()




