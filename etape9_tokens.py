from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("gpt2")  # ~500Ko, rapide
phrases = [
    "const [count, setCount] = useState(0);",
    "Quand le cours TendancesTechnologiques ?",
    "Lundi 08h-12h avec Mourad Sehboub",
]
for p in phrases:
    ids = tok.encode(p)
    print(f"{p!r}\n  -> {len(ids)} tokens : {ids[:12]}...\n  -> decode : {tok.decode(ids[:8])!r}\n")
print("Lien atelier : NUM_CTX=8192 tokens max, vos 12000 car. cours sont tronques. D'ou passages_utiles().")