FROM python:alpine

EXPOSE 8000
VOLUME ["/data"]

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
