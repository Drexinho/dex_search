# Uživatelská příručka - Dex Search

## Přehled

Dex Search je offline RAG (Retrieval-Augmented Generation) systém pro vyhledávání v lokálních dokumentech. Aplikace kombinuje moderní AI modely s intuitivním rozhraním pro efektivní práci s dokumenty.

## Hlavní funkce

### 🔍 Inteligentní vyhledávání
- **Semantické vyhledávání** - Najde relevantní dokumenty i bez přesných klíčových slov
- **AI chat** - Ptejte se na obsah dokumentů přirozeným jazykem
- **Filtrování** - Omezujte vyhledávání podle složek, tagů nebo dat

### 📁 Správa dokumentů
- **Automatická indexace** - Dokumenty se indexují automaticky při změnách
- **Plánované zpracování** - Indexace probíhá v době nečinnosti systému
- **Tagování** - Organizujte dokumenty pomocí tagů

### ⚙️ Inteligentní plánování
- **Idle-aware scraping** - Zpracování pouze při nečinnosti systému
- **Konfigurovatelné časové okno** - Nastavte kdy má probíhat indexace
- **Systémové limity** - Kontrola CPU a RAM využití

## První kroky

### 1. Přidání složky

1. Přejděte na záložku **"Složky"**
2. Klikněte na **"Přidat složku"**
3. Zadejte cestu k složce s dokumenty
4. Nastavte tagy (např. "práce", "osobní")
5. Vyberte podporované formáty souborů
6. Klikněte na **"Přidat složku"**

### 2. První indexace

1. Po přidání složky klikněte na **"Indexovat"**
2. Počkejte na dokončení procesu
3. Zkontrolujte status v sekci "Poslední indexace"

### 3. Vyhledávání

1. Přejděte na záložku **"Vyhledávání"**
2. Zadejte dotaz do vyhledávacího pole
3. Klikněte na **"Vyhledat"** nebo stiskněte Enter
4. Prohlížejte výsledky a AI odpovědi

## Detailní průvodce

### Dashboard

Dashboard poskytuje přehled o stavu systému:

- **Sledované složky** - Počet aktivních složek
- **Celkem dokumentů** - Počet indexovaných souborů
- **Indexované chunky** - Počet textových segmentů
- **CPU využití** - Aktuální zatížení systému

### Správa složek

#### Přidání nové složky
1. Klikněte na **"Přidat složku"**
2. Vyplňte formulář:
   - **Cesta**: Absolutní cesta k složce
   - **Tagy**: Oddělené čárkami (např. "práce, 2024")
   - **Rekurze**: Zahrnout podsložky
   - **Formáty**: Vyberte podporované typy souborů

#### Nastavení složky
- **Zapnout/Vypnout**: Klikněte na ikonu oka
- **Indexovat nyní**: Manuální spuštění indexace
- **Upravit**: Změna nastavení složky
- **Odstranit**: Smazání složky z sledování

#### Status složky
- 🟢 **Indexováno** - Složka je aktuální
- 🟡 **Čeká na indexaci** - Změny nebyly zpracovány
- 🔴 **Chyba** - Problém při indexaci

### Vyhledávání

#### Základní vyhledávání
1. Zadejte dotaz do vyhledávacího pole
2. Výsledky se zobrazí automaticky
3. Klikněte na výsledek pro zobrazení kontextu

#### Pokročilé možnosti
- **Počet výsledků**: Nastavte limit (5-50)
- **AI chat**: Zapněte pro generování odpovědí
- **Filtry**: Omezte podle složek nebo tagů

#### Tipy pro vyhledávání
- Používejte přirozený jazyk: "Jak najít dokumenty o..."
- Kombinujte klíčová slova: "report 2024 finance"
- Používejte uvozovky pro přesné fráze: "kvalita produktu"

### Plánování

#### Nastavení časového okna
1. Přejděte na **"Plánování"**
2. Nastavte začátek a konec časového okna
3. Zapněte **"Pouze při nečinnosti"**
4. Nastavte limity CPU a RAM

#### Status plánování
- **Aktivní**: Plánování je zapnuté
- **Časové okno**: Kdy probíhá indexace
- **Systém idle**: Zda je systém nečinný
- **Zpracovávat nyní**: Zda lze spustit indexaci

#### Manuální akce
- **Test plánování**: Spusťte testovací indexaci
- **Pozastavit/Obnovit**: Dočasně vypněte plánování

### Nastavení

#### LLM modely
- **Phi-3 Mini**: Rychlý, pro slabší hardware
- **Mistral-7B**: Vyvážený výkon
- **Llama-3 8B**: Nejvyšší kvalita

#### Embedding modely
- **BGE Base EN**: Pro anglické dokumenty
- **All-MiniLM**: Rychlý, univerzální
- **Multilingual E5**: Pro vícejazyčné dokumenty

#### Vektorové databáze
- **ChromaDB**: Doporučená, jednoduchá
- **FAISS**: Rychlá, od Facebooku
- **Weaviate**: Pokročilá funkcionalita

## Klávesové zkratky

### Obecné
- `Ctrl + /` - Rychlé vyhledávání
- `Ctrl + K` - Otevření menu
- `Esc` - Zavření modálů

### Vyhledávání
- `Enter` - Spustit vyhledávání
- `Ctrl + Enter` - Spustit s AI chat
- `Tab` - Navigace mezi výsledky

## Řešení problémů

### Indexace nefunguje
1. Zkontrolujte oprávnění k složce
2. Ověřte podporované formáty
3. Zkontrolujte logy v nastavení

### Vyhledávání nefunguje
1. Ověřte, že jsou dokumenty indexované
2. Zkontrolujte připojení k backendu
3. Restartujte aplikaci

### Pomalé vyhledávání
1. Zkontrolujte systémové zdroje
2. Zmenšete počet výsledků
3. Vypněte AI chat pro rychlejší výsledky

### Chyby s modely
1. Zkontrolujte dostatek místa na disku
2. Ověřte internetové připojení pro stažení modelů
3. Zkuste jiný model v nastavení

## Tipy a triky

### Efektivní organizace
- Používejte konzistentní tagy
- Organizujte dokumenty do logických složek
- Pravidelně kontrolujte status indexace

### Optimalizace výkonu
- Nastavte vhodné časové okno pro indexaci
- Používejte menší modely na slabším hardware
- Pravidelně čistěte cache

### Pokročilé vyhledávání
- Kombinujte tagy s textovým vyhledáváním
- Používejte AI chat pro komplexní dotazy
- Využívejte historii vyhledávání

## Podpora

### Logy
- Backend logy: `backend/logs/`
- Frontend logy: Prohlížeč → Developer Tools → Console

### API dokumentace
- Dostupná na: http://localhost:8000/docs
- Interaktivní testování endpointů

### Kontakt
- GitHub Issues: Pro hlášení chyb
- Dokumentace: Podrobné technické informace 