import requests, pathlib, re, random

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"
def lire_cours(): return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")
COURS_TXT = lire_cours().lower()
SYSTEM = "Tu es agent prof React. Pour le cours utilise l'outil lire_cours. Sinon: Hors-matiere."
OUTIL=[{"type":"function","function":{"name":"lire_cours","description":"Lit cours/react.txt","parameters":{"type":"object","properties":{},"required":[]}}}]

# --- BANQUE QUIZ = VOTRE matiere, pas la memoire du LLM ---
QUIZ = [
    {"q":"Pour modifier count avec useState, on fait ?","choix":["A) count=count+1","B) setCount(count+1)","C) update(count)"],"rep":"B"},
    {"q":"useEffect(()=>{...},[count]) se relance quand ?","choix":["A) a chaque fois","B) quand count change","C) jamais"],"rep":"B"},
    {"q":"Props sert a ?","choix":["A) parent->enfant","B) enfant->parent","C) rien"],"rep":"A"},
    {"q":"Un composant React s'ecrit ?","choix":["A) function Carte(){return <div/>}","B) function carte(){return}","C) <div>carte</div>"],"rep":"A"},
]
actif = None

def run_quiz():
    global actif
    actif = random.sample(QUIZ, 2)
    txt = "QUIZ React (reponds ex: 1B 2A) :\n"
    for i,x in enumerate(actif,1):
        txt += f"\n{i}. {x['q']}\n   " + "\n   ".join(x["choix"]) + "\n"
    return txt

def corrige_quiz(rep_user):
    global actif
    lettres = re.findall(r"[ABC]", rep_user.upper())
    if not actif or len(lettres) < len(actif): return "Reponds ex: 1B 2A"
    score = sum(1 for i,x in enumerate(actif) if lettres[i]==x["rep"])
    detail = " ".join([f"{i+1}:{lettres[i]}={'OK' if lettres[i]==x['rep'] else 'NON->'+x['rep']}" for i,x in enumerate(actif)])
    actif = None
    return f"Score {score}/2 - {detail}"

def run_agent(q):
    ql = q.lower()
    # PORTE DE DECISION = entrainement par regle
    if "quiz" in ql or "qcm" in ql or "teste" in ql:
        print("[outil] generer_quiz() [regle Python]")
        return run_quiz()
    if actif and re.search(r"[ABC]", q.upper()):
        print("[outil] verifier_reponse() [regle Python]")
        return corrige_quiz(q)
    r = requests.post(URL, json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q}],"stream":False,"tools":OUTIL,"options":{"temperature":0.0}},timeout=120).json()["message"]
    if r.get("tool_calls"):
        print("[outil] lire_cours()")
        c = lire_cours()
        r2 = requests.post(URL, json={"model":MODEL,"messages":[{"role":"system","content":SYSTEM},{"role":"user","content":q},{"role":"assistant","content":"","tool_calls":r["tool_calls"]},{"role":"tool","content":c[:4000]}],"stream":False,"options":{"temperature":0.0}},timeout=120).json()["message"]
        return r2.get("content")
    return r.get("content")

if __name__ == "__main__":
    print("Commandes: 'donne-moi un quiz' puis '1B 2A'")
    while True:
        q = input("\n> ")
        if not q.strip(): break
        print(run_agent(q))