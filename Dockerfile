FROM python:3.11

# Download ID is set as a space variable 
# By default it is a download of all Solanum preserved specimen records (c600K)
ARG GBIF_DOWNLOAD_ID=$GBIF_DOWNLOAD_ID
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD https://docs.google.com/uc?export=download&id=17mI5W0qiGiBp_RV1jy3QR3KtN7Ah-1Ha /code/ihinst.db

# Download GBIF occurrences and prepare for use with datasette
RUN mkdir /data
ADD https://api.gbif.org/v1/occurrence/download/request/${GBIF_DOWNLOAD_ID}.zip /data/gbif-occs.zip
RUN ls -l /data
RUN unzip /data/gbif-occs.zip -d /data
RUN ls -l /data
COPY ./tab2csv.py /code/tab2csv.py

## Setup to parse collector names using Bionomia utils (reqs Ruby)
## Install ruby
#RUN \
#  apt-get update && \
#  apt-get install -y ruby
#RUN gem install dwc_agent

#COPY ./extractcollectorname.py /code/extractcollectorname.py
RUN python tab2csv.py --createcols /data/${GBIF_DOWNLOAD_ID}.csv /data/gbifocc.csv 
#RUN python extractcollectorname.py /data/gbifocc-temp.csv /data/gbifocc.csv 
RUN csvs-to-sqlite /data/gbifocc.csv /code/gbifocc.db
RUN ls -l /code
RUN sqlite-utils tables /code/gbifocc.db --counts
RUN sqlite-utils enable-fts /code/gbifocc.db gbifocc collectorNameAndNumber

#RUN sqlite-utils tables /code/ihinst.db --counts
RUN chmod 755 /code/gbifocc.db

COPY ./metadata.json /code/metadata.json

CMD ["datasette", "/code/gbifocc.db", "-m", "/code/metadata.json", "--host", "0.0.0.0", "--port", "7860"]
