#!/bin/bash

echo "🚀 Spouštím Dex Search v Docker kontejneru..."

# Spuštění Ollama v pozadí
echo "📦 Spouštím Ollama..."
ollama serve &
OLLAMA_PID=$!

# Počkat na Ollama
echo "⏳ Čekám na Ollama..."
sleep 10

# Stažení potřebných modelů
echo "📥 Stahuji AI modely..."
ollama pull nomic-embed-text:latest &
ollama pull llama3.2:3b &
wait

# Spuštění backendu
echo "🐍 Spouštím Python backend..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Počkat na backend
echo "⏳ Čekám na backend..."
sleep 5

# Spuštění frontendu
echo "🌐 Spouštím Nuxt frontend..."
cd ../frontend
npm run preview &
FRONTEND_PID=$!

echo "✅ Všechny služby jsou spuštěny!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "🤖 Ollama: http://localhost:11434"

# Funkce pro ukončení
cleanup() {
    echo "🛑 Ukončuji služby..."
    kill $BACKEND_PID $FRONTEND_PID $OLLAMA_PID 2>/dev/null
    exit 0
}

# Zachytit SIGTERM a SIGINT
trap cleanup SIGTERM SIGINT

# Čekat na ukončení
wait 