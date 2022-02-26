FROM python:3.9

RUN groupadd -r app && useradd -r -g app app

RUN mkdir /app && chown -R app:app /app/

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app/

WORKDIR /app

EXPOSE 8080

CMD ["python", "main.py"]
