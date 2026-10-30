import requests

MODEL = "llama3.2:latest"
#URL = "http://localhost:11434/api/chat"
URL = "http://127.0.0.1:11434/api/chat"

SYSTEM = "Tu es prof React au College LaSalle. Reponds en francais concis, avec 1 petit exemple de code."

def poser(question):
    r = requests.post(URL, json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question}
        ],
        "stream": False,
        "options": {"temperature": 0.2}
    }, timeout=120)
    r.raise_for_status()
    return r.json()["message"]["content"]

if __name__ == "__main__":
    q = input("Question React [defaut: Explique useState avec exemple simple] : ")
    if not q.strip():
        q = "Explique useState en React avec un exemple simple de compteur."
    print("\n--- reponse ---\n")
    print(poser(q))