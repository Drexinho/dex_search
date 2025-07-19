#!/bin/bash

echo "🚀 Instalace Dex Search - Offline RAG systém"
echo "=============================================="

# Kontrola Python verze
echo "📋 Kontrola Python verze..."
python3 --version || { echo "❌ Python 3 není nainstalován"; exit 1; }

# Kontrola Node.js verze
echo "📋 Kontrola Node.js verze..."
node --version || { echo "❌ Node.js není nainstalován"; exit 1; }

# Vytvoření virtuálního prostředí pro Python
echo "🐍 Vytváření Python virtuálního prostředí..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Instalace Python závislostí
echo "📦 Instalace Python závislostí..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Instalace Node.js závislostí
echo "📦 Instalace Node.js závislostí..."
cd frontend
npm install
cd ..

# Vytvoření potřebných složek
echo "📁 Vytváření složek pro data..."
mkdir -p backend/data/{documents,embeddings,config}
mkdir -p frontend/.nuxt

# Nastavení oprávnění
echo "🔐 Nastavování oprávnění..."
chmod +x install.sh
chmod +x start.sh

echo "✅ Instalace dokončena!"
echo ""
echo "📖 Pro spuštění aplikace použijte:"
echo "   ./start.sh"
echo ""
echo "📖 Nebo spusťte backend a frontend samostatně:"
echo "   Backend:  cd backend && python main.py"
echo "   Frontend: cd frontend && npm run dev" 