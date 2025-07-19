# Dex Search - Offline RAG systém pro lokální dokumenty

Kompletní offline RAG (Retrieval-Augmented Generation) systém s moderním GUI pro vyhledávání v lokálních dokumentech.

## 🚀 Funkce

- **Moderní GUI** - Nuxt UI s Tailwind CSS
- **Offline LLM** - Podpora pro Mistral-7B, Phi-3-mini a další
- **Inteligentní indexace** - Plánování, idle-aware scraping
- **Flexibilní správa složek** - Tagování, rekurze, formáty
- **RAG pipeline** - Embedding + vyhledávání + generování odpovědí
- **Vektorová DB** - ChromaDB pro rychlé vyhledávání

## 📁 Struktura projektu

```
Dex_search/
├── frontend/          # Nuxt UI aplikace
├── backend/           # Python FastAPI server
├── docs/             # Dokumentace
└── scripts/          # Pomocné skripty
```

## 🛠️ Rychlá instalace

### Automatická instalace
```bash
./install.sh
./start.sh
```

### Ruční instalace

#### Backend (Python)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python main.py
```

#### Frontend (Nuxt.js)
```bash
cd frontend
npm install
npm run dev
```

## 📖 Dokumentace

- [Instalace](docs/INSTALLATION.md) - Detailní instrukce pro instalaci
- [Uživatelská příručka](docs/USAGE.md) - Jak používat aplikaci
- [API dokumentace](http://localhost:8000/docs) - Po spuštění backendu

## 🎯 Použití

1. Spusťte aplikaci pomocí `./start.sh`
2. Otevřete http://localhost:3000 v prohlížeči
3. Přidejte složky k sledování
4. Nastavte plánování indexace
5. Začněte vyhledávat v dokumentech

## 📋 Podporované formáty

- PDF (.pdf)
- Word (.docx, .doc)
- Text (.txt)
- Markdown (.md)

## 🤖 Podporované LLM modely

- Mistral-7B-Instruct-v0.2
- Phi-3-mini-4k-instruct
- Meta-Llama-3-8B
- OpenChat-3.5-1210 