# Instalace Dex Search

## Požadavky

### Systémové požadavky
- **OS**: Linux, macOS, nebo Windows
- **Python**: 3.8 nebo novější
- **Node.js**: 16 nebo novější
- **RAM**: Minimálně 4GB (8GB doporučeno)
- **Disk**: Minimálně 2GB volného místa

### Hardware pro LLM
- **Minimální**: 8GB RAM, 4 jádra CPU
- **Doporučené**: 16GB RAM, 8 jader CPU
- **GPU**: Volitelné, ale zrychluje zpracování

## Rychlá instalace

### 1. Klonování repozitáře
```bash
git clone <repository-url>
cd Dex_search
```

### 2. Automatická instalace
```bash
./install.sh
```

### 3. Spuštění aplikace
```bash
./start.sh
```

Aplikace bude dostupná na:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000

## Ruční instalace

### Backend (Python)

1. **Vytvoření virtuálního prostředí**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# nebo
venv\Scripts\activate     # Windows
```

2. **Instalace závislostí**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Spuštění backendu**
```bash
python main.py
```

### Frontend (Nuxt.js)

1. **Instalace závislostí**
```bash
cd frontend
npm install
```

2. **Spuštění vývojového serveru**
```bash
npm run dev
```

## Konfigurace

### Backend konfigurace

Vytvořte soubor `backend/.env`:
```env
# Základní nastavení
APP_NAME=Dex Search
DEBUG=true

# LLM modely
DEFAULT_LLM_MODEL=microsoft/phi-3-mini-4k-instruct
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Vektorová DB
VECTOR_DB_TYPE=chromadb

# Plánování
DEFAULT_SCHEDULE_START=23:00
DEFAULT_SCHEDULE_END=07:00
DEFAULT_CPU_THRESHOLD=30
DEFAULT_RAM_THRESHOLD=50
```

### Frontend konfigurace

Vytvořte soubor `frontend/.env`:
```env
# API konfigurace
API_BASE=http://localhost:8000
```

## První spuštění

1. **Spusťte aplikaci**
```bash
./start.sh
```

2. **Otevřete prohlížeč**
Přejděte na http://localhost:3000

3. **Přidejte první složku**
- Klikněte na "Složky" v navigaci
- Klikněte na "Přidat složku"
- Zadejte cestu k složce s dokumenty
- Nastavte tagy a formáty
- Klikněte na "Přidat složku"

4. **Spusťte první indexaci**
- Klikněte na "Indexovat" u přidané složky
- Počkejte na dokončení indexace

5. **Začněte vyhledávat**
- Přejděte na "Vyhledávání"
- Zadejte dotaz a klikněte na "Vyhledat"

## Řešení problémů

### Backend se nespustí
```bash
# Kontrola Python verze
python3 --version

# Kontrola závislostí
cd backend
pip list

# Spuštění s debug informacemi
python main.py --debug
```

### Frontend se nespustí
```bash
# Kontrola Node.js verze
node --version

# Vymazání cache
cd frontend
rm -rf node_modules .nuxt
npm install
```

### Chyby s LLM modely
```bash
# Stažení modelu manuálně
cd backend
python -c "from transformers import AutoTokenizer, AutoModel; AutoTokenizer.from_pretrained('microsoft/phi-3-mini-4k-instruct')"
```

### Problémy s oprávněními
```bash
# Nastavení oprávnění
chmod +x install.sh start.sh
chmod -R 755 backend/data
```

## Vývoj

### Backend vývoj
```bash
cd backend
source venv/bin/activate
python main.py --reload
```

### Frontend vývoj
```bash
cd frontend
npm run dev
```

### API dokumentace
Po spuštění backendu je dostupná na:
http://localhost:8000/docs

## Podporované formáty

- **PDF** (.pdf) - Portable Document Format
- **Word** (.docx, .doc) - Microsoft Word dokumenty
- **Text** (.txt) - Prosté textové soubory
- **Markdown** (.md) - Markdown dokumenty

## LLM modely

### Doporučené modely
- **Phi-3 Mini** (3.8B) - Rychlý, efektivní
- **Mistral-7B** (7B) - Dobrý poměr výkon/cena
- **Llama-3 8B** (8B) - Vysoce kvalitní

### Embedding modely
- **BGE Base EN** - Pro anglické dokumenty
- **All-MiniLM** - Rychlý, univerzální
- **Multilingual E5** - Pro vícejazyčné dokumenty 