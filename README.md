# 🩺 DermaSkan

**DermaSkan** — это интеллектуальная система поддержки принятия врачебных решений в области дерматологии, использующая современные методы компьютерного зрения и глубокого обучения для анализа кожных новообразований.

Система предназначена как для исследовательских задач в области Medical AI, так и для практического применения в качестве инструмента поддержки врача.

# 🚀 Основные возможности

<div align="center">

| Возможность                          | Описание                                                 |
| :----------------------------------- | :------------------------------------------------------- |
| 🔍 **Бинарная классификация**        | Определение: злокачественное / доброкачественное         |
| 🧬 **Мультиклассовая классификация** | Меланома • Невус • Кератоз • Basal Cell Carcinoma        |
| 🌡️ **Grad-CAM визуализация**        | Подсветка областей изображения, влияющих на предсказание |
| 🔐 **Система ролей**                 | Поддержка пользователей и прав доступа                   |

</div>

## 📸 Интерфейс приложения
<img src="screenshots/login.png">
<img src="screenshots/analysis.png">
<img src="screenshots/prediction.png">
<img src="screenshots/ml_models.png">

# 🛠️ Технологический стек

<div align="center">

| Backend     | ML/AI              | Frontend      | Infrastructure |
| ----------- | ------------------ | ------------- | -------------- |
| FastAPI     | PyTorch            | HTML5         | Docker         |
| Python 3.11 | Vision Transformer | TailwindCSS   | Docker Compose |
| SQLAlchemy  | CNN                | JavaScript    | PostgreSQL     |
| JWT Auth    | Grad-CAM           | Responsive UI | Nginx          |

</div>

# ⚙️ Быстрый старт

### 1️⃣ Клонирование репозитория

```bash
git clone https://github.com/gigAntov3/derma-ml-skan.git
cd derma-ml-skan
```

### 2️⃣ Запуск проекта

```bash
docker-compose up -d
```

### 3️⃣ Настройка ролей пользователя

```bash
docker exec -it postgres-db psql -U derma_user -d derma_ml_db \
-c "INSERT INTO user_roles (user_id, role_id) VALUES (1, 4);"
```

# 🌐 Доступ к сервисам

| Сервис            | URL                         |
| ----------------- | --------------------------- |
| 🖥️ Веб-интерфейс | `http://localhost`          |
| 📘 Swagger API    | `http://localhost/api/docs` |
| ❤️ Health Check   | `http://localhost/api/health`   |