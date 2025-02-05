FROM python:3.13-slim AS builder
WORKDIR /builer
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY pyproject.toml .
RUN apt-get update && apt-get install git openssh-client
RUN --mount=type=ssh <<EOT
    mkdir ~/.ssh
    ssh-keyscan -H github.com >> ~/.ssh/known_hosts
    ssh-add -l
EOT
RUN pip install --upgrade pip && pip download .
COPY src src
RUN pip install .

FROM python:3.13-slim
LABEL authors="kim-minh"
EXPOSE 50051
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
RUN groupadd --system --gid 1000 xPortfolio && useradd --system --uid 1000 --gid xPortfolio xPortfolio
COPY --from=builder --chown=xPortfolio:xPortfolio /opt/venv /opt/venv
USER xPortfolio
ENTRYPOINT ["xPortfolio"]
