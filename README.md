# fast-api-blogicum

# Полезные команды для работы с alembic

Перед запуском добавить файл .env 

SECRET_AUTH_KEY=SUPER_SECRET_KEY

```bash
# Показать текущую версию
alembic current

# Показать историю миграций
alembic history

# Откатиться на шаг назад
alembic downgrade -1

# Откатиться до конкретной ревизии
alembic downgrade <revision_id>

# Обновить до последней версии
alembic upgrade head

# Создать пустую миграцию вручную
alembic revision -m "add column to users"

# Показать SQL, который будет выполнен
alembic upgrade head --sql
```

