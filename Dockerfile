FROM python:3.11-slim AS builder

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=1
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx
ENV PATH="/root/.local/bin:${PATH}"
RUN pipx install poetry==1.8.4
COPY . .
RUN poetry lock --no-update
RUN poetry install --only main --no-root 

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes \
    libopencv-dev python3-opencv libmagic1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /app /app
EXPOSE 8282
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8282"]
