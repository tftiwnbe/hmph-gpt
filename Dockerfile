FROM python:3.13-slim

RUN pip install --no-cache-dir watchdog

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DEVELOPMENT=false
ENV IN_CONTAINER=true

CMD ["bash", "-c", "if [ \"$DEVELOPMENT\" = \"true\" ]; then \
  cd bot && watchmedo auto-restart --patterns='*.py' --recursive -- python main.py; \
  else \
  cd bot && python main.py; \
  fi"]
