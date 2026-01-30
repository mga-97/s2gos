FROM ghcr.io/prefix-dev/pixi:0.50.2-bookworm-slim AS build

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pixi
RUN mkdir src

COPY ./src ./src
COPY ./pyproject.toml ./pyproject.toml
COPY ./packages ./packages
COPY ./pixi.lock ./pixi.lock
COPY ./run_step.py ./run_step.py
COPY ./s2gos_settings.yaml ./s2gos_settings.yaml

RUN pixi install --locked

# install dependencies + eradiate
RUN pixi add apache-airflow-providers-cncf-kubernetes

#RUN pip install git+https://github.com/eo-tools/eozilla.git@main
RUN pixi add --pypi "procodile@git+https://github.com/eo-tools/eozilla.git#subdirectory=procodile"
RUN pixi add --pypi "gavicore@git+https://github.com/eo-tools/eozilla.git#subdirectory=gavicore"
RUN pixi add --pypi "wraptile@git+https://github.com/eo-tools/eozilla.git#subdirectory=wraptile"
RUN pixi add --pypi "cuiman@git+https://github.com/eo-tools/eozilla.git#subdirectory=cuiman"
RUN pixi add --pypi "appligator@git+https://github.com/eo-tools/eozilla.git#subdirectory=appligator"

RUN ls -la /opt/pixi

#Stage 2 ---------------------------
FROM ubuntu:resolute
WORKDIR /opt/pixi

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build ./opt/pixi/.pixi/ /opt/pixi/.pixi/
COPY --from=build ./opt/pixi/src /opt/pixi/src
COPY --from=build ./opt/pixi/pyproject.toml /opt/pixi
COPY --from=build ./opt/pixi/pixi.lock /opt/pixi
COPY --from=build ./opt/pixi/packages /opt/pixi
COPY --from=build ./opt/pixi/run_step.py  /opt/pixi/
COPY --from=build ./opt/pixi/s2gos_settings.yaml  /opt/pixi/s2gos_settings.yaml

ENV PIXI_ENV="/opt/pixi/.pixi/envs/default"
ENV LD_LIBRARY_PATH="$PIXI_ENV/lib:$LD_LIBRARY_PATH"
ENV PROJ_DATA="$PIXI_ENV/share/proj"
ENV PATH="$PIXI_ENV/bin:$PATH"

#RUN mkdir -p $ERADIATE_CACHE_DIR $ERADIATE_DATA_DIR

## Run the asset install once at build time
## Replace this with your actual command
RUN eradiate data install core gecko monotropa

### ensure runtime user can read
#RUN chown -R 1000:1000 /opt/pixi/
