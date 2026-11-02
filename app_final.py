"""APP FINALE TechWeek - LLM + Python + RAG sur une interface style Claude (CSS local, zero CDN).
Modes : Cours (RAG docx/pdf) | Quiz | Banque codes | Corriger code (hybride) | Eval comprehension (hybride).
Lancer : python app_final.py  ->  http://127.0.0.1:3000 (fonctionne sans internet)."""
import pathlib, re, random, json, ast, difflib, builtins, sys, os, requests, subprocess, unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

def RACINE():
    # .exe PyInstaller : donnees dans _MEIPASS ; .py : dossier courant
    if getattr(sys, "frozen", False):
        return pathlib.Path(sys._MEIPASS)
    return pathlib.Path(".")

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
CLE_ACCES = os.environ.get("CLE_ACCES", "").strip()  # vide = ouvert (local) ; sinon ?k=... exigee
SYSTEM = ("Tu es agent tuteur. Tu reponds UNIQUEMENT d'apres le CONTEXTE renvoye par l'outil lire_cours. "
          "Le contexte contient des extraits 'SOURCE: ... p.N' : termine ta reponse par une ligne "
          "'Sources : [fichier p.N, ...]' avec uniquement les pages que tu as utilisees. "
          "Ne recopie jamais les entetes '=== SOURCE' ni le texte du contexte. "
          "Si la reponse n'est pas dans le contexte, ecris exactement : Hors-matiere. "
          "N'invente jamais une date, un horaire, un chapitre ni un exemple absent des sources. "
          "Si date/horaire : donne la date exacte du calendrier.")
OUTIL = [
    {"type": "function", "function": {"name": "lire_cours", "description": "Lit les docs de cours/", "parameters": {"type": "object", "properties": {}, "required": []}}},
    {"type": "function", "function": {"name": "corriger_code", "description": "Corrige le code colle", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}}},
]

# ---------- INDEX DU LIVRE (un PDF volumineux est indexe, pas tronque) ----------
try:
    import index_livre
    from index_livre import IndexLivre, mots as mots_index
except ImportError:  # l'agent reste utilisable sans le module : on retombe sur la troncature
    index_livre = None
    IndexLivre = None
    mots_index = None
INDEX_LIVRES = []        # rempli par lire_cours() : un index BM25 par PDF volumineux
SEUIL_LIVRE = 20000      # caracteres : au-dela, on indexe au lieu de couper a 6 000
_CACHE_COURS = {"sig": None, "txt": None, "vocab": None}

def _signature_cours():
    """Empreinte des fichiers de cours/ : si un document change, on recharge tout seul."""
    racine = RACINE() / "cours"
    if not racine.exists(): return ()
    return tuple(sorted(
        (str(p), p.stat().st_size, int(p.stat().st_mtime))
        for p in racine.rglob("*")
        if p.is_file() and "cache_index" not in str(p)))

# ---------- LECTURE DOCS ----------
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
        txt = "\n".join([(p.extract_text() or "") for p in PdfReader(str(path)).pages])
        if len(txt.strip()) < 200:
            return "[PDF scanne image : besoin OCR, ignore.]"
        return txt
    except Exception as e:
        return f"[PDF illisible {e}]"

def _bloc_livre(index, nom_pdf):
    """Ce que le modele voit du livre : un resume, pas 844 pages. Les pages viennent a la question."""
    INDEX_LIVRES.append(index)
    return (f"\n\n=== SOURCE: {nom_pdf} ===\n"
            f"[Livre indexe : {index.pages_total} pages, {len(index.morceaux)} morceaux. "
            f"Recherche BM25 page par page ; seuls les meilleurs morceaux sont envoyes.]\n")

def lire_cours():
    """Tout ce que l'agent a le droit de savoir. Les gros PDF sont indexes, pas tronques."""
    signature = _signature_cours()
    if _CACHE_COURS["sig"] == signature and _CACHE_COURS["txt"] is not None:
        return _CACHE_COURS["txt"]
    INDEX_LIVRES.clear()
    tout = ""
    for d in sorted((RACINE() / "cours").rglob("*.docx")):
        try: tout += f"\n\n=== SOURCE: {d.name} ===\n" + lire_docx(d)[:60000]
        except Exception as e: tout += f"\n[SOURCE {d.name} illisible: {e}]"
    cache = RACINE() / "cours" / "cache_index"
    for p in sorted((RACINE() / "cours").rglob("*.pdf")):
        try:
            # Livre deja indexe : on relit le cache (0,2 s) au lieu d'extraire 844 pages a chaque demarrage.
            if IndexLivre and index_livre.en_cache(p, cache):
                index = IndexLivre.charger(p, cache)
                if index.morceaux:
                    tout += _bloc_livre(index, p.name)
                    continue
            pages = index_livre.extraire_pdf(p) if IndexLivre else None
            txt = "\n".join(t for _, t in pages) if pages is not None else lire_pdf(p)
            if pages is not None and len(txt.strip()) < 200:
                txt = "[PDF scanne image : besoin OCR, ignore.]"
            if IndexLivre and len(txt) > SEUIL_LIVRE:
                index = IndexLivre.charger(p, cache, pages=pages)
                if index.morceaux:
                    tout += _bloc_livre(index, p.name)
                    continue
            tout += f"\n\n=== SOURCE: {p.name} ===\n" + txt[:6000]
        except Exception as e: tout += f"\n[SOURCE {p.name} illisible: {e}]"
    for t in sorted((RACINE() / "cours").glob("*.txt")) + sorted((RACINE() / "cours").glob("web_*.txt")):
        try: tout += f"\n\n=== SOURCE: {t.name} ===\n" + t.read_text(encoding="utf-8")[:4000]
        except Exception: pass
    resultat = tout[:120000] if tout.strip() else "Aucune source locale."
    _CACHE_COURS.update(sig=signature, txt=resultat, vocab=None)
    return resultat

WEB_SITES = {
    "react.dev": "https://react.dev/reference/react",
    "mdn": "https://developer.mozilla.org/fr/docs/Web/JavaScript",
    "javascript.info": "https://javascript.info",
    "vite": "https://vite.dev/guide/",
    "tailwind": "https://tailwindcss.com/docs",
}
def lire_page(url, max_car=4000):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "TechWeek-Atelier/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8", "ignore")
    txt = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", txt)
    return re.sub(r"\s+", " ", txt)[:max_car]

def enrichir_web(question, deja):
    # wifi : 1 seul fetch ciblé, mis en cache pour le offline
    ql = question.lower()
    url = next((u for k, u in WEB_SITES.items() if k in ql), None)
    if not url and not deja.strip(): url = WEB_SITES["react.dev"]
    if not url: return ""
    try:
        cache = RACINE() / "cours" / "cache_web"; cache.mkdir(parents=True, exist_ok=True)
        nom = re.sub(r"\W+", "_", url)[:40] + ".txt"
        fp = cache / nom
        if fp.exists(): return f"\n\n=== SOURCE WEB (cache): {url} ===\n" + fp.read_text(encoding="utf-8")[:4000]
        txt = lire_page(url)
        fp.write_text(txt, encoding="utf-8")
        return f"\n\n=== SOURCE WEB (live): {url} ===\n" + txt
    except Exception as e:
        return f"\n[SOURCE WEB {url} inaccessible: {e}]"

def _passages_notes(question, gros_texte, max_car=3500, repli=True):
    mots = [w.lower() for w in re.findall(r"[a-zA-Zéèêàç]{4,}", question)]
    STOP = {"cours", "quoi", "quand", "comment", "pourquoi", "dans", "avec", "cette", "sont", "plus", "faire", "donne"}
    rares = [m for m in mots if m not in STOP] or mots
    paras = [p.strip() for p in re.split(r"\n+", gros_texte) if len(p.strip()) > 40]
    src, notes = "?", []
    for p in paras:
        if p.startswith("=== SOURCE:"): src = p; continue
        pl = p.lower()
        score = sum(3 if m in pl and len(m) > 6 else 1 for m in rares if m in pl)
        if score: notes.append((score, f"[{src}] {p}"))
    notes.sort(key=lambda x: -x[0])
    out, total = [], 0
    for _, p in notes[:40]:
        if total + len(p) > max_car: break
        out.append(p); total += len(p)
    if out: return "\n".join(out)
    return ("\n".join(paras[:12])[:max_car]) if repli else ""

def passages_utiles(question, gros_texte, max_car=3500):
    """Les meilleures pages du livre (si indexe), puis les notes de cours."""
    if not INDEX_LIVRES:
        return _passages_notes(question, gros_texte, max_car)
    budget_livre = 1800 if max_car >= 2400 else max_car // 2
    base = _passages_notes(question, gros_texte, max_car - budget_livre, repli=False)
    part = max(700, budget_livre // max(1, len(INDEX_LIVRES)))   # plusieurs livres : on partage le budget
    livre = "\n\n".join(
        bloc for bloc in (idx.contexte(question, k=8, max_car=part) for idx in INDEX_LIVRES) if bloc)
    if not base and not livre:
        return _passages_notes(question, gros_texte, max_car)
    if livre:
        livre = "EXTRAITS DU LIVRE INDEXE (la preuve est la page PDF) :\n" + livre
    return "\n\n".join(bloc for bloc in (livre, base) if bloc).strip()

def extraire_sources(ctx):
    """Preuve Python (pas LLM) : quelles SOURCES ont nourri la reponse."""
    srcs = re.findall(r"===\s*SOURCE(?: WEB \(live| WEB \(cache)?\s*:?\s*([^=\]]+)", ctx)
    vus, out = set(), []
    for s in srcs:
        s = s.strip()
        if s and s not in vus: vus.add(s); out.append(s)
    return out[:8]

def reponse_calendrier(q, cc):
    ql = q.lower()
    if not any(m in ql for m in ["quand", "horaire", "date", "calendrier", "enseignant", "groupe", "prof", "séance", "seance", "hora"]):
        return None
    jours = sorted(set(re.findall(r"(?i)(?:lundi|mardi|mercredi|jeudi|vendredi)\s*\d{2}h\s*-\s*\d{2}h[^\n]*", cc)))
    codes = sorted(set(re.findall(r"420-[A-Z0-9-]+", cc)))
    sems = sorted(set(re.findall(r"(?i)(hiver|automne)\s*(202\d)?", cc)))
    ens = sorted(set(re.findall(r"(?i)enseignant\s*:\s*([A-ZÀ-Þ][\wÀ-þ\-']+(?:\s+[A-ZÀ-Þ][\wÀ-þ\-']+)?)", cc)))
    if not (jours or codes or ens): return None
    txt = "[outil] lire_cours() [calendrier Python, 0 LLM]\nD'apres le calendrier :\n"
    if codes: txt += "Cours : " + ", ".join(codes) + "\n"
    if sems: txt += "Semestre : " + ", ".join([" ".join(s).strip() for s in sems]) + "\n"
    if ens: txt += "Enseignant : " + ", ".join(ens) + "\n"
    if jours: txt += "Horaires : " + " | ".join([j.strip() for j in jours]) + "\n"
    return {"type": "cours", "txt": txt, "sources": extraire_sources(cc)[:6] or ["calendrier (cours/)"]}

# ---------- BANQUE CODES (fichier externe, 1 entree = 1 snippet) ----------
try:
    from banque_react import EXEMPLES
except ImportError:
    EXEMPLES = {"usestate": ("Compteur", "const [count, setCount] = useState(0);")}
try:
    import etape10_ressources as RESS
except ImportError:
    RESS = None
def trouver_exemple(question):
    # INTENTION D'ABORD : definition/matiere/cours -> RAG, pas la banque.
    # Seul un mot code/exemple/snippet declenche un snippet.
    # INTENTION : "donne/montre... le code X" -> banque. Parler DU code -> RAG.
    ql = question.lower()
    veut = ("code" in ql or "exemple" in ql or "snippet" in ql) and any(
        m in ql for m in ["donne", "donnez", "montre", "montrez", "affiche", "ecris", "exemple", "snippet", "veux", "besoin", "envoie"])
    if not veut:
        return None
    for cle, (titre, code) in EXEMPLES.items():
        if cle in ql or cle.replace("_", " ") in ql:
            return {"type": "cours", "txt": f"[outil] banque_exemples() -> {titre}\n{code}", "sources": [f"banque_react.py:{cle}"]}
    liste = "\n".join([f"- {k} : {v[0]}" for k, v in EXEMPLES.items()])
    return {"type": "cours", "txt": f"[outil] banque_exemples()\nPrecisez : usestate / useeffect / props / composant / lire_fichier / modifier\n{liste}"}

# ---------- QUIZ ----------
QUIZ = [
    {"q": "Pour modifier count avec useState ?", "choix": ["A) count=count+1", "B) setCount(count+1)", "C) update(count)"], "rep": "B"},
    {"q": "useEffect(..., [count]) se relance quand ?", "choix": ["A) toujours", "B) quand count change", "C) jamais"], "rep": "B"},
    {"q": "Props sert a ?", "choix": ["A) parent->enfant", "B) enfant->parent", "C) rien"], "rep": "A"},
]
status = None
def run_quiz():
    global status
    status = random.sample(QUIZ, min(2, len(QUIZ)))
    return {"type": "quiz", "questions": [{"q": x["q"], "choix": x["choix"]} for x in status]}
def corrige_quiz(L):
    global status
    if not status: return {"type": "score", "txt": "Lance d'abord le quiz"}
    s = sum(1 for i, x in enumerate(status) if i < len(L) and L[i] == x["rep"])
    d = " ".join([f"{i+1}:{L[i] if i < len(L) else '?'}={'OK' if i < len(L) and L[i] == x['rep'] else 'NON->' + x['rep']}" for i, x in enumerate(status)])
status = None
def reset_etat():
    global status
    status = None
    EVAL["courant"] = None
    return {"type": "cours", "txt": "Session remise a zero (quiz + eval effaces)."}
    return {"type": "score", "txt": f"Score {s}/{len(status) if False else 2} - {d}"}

# ---------- CORRECTEUR HYBRIDE ----------
def corriger_code(code):
    erreurs = []
    if len(code.splitlines()) > 200:
        return {"type": "code", "txt": "[outil] corriger_code()\n- Extrait etudiant (<30 lignes) SVP."}
    if "serve_forever" in code:
        erreurs.append("Attention : serve_forever() boucle sans fin (timeout sandbox 10s).")
    if re.search(r"\bcount\s*=", code) and "setCount" not in code:
        erreurs.append("count= interdit par le cours : utilisez setCount(count+1).")
    if re.search(r"function\s+[a-z]", code):
        erreurs.append("Composant en minuscule : majuscule ex: function Carte().")
    try:
        tree = ast.parse(code)
        definis = set(dir(builtins)) | {"True", "False", "None"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names: definis.add((a.asname or a.name).split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names: definis.add(a.asname or a.name)
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)): definis.add(n.name)
            elif isinstance(n, ast.arg): definis.add(n.arg)
        connus = list(definis) + ["HTTPServer", "run_quiz", "run_agent", "corriger_code", "status", "json", "pathlib", "PAGE", "H"]
        vus = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in definis and n.id not in vus:
                sug = difflib.get_close_matches(n.id, connus, n=1, cutoff=0.7)
                if sug: erreurs.append(f"Faute de frappe probable : '{n.id}' -> '{sug[0]}' ?"); vus.add(n.id)
    except SyntaxError as e:
        erreurs.append(f"Erreur syntaxe ligne {e.lineno} : {e.msg}")
    faits = "\n".join("- " + e for e in erreurs) if erreurs else "OK - aucune erreur."
    txt = "CORRECTION PYTHON :\n" + faits
    if ("def " in code or "print(" in code) and "serve_forever" not in code:
        (RACINE() / "sandbox").mkdir(exist_ok=True)
        fp = RACINE() / "sandbox" / "tmp_test.py"; fp.write_text(code, encoding="utf-8")
        try:
            p = subprocess.run(["python", str(fp)], capture_output=True, text=True, timeout=10)
            out = (p.stdout + p.stderr)[-1200:]
            txt += f"\n\nEXECUTION (code {p.returncode}) :\n{out if out.strip() else '(aucune sortie)'}"
        except Exception as e:
            txt += f"\n\nEXECUTION impossible : {e}"
    try:
        r = requests.post(URL, json={"model": MODEL, "messages": [
            {"role": "system", "content": "Tuteur bienveillant. Explique UNIQUEMENT les FAITS, 3 lignes max. Si OK, felicite 1 ligne."},
            {"role": "user", "content": f"CODE:\n{code[:2000]}\n\nFAITS:\n{txt[:2000]}"}], "stream": False, "options": {"temperature": 0.2, "num_ctx": 8192}}, timeout=90)
        txt += "\n\nEXPLICATION IA :\n" + r.json()["message"]["content"]
    except Exception as e:
        txt += f"\n\nIA indisponible ({e})."
    return {"type": "code", "txt": "[outil] corriger_code() [Python] + [IA]\n" + txt}

# ---------- AGENT COURS (RAG) ----------
def sans_accents(texte):
    return unicodedata.normalize("NFD", texte).encode("ascii", "ignore").decode().lower()

def garde_hors_matiere(question, corpus):
    """Aucun mot important de la question n'existe dans cours/ ni dans le livre -> refus Python, 0 LLM."""
    if mots_index is None:
        return False
    # meme normalisation que l'index : pluriels et accents ne doivent pas faire refuser
    qmots = [m for m in mots_index(question) if len(m) >= 4]
    if not qmots: return False
    if _CACHE_COURS["vocab"] is None:
        _CACHE_COURS["vocab"] = set(mots_index(corpus))
    if any(m in _CACHE_COURS["vocab"] for m in qmots): return False
    if any(m in idx.vocabulaire for m in qmots for idx in INDEX_LIVRES): return False
    return not any(site in sans_accents(question)
                   for site in ("react.dev", "mdn", "javascript.info", "vite", "tailwind"))

def _sans_echo(texte):
    """llama3.2 recopie parfois les entetes du contexte : on les retire, le contenu reste intact."""
    garde = []
    for ligne in (texte or "").splitlines():
        nu = ligne.strip()
        if nu.startswith("EXTRAITS DU LIVRE INDEXE") or nu.startswith("[=== SOURCE:") or nu == "CONTEXTE:":
            continue
        garde.append(ligne)
    return "\n".join(garde).strip()

def repondre_rag(q, cc):
    """Python apporte les passages, le LLM redige. Appele par l'outil OU en repli si le petit modele n'appelle rien."""
    ctx = passages_utiles(q, cc)
    if len(ctx) < 600 or any(m in q.lower() for m in ["react.dev", "mdn", "site", "officiel", "documentation", "javascript.info", "vite", "tailwind"]):
        ctx += enrichir_web(q, ctx)
    r = requests.post(URL, json={"model": MODEL, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"CONTEXTE:\n{ctx[:8000]}\n\nQUESTION: {q}"}],
        "stream": False, "options": {"temperature": 0.0, "num_ctx": 8192}}, timeout=120).json()["message"]
    srcs = extraire_sources(ctx)
    return {"type": "cours", "txt": "[outil] lire_cours() [RAG+WEB]\n" + _sans_echo(r.get("content") or ""),
            "sources": srcs or ["aucune (reponse memoire LLM - mefiance)"]}

def run_agent_cours(q):
    if "```" in q or "function " in q or "def " in q or "<div" in q:
        if "\n" in q or "{" in q or "=" in q: return corriger_code(q.replace("```", ""))
    ex = trouver_exemple(q)
    if ex: return ex
    cc = lire_cours()
    try:
        cal = reponse_calendrier(q, cc)
        if cal: return cal
    except Exception: pass
    if garde_hors_matiere(q, cc):
        return {"type": "cours", "sources": [], "txt":
                "Hors-matiere - voir le manuel.\n"
                "Aucun mot de votre question n'apparait dans les documents de cours/ "
                "ni dans le livre indexe. L'agent ne repond pas de memoire : c'est le contrat."}
    # Python choisit le chemin (banque, calendrier, garde) ; pour le RAG, Python apporte
    # les passages et le modele redige. Une seule requete au modele, et jamais de memoire.
    return repondre_rag(q, cc)

# ---------- EVAL ----------
def eval_next():
    corpus = ""
    for d in sorted((RACINE() / "cours").glob("*.docx")):
        try:
            import zipfile
            x = zipfile.ZipFile(d).read("word/document.xml").decode("utf-8")
            corpus += "\n" + re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))[:6000]
        except Exception: pass
    phrases = [p.strip() for p in re.split(r"\n+", corpus) if 60 < len(p.strip()) < 220]
    if len(phrases) < 3: return {"type": "eval", "q": None, "txt": "Ajoutez de la matiere dans cours/*.docx"}
    bonne = random.choice(phrases)
    leurres = random.sample([p for p in phrases if p != bonne], 2)
    q = {"bonne": bonne, "choix": sorted([bonne] + leurres, key=lambda _: random.random())}
    EVAL["courant"] = q
    return {"type": "eval", "q": q["choix"], "txt": "Quel passage vient VRAIMENT du cours ?"}
EVAL = {"courant": None}

PAGE = """<!DOCTYPE html><html lang=fr><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<link rel='stylesheet' href='/app.css'>
<title>Agent React - Atelier (LLM + Python + RAG)</title></head>
<body class='bg-slate-100 min-h-screen'>
<div class='max-w-4xl mx-auto p-4'>
<header class='bg-slate-900 text-white rounded-2xl p-5 mb-4'>
<h1 class='text-xl font-bold'>Agent React - TechWeek LaSalle</h1>
<p class='text-sm text-slate-300'>LLM (Ollama llama3.2) + Python (regles, quiz, execution) + RAG (vos .docx/.pdf) - 100% local, CSS et polices inclus</p>
<div class='mt-3 flex flex-wrap gap-2'>
<button onclick="mode('cours')" class='bg-emerald-500 px-3 py-1 rounded'>Cours RAG</button>
<button onclick="mode('quiz')" class='bg-sky-500 px-3 py-1 rounded'>Quiz</button>
<button onclick="mode('banque')" class='bg-violet-500 px-3 py-1 rounded'>Banque codes</button>
<button onclick="mode('corrige')" class='bg-amber-500 px-3 py-1 rounded text-black'>Corriger code</button>
<button onclick="mode('eval')" class='bg-rose-500 px-3 py-1 rounded'>Eval comprehension</button>
<button onclick="mode('ressources')" class='bg-teal-500 px-3 py-1 rounded'>Livre + Web</button>
<button onclick="reset()" class='bg-slate-500 px-3 py-1 rounded' title='Efface quiz, eval et reponses'>Reset</button>
</div></header>
<main class='bg-white rounded-2xl p-4 shadow'>
<div id='zone-cours'><input id='q' class='w-full border rounded p-2' placeholder='Ex: Que dit la matiere sur Tailwind ? / Quand le cours 420-TT4-AS ?'><button onclick='cours()' class='mt-2 bg-slate-900 text-white px-4 py-2 rounded'>Envoyer</button></div>
<div id='zone-quiz' class='hidden'><button onclick='quiz()' class='bg-sky-500 text-white px-4 py-2 rounded'>Lancer Quiz</button><div id='qz' class='mt-2'></div></div>
<div id='zone-banque' class='hidden'><div class='flex flex-wrap gap-2'>
<button onclick="ex('donne le code usestate')" class='border px-2 py-1 rounded'>useState</button>
<button onclick="ex('donne le code useeffect')" class='border px-2 py-1 rounded'>useEffect</button>
<button onclick="ex('donne le code props')" class='border px-2 py-1 rounded'>Props</button>
<button onclick="ex('donne le code lire_fichier')" class='border px-2 py-1 rounded'>Lire fichier</button>
<button onclick="ex('donne le code modifier')" class='border px-2 py-1 rounded'>Modifier</button>
<button onclick="ex('donne le code usereducer')" class='border px-2 py-1 rounded'>useReducer</button>
<button onclick="ex('donne le code usecontext')" class='border px-2 py-1 rounded'>useContext</button>
<button onclick="ex('donne le code fetch')" class='border px-2 py-1 rounded'>Fetch API</button>
<button onclick="ex('donne le code formulaire')" class='border px-2 py-1 rounded'>Formulaire</button>
<button onclick="ex('donne le code listes')" class='border px-2 py-1 rounded'>Listes</button>
</div></div>
<div id='zone-corrige' class='hidden'><textarea id='code' class='w-full border rounded p-2 h-28'>function carte(){ count=count+1; return <div/> }</textarea><button onclick='code()' class='mt-2 bg-amber-500 px-4 py-2 rounded'>Corriger mon code</button></div>
<div id='zone-eval' class='hidden'><button onclick='evn()' class='bg-rose-500 text-white px-4 py-2 rounded'>Question suivante</button><div id='ev' class='mt-2'></div></div>
<div id='zone-ressources' class='hidden'><button onclick='ress()' class='bg-teal-500 text-white px-4 py-2 rounded'>Afficher livre + sites</button><p class='text-sm mt-1'>Livre : deposez votre PDF dans <b>cours/livres/</b> (il sera lu comme les autres docs).</p></div>
<pre id='r' class='mt-4 bg-slate-900 text-green-200 p-3 rounded-xl whitespace-pre-wrap text-sm'>Choisissez un mode ci-dessus.</pre>
<div id='src' class='mt-2 text-xs'></div>
</main></div>
<script>
let M='cours';
function mode(m){M=m;['cours','quiz','banque','corrige','eval','ressources'].forEach(x=>document.getElementById('zone-'+x).classList.add('hidden'));document.getElementById('zone-'+m).classList.remove('hidden');}
async function post(d){let x=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return x.json();}
function showsrc(j){let s=document.getElementById('src');if(j.sources&&j.sources.length){s.innerHTML='<b>Sources consultees (preuve Python) :</b> '+j.sources.map(x=>"<span class='inline-block bg-teal-100 border border-teal-500 rounded px-2 py-0.5 m-0.5'>"+x+"</span>").join('');}else{s.innerHTML='';}}
async function cours(){r.textContent='...';let j=await post({a:'cours',q:q.value});r.textContent=j.txt;showsrc(j);}
async function ex(t){r.textContent='...';let j=await post({a:'cours',q:t});r.textContent=j.txt;showsrc(j);}
async function quiz(){let j=await post({a:'quiz'});let d=document.getElementById('qz');d.innerHTML='';j.questions.forEach((e,i)=>{d.innerHTML+='<p class=mt-2><b>'+(i+1)+'. '+e.q+'</b><br>'+e.choix.map(c=>"<label><input type=radio name=q"+i+" value='"+c[0]+"'> "+c+"</label><br>").join('')+'</p>';});d.innerHTML+='<button onclick=corr() class="mt-2 bg-slate-900 text-white px-3 py-1 rounded">Valider</button>';}
async function corr(){let L=[0,1].map(i=>{let e=document.querySelector('input[name=q'+i+']:checked');return e?e.value:'?';});let j=await post({a:'corr',lettres:L});r.textContent='[quiz Python] '+j.txt;}
async function code(){r.textContent='...';let j=await post({a:'code',q:document.getElementById('code').value});r.textContent=j.txt;}
async function evn(){let j=await post({a:'eval'});let d=document.getElementById('ev');if(!j.q){r.textContent=j.txt;return;}d.innerHTML='<p><b>Quel passage vient VRAIMENT du cours ?</b></p>'+j.q.map((c,i)=>"<label><input type=radio name=ev value='"+i+"'> "+c.slice(0,120)+"...</label><br>").join('')+'<button onclick=eva() class="mt-2 bg-slate-900 text-white px-3 py-1 rounded">Valider</button>';}
async function eva(){let e=document.querySelector('input[name=ev]:checked');let j=await post({a:'evalrep',i:e?+e.value:-1});r.textContent=j.txt;}
async function ress(){r.textContent='...';let j=await post({a:'ressources'});r.textContent=j.txt;showsrc(j);}
async function reset(){await post({a:'reset'});r.textContent='Session remise a zero.';document.getElementById('qz').innerHTML='';document.getElementById('ev').innerHTML='';document.getElementById('q').value='';document.querySelectorAll('input[type=radio]').forEach(e=>e.checked=false);}
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def _acces_ok(self):
        # Sans CLE_ACCES : ouvert (usage local). Avec : ?k=... ou cookie deja pose.
        if not CLE_ACCES: return True
        from urllib.parse import urlparse, parse_qs
        if parse_qs(urlparse(self.path).query).get("k", [""])[0] == CLE_ACCES: return True
        return ("acces=" + CLE_ACCES) in (self.headers.get("Cookie") or "")

    def _refuse(self, json_mode=False):
        b = (b'{"txt":"403 : cle d acces manquante."}' if json_mode else
             "<h1>403</h1><p>Lien incomplet : ajoutez ?k=VOTRE_CLE a l'adresse.</p>".encode("utf-8"))
        self.send_response(403)
        self.send_header("Content-type", "application/json" if json_mode else "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if not self._acces_ok(): return self._refuse()
        p = self.path.split("?")[0]
        if p in ("/app.css", "/mathjax.js"):
            rel = "static/app.css" if p == "/app.css" else "static/mathjax-tex-svg.js"
            typ = "text/css; charset=utf-8" if p == "/app.css" else "application/javascript; charset=utf-8"
            try: b = (RACINE() / rel).read_bytes()
            except Exception: b = b""
            self.send_response(200); self.send_header("Content-type", typ)
            self.send_header("Cache-Control", "max-age=600")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            return
        b = PAGE.encode("utf-8")
        self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8")
        if CLE_ACCES: self.send_header("Set-Cookie", "acces=%s; Path=/; SameSite=Lax" % CLE_ACCES)
        self.send_header("Cache-Control", "no-store"); self.send_header("Pragma", "no-cache")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        if not self._acces_ok(): return self._refuse(True)
        n = int(self.headers.get("Content-Length", 0))
        d = json.loads(self.rfile.read(n).decode("utf-8"))
        a = d.get("a")
        if a == "quiz": out = run_quiz()
        elif a == "reset": out = reset_etat()
        elif a == "ressources":
            out = {"type": "cours", "txt": RESS.texte_ressources() if RESS else "etape10_ressources.py manquant."}
        elif a == "corr": out = corrige_quiz(d.get("lettres", []))
        elif a == "code": out = corriger_code(d.get("q", ""))
        elif a == "eval":
            out = eval_next()
            if out.get("q"): out = {"type": "eval", "questions": [], "q": out["q"], "txt": out["txt"]}
        elif a == "evalrep":
            cur = EVAL.get("courant")
            if not cur: out = {"type": "cours", "txt": "Cliquez Question suivante d'abord."}
            else:
                i = d.get("i", -1)
                bon = cur["choix"].index(cur["bonne"])
                out = {"type": "cours", "txt": ("OK" if i == bon else f"NON -> bonne = option {bon+1} : {cur['bonne'][:200]}") + "  [SOURCE cours/]"}
        else: out = run_agent_cours(d.get("q", ""))
        b = json.dumps(out).encode("utf-8")
        self.send_response(200); self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

def check_moteur():
    # Premier lancement (exe ou .bat) : Ollama present ? modele pret ?
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=5).json()
        noms = [m.get("name", "") for m in r.get("models", [])]
        if any("llama3.2" in n for n in noms):
            print("Moteur OK : Ollama + llama3.2 prets.")
        else:
            print("Moteur INCOMPLET : Ollama repond mais llama3.2 absent -> ollama pull llama3.2:latest")
    except Exception:
        print("Moteur ABSENT : installez Ollama (ollama.com/download) puis ollama pull llama3.2:latest.")

if __name__ == "__main__":
    check_moteur()
    lire_cours()  # precharge les notes + l'index des livres, une seule fois
    for index in INDEX_LIVRES:
        print(f"Livre indexe : {index.nom} ({index.pages_total} pages) -> "
              f"{len(index.morceaux)} morceaux, recherche BM25 par page.")
    print("BUILD app-finale v10 (livre indexe BM25) - Ouvrez http://127.0.0.1:3000")
    ThreadingHTTPServer(("127.0.0.1", 3000), H).serve_forever()
