FROM python:3.11

WORKDIR /app    // this is the root directory inside the container which will contain the entrire project 


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . . // this command copies the entire local project directory to the current working directory in the container (which is /app)


EXPOSE 7860

CMD ["uvicorn", "Backend.api:app", "--host", "0.0.0.0", "--port", "7860"]