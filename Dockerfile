FROM python:3

ENV TZ Europe/Moscow
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

COPY . .

CMD [ "python", "./app.py" ]