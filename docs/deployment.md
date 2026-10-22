# StudyFlow — инструкция по запуску и развёртыванию

## 1. Требования

Для запуска проекта необходимы:

- Python 3.12;
- Git;
- pip;
- зависимости из файла `requirements.txt`.

Для облачного развёртывания используются Render, Gunicorn и PostgreSQL.

## 2. Получение проекта

Клонируйте репозиторий:

```powershell
git clone https://github.com/Anastasiks/SRS_7.git
cd SRS_7
```

## 3. Локальный запуск

### 3.1. Создание виртуального окружения

Выполните команды в PowerShell из корневой папки проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если PowerShell запрещает запуск сценария активации, можно использовать командную оболочку, в которой активация разрешена, либо выполнять Python через `.venv\Scripts\python.exe`.

### 3.2. Установка зависимостей

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3.3. Настройка окружения

Создайте файл `.env` на основе `.env.example` и укажите параметры локального запуска:

```text
DJANGO_SECRET_KEY=replace-with-a-new-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=
DATABASE_URL=
```

Замените демонстрационный ключ на случайный локальный ключ. Не публикуйте `.env` и реальные секреты в репозитории.

Настройки проекта читают переменные через `os.environ`. Если значения из `.env` не передаются в окружение автоматически, задайте их в терминале или настройках запуска IDE.

При отсутствии `DATABASE_URL` проект использует локальную базу SQLite `db.sqlite3`.

### 3.4. Проверка и миграции

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

Для создания административного пользователя:

```powershell
python manage.py createsuperuser
```

### 3.5. Запуск сервера разработки

```powershell
python manage.py runserver
```

Откройте в браузере:

- Главная страница: `http://127.0.0.1:8000/`
- Проекты: `http://127.0.0.1:8000/projects/`
- Задачи: `http://127.0.0.1:8000/tasks/`
- REST API: `http://127.0.0.1:8000/api/`
- Административная панель: `http://127.0.0.1:8000/admin/`

## 4. Развёртывание на Render

Адрес развёрнутого приложения:

`https://studyflow-bers.onrender.com`

### 4.1. Подготовка сервиса

В Render создайте или откройте Web Service, связанный с репозиторием GitHub.

Проверьте настройки сборки и запуска. Если проект использует соответствующие скрипты, укажите:

- Build Command: `./build.sh`
- Start Command: `./start.sh`

Команды должны соответствовать фактическому содержимому файлов `build.sh` и `start.sh` в репозитории.

### 4.2. Переменные окружения

В настройках Web Service в разделе Environment задайте следующие переменные:

| Переменная | Значение |
|---|---|
| `DJANGO_SECRET_KEY` | Случайный секретный ключ |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `studyflow-bers.onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://studyflow-bers.onrender.com` |
| `DATABASE_URL` | URL базы PostgreSQL, предоставленный Render |

Не сохраняйте реальные секреты в GitHub и не включайте их в документацию.

### 4.3. Подключение PostgreSQL

Создайте PostgreSQL-базу данных в Render и подключите её к Web Service.

Значение `DATABASE_URL` должно соответствовать адресу подключения, предоставленному Render. После настройки проверьте, что приложение использует именно облачную базу данных.

Локальная SQLite и PostgreSQL в Render являются разными базами. Данные из `db.sqlite3` автоматически не переносятся.

### 4.4. Проверка после развёртывания

После успешной сборки откройте:

- `https://studyflow-bers.onrender.com/`
- `https://studyflow-bers.onrender.com/projects/`
- `https://studyflow-bers.onrender.com/tasks/`
- `https://studyflow-bers.onrender.com/api/`
- `https://studyflow-bers.onrender.com/admin/`

Проверьте загрузку интерфейса, авторизацию, доступность API и выполнение операций с тестовыми данными.

Если приложение не запускается, изучите логи сборки и запуска в Render.

## 5. Диагностические команды

Для проверки конфигурации и состояния базы данных выполните:

```powershell
python manage.py check
python manage.py showmigrations
python manage.py migrate
python manage.py makemigrations --check --dry-run
```

Для проверки REST API можно использовать браузер, интерфейс DRF или инструмент отправки HTTP-запросов.

## 6. Воспроизводимость запуска

Для проверки воспроизводимости используйте чистый клон репозитория и новое виртуальное окружение.

Зафиксируйте результаты следующих проверок:

1. Установка зависимостей из `requirements.txt`.
2. Проверка проекта командой `python manage.py check`.
3. Применение миграций к чистой базе данных.
4. Запуск веб-сервера и открытие главной страницы.
5. Получение ответа от REST API.
6. Выполнение операции изменения данных и проверка результата.
7. Проверка доступности приложения после развёртывания на Render.

Скриншоты и фактические результаты проверок включите в отчёт по СРС №8. Не отмечайте проверку как успешную, пока она действительно не выполнена.

