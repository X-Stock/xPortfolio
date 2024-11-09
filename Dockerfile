FROM python:3.13 AS builder
WORKDIR /builer
RUN apt-get update && apt-get install -y libopenblas-dev
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml .
RUN pip download .
COPY setup.py .
COPY src src
RUN pip install .

FROM python:3.13-slim
LABEL authors="kim-minh"
EXPOSE 50051
RUN apt-get update && apt-get install -y libopenblas-dev
RUN groupadd --system --gid 1000 xstockai && useradd --system --uid 1000 --gid xstockai xstockai
COPY --from=builder --chown=xstockai:xstockai /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
USER xstockai
ENTRYPOINT ["xstockai"]