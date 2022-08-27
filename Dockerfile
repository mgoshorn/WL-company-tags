FROM python:3.9
WORKDIR /usr/src/app

RUN apt-get -q update && apt-get -qy install netcat

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src ./src
COPY ./wait-for-it.sh ./wait-for-it.sh
COPY ./wanted-temp-data.csv ./wanted-temp-data.csv
CMD [ "python", "./src/populate.py", "&&", "python", "./src/app.py"]
