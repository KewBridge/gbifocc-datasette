FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

ADD https://drive.google.com/file/d/17mI5W0qiGiBp_RV1jy3QR3KtN7Ah-1Ha/view?usp=sharing /code/ihinst.db

RUN sqlite-utils tables /code/ihinst.db --counts
RUN chmod 755 /code/ihinst.db

COPY ./metadata.json /code/metadata.json

CMD ["datasette", "/code/ihinst.db", "-m", "/code/metadata.json", "--host", "0.0.0.0", "--port", "7860"]
