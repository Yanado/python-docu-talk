FROM python:3.10.13

EXPOSE 8080

WORKDIR /app

COPY .streamlit /app/.streamlit
COPY credentials /app/credentials
COPY src /app/src
COPY media /app/media
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY .env /app/.env

RUN pip install -r /app/requirements.txt

ENV PORT=8080

CMD streamlit run --server.port 8080 --server.enableCORS false app.py