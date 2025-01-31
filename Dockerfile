FROM python:3.12-slim AS builder
WORKDIR /builer
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml .
RUN pip download .
COPY setup.py .
COPY src src
RUN pip install .

FROM python:3.12-slim
LABEL authors="kim-minh"
EXPOSE 50051
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
RUN groupadd --system --gid 1000 xPortfolio && useradd --system --uid 1000 --gid xPortfolio xPortfolio
COPY --from=builder --chown=xPortfolio:xPortfolio /opt/venv /opt/venv
USER xPortfolio
ENTRYPOINT ["xportfolio"]