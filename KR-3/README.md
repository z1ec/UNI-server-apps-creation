# KR-3

В папке собраны отдельные решения для заданий `6.1`–`6.5`.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Запуск

### Задание 6.1

```bash
uvicorn task_6_1:app --reload
```

### Задание 6.2

```bash
uvicorn task_6_2:app --reload
```

### Задание 6.3

```bash
uvicorn task_6_3:app --reload
```

### Задание 6.4

```bash
uvicorn task_6_4:app --reload
```

### Задание 6.5

```bash
uvicorn task_6_5:app --reload
```

## Проверка через curl

### 6.1

```bash
curl -i -u admin:qwerty http://localhost:8000/login
curl -i -u admin:wrong http://localhost:8000/login
```

### 6.2

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}'

curl -i -u user1:correctpass http://localhost:8000/login
curl -i -u user1:wrongpass http://localhost:8000/login
```

### 6.3

```bash
curl -i -u docs:docs123 http://localhost:8000/docs
curl -i http://localhost:8000/openapi.json
```

Для проверки `PROD`:

```bash
MODE=PROD uvicorn task_6_3:app --reload
curl -i http://localhost:8000/docs
```

### 6.4

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"securepassword123"}'

curl -H "Authorization: Bearer TOKEN" http://localhost:8000/protected_resource
```

### 6.5

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}'

curl -H "Authorization: Bearer TOKEN" http://localhost:8000/protected_resource
```
