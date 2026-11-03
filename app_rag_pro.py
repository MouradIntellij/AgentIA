"""
APP RAG PRO - TechWeek (Version Optimisée)
Utilise PyTorch + Sentence-Transformers pour une recherche sémantique.
Correction : Gestion du bruit sémantique pour différencier les types de 'mémoire'.
"""
import pathlib, re, json, os, requests, sys
import torch 
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from sentence_transformers import SentenceTransformer, util

# ---------- CONFIGURATION ----------
MODEL_LLM = "llama3.2:latest"
URL_LLM = "http://127.0.0.1:11434/api/chat"
# Modèle PyTorch pour les embeddings
MODEL_EMBED = 'all-MiniLM-L6-v2' 

print("\n--- INITIALISATION DU MOTEUR PYTORCH ---")
try:
    print(f"Chargement du modèle sémantique {MODEL_EMBED}...")
    embedder = SentenceTransformer(MODEL_EMBED)
    print("✅ Modèle PyTorch chargé avec succès.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    sys.exit()

def RACINE():
    return pathlib.Path(".")

# ---------- LECTURE DOCUMENTS ----------
def lire_docx(path):
    try:
        import zipfile
        x = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        return re.sub(r"<[^>]+>", "", re.sub(r"</w:p[^>]*>", "\n", x))
    except: return ""

def lire_pdf(path):
    try:
        from pypdf import PdfReader
        txt = "\n".join([(p.extract_text() or "") for p in PdfReader(str(path)).pages])
        return txt
    except Exception as e: 
        return f"[Erreur PDF: {e}]"

def charger_base_connaissance():
    """Découpe les documents en fragments pour l'IA"""
    corpus = []
    sources = []
    
    for d in sorted((RACINE() / "cours").rglob("*.docx")):
        txt = lire_docx(d)
        for p in txt.split('\n'):
            if len(p.strip()) > 40: 
                corpus.append(p.strip())
                sources.append(d.name)
                
    for p in sorted((RACINE() / "cours").rglob("*.pdf")):
        txt = lire_pdf(p)
        for para in txt.split('\n'):
            if len(para.strip()) > 40: 
                corpus.append(para.strip())
                sources.append(p.name)
    
    txt_file = RACINE() / "cours" / "react.txt"
    if txt_file.exists():
        txt = txt_file.read_text(encoding="utf-8")
        for p in txt.split('\n'):
            if len(p.strip()) > 40:
                corpus.append(p.strip())
                sources.append("react.txt")

    return corpus, sources

# --- INDEXATION SÉMANTIQUE ---
print("Indexation sémantique des documents en cours...")
CORPUS, SOURCES = charger_base_connaissance()

if not CORPUS:
    print("❌ Aucun document trouvé dans le dossier 'cours/'.")
    sys.exit()

# Transformation du texte en vecteurs PyTorch
CORPUS_EMBEDDINGS = embedder.encode(CORPUS, convert_to_tensor=True)
print(f"✅ Indexation terminée. {len(CORPUS)} fragments indexés.")

# ---------- RECHERCHE SÉMANTIQUE (Optimisée) ----------
def recherche_semantique(question, top_k=5):
    """Calcule la similarité cosinus et récupère les meilleurs fragments"""
    question_embedding = embedder.encode(question, convert_to_tensor=True)
    cos_scores = util.cos_sim(question_embedding, CORPUS_EMBEDDINGS)[0]
    
    # Récupération des top K résultats
    top_results = torch.topk(cos_scores, k=min(top_k, len(CORPUS)))
    
    resultats = []
    for score, idx in zip(top_results[0], top_results[1]):
        # SEUIL ABAISSÉ à 0.20 pour capturer plus de fragments potentiels
        if score > 0.20: 
            resultats.append(f"[{SOURCES[idx]}] {CORPUS[idx]}")
    
    return "\n\n".join(resultats) if resultats else "Aucun passage pertinent trouvé."

# ---------- AGENT IA ----------
def run_agent_rag(q):
    # 1. Recherche sémantique (on demande 5 fragments pour éviter de rater le bon)
    ctx = recherche_semantique(q, top_k=5)
    
    # --- DEBUG TERMINAL : Indispensable pour voir ce que PyTorch a trouvé ---
    print("\n" + "="*50)
    print(f"QUESTION : {q}")
    print("FRAGMENTS RÉCUPÉRÉS PAR PYTORCH :")
    print("-" * 30)
    print(ctx)
    print("="*50 + "\n")
    
    # 2. Prompt strict pour éviter la confusion 'Mémoire Liste' vs 'Mémoire État'
    system_prompt = (
        "Tu es un tuteur pédagogique expert. Analyse les fragments de cours fournis.\n"
        "CONSIGNE CRITIQUE : Ne confonds pas la 'mémoire d'une liste/clé' avec le 'stockage d'une valeur (useState)'.\n"
        "Si la question porte sur comment garder une valeur en mémoire, utilise impérativement le passage sur useState.\n"
        "Réponds UNIQUEMENT en utilisant les sources. Si rien n'est pertinent, dis 'Hors-matière'.\n\n"
        f"SOURCES :\n{ctx}"
    )
    
    try:
        r = requests.post(URL_LLM, json={
            "model": MODEL_LLM,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": q}
            ],
            "stream": False,
            "options": {"temperature": 0.0}
        }, timeout=120).json()
        
        reponse = r["message"]["content"]
        return {"type": "cours", "txt": f"[Moteur PyTorch Sémantique]\n\n{reponse}"}
    except Exception as e:
        return {"type": "error", "txt": f"Erreur LLM: {e}"}

# ---------- INTERFACE WEB ----------
PAGE = """<!DOCTYPE html><html lang=fr><head><meta charset=utf-8><title>RAG PRO - PyTorch</title>
<style>
    body{font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width:800px; margin:40px auto; background:#f0f2f5; color:#333} 
    .box{background:white; padding:30px; border-radius:20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1)}
    h1{color:#007bff; text-align:center}
    .subtitle{text-align:center; color:#666; margin-bottom:30px}
    .input-group{display:flex; gap:10px; margin-bottom:20px}
    input{flex:1; padding:12px; border:1px solid #ddd; border-radius:8px; font-size:16px} 
    button{padding:12px 24px; background:#007bff; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold}
    button:hover{background:#0056b3}
    pre{background:#1e1e1e; color:#dcdcdc; padding:20px; border-radius:12px; white-space:pre-wrap; min-height:100px; font-size:15px; line-height:1.5; border-left: 5px solid #007bff}
</style>
</head><body><div class='box'>
<h1>🚀 Agent RAG Pro (PyTorch)</h1>
<p class='subtitle'>Recherche sémantique : je comprends le sens, pas juste les mots-clés.</p>
<div class='input-group'>
    <input id='q' placeholder='Ex: Comment garder une valeur en mémoire ?'>
    <button onclick='ask()'>Envoyer</button>
</div>
<pre id='r'>En attente de votre question...</pre>
</div>
<script>
async function ask(){
    let r=document.getElementById('r'); 
    let q=document.getElementById('q').value;
    if(!q) return;
    r.textContent='Calcul sémantique PyTorch et génération de la réponse...';
    try {
        let j=await fetch('/api',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({q:q})
        }).then(res=>res.json());
        r.textContent=j.txt;
    } catch(e) {
        r.textContent='Erreur de connexion au serveur.';
    }
}
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(PAGE.encode('utf-8'))

    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        d = json.loads(self.rfile.read(n).decode('utf-8'))
        out = run_agent_rag(d.get('q', ''))
        b = json.dumps(out).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a): pass

if __name__ == "__main__":
    print("\n🚀 Lancement de l'Agent RAG PRO sur http://127.0.0.1:3000")
    print("Tuez tout processus Python avant de relancer si le port est occupé.")
    ThreadingHTTPServer(("127.0.0.1", 3000), H).serve_forever()