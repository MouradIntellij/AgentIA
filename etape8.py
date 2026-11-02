"""ETAPE 8 - L'AGENT HYBRIDE : Python decide, le LLM explique, les preuves s'affichent.

Ce script montre, en console, le coeur de app_final.py :
  1. INTENTION  : Python choisit le chemin AVANT d'appeler le LLM
                  (code -> banque | date -> calendrier | matiere -> RAG | hors-sujet -> refus).
  2. RAG        : on ne donne au LLM que les passages utiles de cours/ (pas 24 000 caracteres).
  3. PREUVES    : la liste "Sources consultees" est extraite du texte lu par Python,
                  elle ne sort JAMAIS de l'imagination du modele.
  4. PANNE      : si Ollama est eteint, le script affiche quand meme les passages
                  (mode "preuve sans IA") au lieu de planter.

Lancer :  python etape8.py            -> mode questions (tapez vos questions)
          python etape8.py --demo     -> les 4 demonstrations du guide, sans clavier

Prerequis : Ollama demarre + llama3.2:latest (sinon le mode degrade s'active tout seul).
"""
import sys, re, json, pathlib, unicodedata

try:  # accents corrects dans la console Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:  # index BM25 des PDF volumineux (facultatif : le script marche sans)
    from index_livre import IndexLivre
except ImportError:
    IndexLivre = None

INDEX_LIVRES = []      # rempli par lire_cours() : un index par livre PDF
SEUIL_LIVRE = 20000    # caracteres : au-dela, on indexe au lieu de couper a 6 000

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
BUILD = "etape8 v2 - hybride + RAG + livre indexe + preuves"

# ------------------------------------------------------------------ 1. LIRE LA MATIERE
def lire_docx(path):
    import zipfile
    x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))

def lire_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return "[PDF ignore : pip install pypdf]"
    try:
        txt = "\n".join((p.extract_text() or "") for p in PdfReader(str(path)).pages)
        if len(txt.strip()) < 200:
            return "[PDF scanne image : besoin OCR, ignore.]"
        return txt
    except Exception as e:
        return f"[PDF illisible {e}]"

def lire_cours():
    """Le BRAS : tout ce que l'agent a le droit de savoir est dans cours/.
    Un PDF volumineux est INDEXE (BM25, page par page) au lieu d'etre tronque a 6 000 caracteres."""
    INDEX_LIVRES.clear()
    tout = ""
    for d in sorted(pathlib.Path("cours").rglob("*.docx")):
        try:
            tout += f"\n\n=== SOURCE: {d.name} ===\n" + lire_docx(d)[:6000]
        except Exception as e:
            tout += f"\n[SOURCE {d.name} illisible: {e}]"
    for p in sorted(pathlib.Path("cours").rglob("*.pdf")):
        try:
            txt = lire_pdf(p)
            if IndexLivre and len(txt) > SEUIL_LIVRE:
                index = IndexLivre.charger(p, pathlib.Path("cours") / "cache_index")
                if index.morceaux:
                    INDEX_LIVRES.append(index)
                    tout += (f"\n\n=== SOURCE: {p.name} ===\n[Livre indexe : {index.pages_total} pages, "
                             f"{len(index.morceaux)} morceaux, recherche BM25 par page.]\n")
                    continue
            tout += f"\n\n=== SOURCE: {p.name} ===\n" + txt[:6000]
        except Exception as e:
            tout += f"\n[SOURCE {p.name} illisible: {e}]"
    for t in sorted(pathlib.Path("cours").glob("*.txt")):
        try:
            tout += f"\n\n=== SOURCE: {t.name} ===\n" + t.read_text(encoding="utf-8")[:4000]
        except Exception:
            pass
    return tout[:24000] if tout.strip() else "Aucune source locale."

# ------------------------------------------------------------------ 2. RAG : PASSAGES UTILES
def _passages_texte(question, gros_texte, max_car=3500, repli=True):
    """Note chaque paragraphe : +3 si un mot rare de la question y est, +1 sinon.
    On n'envoie au LLM que les meilleurs paragraphes (le RAG, c'est ce tri)."""
    mots = [w.lower() for w in re.findall(r"[a-zA-Zéèêàç]{4,}", question)]
    STOP = {"cours", "quoi", "quand", "comment", "pourquoi", "dans", "avec",
            "cette", "sont", "plus", "faire", "donne", "explique", "matiere"}
    rares = [m for m in mots if m not in STOP] or mots
    paras = [p.strip() for p in re.split(r"\n+", gros_texte) if len(p.strip()) > 40]
    src, notes = "?", []
    for p in paras:
        if p.startswith("=== SOURCE:"):
            src = p
            continue
        pl = p.lower()
        score = sum(3 if m in pl and len(m) > 6 else 1 for m in rares if m in pl)
        if score:
            notes.append((score, f"[{src}] {p}"))
    notes.sort(key=lambda x: -x[0])
    out, total = [], 0
    for _, p in notes[:40]:
        if total + len(p) > max_car:
            break
        out.append(p)
        total += len(p)
    if out:
        return "\n".join(out)
    return ("\n".join(paras[:12])[:max_car]) if repli else ""

def passages_utiles(question, gros_texte, max_car=3500):
    """Les meilleures pages du livre (si indexe), puis les notes de cours."""
    if not INDEX_LIVRES:
        return _passages_texte(question, gros_texte, max_car)
    budget_livre = 1800 if max_car >= 2400 else max_car // 2
    base = _passages_texte(question, gros_texte, max_car - budget_livre, repli=False)
    livre = "\n\n".join(
        bloc for bloc in (idx.contexte(question, k=8, max_car=budget_livre) for idx in INDEX_LIVRES) if bloc)
    if not base and not livre:
        return _passages_texte(question, gros_texte, max_car)
    if livre:
        livre = "EXTRAITS DU LIVRE INDEXE (la preuve est la page PDF) :\n" + livre
    return "\n\n".join(bloc for bloc in (livre, base) if bloc).strip()

def extraire_sources(ctx):
    """PREUVE Python : les fichiers qui ont REELLEMENT nourri la reponse."""
    srcs = re.findall(r"===\s*SOURCE(?: WEB \(live| WEB \(cache)?\s*:?\s*([^=\]]+)", ctx)
    vus, out = set(), []
    for s in srcs:
        s = s.strip()
        if s and s not in vus:
            vus.add(s)
            out.append(s)
    return out[:8]

def sources_contenant(corpus, extraits):
    """Quels fichiers contiennent vraiment l'extrait cite ? (preuve, pas decoration)"""
    blocs = re.split(r"(?m)^===\s*SOURCE\s*:\s*(.+?)\s*===\s*$", corpus)
    out = []
    for i in range(1, len(blocs), 2):
        nom, contenu = blocs[i].strip(), blocs[i + 1]
        if any(e and e in contenu for e in extraits) and nom not in out:
            out.append(nom)
    return out[:6]

# ------------------------------------------------------------------ 3. PYTHON DECIDE
def sans_accents(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()

def reponse_calendrier(q, corpus):
    """Date / horaire / enseignant : lecture exacte du calendrier, 0 LLM."""
    ql = sans_accents(q)
    if not any(m in ql for m in ["quand", "horaire", "date", "calendrier", "enseignant",
                                 "groupe", "prof", "seance", "hora"]):
        return None
    cc = corpus
    jours = []
    for j in re.findall(r"(?i)(?:lundi|mardi|mercredi|jeudi|vendredi)\s*\d{1,2}\s*h\s*\d{0,2}\s*-?\s*\d{0,2}\s*h?[^\n]*", cc):
        if re.sub(r"\s+", " ", j).strip().lower() not in [re.sub(r"\s+", " ", x).strip().lower() for x in jours]:
            jours.append(j.strip()[:90])
    jours = sorted(jours)
    codes = sorted(set(re.findall(r"420-[A-Z0-9-]+", cc)))
    sems = sorted(set(re.findall(r"(?i)(hiver|automne)\s*(202\d)?", cc)))
    ens = sorted(set(re.findall(r"(?i)enseignant\s*:\s*([A-ZÀ-Þ][\wÀ-þ\-']+(?:\s+[A-ZÀ-Þ][\wÀ-þ\-']+)?)", cc)))
    if not (jours or codes or ens):
        return None
    txt = "D'apres le calendrier :\n"
    if codes:
        txt += "Cours : " + ", ".join(codes) + "\n"
    if sems:
        txt += "Semestre : " + ", ".join(" ".join(s).strip() for s in sems) + "\n"
    if ens:
        txt += "Enseignant : " + ", ".join(ens) + "\n"
    if jours:
        txt += "Horaires : " + " | ".join(jours[:2]) + "\n"
    preuves = jours[:1] + codes[:1] + ens[:1]
    return txt, sources_contenant(corpus, preuves)

def trouver_exemple(question):
    """Code demande explicitement -> banque validee par le prof, 0 LLM.
    'Explique useReducer' n'est PAS une demande de code : ca part en RAG."""
    try:
        from banque_react import EXEMPLES
    except ImportError:
        return None
    ql = question.lower()
    veut = ("code" in ql or "exemple" in ql or "snippet" in ql) and any(
        m in ql for m in ["donne", "donnez", "montre", "montrez", "affiche",
                          "ecris", "exemple", "snippet", "veux", "besoin", "envoie"])
    if not veut:
        return None
    for cle, (titre, code) in EXEMPLES.items():
        if cle in ql or cle.replace("_", " ") in ql:
            return f"Banque (validee par le prof) : {titre}\n{code}", [f"banque_react.py:{cle}"]
    liste = "\n".join(f"- {k} : {v[0]}" for k, v in EXEMPLES.items())
    return f"Precisez le snippet :\n{liste}", ["banque_react.py"]

def garde_hors_matiere(question, corpus):
    """Aucun mot important de la question n'existe dans cours/ -> refus Python, 0 LLM."""
    mots = [w.lower() for w in re.findall(r"[a-zA-Zéèêàç]{5,}", question)]
    STOP = {"quelle", "quels", "quelles", "explique", "expliquer", "donner", "peux",
            "pouvez", "comment", "pourquoi", "matiere", "cours", "selon", "dossier"}
    mots = [m for m in mots if sans_accents(m) not in STOP]
    if not mots:
        return False
    corpus_low = sans_accents(corpus)
    if any(sans_accents(m) in corpus_low for m in mots):
        return False
    # le livre indexe fait partie de la matiere : s'il connait le mot, la question est legitime
    return not any(sans_accents(m) in idx.vocabulaire for m in mots for idx in INDEX_LIVRES)

# ------------------------------------------------------------------ 4. LE LLM EXPLIQUE
def ollama_disponible():
    try:
        import requests
        return requests.get("http://127.0.0.1:11434/api/tags", timeout=3).status_code == 200
    except Exception:
        return False

def demander_llm(question, contexte):
    import requests
    system = ("Tu es agent tuteur React. Reponds UNIQUEMENT d'apres le CONTEXTE. "
              "Le contexte contient des extraits 'SOURCE: ... p.N' : cite le fichier ET la page entre crochets. "
              "Si le contexte ne suffit pas, ecris : Hors-matiere - voir manuel. "
              "N'invente jamais une date ni un horaire.")
    r = requests.post(URL, json={
        "model": MODEL,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": f"CONTEXTE:\n{contexte[:8000]}\n\nQUESTION: {question}"}],
        "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 8192},
    }, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]

# ------------------------------------------------------------------ 5. LE GUICHET
def repondre(question, corpus):
    """Rend un dictionnaire : chemin, texte, sources, llm (nombre d'appels)."""
    ql = sans_accents(question)

    # a) demande de code explicite
    ex = trouver_exemple(question)
    if ex:
        txt, srcs = ex
        return {"chemin": "BANQUE (Python seul)", "txt": txt, "sources": srcs, "llm": 0}

    # b) date / horaire
    cal = reponse_calendrier(question, corpus)
    if cal:
        txt, srcs = cal
        return {"chemin": "CALENDRIER (Python seul)", "txt": txt,
                "sources": srcs or ["calendrier (cours/)"], "llm": 0}

    # c) hors matiere
    if garde_hors_matiere(question, corpus):
        return {"chemin": "GARDE (Python seul)", "llm": 0,
                "txt": "Hors-matiere - voir manuel. Aucun mot de la question n'apparait dans cours/ ni dans le livre indexe.",
                "sources": []}

    # d) RAG : on trie les passages AVANT d'appeler le LLM
    ctx = passages_utiles(question, corpus)
    srcs = extraire_sources(ctx)
    if not ollama_disponible():
        return {"chemin": "RAG sans IA (mode degrade)", "llm": 0, "txt":
                "Ollama ne repond pas : voici les passages que l'agent utiliserait.\n\n" + ctx[:1800],
                "sources": srcs}
    try:
        return {"chemin": "RAG (Python trie, LLM redige)", "llm": 1,
                "txt": demander_llm(question, ctx), "sources": srcs}
    except Exception as e:
        return {"chemin": "RAG sans IA (panne Ollama)", "llm": 0,
                "txt": f"IA indisponible ({e}).\nPassages trouves :\n\n" + ctx[:1500],
                "sources": srcs}

# ------------------------------------------------------------------ 6. AFFICHAGE
def afficher(question, corpus):
    print("\n" + "=" * 72)
    print("QUESTION :", question)
    r = repondre(question, corpus)
    print(f"[outil] lire_cours() / tri Python   |   chemin : {r['chemin']}   |   {r['llm']} appel(s) LLM")
    print("-" * 72)
    print(r["txt"].strip())
    print("-" * 72)
    if r["sources"]:
        print("Sources consultees (preuve Python) :", "  ".join(f"[{s}]" for s in r["sources"]))
    else:
        print("Sources consultees (preuve Python) : aucune")
    print("=" * 72)

DEMOS = [
    "Que dit la matiere sur Tailwind ?",
    "Quand le cours 420-TT4-AS ?",
    "Explique useReducer ?",
    "donne le code usereducer",
    "Quelle est la recette de la tarte aux pommes ?",
]

def main():
    corpus = lire_cours()
    print(BUILD)
    print(f"Matiere chargee : {len(corpus)} caracteres depuis cours/  |  Ollama : {'OK' if ollama_disponible() else 'ABSENT (mode degrade)'}")
    for idx in INDEX_LIVRES:
        print(f"Livre indexe : {idx.nom} ({idx.pages_total} pages) -> {len(idx.morceaux)} morceaux, citations p.X")
    print("Rappel : le LLM ne lit JAMAIS le disque ; c'est Python qui lui apporte les passages.")
    print("Tapez une question, ou 'demo' pour les demonstrations, vide = quitter.")

    demos = list(DEMOS)
    if INDEX_LIVRES:
        demos.append("Que dit le livre sur useReducer et les etats complexes ?")

    if "--demo" in sys.argv:
        for q in demos:
            afficher(q, corpus)
        return

    while True:
        try:
            q = input("\nQuestion React (demo / vide=quitter) : ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        if q.lower() in ("demo", "démo"):
            for d in demos:
                afficher(d, corpus)
            continue
        afficher(q, corpus)

if __name__ == "__main__":
    main()
