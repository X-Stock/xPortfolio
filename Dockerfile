FROM python:3.13-slim AS base
ENV PATH="/opt/venv/bin:$PATH"

FROM base AS builder
WORKDIR /builer
RUN <<EOF
    apt-get update
    apt-get install -y git
    mkdir ~/.ssh
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts
EOF
RUN python -m venv /opt/venv
COPY pyproject.toml .
RUN --mount=type=ssh <<EOT
    pip install --upgrade pip
    pip download .
EOT
COPY src src
RUN --mount=type=ssh pip install .

FROM base
LABEL authors="kim-minh"
EXPOSE 50051
ENV PYTHONUNBUFFERED=1
RUN groupadd --system xPortfolio && useradd -l --system --gid xPortfolio xPortfolio
COPY --from=builder --chown=xPortfolio:xPortfolio /opt/venv /opt/venv
USER xPortfolio
ENTRYPOINT ["xPortfolio"]
