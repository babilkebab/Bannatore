FROM python:3.12-slim-bullseye

COPY message_picker.py /app/message_picker.py
COPY requirements.txt ./

RUN pip install -r requirements.txt --break-system-packages

ENTRYPOINT ["python", "/app/message_picker.py"]
