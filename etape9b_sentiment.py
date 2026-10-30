from transformers import pipeline
print("Chargement distilbert (~250Mo, 1ere fois seulement)...")
clf = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
avis = [
    "I loved this React course, the quiz really helped!",
    "The correction was confusing and slow.",
    "J'ai adore le quiz React !",  # piege volontaire
]
for a in avis:
    r = clf(a)[0]
    print(f"{a!r}\n  -> {r['label']} ({r['score']:.2f})\n")
print("Note : modele anglais -> 3e avis peu fiable. Le fine-tuning FR (votre quiz_react.jsonl) corrigerait ca.")