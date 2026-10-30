import pathlib, re, random, json
DOSSIER = pathlib.Path("cours")  # changez par cours_math, cours_physique... meme code
MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"

def lire_docx(p):
    import zipfile
    x = zipfile.ZipFile(p).read("word/document.xml").decode("utf-8")
    return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))

def generer_qcm_ia(passage, autres):
    # IA = auteur surveillee : reformule + propose leurres, Python validera
    import requests
    r = requests.post(URL, json={"model": MODEL,
        "messages": [
            {"role": "system", "content": "Tu es auteur QCM. A partir du PASSAGE, ecris 1 question de comprehension + recopie la bonne reponse (<=15 mots, fidele au passage) + 2 reponses fausses plausibles mais differentes. Reponds en JSON strict : {\"question\":..., \"bonne\":..., \"fausses\":[...]}. N'invente rien hors passage."},
            {"role": "user", "content": f"PASSAGE:\n{passage[:600]}"}],
        "stream": False, "options": {"temperature": 0.2}}, timeout=90)
    txt = r.json()["message"]["content"]
    m = re.search(r"\{.*\}", txt, re.S)
    d = json.loads(m.group(0))
    bonne, fausses = d["bonne"].strip(), [f.strip() for f in d["fausses"][:2]]
    # VERROU Python : la bonne doit venir du passage, les fausses en differer NETTEMENT
    import difflib
    norm = lambda s: re.sub(r"\W+", "", s.lower())
    if bonne.lower() not in passage.lower() and passage.lower() not in bonne.lower():
        raise ValueError("bonne reponse hors-passage, rejet IA")
    propres = []
    for f in fausses:
        if norm(f) == norm(bonne): raise ValueError("leurre = bonne, rejet IA")
        if difflib.SequenceMatcher(None, norm(f), norm(bonne)).ratio() > 0.85:
            raise ValueError(f"leurre quasi-identique a la bonne ({f!r}), rejet IA")
        if any(difflib.SequenceMatcher(None, norm(f), norm(g)).ratio() > 0.9 for g in propres):
            raise ValueError("leurres identiques entre eux, rejet IA")
        propres.append(f)
    if len(propres) < 2: raise ValueError("pas assez de leurres distincts")
    return d["question"], bonne, propres

corpus = ""
for d in sorted(DOSSIER.glob("*.docx")):
    try: corpus += "\n" + lire_docx(d)[:6000]
    except Exception: pass
phrases = [p.strip() for p in re.split(r"\n+", corpus) if 60 < len(p.strip()) < 220 and (":" in p or "est " in p.strip()[:60])]
base = random.sample(phrases, min(3, len(phrases)))  # tirage neuf a chaque lancement
print(f"{len(phrases)} phrases candidates dans {DOSSIER}/")
score = 0
for i, bonne in enumerate(base, 1):
    try:
        question, bonne_affichee, leurres = generer_qcm_ia(bonne, phrases)
        print(f"\n{i}. [IA auteur] {question}")
        tag = "  [SOURCE cours/ + IA]"
    except Exception as e:
        bonne_affichee, leurres = bonne, random.sample([p for p in phrases if p != bonne], 2)
        print(f"\n{i}. [Python seul, IA indisponible: {e}] Quel passage vient VRAIMENT du cours ?")
        tag = "  [SOURCE cours/]"
    choix = sorted([bonne_affichee] + leurres, key=lambda _: random.random())
    for j, c in enumerate(choix): print(f"   {chr(65+j)}) {c[:140]}...")
    rep = input("Votre lettre : ").strip().upper()
    bon = chr(65 + choix.index(bonne_affichee))
    ok = (rep == bon)
    score += ok
    print(("OK" if ok else f"NON -> {bon}") + tag)
pathlib.Path("resultats").mkdir(exist_ok=True)
open("resultats/eval.csv", "a").write(f"{DOSSIER};{score}/{len(base)}\n")
print(f"\nScore comprehension : {score}/{len(base)} -> resultats/eval.csv")
