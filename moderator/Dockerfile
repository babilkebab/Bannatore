FROM python:3.12-slim-bullseye

COPY moderator.py /app/moderator.py
COPY requirements.txt ./

RUN pip install -r requirements.txt --break-system-packages

ENTRYPOINT ["python", "/app/moderator.py"]