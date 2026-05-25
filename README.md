# 🩺 DermaSkan

<div align="center">

### Интеллектуальная система анализа кожных новообразований

#### Гибридная AI-архитектура на базе Vision Transformer + CNN

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p align="center">
  <b>AI-платформа для поддержки диагностики в дерматологии</b><br>
  Анализ изображений • Grad-CAM визуализация • ViT + CNN • FastAPI
</p>

</div>

---

# ✨ О проекте

**DermaSkan** — это интеллектуальная система поддержки принятия врачебных решений в области дерматологии, использующая современные методы компьютерного зрения и глубокого обучения для анализа кожных новообразований.

Проект сочетает:

* 🧠 **Vision Transformer (ViT)** для глобального анализа изображения
* 🔬 **CNN-архитектуры** для извлечения локальных признаков
* 🌡️ **Grad-CAM визуализацию** для интерпретации решений модели
* ⚡ **FastAPI backend** для высокопроизводительного inference API

Система предназначена как для исследовательских задач в области Medical AI, так и для практического применения в качестве инструмента поддержки врача.

---

# 🚀 Основные возможности

<div align="center">

| Возможность                          | Описание                                                 |
| :----------------------------------- | :------------------------------------------------------- |
| 🔍 **Бинарная классификация**        | Определение: злокачественное / доброкачественное         |
| 🧬 **Мультиклассовая классификация** | Меланома • Невус • Кератоз • Basal Cell Carcinoma        |
| 🌡️ **Grad-CAM визуализация**        | Подсветка областей изображения, влияющих на предсказание |
| 📊 **Интерпретируемый AI**           | Повышение прозрачности работы модели                     |
| ⚡ **Быстрый inference**              | Анализ изображения менее чем за 10 секунд                |
| 🐳 **Docker-ready**                  | Полная контейнеризация проекта                           |
| 📘 **REST API**                      | Интеграция с внешними сервисами                          |
| 🔐 **Система ролей**                 | Поддержка пользователей и прав доступа                   |

</div>

---

## 📸 Интерфейс приложения

<details open>
<summary>🔐 Авторизация</summary>

<img src="screenshots/login.png">

</details>

<details>
<summary>🩺 Анализ изображения</summary>

<img src="screenshots/analysis.png">

</details>

<details>
<summary>🧠 ML Models</summary>

<img src="screenshots/ml_models.png">

</details>

---

# 🛠️ Технологический стек

<div align="center">

| Backend     | ML/AI              | Frontend      | Infrastructure |
| ----------- | ------------------ | ------------- | -------------- |
| FastAPI     | PyTorch            | HTML5         | Docker         |
| Python 3.11 | Vision Transformer | TailwindCSS   | Docker Compose |
| SQLAlchemy  | CNN                | JavaScript    | PostgreSQL     |
| JWT Auth    | Grad-CAM           | Responsive UI | Nginx          |

</div>

---

# ⚙️ Быстрый старт

## 📋 Требования

Перед запуском убедитесь, что установлены:

* Docker
* Docker Compose
* Git

---

## 🔧 Установка

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

---

# 🌐 Доступ к сервисам

| Сервис            | URL                         |
| ----------------- | --------------------------- |
| 🖥️ Веб-интерфейс | `http://localhost`          |
| 📘 Swagger API    | `http://localhost/api/docs` |
| ❤️ Health Check   | `http://localhost/health`   |

---

# 🧠 ML-возможности

## Поддерживаемые задачи

### 🔍 Binary Classification

* Злокачественное / доброкачественное образование
* Меланома / не меланома

### 🧬 Multi-class Classification

* Melanoma
* Nevus
* Keratosis
* Basal Cell Carcinoma (BCC)

---

# 🌡️ Explainable AI

Проект использует **Grad-CAM** для визуализации внимания модели.

Это позволяет:

* интерпретировать предсказания нейросети;
* выделять области изображения, влияющие на результат;
* повышать доверие к AI-системе;
* помогать врачам в принятии решений.

---