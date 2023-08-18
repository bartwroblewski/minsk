FROM python:3.9

WORKDIR /app

RUN pip install flask
RUN pip install flask-socketio
RUN pip install simple-websocket
RUN pip install gunicorn

COPY . .

ENV FLASK_APP=views.py

ENTRYPOINT ["python", "views.py"]