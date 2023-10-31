FROM python:3.11


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD https://docs.google.com/uc?export=download&id=17mI5W0qiGiBp_RV1jy3QR3KtN7Ah-1Ha /code/ihinst.db

# Download GBIF occurrences and prepare for use with datasette
RUN mkdir /data
ADD https://api.gbif.org/v1/occurrence/download/request/0032228-231002084531237.zip /data/gbif-occs.zip
RUN ls -l /data
RUN unzip /data/gbif-occs.zip -d /data
RUN ls -l /data
RUN csvs-to-sqlite /data/0032228-231002084531237.csv /code/gbifocc.db
RUN ls -l /code
RUN sqlite-utils tables /code/gbifocc.db --counts

RUN sqlite-utils tables /code/ihinst.db --counts
RUN chmod 755 /code/ihinst.db

COPY ./metadata.json /code/metadata.json

CMD ["datasette", "/code/ihinst.db", "-m", "/code/metadata.json", "--host", "0.0.0.0", "--port", "7860"]
