FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install pyTelegramBotAPI

CMD ["python", "main.py"]