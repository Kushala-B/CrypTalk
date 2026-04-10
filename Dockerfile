FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn pydantic

EXPOSE 8000

CMD ["uvicorn","backend:app","--host","0.0.0.0","--port","8000"]