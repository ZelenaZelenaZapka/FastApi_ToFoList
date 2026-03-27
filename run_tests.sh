#!/bin/bash

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 Запуск тестів...${NC}\n"

# Перевіряємо, чи встановлено pytest
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest не встановлено!${NC}"
    echo "Установи: pip install pytest pytest-asyncio httpx"
    exit 1
fi

# Перевіряємо, чи існує файл .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env не знайдено, використовуємо SQLite для тестів${NC}\n"
fi

# Запускаємо тести
pytest tests/ -v --tb=short

# Отримуємо код виходу
TEST_RESULT=$?

# Виводимо результат
echo -e "\n${YELLOW}════════════════════════════════════${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Tests passed! Ready for deploy${NC}"
    echo -e "${GREEN}🚀 Готово до deploy на Render${NC}"
else
    echo -e "${RED}❌ Tests failed! Deploy blocked${NC}"
    echo -e "${RED}🛑 Виправ помилки перед deploy${NC}"
fi
echo -e "${YELLOW}════════════════════════════════════${NC}\n"

exit $TEST_RESULT