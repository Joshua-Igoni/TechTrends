FROM python:2.7
LABEL maintainer="JoshBolten"
WORKDIR /app
COPY . /app
EXPOSE 3111
RUN pip install -r requirements.txt
RUN python init_db.py
CMD ["python", "app.py"]
