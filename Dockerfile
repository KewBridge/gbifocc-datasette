FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD https://static.simonwillison.net/static/2023/history.db /code/history.db

RUN sqlite-utils tables /code/history.db --counts
RUN chmod 755 /code/history.db

COPY ./metadata.yml /code/metadata.yml

CMD ["datasette", "/code/history.db", "-m", "/code/metadata.yml", "--host", "0.0.0.0", "--port", "7860"]
