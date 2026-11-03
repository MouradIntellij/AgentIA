# -*- coding: utf-8 -*-
"""Genere les diapositives des 10 etapes (charte du PowerPoint de l'atelier).

Entree  : Atelier_Agent_IA_Pedagogique_1.pptx (9 diapos de presentation)
Sortie  : Atelier_Agent_IA_Etapes.pptx (les 9 diapos + 15 diapos de pilotage)

Charte reprise du document : fond 0B1220, titres Georgia 28, accent 22D3EE,
texte F1F5F9, secondaire 94A3B8. Chaque diapo porte ses notes "ce que je dis".
"""
import pathlib
import shutil

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Cm, Pt

RACINE = pathlib.Path(r"C:\LaSalle\Automne2026\TechWeek_Atelier_Agent_IA")
SOURCE = pathlib.Path(r"C:\Users\profm\Downloads\Atelier_Agent_IA_Pedagogique_1.pptx")
SORTIE = RACINE / "Atelier_Agent_IA_Etapes.pptx"

FOND = RGBColor(0x0B, 0x12, 0x20)
CARTE = RGBColor(0x13, 0x1E, 0x31)
TERMINAL = RGBColor(0x07, 0x0E, 0x1B)
BORD = RGBColor(0x23, 0x32, 0x4A)
ENCRE = RGBColor(0xF1, 0xF5, 0xF9)
GRIS = RGBColor(0x94, 0xA3, 0xB8)
CYAN = RGBColor(0x22, 0xD3, 0xEE)
AMBRE = RGBColor(0xFB, 0xBF, 0x24)
VERT = RGBColor(0x34, 0xD3, 0x99)

L = 25.4          # largeur utile
MARGE = 1.27


# ------------------------------------------------------------------ outils
def fond(slide):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = FOND


def zone(slide, x, y, w, h, couleur=CARTE, bord=BORD, radius=0.035, epaisseur=1.0):
    forme = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(x), Cm(y), Cm(w), Cm(h))
    forme.adjustments[0] = radius
    forme.fill.solid()
    forme.fill.fore_color.rgb = couleur
    if bord is None:
        forme.line.fill.background()
    else:
        forme.line.color.rgb = bord
        forme.line.width = Pt(epaisseur)
    forme.shadow.inherit = False
    return forme


def texte(slide, x, y, w, h, lignes, taille=12, couleur=ENCRE, police="Calibri",
          gras=False, italique=False, align=PP_ALIGN.LEFT, ancre=MSO_ANCHOR.TOP,
          interligne=1.05, apres=4, marge=0.0):
    if isinstance(lignes, str):
        lignes = lignes.split("\n")
    boite = slide.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h))
    tf = boite.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Cm(marge)
    tf.margin_top = tf.margin_bottom = Cm(0)
    tf.vertical_anchor = ancre
    for i, ligne in enumerate(lignes):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = interligne
        p.space_after = Pt(apres)
        r = p.add_run()
        r.text = ligne
        r.font.name = police
        r.font.size = Pt(taille)
        r.font.bold = gras
        r.font.italic = italique
        r.font.color.rgb = couleur
    return boite


def etiquette(slide, x, y, w, texte_):
    return texte(slide, x, y, w, 0.6, texte_.upper(), taille=8.5, couleur=GRIS, gras=True)


def pastille(slide, x, y, w, texte_, couleur=CYAN, taille=10):
    forme = zone(slide, x, y, w, 0.72, couleur=couleur, bord=None, radius=0.5)
    tf = forme.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = Cm(0.1)
    tf.margin_top = tf.margin_bottom = Cm(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = texte_
    r.font.name = "Calibri"
    r.font.size = Pt(taille)
    r.font.bold = True
    r.font.color.rgb = FOND
    return forme


def notes(slide, texte_):
    slide.notes_slide.notes_text_frame.text = texte_


def nouvelle(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    fond(slide)
    return slide


# ------------------------------------------------------------------ gabarits
def diapo_etape(prs, n, titre, promesse, cartes, lancer, direct, dire, note):
    """Une diapo de reference : 4 cartes + barre de commande + phrase a dire."""
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 8, 0.6, "ÉTAPE %d SUR 10" % n, taille=9, couleur=CYAN, gras=True)
    texte(slide, L - MARGE - 8, 0.42, 8, 0.6, "Atelier TechWeek · Collège LaSalle",
          taille=9, couleur=GRIS, align=PP_ALIGN.RIGHT)
    texte(slide, MARGE, 0.92, 22.9, 1.25, titre, taille=26, police="Georgia", gras=True)
    texte(slide, MARGE, 2.12, 22.4, 0.95, promesse, taille=14, couleur=CYAN, italique=True)

    positions = [(MARGE, 3.30), (13.05, 3.30), (MARGE, 7.10), (13.05, 7.10)]
    for (x, y), (titre_carte, corps, mono) in zip(positions, cartes):
        zone(slide, x, y, 11.08, 3.55)
        etiquette(slide, x + 0.50, y + 0.38, 10.0, titre_carte)
        texte(slide, x + 0.50, y + 1.00, 10.05, 2.45, corps, taille=11 if not mono else 10.5,
              couleur=ENCRE, police="Consolas" if mono else "Calibri",
              interligne=1.10, apres=5)

    zone(slide, MARGE, 10.95, 22.86, 2.62)
    etiquette(slide, MARGE + 0.50, 11.12, 4, "Lancer")
    texte(slide, MARGE + 0.50, 11.50, 15.6, 0.8, lancer, taille=12.5,
          couleur=ENCRE, police="Consolas")
    pastille(slide, L - MARGE - 5.05, 11.10, 4.55, direct, couleur=CYAN, taille=9)
    etiquette(slide, MARGE + 0.50, 12.28, 4, "À dire")
    texte(slide, MARGE + 0.50, 12.62, 21.7, 0.85, "« %s »" % dire, taille=11.5,
          couleur=ENCRE, italique=True)
    notes(slide, note)
    return slide


# ------------------------------------------------------------------ contenu
ETAPES = [
    dict(
        n=1, titre="1 · Le cerveau seul", fichier="etape1.py",
        promesse="Un modèle local qui parle. Aucune source, aucune mémoire de votre cours.",
        cartes=[
            ("Apport IA",
             "llama3.2 répond en 2 à 8 s, en local, sans clé API ni internet.\n"
             "C'est la brique de base : une question, une réponse, rien d'autre.", False),
            ("Apport pédagogique",
             "On montre la matière première : une réponse fluide, bien écrite… et sans preuve.\n"
             "Le point de départ du raisonnement de tout l'atelier.", False),
            ("Soutien étudiant",
             "Une explication immédiate et un exemple de code, disponible à 23 h,\n"
             "sans connexion et sans compte.", False),
            ("Fonctions utilisées",
             "poser(question)\n"
             "MODEL = \"llama3.2:latest\"   URL = 127.0.0.1:11434/api/chat\n"
             "options : temperature 0.2", True),
        ],
        lancer="python etape1.py",
        direct="EN DIRECT · 8 MIN",
        dire="Il répond en trois secondes. Il n'a lu aucun de vos documents.",
        note=(
            "CE QUE JE DIS (30 s)\n"
            "Voici la brique la plus simple : un fichier de 27 lignes qui envoie votre question à un modèle "
            "qui tourne sur cette machine. Pas de compte, pas de clé, pas de facture. Le modèle s'appelle "
            "llama3.2, il pèse 2 Go, et il répond en français.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance python etape1.py, je tape Entrée pour accepter la question par défaut, et je laisse "
            "la réponse s'afficher. Je ne commente pas le contenu : je commente l'absence de source.\n\n"
            "QUESTION À POSER AUX PARTICIPANTS\n"
            "« Où est le cours de React dans ce programme ? » Réponse attendue : nulle part. Il n'y a "
            "aucun fichier lu, aucun document, aucune preuve.\n\n"
            "SI ÇA CASSE\n"
            "Ollama ne répond pas : lancer l'application Ollama, puis « ollama list ». Modèle absent : "
            "« ollama pull llama3.2:latest ». Erreur de port : vérifier qu'aucun autre python ne tourne."
        ),
    ),
    dict(
        n=2, titre="2 · La matière", fichier="etape2.py",
        promesse="Le même modèle, avec un classeur de 515 caractères.",
        cartes=[
            ("Apport IA",
             "cours/react.txt entre dans le prompt système : le modèle ne répond plus que de ça.\n"
             "Même modèle, même question, autre réponse.", False),
            ("Apport pédagogique",
             "Premier réflexe d'enseignant : fermer le champ. La limite est du code,\n"
             "pas une consigne qu'on espère voir respectée.", False),
            ("Soutien étudiant",
             "Réponse juste sur ce qui a été vu en classe, et refus immédiat hors sujet,\n"
             "sans faire attendre l'étudiant.", False),
            ("Fonctions utilisées",
             "garde_hors_matiere(question)\nposer(question)\nSYSTEM = ... + COURS", True),
        ],
        lancer="python etape2.py",
        direct="EN DIRECT · 10 MIN",
        dire="Demandez useReducer : il refuse. Pas parce qu'il ne sait pas — parce qu'il n'a pas le droit.",
        note=(
            "CE QUE JE DIS\n"
            "Même modèle, même température. La seule différence tient dans un fichier de 515 caractères "
            "glissé dans le prompt. Et une fonction de dix lignes qui refuse la question avant même "
            "d'appeler le modèle.\n\n"
            "CE QUE JE FAIS\n"
            "1) « Que dit le cours sur useState ? » → réponse correcte, courte.\n"
            "2) « Explique useReducer » → refus immédiat, alors que le modèle sait très bien l'expliquer.\n"
            "Je fais constater le refus, puis j'explique : la garde est volontairement bête. Elle protège, "
            "mais elle bloque aussi des questions légitimes. C'est l'étape 8 qui réparera ça, pas un "
            "nouveau prompt.\n\n"
            "PHRASE À RETENIR\n"
            "« Le prompt est de la politesse. Le code, c'est la police. »\n\n"
            "SI ÇA CASSE\n"
            "Refus sur une question légitime ? C'est normal : le cours fait 515 caractères. Le montrer, "
            "c'est déjà la leçon."
        ),
    ),
    dict(
        n=3, titre="3 · Les mains", fichier="etape3.py",
        promesse="Le modèle ne lit pas le disque : il demande, Python exécute.",
        cartes=[
            ("Apport IA",
             "Function calling : le modèle émet un appel d'outil, Python exécute lire_cours()\n"
             "et renvoie le texte. Le modèle n'a jamais accès au fichier.", False),
            ("Apport pédagogique",
             "La séparation des pouvoirs : l'IA propose, le code décide.\n"
             "C'est la thèse de l'atelier, démontrée en une ligne de console.", False),
            ("Soutien étudiant",
             "La réponse vient d'un fichier lu à la demande, avec la ligne [outil] qui dit\n"
             "ce qui s'est réellement passé.", False),
            ("Fonctions utilisées",
             "lire_cours() · OUTIL_LIRE\nchat(messages) · parse_secours(texte)\nrun_agent(question)", True),
        ],
        lancer="python etape3.py",
        direct="EN DIRECT · 12 MIN",
        dire="Regardez la ligne [outil] : c'est Python qui a lu. Le modèle n'a jamais touché au disque.",
        note=(
            "CE QUE JE DIS\n"
            "Jusqu'ici, c'est nous qui lisions le fichier et qui le poussions dans le prompt. Maintenant, "
            "c'est le modèle qui demande la lecture — mais il ne peut pas la faire lui-même : il n'a pas "
            "de mains. Il émet un appel, Python exécute, Python répond.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance etape3.py, je pose une question de cours, et je montre la ligne [outil] lire_cours(). "
            "Je fais remarquer que le fichier n'est PAS dans le prompt de départ : il arrive au milieu "
            "de l'échange.\n\n"
            "LE POINT TECHNIQUE À CITER\n"
            "parse_secours() : le petit modèle écrit parfois l'appel en texte au lieu de tool_calls. "
            "On rattrape avec une expression régulière. C'est du bricolage assumé, et ça se voit.\n\n"
            "PHRASE À RETENIR\n"
            "« Un agent, ce n'est pas un modèle qui sait tout : c'est un modèle qui peut demander. »"
        ),
    ),
    dict(
        n=4, titre="4 · Le visage", fichier="etape4.py",
        promesse="Le même agent, dans un navigateur, sans rien installer côté étudiant.",
        cartes=[
            ("Apport IA",
             "Rien de nouveau côté modèle : un serveur HTTP local et vingt lignes de HTML\n"
             "suffisent à rendre l'agent utilisable.", False),
            ("Apport pédagogique",
             "Zéro installation, zéro cloud, zéro compte : la démonstration passe\n"
             "sur n'importe quel portable de la salle.", False),
            ("Soutien étudiant",
             "Il tape sa question comme dans ChatGPT, mais tout tourne chez lui,\n"
             "et la page répond même wifi coupé.", False),
            ("Fonctions utilisées",
             "HTTPServer(127.0.0.1:3000)\nclasse H : do_GET() / do_POST()\nfetch('/api') · run_agent()", True),
        ],
        lancer="python etape4.py   ->   127.0.0.1:3000",
        direct="EN DIRECT · 8 MIN",
        dire="Coupez le wifi : la page marche encore. Rien ne sort de la machine.",
        note=(
            "CE QUE JE DIS\n"
            "Un agent qu'on ne peut pas montrer n'existe pas. On ajoute donc une page web — locale. "
            "Pas de serveur distant, pas de nom de domaine, pas de certificat.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance etape4.py, j'ouvre 127.0.0.1:3000, je pose une question. Puis je fais le geste "
            "qui marque : je coupe le wifi et je repose la question. Ça répond.\n\n"
            "POURQUOI 127.0.0.1 ET PAS LOCALHOST\n"
            "Sur certaines machines de collège, localhost résout en IPv6 et le serveur écoute en IPv4 : "
            "la page ne s'ouvre pas. 127.0.0.1 ne pose jamais la question.\n\n"
            "SI ÇA CASSE\n"
            "Port 3000 occupé : fermer l'ancien python (ou redémarrer le terminal). Page blanche : "
            "vérifier que le terminal affiche bien « Ouvrez http://127.0.0.1:3000 »."
        ),
    ),
    dict(
        n=5, titre="5 · Le contrôle", fichier="etape5_web.py",
        promesse="La note ne sort pas du modèle.",
        cartes=[
            ("Apport IA",
             "Aucun appel au modèle pour noter : quatre questions écrites par le professeur,\n"
             "deux tirées au hasard, correction par lettres.", False),
            ("Apport pédagogique",
             "L'évaluation reste la propriété de l'enseignant. Le modèle ne corrige pas,\n"
             "il n'attribue pas de note, il n'invente pas de barème.", False),
            ("Soutien étudiant",
             "Score immédiat et bonne réponse affichée à chaque erreur :\n"
             "« 2:B » plutôt qu'un 1/2 sec.", False),
            ("Fonctions utilisées",
             "QUIZ (écrit par le prof)\nrun_quiz() · random.sample()\ncorrige_quiz(reponse) · re.findall()", True),
        ],
        lancer="python etape5_web.py",
        direct="EN DIRECT · 10 MIN",
        dire="Qui a corrigé ? Python. Combien d'appels au modèle ? Zéro.",
        note=(
            "CE QUE JE DIS\n"
            "C'est le moment où l'on met la note hors de portée du modèle. Un quiz noté, ce n'est pas "
            "un texte à générer : c'est une réponse à comparer.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance, je clique Quiz, je réponds volontairement faux à une question pour montrer que "
            "la correction affiche la bonne lettre. Je compte les appels au modèle à voix haute : zéro.\n\n"
            "LA QUESTION QUI FÂCHE, ET LA RÉPONSE\n"
            "« Pourquoi ne pas laisser l'IA générer les questions ? » Parce qu'une question générée peut "
            "être fausse, ambigüe, ou avoir deux bonnes réponses — et personne ne le verra avant l'examen. "
            "L'étape 9 montrera comment on génère des questions en les faisant valider par du code.\n\n"
            "SI ÇA CASSE\n"
            "Le quiz ne se lance pas : le routage cherche « quiz », « qcm » ou « teste » dans la question."
        ),
    ),
    dict(
        n=6, titre="6 · La bibliothèque", fichier="etape6_web.py",
        promesse="Le code vient du professeur, pas du modèle.",
        cartes=[
            ("Apport IA",
             "22 snippets validés dans banque_react.py. Le modèle n'écrit que l'explication\n"
             "des faits constatés par Python.", False),
            ("Apport pédagogique",
             "Un code de cours ne s'invente pas : il se cite. La pastille dit quel snippet\n"
             "a réellement servi.", False),
            ("Soutien étudiant",
             "Il demande « le code useReducer » et reçoit un exemple qui compile,\n"
             "déjà relu par le professeur.", False),
            ("Fonctions utilisées",
             "trouver_exemple(question)\ncorriger_code(code) · subprocess · difflib\nbanque_react.py (22 clés)", True),
        ],
        lancer="python etape6_web.py",
        direct="EN DIRECT · 12 MIN",
        dire="Demandez le code useReducer : la réponse existe avant le modèle. Regardez la pastille.",
        note=(
            "CE QUE JE DIS\n"
            "Un modèle écrit du code plausible. Plausible n'est pas exécutable. Ici, le code ne sort "
            "jamais du modèle : il sort d'une banque de 22 snippets que j'ai relus, et la pastille "
            "affiche la clé utilisée.\n\n"
            "CE QUE JE FAIS\n"
            "1) « donne le code usereducer » → snippet + pastille banque_react.py:usereducer.\n"
            "2) Je colle un code volontairement faux dans « Corriger » : Python l'exécute, constate "
            "l'erreur, et le modèle n'a plus qu'à l'expliquer.\n\n"
            "LA PHRASE\n"
            "« Le modèle propose, Python décide. » Sur le code, c'est vérifiable en direct.\n\n"
            "SI ÇA CASSE\n"
            "Un snippet manquant ? La question bascule sur le RAG documentaire, avec le nom du fichier "
            "en pastille. Rien ne casse, mais la preuve change de nature : le dire à voix haute."
        ),
    ),
    dict(
        n=7, titre="7 · La mémoire documentaire", fichier="etape6_web_doc.py",
        promesse="Vos vrais documents remplacent le petit fichier .txt.",
        cartes=[
            ("Apport IA",
             "DOCX et PDF lus par Python (pypdf), passages triés par mots rares,\n"
             "3 500 caractères envoyés au maximum.", False),
            ("Apport pédagogique",
             "Les dates et horaires viennent d'un fichier officiel : reponse_calendrier()\n"
             "répond sans appeler le modèle.", False),
            ("Soutien étudiant",
             "L'agent connaît SON cours, SON calendrier, SES documents —\n"
             "pas un web générique.", False),
            ("Fonctions utilisées",
             "lire_docx() · lire_pdf()\npassages_utiles(question, texte)\nlire_cours() · reponse_calendrier()", True),
        ],
        lancer="python etape6_web_doc.py",
        direct="EN DIRECT · 10 MIN",
        dire="Le calendrier n'est pas dans le prompt : il est lu à la question. C'est pour ça qu'il est juste.",
        note=(
            "CE QUE JE DIS\n"
            "On remplace le fichier de 515 caractères par les vrais documents du cours : le guide, "
            "le calendrier, les notes. Et on ajoute une fonction qui répond aux dates sans modèle du tout.\n\n"
            "CE QUE JE FAIS\n"
            "1) « Quand le cours 420-TT4-AS ? » → réponse instantanée, pastille du calendrier.\n"
            "2) « Que dit le cours sur useState ? » → réponse + nom du fichier.\n"
            "Je montre que le modèle n'a pas le calendrier dans son prompt : il ne l'a jamais vu.\n\n"
            "LA LIMITE À AVOUER\n"
            "Un PDF scanné est une image : sans OCR, il ne contient pas de texte. Un .doc renommé en "
            ".docx ne s'ouvre pas. Et au-delà de 20 000 caractères, un PDF est indexé page par page "
            "— c'est l'étape 8.\n\n"
            "SI ÇA CASSE\n"
            "Un document n'apparaît jamais : vérifier son extension réelle et sa taille."
        ),
    ),
    dict(
        n=8, titre="8 · Le tri et la preuve", fichier="etape8.py",
        promesse="Cinq questions (six avec le livre), quatre chemins, deux appels au modèle.",
        cartes=[
            ("Apport IA",
             "Python classe la question AVANT d'appeler le modèle : code, date, hors-sujet,\n"
             "documents. Puis il n'envoie que les passages utiles, 3 000 caractères.", False),
            ("Apport pédagogique",
             "Chaque réponse porte la source réellement envoyée : fichier et page.\n"
             "Un agent sans preuve est un moteur à vraisemblance.", False),
            ("Soutien étudiant",
             "Il peut vérifier chaque réponse — ou constater un refus immédiat.\n"
             "Il apprend à demander la preuve, pas à croire la forme.", False),
            ("Fonctions utilisées",
             "repondre() · passages_utiles() · extraire_sources()\n"
             "garde_hors_matiere() · trouver_exemple()\ndemander_llm() · num_ctx 8192", True),
        ],
        lancer="python etape8.py --demo",
        direct="NE PAS SAUTER · 15 MIN",
        dire="Comptez les appels avec moi. Deux sur cinq : le reste, c'est du Python.",
        note=(
            "CE QUE JE DIS\n"
            "On assemble tout. Le modèle ne choisit plus rien : Python regarde la question, décide du "
            "chemin, et n'appelle le modèle que s'il en a besoin. C'est le cœur de app_final.py.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance --demo et je commente les lignes de résultat :\n"
            "1. Tailwind → RAG, pastille du .docx.\n"
            "2. Quand le cours → calendrier, 0 appel.\n"
            "3. Explique useReducer → RAG, réponse tirée du guide.\n"
            "4. Donne le code useReducer → banque, 0 appel.\n"
            "5. Recette de la tarte → garde, refus instantané, 0 appel.\n"
            "6. Si le livre est indexé, la batterie ajoute « Que dit le livre sur Redux et les "
            "reducers ? » → pastille fullstack-react p.565.\n\n"
            "LE MOMENT FORT\n"
            "« Ouvrez le livre à la page 565. » La citation est vraie : ce n'est pas une politesse, "
            "c'est une preuve.\n\n"
            "SI ÇA CASSE\n"
            "Sans livre indexé, la batterie fait cinq questions et deux appels : le dire, ne pas improviser."
        ),
    ),
    dict(
        n=9, titre="9 · La mesure", fichier="etape9_tokens.py · etape9c_eval.py",
        promesse="Pourquoi on ne peut pas tout envoyer au modèle.",
        cartes=[
            ("Apport IA",
             "8 192 tokens ≈ 30 000 caractères. Le corpus en fait 68 000.\n"
             "Un token n'est ni un mot ni un caractère.", False),
            ("Apport pédagogique",
             "On mesure l'outil au lieu de le croire : tokens, sentiment (biais anglais),\n"
             "QCM généré puis validé par du code.", False),
            ("Soutien étudiant",
             "Il comprend la contrainte réelle d'un modèle local — et pourquoi\n"
             "découper n'est pas une option.", False),
            ("Fonctions utilisées",
             "AutoTokenizer.encode() · len(ids)\npipeline('sentiment-analysis')\ngenerer_qcm_ia() + verrou difflib", True),
        ],
        lancer="python etape9_tokens.py   puis   python etape9c_eval.py",
        direct="EN DIRECT · 7 MIN",
        dire="Vos notes ne rentrent pas. Ce n'est pas un bug : c'est la raison d'être du RAG.",
        note=(
            "CE QUE JE DIS\n"
            "Jusqu'ici, on a découpé sans le prouver. On le prouve : un token, ce n'est pas un mot, "
            "et 8 192 tokens, ce n'est pas 8 192 caractères.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance etape9_tokens.py : trois phrases, trois comptes. Je montre que le code React coûte "
            "plus cher que la phrase française à longueur égale.\n"
            "Si le temps le permet, etape9c_eval.py : l'IA écrit un QCM, et le code rejette les leurres "
            "trop proches de la bonne réponse.\n\n"
            "CE QUE JE NE FAIS PAS\n"
            "Le sentiment (etape9b) : le modèle est anglais, le troisième avis en français est faux. "
            "C'est un exemple de biais à citer, pas une démo à lancer.\n\n"
            "SI ON EST EN RETARD\n"
            "Trois minutes : garder seulement les comptes de tokens. C'est la seule diapo dont la "
            "conclusion sert à l'étape 10."
        ),
    ),
    dict(
        n=10, titre="10 · L'ouverture", fichier="etape10_ressources.py",
        promesse="Un livre de 844 pages tient dans l'agent, avec la page citée.",
        cartes=[
            ("Apport IA",
             "Index BM25 : 1 696 morceaux, seuls quatre ou cinq partent au modèle.\n"
             "Le cache JSON rend le démarrage instantané.", False),
            ("Apport pédagogique",
             "Des sources légales et vérifiables : le PDF du professeur, pas un pirate.\n"
             "On cite p.565, pas « le livre ».", False),
            ("Soutien étudiant",
             "Une bibliothèque personnelle interrogeable, plus les sites officiels :\n"
             "react.dev, MDN, Vite, Tailwind.", False),
            ("Fonctions utilisées",
             "texte_ressources()\nIndexLivre · en_cache() · charger()\ncontexte(question, k=8)", True),
        ],
        lancer="python etape10_ressources.py",
        direct="EN DIRECT · 6 MIN",
        dire="Ouvrez le livre à la page 565 : la citation est vraie. C'est ça, une preuve.",
        note=(
            "CE QUE JE DIS\n"
            "On termine par la pièce qui change l'échelle : un livre entier. 844 pages, un million de "
            "caractères, trente fois la fenêtre du modèle. On ne le coupe pas : on l'indexe.\n\n"
            "CE QUE JE FAIS\n"
            "Je lance etape10_ressources.py : la liste des livres présents et des sites. Puis je pose "
            "« Que dit le livre sur Redux et les reducers ? » et j'ouvre le PDF à la page citée.\n\n"
            "LA RÈGLE DE L'ATELIER\n"
            "Aucun PDF pirate. Le livre est une copie légale, et il reste hors du dépôt Git "
            "(.gitignore). Ce que l'on montre, c'est la méthode, pas le fichier.\n\n"
            "L'HONNÊTETÉ SUR CE LIVRE\n"
            "Il est en anglais et date de 2016 : composants à classes, props, state, Redux — pas les "
            "hooks. Pour une démo « le livre explique useEffect », il faut un manuel plus récent."
        ),
    ),
]


# ------------------------------------------------------------------ diapos 1a-1c
def diapo_commandes(prs):
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 14, 0.6, "ÉTAPE 1 · MODE D'EMPLOI", taille=9, couleur=CYAN, gras=True)
    texte(slide, L - MARGE - 8, 0.42, 8, 0.6, "Atelier TechWeek · Collège LaSalle",
          taille=9, couleur=GRIS, align=PP_ALIGN.RIGHT)
    texte(slide, MARGE, 0.92, 22.9, 1.2, "Trois commandes, une question", taille=26,
          police="Georgia", gras=True)
    texte(slide, MARGE, 2.02, 22, 0.8, "Tout se passe dans le dossier mon_agent_react.", taille=14,
          couleur=CYAN, italique=True)

    zone(slide, MARGE, 2.95, 14.6, 8.0, couleur=TERMINAL)
    etiquette(slide, MARGE + 0.55, 3.15, 6, "Terminal")
    texte(slide, MARGE + 0.55, 3.62, 13.6, 7.0, [
        "ollama pull llama3.2:latest    # une fois, ~2 Go",
        "ollama list                    # le modele est pret",
        "",
        "python etape1.py",
        "Question React [defaut: Explique useState...] :",
        "                               # Entree = question par defaut",
        "--- reponse ---",
        "useState est une fonction de hook qui permet de",
        "stocker et recuperer un etat dans un composant.",
    ], taille=11.5, police="Consolas", interligne=1.22, apres=0)

    zone(slide, 16.35, 2.95, 7.78, 8.0)
    etiquette(slide, 16.85, 3.15, 7, "Ce que la console affiche")
    texte(slide, 16.85, 3.65, 6.9, 4.6, [
        "Une réponse en français,",
        "un exemple de code JSX,",
        "puis le curseur revient.",
        "",
        "Aucune ligne ne dit d'où vient",
        "la réponse : c'est le problème.",
    ], taille=11.5, interligne=1.2, apres=5)
    pastille(slide, 16.85, 8.55, 2.55, "2 À 8 S", couleur=CYAN, taille=10)
    pastille(slide, 19.55, 8.55, 4.10, "0 CLÉ API", couleur=VERT, taille=10)
    texte(slide, 16.85, 9.55, 6.9, 1.3,
          "Premier appel : chargement du modèle.\nEnsuite : 2 à 4 s par question.",
          taille=10, couleur=GRIS, interligne=1.15, apres=2)

    zone(slide, MARGE, 11.2, 22.86, 2.35)
    etiquette(slide, MARGE + 0.5, 11.38, 12, "À dire pendant que ça tourne")
    texte(slide, MARGE + 0.5, 11.75, 21.6, 1.6,
          "« Deux commandes, un fichier de 27 lignes, et votre premier agent répond.\n"
          "Copiez tel quel : on ne code rien pour l'instant, on constate. »",
          taille=12, italique=True, interligne=1.2, apres=4)
    notes(slide,
          "CE QUE J'AFFICHE\n"
          "Cette diapo reste à l'écran pendant que les participants tapent. Elle contient les seules "
          "commandes nécessaires, la question par défaut, et un extrait de la sortie réelle.\n\n"
          "CE QUE JE DIS\n"
          "« Deux commandes. La première télécharge le modèle, une fois pour toutes, deux gigaoctets. "
          "La seconde vérifie qu'il est là. Ensuite, python etape1.py, et vous tapez Entrée. »\n\n"
          "LE DÉTAIL QUI RASSURE\n"
          "Si un étudiant n'a pas le modèle, la réponse est un message d'erreur clair, pas un écran "
          "blanc. C'est déjà une qualité d'ingénierie : échouer proprement.\n\n"
          "LE PIÈGE À ÉVITER\n"
          "Ne pas laisser tout le monde lancer en même temps sur une seule machine : le premier appel "
          "charge le modèle (3 à 8 s), les suivants sont rapides. Faire lancer par deux ou trois "
          "volontaires, les autres regardent.")


def diapo_piege(prs):
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 14, 0.6, "ÉTAPE 1 · LE PIÈGE", taille=9, couleur=CYAN, gras=True)
    texte(slide, L - MARGE - 8, 0.42, 8, 0.6, "Atelier TechWeek · Collège LaSalle",
          taille=9, couleur=GRIS, align=PP_ALIGN.RIGHT)
    texte(slide, MARGE, 0.92, 22.9, 1.2, "Convaincant n'est pas vrai", taille=26,
          police="Georgia", gras=True)
    texte(slide, MARGE, 2.02, 22.4, 0.75,
          "La réponse la plus convaincante de la séance est souvent la plus fausse.",
          taille=13, couleur=CYAN, italique=True)

    zone(slide, MARGE, 2.95, 22.86, 2.20, couleur=RGBColor(0x1A, 0x16, 0x22), bord=RGBColor(0x4A, 0x2F, 0x1A))
    etiquette(slide, MARGE + 0.55, 3.10, 8, "Question posée au modèle")
    texte(slide, MARGE + 0.55, 3.48, 21.6, 1.4,
          "« Quelle est la date de l'examen du cours 420-TT4-AS ? »",
          taille=16, couleur=AMBRE, italique=False)

    zone(slide, MARGE, 5.40, 13.4, 4.80)
    etiquette(slide, MARGE + 0.5, 5.58, 8, "Ce qu'il répond (extrait réel)")
    texte(slide, MARGE + 0.5, 5.98, 12.4, 3.95, [
        "« Je ne suis pas en mesure de fournir",
        "  l'information sur la date de l'examen…",
        "  Cependant, voici un exemple de code",
        "  JavaScript qui pourrait vous aider… »",
        "",
        "+ trois conseils : le site du collège,",
        "le professeur, votre agenda.",
    ], taille=10.5, police="Calibri", interligne=1.2, apres=0, couleur=ENCRE)

    zone(slide, 15.15, 5.40, 8.98, 4.80)
    etiquette(slide, 15.65, 5.58, 8, "Ce que ça prouve")
    texte(slide, 15.65, 5.98, 8.0, 3.95, [
        "Aucun fichier n'a été lu :",
        "il ne pouvait pas savoir.",
        "",
        "Il ne dit pas « je ne sais pas » :",
        "il meuble, et propose du code",
        "hors sujet.",
        "Rien ne prouve rien.",
    ], taille=10.5, interligne=1.18, apres=0)

    zone(slide, MARGE, 10.50, 22.86, 2.85, couleur=RGBColor(0x07, 0x1B, 0x20), bord=CYAN)
    etiquette(slide, MARGE + 0.55, 10.66, 12, "La phrase à dire, puis à répéter à chaque étape")
    texte(slide, MARGE + 0.55, 11.05, 21.6, 1.9, [
        "« Le modèle ne sait pas ce qu'il ne sait pas.",
        "  C'est à Python de le lui interdire — et à nous de le prouver. »",
    ], taille=14.5, couleur=CYAN, italique=True, interligne=1.28, apres=0)

    texte(slide, MARGE, 13.62, 22.86, 0.5,
          "Neuf étapes, deux heures : c'est exactement ce que l'on va construire.",
          taille=10, couleur=GRIS)

    notes(slide,
          "CE QUE JE FAIS (60 s, le moment le plus important de l'étape 1)\n"
          "Je pose la question sur la date d'examen. Je laisse la réponse s'afficher en entier, sans "
          "commenter. Puis je demande : « Qui peut me dire où il a trouvé cette date ? »\n"
          "Silence. Puis : « Il ne l'a pas trouvée. Il ne pouvait pas. Et pourtant, la réponse est "
          "polie, structurée, et elle propose même du code. »\n\n"
          "CE QUE JE MONTRE ENSUITE\n"
          "Je pose « Quel est l'horaire du cours 420-TT4-AS ? » : même mécanisme, même aplomb, autre "
          "réponse inventée. Deux fois, ce n'est plus un accident.\n\n"
          "LA TRANSITION (à dire mot pour mot)\n"
          "« Voilà le problème que l'atelier résout. Pas en changeant de modèle : en changeant ce qu'on "
          "met autour du modèle. Neuf étapes, et à la fin, la même question donnera une réponse refusée "
          "instantanément, sans appel au modèle. »\n\n"
          "NE PAS FAIRE\n"
          "Ne pas humilier le modèle, ne pas dire « l'IA est nulle ». Le modèle fait exactement ce qu'on "
          "lui demande : produire du texte plausible. Le défaut est dans le montage, pas dans le modèle.")


def diapo_priorites(prs):
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 14, 0.6, "PILOTAGE", taille=9, couleur=CYAN, gras=True)
    texte(slide, L - MARGE - 8, 0.42, 8, 0.6, "Atelier TechWeek · Collège LaSalle",
          taille=9, couleur=GRIS, align=PP_ALIGN.RIGHT)
    texte(slide, MARGE, 0.92, 22.9, 1.2, "Ce que je lance, et ce que je coupe", taille=26,
          police="Georgia", gras=True)
    texte(slide, MARGE, 2.02, 22, 0.8,
          "Trois niveaux de priorité — dans cet ordre, jamais autrement.", taille=14,
          couleur=CYAN, italique=True)

    blocs = [
        ("BLOQUANT", "jamais sauter · 35 min", CYAN, [
            ("1", "Le cerveau seul", "8 min"),
            ("3", "Les mains", "12 min"),
            ("8", "Le tri et la preuve", "15 min"),
        ], "Sans ces trois-là, l'atelier n'a pas de démonstration."),
        ("CŒUR", "à garder si possible · 46 min", GRIS, [
            ("2", "La matière", "10 min"),
            ("4", "Le visage", "8 min"),
            ("6", "La bibliothèque", "12 min"),
            ("7", "La mémoire documentaire", "10 min"),
            ("10", "L'ouverture", "6 min"),
        ], "Ce sont les preuves que le public peut vérifier."),
        ("VARIABLE", "5 à 7 min chacun · 17 min", RGBColor(0x64, 0x74, 0x8B), [
            ("5", "Le contrôle", "10 min"),
            ("9", "La mesure", "7 min"),
        ], "Utiles, mais remplaçables par une phrase."),
    ]
    for i, (titre_bloc, sous, couleur, lignes, pied) in enumerate(blocs):
        x = MARGE + i * 7.78
        zone(slide, x, 3.05, 7.30, 7.55, bord=couleur)
        texte(slide, x + 0.5, 3.28, 6.3, 0.5, titre_bloc, taille=11, couleur=couleur, gras=True)
        texte(slide, x + 0.5, 3.72, 6.3, 0.5, sous, taille=9, couleur=GRIS)
        for j, (num, nom, duree) in enumerate(lignes):
            y = 4.45 + j * 1.25
            texte(slide, x + 0.5, y, 0.8, 0.6, num, taille=12, couleur=couleur, police="Consolas", gras=True)
            texte(slide, x + 1.25, y - 0.05, 4.5, 0.6, nom, taille=11)
            texte(slide, x + 5.75, y - 0.05, 1.2, 0.6, duree, taille=9.5, couleur=GRIS, align=PP_ALIGN.RIGHT)
        texte(slide, x + 0.5, 9.55, 6.3, 0.9, pied, taille=9, couleur=GRIS, interligne=1.15)

    zone(slide, MARGE, 10.85, 22.86, 1.75)
    texte(slide, MARGE + 0.5, 11.02, 21.8, 1.4, [
        "98 min de démonstrations + 10 min d'introduction + 12 min de questions = 2 h.",
        "En retard de 15 min : fusionner l'étape 2 dans la 3, et réduire l'étape 9 à 3 min (tokens seulement).",
    ], taille=10.5, interligne=1.2, apres=3)
    notes(slide,
          "CE QUE J'AFFICHE (30 s, juste avant de commencer)\n"
          "« Voici l'ordre de coupe, décidé à froid, pas au moment du stress. »\n\n"
          "CE QUE JE DIS\n"
          "Les trois étapes bloquantes sont 1, 3 et 8. Si je dois couper, je coupe 5 et 9 — jamais 8. "
          "L'étape 8 est la seule qui montre les quatre chemins et les preuves en même temps : sans "
          "elle, l'atelier est une suite de fonctionnalités, pas une démonstration.\n\n"
          "RÈGLE DE SALLE\n"
          "Toujours annoncer la durée avant de lancer une démo. « Douze minutes, deux questions, une "
          "seule commande. » Cela évite les interruptions et les questions de détail qui cassent le "
          "rythme.\n\n"
          "SI UNE DÉMO ÉCHOUE\n"
          "Ne pas déboguer en direct plus de 60 s. Dire : « je garde ça pour la fin », ouvrir "
          "app_final.py qui contient la même logique, et continuer.")


def diapo_apps(prs):
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 14, 0.6, "APRÈS LES DIX ÉTAPES", taille=9, couleur=CYAN, gras=True)
    texte(slide, L - MARGE - 8, 0.42, 8, 0.6, "Atelier TechWeek · Collège LaSalle",
          taille=9, couleur=GRIS, align=PP_ALIGN.RIGHT)
    texte(slide, MARGE, 0.92, 22.9, 1.2, "La version spectacle", taille=26,
          police="Georgia", gras=True)
    texte(slide, MARGE, 2.02, 22, 0.8,
          "Ce qu'on ajoute après les dix étapes — et ce que ça coûte.",
          taille=13, couleur=CYAN, italique=True)

    cartes = [
        ("app_rag_pro.py", "Recherche sémantique",
         "SentenceTransformer (all-MiniLM-L6-v2) : similarité cosinus au lieu de mots-clés.", GRIS),
        ("app_ia_final.py", "+ OCR et voix",
         "easyocr lit une photo de code ; le navigateur lit et prononce la réponse.", GRIS),
        ("app_ultimate_ia_*.py", "+ mémoire et contrôle",
         "Historique par étudiant, mode Socrate, RAG PRO, quiz, journal des échanges.", GRIS),
        ("app_ultimate_ia_production.py", "+ enseignant",
         "Login, logs_pedagogie.json, tableau de bord /admin, langue détectée.", CYAN),
    ]
    for i, (fichier, titre_carte, corps, couleur) in enumerate(cartes):
        x = MARGE + i * 5.85
        zone(slide, x, 2.95, 5.45, 5.45, bord=couleur)
        texte(slide, x + 0.42, 3.15, 4.75, 0.55, fichier, taille=7.5, couleur=couleur,
              police="Consolas", gras=True)
        texte(slide, x + 0.42, 3.68, 4.6, 0.7, titre_carte, taille=12.5, gras=True)
        texte(slide, x + 0.42, 4.40, 4.65, 3.7, corps, taille=9.5, couleur=ENCRE, interligne=1.2)
        if i < 3:
            texte(slide, x + 5.02, 5.15, 0.8, 1.1, "›", taille=22, couleur=GRIS, gras=True)

    zone(slide, MARGE, 8.70, 11.08, 3.15, bord=AMBRE)
    etiquette(slide, MARGE + 0.5, 8.88, 10, "Ce que ça coûte")
    texte(slide, MARGE + 0.5, 9.30, 10.1, 2.5, [
        "torch + sentence-transformers + easyocr ≈ 2 Go,",
        "et un premier lancement qui télécharge des modèles.",
        "Sur un portable de salle, c'est un pari.",
    ], taille=10.5, interligne=1.25, apres=4)

    zone(slide, 13.05, 8.70, 11.08, 3.15, bord=VERT)
    etiquette(slide, 13.55, 8.88, 10, "Comment je le montre")
    texte(slide, 13.55, 9.30, 10.1, 2.5, [
        "Trois minutes, en fin de séance : le code à l'écran,",
        "une capture du tableau de bord /admin,",
        "et une phrase : « tout ceci est le même agent, avec plus de briques ».",
    ], taille=10.5, interligne=1.25, apres=4)

    texte(slide, MARGE, 12.15, 22.86, 1.4,
          "Aujourd'hui, easyocr n'est pas installé sur la machine : le mode image est désactivé, le reste tourne "
          "(le code le dit au démarrage). Ne pas promettre l'OCR sans l'avoir testé.",
          taille=9.5, couleur=GRIS, interligne=1.2)
    notes(slide,
          "CE QUE JE DIS\n"
          "« Tout ce que vous venez de voir tient en trois cents lignes. Les versions ultimate ajoutent "
          "des briques : recherche sémantique, OCR, voix, mémoire par étudiant, journal, tableau de bord. "
          "Le principe ne change pas : le modèle propose, Python décide. »\n\n"
          "CE QUE JE MONTRE\n"
          "Le code de app_ultimate_ia_production.py à l'écran, trois fonctions : charger_base_connaissance(), "
          "recherche_semantique(), save_log(). Puis /admin avec deux lignes de journal.\n\n"
          "CE QUE JE NE FAIS PAS\n"
          "Je ne lance pas ces versions en direct : torch, easyocr et le téléchargement des modèles "
          "prennent plus de temps que la démo elle-même. Et un échec de dépendance en fin de séance "
          "efface deux heures de travail.\n\n"
          "SI ON ME DEMANDE « pourquoi pas ça dès le début ? »\n"
          "Parce que l'atelier n'apprend pas à installer des bibliothèques : il apprend où mettre la "
          "preuve, la note et la garde. Ces briques s'ajoutent après, sans changer la thèse."
          )


def diapo_fin(prs):
    slide = nouvelle(prs)
    texte(slide, MARGE, 0.42, 14, 0.6, "CE QUI RESTE", taille=9, couleur=CYAN, gras=True)
    texte(slide, MARGE, 1.35, 22.86, 3.2,
          "« Le modèle propose. Python décide.\nL'enseignant garde la parole. »",
          taille=28, police="Georgia", gras=True, interligne=1.28, apres=0)
    texte(slide, MARGE, 4.75, 22.86, 0.6,
          "Trois idées à emporter, dans l'ordre où elles se démontrent.", taille=13,
          couleur=CYAN, italique=True)

    lignes = [
        ("01", "Pas de source, pas de réponse.",
         "Chaque affirmation porte un fichier et, s'il y en a un, un numéro de page."),
        ("02", "Pas de fichier, pas de note.",
         "Le quiz, le code et les dates viennent de vos documents, jamais du modèle."),
        ("03", "Pas de preuve, pas de confiance.",
         "L'étudiant peut vérifier — c'est ce qui distingue un tuteur d'un moteur à vraisemblance."),
    ]
    for i, (num, titre_ligne, corps) in enumerate(lignes):
        y = 5.70 + i * 2.30
        texte(slide, MARGE, y, 1.6, 0.9, num, taille=16, couleur=CYAN, police="Consolas", gras=True)
        texte(slide, MARGE + 1.6, y - 0.08, 21.0, 0.8, titre_ligne, taille=15, gras=True)
        texte(slide, MARGE + 1.6, y + 0.62, 20.8, 1.0, corps, taille=11, couleur=GRIS, interligne=1.2)

    texte(slide, MARGE, 12.85, 22.86, 0.9,
          "Dépôt : github.com/MouradIntellij/AgentIA  ·  dossier mon_agent_react  ·  aucun PDF dans le dépôt.",
          taille=9.5, couleur=GRIS)
    notes(slide,
          "CE QUE JE DIS POUR FINIR (90 s)\n"
          "« Vous avez vu dix étapes. Aucune ne consiste à mieux parler au modèle. Toutes consistent à "
          "mettre du code autour de lui : pour lire, pour trier, pour refuser, pour prouver. »\n\n"
          "LA PHRASE DE CLÔTURE\n"
          "« Un agent qui répond à tout sans source n'est pas un professeur : c'est un moteur à "
          "vraisemblance. Ce que nous avons construit ce soir, c'est la différence. »\n\n"
          "CE QUE JE DONNE À LA SORTIE\n"
          "Le dossier mon_agent_react, le livre de l'atelier (conducteur 33 pages), et les commandes "
          "pour relancer chez soi : ollama pull, python app_final.py, 127.0.0.1:3000.\n\n"
          "LA DERNIÈRE CHOSE À DIRE\n"
          "« Rien de ce que vous avez vu n'a besoin d'internet, d'un compte ou d'une clé API. C'est le "
          "seul argument qui compte dans un collège. »")


# ------------------------------------------------------------------ montage
def main():
    if not SORTIE.exists() or SORTIE.stat().st_mtime < SOURCE.stat().st_mtime:
        shutil.copyfile(SOURCE, SORTIE)
    prs = Presentation(SORTIE)
    # on repart toujours des 9 diapos d'origine
    while len(prs.slides) > 9:
        rid = prs.slides._sldIdLst[-1].rId
        prs.part.drop_rel(rid)
        del prs.slides._sldIdLst[-1]

    diapo_etape(prs, **{k: v for k, v in ETAPES[0].items() if k != "fichier"})
    diapo_commandes(prs)
    diapo_piege(prs)
    for e in ETAPES[1:]:
        diapo_etape(prs, **{k: v for k, v in e.items() if k != "fichier"})
    diapo_priorites(prs)
    diapo_apps(prs)
    diapo_fin(prs)

    prs.save(SORTIE)
    print("OK ->", SORTIE)
    print("diapos :", len(prs.slides))


if __name__ == "__main__":
    main()
