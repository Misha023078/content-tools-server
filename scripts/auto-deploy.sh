#!/bin/bash
# Автоматическое развёртывание content-tools-server

set -e

echo "🚀 Автоматическое развёртывание content-tools-server..."

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой папки проекта"
    exit 1
fi

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker compose down -v 2>/dev/null || true

# Очищаем Docker кэш
echo "🧹 Очищаем Docker кэш..."
docker system prune -f
docker builder prune -f

# Создаём конфигурационные файлы если их нет
echo "📝 Создаём конфигурационные файлы..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Создан .env из шаблона"
    echo "⚠️  ВАЖНО: Отредактируйте .env с вашими API ключами!"
fi

if [ ! -f "config.yaml" ]; then
    cp config.yaml.example config.yaml
    echo "✅ Создан config.yaml из шаблона"
fi

# Пробуем разные стратегии сборки
echo "🔨 Пробуем сборку с упрощённым Dockerfile..."

# Стратегия 1: Упрощённый Dockerfile
if [ -f "Dockerfile.simple" ]; then
    echo "📦 Используем упрощённый Dockerfile..."
    docker compose -f docker-compose.simple.yml build --no-cache
    if [ $? -eq 0 ]; then
        echo "✅ Сборка успешна с упрощённым Dockerfile"
        docker compose -f docker-compose.simple.yml up -d
        echo "🎉 Приложение запущено!"
        echo "📊 Проверьте статус: docker compose -f docker-compose.simple.yml ps"
        echo "📋 Логи: docker compose -f docker-compose.simple.yml logs -f"
        exit 0
    fi
fi

# Стратегия 2: Обычный Dockerfile с ретраями
echo "📦 Пробуем обычный Dockerfile с ретраями..."
docker compose build --no-cache
if [ $? -eq 0 ]; then
    echo "✅ Сборка успешна с обычным Dockerfile"
    docker compose up -d
    echo "🎉 Приложение запущено!"
    echo "📊 Проверьте статус: docker compose ps"
    echo "📋 Логи: docker compose logs -f"
    exit 0
fi

# Стратегия 3: Минимальные зависимости
echo "📦 Пробуем с минимальными зависимостями..."
if [ -f "requirements-minimal.txt" ]; then
    cp requirements-minimal.txt requirements.txt
    docker compose build --no-cache
    if [ $? -eq 0 ]; then
        echo "✅ Сборка успешна с минимальными зависимостями"
        docker compose up -d
        echo "🎉 Приложение запущено!"
        exit 0
    fi
fi

echo "❌ Все стратегии сборки не удались"
echo "💡 Попробуйте:"
echo "   1. Проверить интернет-соединение"
echo "   2. Запустить: docker compose logs"
echo "   3. Использовать готовый образ: docker pull python:3.11-slim"
exit 1
