# OrnelBot – Chatbot personnel avec Streamlit & Groq

[![CI/CD](https://github.com/orneldreams/ornelbot/actions/workflows/main.yml/badge.svg)](https://github.com/orneldreams/ornelbot/actions)

Bienvenue sur **OrnelBot**, un assistant intelligent développé par **Ornel Rony DIFFO**.  
Ce chatbot est un projet personnel interactif, stylisé avec CSS, propulsé par l'API **Groq** (LLaMA 3) et conçu avec **Streamlit**.

---

## Objectif

Créer une interface responsive et interactive pour permettre à un visiteur de poser des questions à une IA représentant Ornel.  
L'interface se veut claire, fluide et personnalisée, avec un style inspiré de ChatGPT.

---

## Fonctionnalités

- Interface conversationnelle stylisée  
- Mémoire temporaire des échanges (stateless avec session)  
- Génération des réponses via Groq `llama3-70b-8192`  
- Avatar centré, avec affichage dans les réponses  
- Liens vers les profils [GitHub](https://github.com/orneldreams) et [LinkedIn](https://www.linkedin.com/in/ornel-rony-d-01737b267/)  
- Footer dynamique et citation personnelle  
- Workflow CI/CD GitHub Actions intégré  

---

## Démo

Lancer l'application en local :

```bash
git clone https://github.com/orneldreams/ornelbot.git
cd ornelbot
pip install -r requirements.txt
streamlit run app.py
```

ornelbot/  
│  
├── app.py                  # Application principale  
├── profile.json            # Profil d’Ornel (bio, vision, etc.)  
├── .env                    # Clé API Groq (non versionné)  
│  
├── core/  
│   ├── groq_client.py      # Appel à l'API Groq  
│   └── prompt_builder.py   # Construction des prompts  
│  
├── assets/  
│   └── avatar.png          # Avatar affiché à l'écran  
│  
├── style/  
│   └── style.css           # Personnalisation CSS  
│  
└── README.md               # Fichier de présentation  

---

## Documentation

### Liens utiles

- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Groq API Reference](https://console.groq.com/docs)  
- [CSS Styling dans Streamlit](https://docs.streamlit.io/develop/concepts/layout-and-style/customizing)  
- [Python `os` module](https://docs.python.org/3/library/os.html)  
- [Python `dotenv`](https://pypi.org/project/python-dotenv/)  
- [Pillow (PIL)](https://pillow.readthedocs.io/)  
- [GitHub Actions](https://docs.github.com/en/actions)  
- [LLaMA 3 Model (Groq)](https://www.groq.com/blog/llama3-now-available-on-groqcloud)  

---

### Exemple d’utilisation

> **User** : « Que fais-tu en ce moment ? »  
> **Bot** : « En ce moment, je travaille sur l’optimisation d’un robot suiveur de ligne basé sur STM32. »

---

### Profil dynamique

Le bot utilise le fichier `profile.json` pour adapter :

- Son ton (humain, structuré, passionné)  
- Son historique de projets et compétences  
- Ses anecdotes et objectifs  
- Sa citation inspirante  

---

## Technologies

| Outil / Lib        | Usage                                 |
|--------------------|----------------------------------------|
| Streamlit          | Interface web interactive              |
| Groq API           | Génération IA (LLaMA 3)                |
| Python             | Backend / logique                      |
| CSS                | Stylisation custom                     |
| dotenv             | Gestion des variables d’environnement  |
| Pillow (PIL)       | Affichage & traitement de l’avatar     |
| GitHub Actions     | CI/CD automatique                      |

---

## Auteur

**Ornel Rony DIFFO**  
Étudiant en M1 à l’ESIEA, passionné par les systèmes embarqués, l’IA, la data et la supervision.

- [LinkedIn](https://www.linkedin.com/in/ornel-rony-d-01737b267/)  
- [GitHub](https://github.com/orneldreams)
