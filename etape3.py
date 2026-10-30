import requests, pathlib, json, re

MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/chat"

SYSTEM = """Tu es agent prof React. Regle : AGIS, ne raconte pas.
Si question sur le cours, tu DOIS d'abord appeler l'outil lire_cours.
Ensuite tu reponds UNIQUEMENT d'apres le resultat de l'outil.
Si absent du cours, dis exactement : Hors-matiere - voir manuel."""

# --- BRAS Python (le LLM ne touche jamais le disque) ---
def lire_cours():
    return pathlib.Path("cours/react.txt").read_text(encoding="utf-8")

COURS_TXT = pathlib.Path("cours/react.txt").read_text(encoding="utf-8").lower()
def garde_hors_matiere(question):
    mots_q = [w.lower() for w in re.findall(r"[a-zA-Z]+", question) if len(w) > 4]
    return mots_q and not any(w in COURS_TXT for w in mots_q)

OUTIL_LIRE = {
    "type": "function",
    "function": {
        "name": "lire_cours",
        "description": "Lit le fichier cours/react.txt contenant la matiere React examen.",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
}

def chat(messages):
    r = requests.post(URL, json={
        "model": MODEL, "messages": messages,
        "stream": False, "tools": [OUTIL_LIRE],
        "options": {"temperature": 0.0}
    }, timeout=120)
    r.raise_for_status()
    return r.json()["message"]

def parse_secours(texte):
    # petit modele qui ecrit l'appel en TEXTE au lieu de tool_calls
    m = re.search(r'\{"name"\s*:\s*"lire_cours".*?\}', texte or "")
    if m: return [{"function": {"name": "lire_cours", "arguments": {}}}]
    return []

def run_agent(question):

    if garde_hors_matiere(question):
        print("[outil] lire_cours() [force par garde]")
        _ = lire_cours()
        return "Hors-matiere - voir manuel. (bloque par garde Python, concept absent de cours/react.txt)"

    history = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": question}
    ]
    for tour in range(5):
        msg = chat(history)
        history.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": msg.get("tool_calls")})
        calls = msg.get("tool_calls") or parse_secours(msg.get("content"))
        if not calls:
            return msg.get("content") or "(vide)"
        for c in calls:
            nom = c["function"]["name"]
            print(f"[outil] {nom}()")
            resultat = lire_cours() if nom == "lire_cours" else "outil inconnu"
            # 2 regles d'or : on renvoie TEL QUEL + meme id en role=tool
            history.append({"role": "tool", "content": resultat[:4000]})
    return "Abandon apres 5 tours."

if __name__ == "__main__":
    while True:
        q = input("\nQuestion React (vide=quitter) : ")
        if not q.strip(): break
        print("\n--- agent ---\n")
        print(run_agent(q))