FROM python:3.11

# Download ID is set as a space variable 
# By default it is a download of all Solanum preserved specimen records (c600K)
ARG GBIF_DOWNLOAD_ID=$GBIF_DOWNLOAD_ID
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Download GBIF occurrences and prepare for use with datasette
RUN mkdir /data
ADD https://api.gbif.org/v1/occurrence/download/request/${GBIF_DOWNLOAD_ID}.zip /data/gbif-occs.zip
RUN ls -lh /data
RUN unzip /data/gbif-occs.zip -d /data
RUN ls -lh /data
COPY ./tab2csv.py /code/tab2csv.py


RUN python tab2csv.py --createcols /data/${GBIF_DOWNLOAD_ID}.csv /data/gbifocc.csv 
RUN csvs-to-sqlite /data/gbifocc.csv /code/gbifocc.db
RUN ls -l /code
RUN sqlite-utils tables /code/gbifocc.db --counts
RUN sqlite-utils enable-fts /code/gbifocc.db gbifocc collectorNameAndNumber
RUN chmod 755 /code/gbifocc.db

# Create datasette metadata file
COPY ./getDownloadMetadata.py /code/getDownloadMetadata.py
COPY ./metadata.json /code/metadata.json
RUN python getDownloadMetadata.py /code/metadata.json /code/metadata.json --download_id=$GBIF_DOWNLOAD_ID

CMD ["datasette", "/code/gbifocc.db", "-m", "/code/metadata.json", "--host", "0.0.0.0", "--port", "7860"]
