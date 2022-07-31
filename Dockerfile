FROM python:alpine

EXPOSE 8000
VOLUME ["/data"]

WORKDIR /app
COPY . .

RUN apk update
RUN apk --no-cache add freetype-dev
RUN apk --no-cache add --virtual .builddeps gcc g++ && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .builddeps && rm -rf /var/cache/apk/*

ENTRYPOINT ["python", "main.py"]
