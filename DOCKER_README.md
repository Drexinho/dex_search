# Dex Search - Docker verze

Tato verze obsahuje celou aplikaci v Docker kontejneru včetně Ollama AI modelů.

## 🐳 Rychlé spuštění

### 1. Build Docker image
```bash
docker build -t dex-search:latest .
```

### 2. Spuštění s docker-compose (doporučeno)
```bash
docker-compose up -d
```

### 3. Nebo spuštění s Docker run
```bash
docker run -d \
  --name dex-search \
  -p 8000:8000 \
  -p 3000:3000 \
  -p 11434:11434 \
  -v dex_data:/home/dexuser/data \
  -v ollama_data:/home/dexuser/.ollama \
  dex-search:latest
```

## 🌐 Přístup k aplikaci

Po spuštění bude aplikace dostupná na:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Ollama API**: http://localhost:11434

## 📁 Persistentní data

Aplikace používá Docker volumes pro ukládání dat:
- `dex_data`: Dokumenty, embeddings, konfigurace
- `ollama_data`: AI modely a cache

## 🔧 Správa

### Zastavení
```bash
docker-compose down
```

### Logy
```bash
docker-compose logs -f
```

### Restart
```bash
docker-compose restart
```

### Aktualizace
```bash
docker-compose pull
docker-compose up -d
```

## 🚀 První spuštění

Při prvním spuštění se automaticky:
1. Stáhnou AI modely (nomic-embed-text, llama3.2:3b)
2. Spustí všechny služby
3. Vytvoří databázi

Může to trvat několik minut.

## 🔍 Použití

1. Otevřete http://localhost:3000
2. Přejděte na "Files" pro procházení dokumentů
3. Přejděte na "AI Search" pro vyhledávání
4. Přejděte na "Ollama AI Search" pro AI vyhledávání

## 🛠️ Troubleshooting

### Kontrola stavu
```bash
docker-compose ps
```

### Kontrola logů
```bash
docker-compose logs dex-search
```

### Restart služeb
```bash
docker-compose restart dex-search
```

### Vyčištění dat
```bash
docker-compose down -v
docker-compose up -d
```

## 📦 Docker Hub

Pro stažení z Docker Hub:
```bash
docker pull yourusername/dex-search:latest
```

## 🔐 Bezpečnost

- Aplikace běží jako neprivilegovaný uživatel `dexuser`
- Porty jsou omezené na localhost
- Data jsou persistentní přes Docker volumes 