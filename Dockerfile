FROM python:3.12

RUN mkdir -p /home/app
WORKDIR /home/app
COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "main.py" ]
