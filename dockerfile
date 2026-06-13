FROM python:3.11

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy full project
COPY . .

# expose HF port
EXPOSE 7860

# run fastapi
CMD ["uvicorn", "Backend.api:app", "--host", "0.0.0.0", "--port", "7860"]