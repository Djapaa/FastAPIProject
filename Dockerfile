FROM python:3.10
LABEL authors="esteb"

WORKDIR /src


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Копируем зависимости
COPY requirements.txt requirements.txt

# Пробрасываем порт
EXPOSE 8000

#Создаем пользователя в ОС без пароля с именем service-user
RUN adduser --disabled-password service-user

#запуск команд будет под созданным пользователем
USER service-user

#Установка зависимостей
RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY src /src