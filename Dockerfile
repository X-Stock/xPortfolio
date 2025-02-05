FROM python:3.13-slim AS builder
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /builer
RUN <<EOF
    apt-get update
    apt-get install -y git
    mkdir ~/.ssh
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts
EOF
RUN python -m venv /opt/venv && pip install --upgrade pip
COPY pyproject.toml .
RUN --mount=type=ssh pip download .
COPY src src
RUN --mount=type=ssh pip install .

FROM python:3.13-slim
LABEL authors="kim-minh"
EXPOSE 50051
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
RUN groupadd --system --gid 1000 xPortfolio && useradd --system --uid 1000 --gid xPortfolio xPortfolio
COPY --from=builder --chown=xPortfolio:xPortfolio /opt/venv /opt/venv
USER xPortfolio
ENTRYPOINT ["xPortfolio"]
