FROM python:3.10.9
RUN apt-get -y update \
    && apt-get install -y gettext git \
    # Cleanup apt cache
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry POETRY_VERSION=1.4.1 python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

ENV PYTHONUNBUFFERED=1

WORKDIR /zadanko
COPY poetry.lock pyproject.toml /zadanko/

ARG INSTALL_DEV=true
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install ; else poetry install --no-dev ; fi"

COPY /zadanko /zadanko

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
