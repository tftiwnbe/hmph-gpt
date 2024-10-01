FROM python:3.12

WORKDIR /code

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "-m", "bot"]
