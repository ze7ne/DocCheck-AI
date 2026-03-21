#!/bin/bash

# ─── AI DocCheck — быстрый запуск ────────────────────────────

echo ""
echo "  DocCheck AI — Анализатор финансовых документов"
echo "  ───────────────────────────────────────────────"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "  [!] Python3 не найден. Установите Python 3.10+"
  exit 1
fi

# Backend dir
BACKEND_DIR="$(dirname "$0")/backend"
FRONTEND_DIR="$(dirname "$0")/frontend"

# Check .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
  if [ -f "$BACKEND_DIR/.env.example" ]; then
    echo "  [!] Файл .env не найден."
    echo "      Скопируйте: cp backend/.env.example backend/.env"
    echo "      Затем укажите ваш Gemini API ключ в backend/.env"
    echo ""
    exit 1
  fi
fi

# Install dependencies if needed
if [ ! -d "$BACKEND_DIR/venv" ]; then
  echo "  [*] Создаём виртуальное окружение..."
  python3 -m venv "$BACKEND_DIR/venv"
fi

echo "  [*] Активируем окружение и устанавливаем зависимости..."
source "$BACKEND_DIR/venv/bin/activate"
pip install -q -r "$BACKEND_DIR/requirements.txt"

echo "  [*] Запускаем сервер на http://localhost:8000"
echo "  [*] Открой frontend/index.html в браузере"
echo ""

# Open frontend in browser (macOS)
if command -v open &>/dev/null; then
  open "$FRONTEND_DIR/index.html"
fi

# Start backend
cd "$BACKEND_DIR"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
