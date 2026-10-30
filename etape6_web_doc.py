import pathlib, re, random, json, ast, difflib, builtins, requests, subprocess, tempfile, os
from http.server import BaseHTTPRequestHandler, HTTPServer

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
#def lire_cours(): return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")

def lire_docx(path):
    import zipfile, re
    z = zipfile.ZipFile(path)
    xml = z.read("word/document.xml").decode("utf-8")
    txt = re.sub(r"</w:p[^>]*>", "\n", xml)
    txt = re.sub(r"<[^>]+>", "", txt)
    return txt






def lire_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        return "[PDF ignore : faites pip install pypdf]"
    try:
        rd = PdfReader(str(path))
        txt = "\n".join([(p.extract_text() or "") for p in rd.pages])
        if len(txt.strip()) < 200:
            return "[PDF scanné image : pas de texte extractible, besoin OCR (tesseract/llava). Contenu ignore.]"
        return txt
    except Exception as e:
        return f"[PDF illisible {e}]"

def passages_utiles(question, gros_texte, max_car=3500):
    # mini-RAG maison v2 : score par mots rares (tendances > cours), source toujours jointe
    mots = [w.lower() for w in re.findall(r"[a-zA-Zéèêàç]{4,}", question)]
    STOP = {"cours","quoi","quand","comment","pourquoi","dans","avec","cette","sont","plus","faire","donne"}
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
    return "\n".join(paras[:12])[:max_car]

def lire_cours():
    docs = sorted(pathlib.Path("cours").glob("*.docx"))
    pdfs = sorted(pathlib.Path("cours").glob("*.pdf"))
    tout = ""
    for d in docs:
        try: tout += f"\n\n=== SOURCE: {d.name} ===\n" + lire_docx(d)[:6000]
        except Exception as e: tout += f"\n[SOURCE {d.name} illisible: {e}]"
    for p in pdfs:
        try: tout += f"\n\n=== SOURCE: {p.name} ===\n" + lire_pdf(p)[:6000]
        except Exception as e: tout += f"\n[SOURCE {p.name} illisible: {e}]"
    if tout.strip(): return tout[:18000]
    return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")

COURS_TXT = lire_cours().lower()
SYSTEM = "Tu es agent tuteur. Tu reponds UNIQUEMENT d'apres le resultat de l'outil lire_cours. Cite la SOURCE entre crochets. Si on demande une date/horaire, donne la date exacte du calendrier (jour, heure, enseignant). N'invente aucun chapitre. Si absent : Hors-matiere."
OUTIL=[
 {"type":"function","function":{"name":"lire_cours","description":"Lit cours/react.txt","parameters":{"type":"object","properties":{},"required":[]}}},
 {"type":"function","function":{"name":"corriger_code","description":"Corrige code React/Python colle par l'etudiant. Appelle-la des que tu vois du code.","parameters":{"type":"object","properties":{"code":{"type":"string"}},"required":["code"]}}}
]

QUIZ=[
 {"q":"Pour modifier count avec useState ?","choix":["A) count=count+1","B) setCount(count+1)","C) update(count)"],"rep":"B"},
 {"q":"useEffect(..., [count]) se relance quand ?","choix":["A) toujours","B) quand count change","C) jamais"],"rep":"B"},
]
status=None
def run_quiz():
    global status
    status=random.sample(QUIZ,2)
    return {"type":"quiz","questions":[{"q":x["q"],"choix":x["choix"]} for x in status]}
def corrige_quiz(L):
    global status
    if not status: return {"type":"score","txt":"Lance d'abord le quiz"}
    s=sum(1 for i,x in enumerate(status) if i<len(L) and L[i]==x["rep"])
    d=" ".join([f"{i+1}:{L[i] if i<len(L) else '?'}={'OK' if i<len(L) and L[i]==x['rep'] else 'NON->'+x['rep']}" for i,x in enumerate(status)])
status=None
# --- BIBLIOTHEQUE PEDAGOGIQUE = codes valides par le prof, pas inventes par le LLM ---
EXEMPLES = {
 "usestate": ("Compteur useState (base states)", "import { useState } from 'react';\nfunction Compteur(){\n  const [count, setCount] = useState(0);\n  return <button onClick={()=>setCount(count+1)}>Clics : {count}</button>;\n}"),
 "useeffect": ("useEffect (hook effet)", "import { useState, useEffect } from 'react';\nfunction Titre({count}){\n  useEffect(()=>{ document.title = `Clics : ${count}`; }, [count]);\n  return <p>{count}</p>;\n}"),
 "props": ("Props parent->enfant", "function Bouton({titre}){\n  return <button>{titre}</button>;\n}\nfunction App(){\n  return <Bouton titre=\"Valider\" />;\n}"),
 "composant": ("Composant + modification", "function Carte({nom}){\n  return <div>{nom}</div>;\n}\nfunction App(){\n  return <Carte nom=\"React\" />;\n}"),
 "lire_fichier": ("Lire un fichier (input file)", "function LireFichier(){\n  const lire = (e)=>{\n    const f = e.target.files[0];\n    const r = new FileReader();\n    r.onload = ()=>alert(r.result.slice(0,200));\n    r.readAsText(f);\n  };\n  return <input type=\"file\" onChange={lire} />;\n}"),
 "modifier": ("Modifier un composant (setState)", "import { useState } from 'react';\nfunction Editable(){\n  const [texte, setTexte] = useState('Bonjour');\n  return (<div>\n    <p>{texte}</p>\n    <button onClick={()=>setTexte('Modifie !')}>Modifier</button>\n  </div>);\n}"),
 "mon_hook": ("Titre", "code..."),
}
def trouver_exemple(question):
    ql = question.lower()
    for cle,(titre,code) in EXEMPLES.items():
        nom = cle.replace("_"," ")
        if cle in ql or nom in ql or titre.lower().split()[0] in ql:
            return {"type":"cours","txt":f"[outil] banque_exemples() -> {titre}\n{code}"}
    # mots larges hooks/props/states -> propose le catalogue
    if any(m in ql for m in ["code","exemple","montre","hook","props","state","states","fichier","composant","modifier"]):
        liste = "\n".join([f"- {k} : {v[0]}" for k,v in EXEMPLES.items()])
        # essai direct : usestate par defaut si hooks demande sans precision
        if "hook" in ql: return {"type":"cours","txt":"[outil] banque_exemples() -> useState (defaut hooks)\n"+EXEMPLES["usestate"][1]}
        return {"type":"cours","txt":f"[outil] banque_exemples()\nPrecisez : usestate / useeffect / props / composant / lire_fichier / modifier\nCatalogue :\n{liste}"}
    return None

# --- OUTIL 2 = VOTRE correcteur, deterministe ---
def corriger_code(code):
    erreurs=[]
    if len(code.splitlines()) > 200:
        return {"type":"code","txt":"[outil] corriger_code()\n- Collez un extrait etudiant (<30 lignes), pas l'agent entier."}
    if "serve_forever" in code:
        erreurs.append("Attention : serve_forever() boucle sans fin (timeout sandbox 10s normal). Pour un test, commentez cette ligne.")
    if re.search(r"\bcount\s*=",code) and "setCount" not in code:
        erreurs.append("Ligne count= : interdit par le cours. Utilisez setCount(count+1).")
    if re.search(r"function\s+[a-z]",code):
        erreurs.append("Composant en minuscule : mettez majuscule ex: function Carte().")
    if "useState" in code and "useState(0)" not in code and "useState(" not in code:
        erreurs.append("useState mal initialise.")
    # Syntaxe Python : oui. Dependances manquantes : non (extrait partiel normal).
    # On ne signale qu'une probable faute de frappe (HTTPSe -> HTTPServer).
    try:
        tree = ast.parse(code)
        definis = set(dir(builtins)) | {"True","False","None"}
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for a in n.names: definis.add((a.asname or a.name).split(".")[0])
            elif isinstance(n, ast.ImportFrom):
                for a in n.names: definis.add(a.asname or a.name)
            elif isinstance(n, (ast.FunctionDef, ast.ClassDef)): definis.add(n.name)
            elif isinstance(n, ast.arg): definis.add(n.arg)
        connus = list(definis) + ["HTTPServer","BaseHTTPRequestHandler","run_quiz","corrige_quiz","run_agent","corriger_code","status","actif","json","pathlib","PAGE","H"]
        vus = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id not in definis and n.id not in vus:
                sug = difflib.get_close_matches(n.id, connus, n=1, cutoff=0.7)
                if sug:
                    erreurs.append(f"Faute de frappe probable : '{n.id}' -> vouliez-vous '{sug[0]}' ?")
                    vus.add(n.id)
                # sinon : dependance externe (import hors extrait), on ignore volontairement
    except SyntaxError as e:
        erreurs.append(f"Erreur syntaxe ligne {e.lineno} : {e.msg}")
    faits = "\n".join("- "+e for e in erreurs) if erreurs else "OK - aucune erreur detectee."
    txt="CORRECTION PYTHON (regles du cours) :\n"+faits
    # Si vrai Python, on l'execute pour montrer l'erreur reelle (sauf serveur bloquant)
    if ("def " in code or "print(" in code) and "serve_forever" not in code:
        pathlib.Path("sandbox").mkdir(exist_ok=True)
        fp=pathlib.Path("sandbox/tmp_test.py");fp.write_text(code,encoding="utf-8")
        try:
            p=subprocess.run(["python",str(fp)],capture_output=True,text=True,timeout=10)
            out=(p.stdout+p.stderr)[-1500:]
            txt+=f"\n\nEXECUTION python (code {p.returncode}) :\n{out if out.strip() else '(aucune sortie)'}"
        except Exception as e:
            txt+=f"\n\nEXECUTION impossible : {e}"
    # HYBRIDE : Python a tranche, l'IA explique poliment SANS inventer (verrouillee sur FAITS)
    try:
        r = requests.post(URL, json={"model": MODEL,
            "messages": [
                {"role":"system","content":"Tu es tuteur bienveillant. Explique UNIQUEMENT a partir des FAITS fournis. N'invente aucune autre erreur. Si FAITS=OK, felicite en 1 ligne. Ton francais, 3 lignes max."},
                {"role":"user","content":f"CODE:\n{code[:2000]}\n\nFAITS PYTHON:\n{txt[:2000]}\n\nExplique a l'etudiant."}],
            "stream": False, "options":{"temperature":0.2}}, timeout=90)
        ia = r.json()["message"]["content"]
        txt += f"\n\nEXPLICATION IA (verrouillee sur faits) :\n{ia}"
    except Exception as e:
        txt += f"\n\nEXPLICATION IA indisponible ({e}) - gardez la partie PYTHON ci-dessus."
    return {"type":"code","txt":"[outil] corriger_code() [Python] + [IA explique]\n"+txt}

def reponse_calendrier(q, cc):
    ql = q.lower()
    if not any(m in ql for m in ["quand","horaire","date","calendrier","enseignant","groupe","prof","séance","seance","hora"]):
        return None
    # extraction sur le TEXTE COMPLET (pas le filtre), sinon les lignes d'horaires sont jetees
    jours = sorted(set(re.findall(r"(?i)(?:lundi|mardi|mercredi|jeudi|vendredi)\s*\d{2}h\s*-\s*\d{2}h[^\n]*", cc)))
    codes = sorted(set(re.findall(r"420-[A-Z0-9-]+", cc)))
    sems = sorted(set(re.findall(r"(?i)(hiver|automne)\s*(202\d)?", cc)))
    ens = sorted(set(re.findall(r"(?i)enseignant\s*:\s*([A-ZÀ-Þ][\wÀ-þ\-']+(?:\s+[A-ZÀ-Þ][\wÀ-þ\-']+)?)", cc)))
    if not (jours or codes or ens):
        return None
    sel = passages_utiles(q, cc, 1500)
    txt = "[outil] lire_cours() [calendrier Python, 0 LLM]\nD'apres le calendrier :\n"
    if codes: txt += "Cours : " + ", ".join(codes) + "\n"
    if sems: txt += "Semestre : " + ", ".join([" ".join(s).strip() for s in sems]) + "\n"
    if ens: txt += "Enseignant : " + ", ".join(ens) + "\n"
    if jours: txt += "Horaires : " + " | ".join([j.strip() for j in jours]) + "\n"
    txt += "\nPassages :\n" + sel[:1500]
    return {"type":"cours","txt":txt}

def run_agent(q):
    # PORTE 1 : code colle -> correcteur (pas le LLM)
    if "```" in q or "function " in q or "def " in q or "setCount" in q or "<div" in q:
        code=q.replace("```","").strip()
        # mais si c'est une demande "donne le code useState" (pas de { ni =), c'est la banque
        if len(code.splitlines()) == 1 and any(m in code.lower() for m in ["donne","montre","exemple","code "]):
            ex = trouver_exemple(q)
            if ex: return ex
        if "\n" in code or "{" in code or "=" in code:
            return corriger_code(code)
    # PORTE 2 : demande de code de base -> banque prof (pas le LLM, 0 hallucination)
    if "useState" in q and len(q.splitlines()) == 1:
        ex = trouver_exemple(q)
        if ex: return ex
    ex = trouver_exemple(q)
    if ex: return ex
    # PORTE 3 : question calendrier/dates -> Python d'abord (anti-hallucination 15 nov/Dupont)
    try:
        cal = reponse_calendrier(q, lire_cours())
        if cal: return cal
    except Exception:
        pass
    r=requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q}],"stream":False,"tools":OUTIL,"options":{"temperature":0.0}},timeout=120).json()["message"]
    for c in (r.get("tool_calls") or []):
        if c["function"]["name"]=="corriger_code":
            arg=c["function"].get("arguments",{})
            if isinstance(arg,str):
                try: arg=json.loads(arg)
                except: arg={"code":q}
            return corriger_code(arg.get("code",q))
        if c["function"]["name"]=="lire_cours":
            cc=lire_cours()
            r2=requests.post(URL,json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q},{"role":"assistant","content":"","tool_calls":r["tool_calls"]},{"role":"tool","content":passages_utiles(q, cc)}],"stream":False,"options":{"temperature":0.0}},timeout=120).json()["message"]
            return {"type":"cours","txt":"[outil] lire_cours()\n"+(r2.get("content") or "")}
    return {"type":"cours","txt":r.get("content") or ""}

PAGE=b"""<meta charset=utf-8><style>body{font-family:Arial;max-width:750px;margin:20px}button{padding:8px;margin:4px}pre{background:#eee;padding:10px;white-space:pre-wrap}textarea{width:100%;height:90px}</style>
<h2>Agent React - Etape 6 (cours + quiz + corrige-code)</h2>
<input id=q size=55 placeholder='Question cours'><button onclick="cours()">Cours</button><button onclick="quiz()">Quiz</button>
<pre id=r></pre><div id=quiz></div>
<h3>Colle ton code :</h3><textarea id=code>function carte(){ count=count+1; return <div/> }</textarea><br><button onclick="code()">Corriger mon code</button>
<script>
async function post(d){let x=await fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return x.json();}
async function cours(){r.textContent='...';let j=await post({a:'cours',q:q.value});r.textContent=j.txt;}
async function quiz(){let j=await post({a:'quiz'});let d=document.getElementById('quiz');d.innerHTML='';j.questions.forEach((e,i)=>{d.innerHTML+=`<p><b>${i+1}. ${e.q}</b><br>`+e.choix.map(c=>`<label><input type=radio name=q${i} value='${c[0]}'> ${c}</label><br>`).join('')+'</p>';});d.innerHTML+=`<button onclick="corr()">Corriger</button>`;}
async function corr(){let L=[0,1].map(i=>{let e=document.querySelector(`input[name=q${i}]:checked`);return e?e.value:'?';});let j=await post({a:'corr',lettres:L});r.textContent='[outil] verifier_reponse()\\n'+j.txt;}
async function code(){r.textContent='...';let j=await post({a:'code',q:document.getElementById('code').value});r.textContent=j.txt;}
</script>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200);self.send_header("Content-type","text/html; charset=utf-8");self.end_headers();self.wfile.write(PAGE)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));d=json.loads(self.rfile.read(n).decode('utf-8'))
        if d.get('a')=='quiz': out=run_quiz()
        elif d.get('a')=='corr': out=corrige_quiz(d.get('lettres',[]))
        elif d.get('a')=='code': out=corriger_code(d.get('q',''))
        else: out=run_agent(d.get('q',''))
        b=json.dumps(out).encode('utf-8')
        self.send_response(200);self.send_header("Content-type","application/json");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def log_message(self,*a): pass
print("BUILD porte3-calendrier v2 - Ouvrez http://127.0.0.1:3000");HTTPServer(("127.0.0.1",3000),H).serve_forever()