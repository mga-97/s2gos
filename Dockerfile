FROM ghcr.io/prefix-dev/pixi:0.50.2-bookworm-slim AS build

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/pixi
RUN mkdir src

COPY ./src ./src
COPY ./pyproject.toml ./pyproject.toml
COPY ./packages ./packages
COPY ./pixi.lock ./pixi.lock
COPY ./run_step.py ./run_step.py
COPY ./s2gos_settings.yaml ./s2gos_settings.yaml
COPY ./eradiate ./eradiate

RUN pixi install --locked

# install dependencies + eradiate
RUN pixi add apache-airflow-providers-cncf-kubernetes

#RUN pip install git+https://github.com/eo-tools/eozilla.git@main
RUN pixi add --pypi "eozilla@git+https://github.com/eo-tools/eozilla.git"

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
COPY --from=build ./opt/pixi/eradiate  /opt/pixi/eradiate


ENV PIXI_ENV="/opt/pixi/.pixi/envs/default"
ENV LD_LIBRARY_PATH="$PIXI_ENV/lib:$LD_LIBRARY_PATH"
ENV PROJ_DATA="$PIXI_ENV/share/proj"
ENV PATH="$PIXI_ENV/bin:$PATH"

ENV ERADIATE_DATA_PATH="/opt/pixi/eradiate/unpacked"

#RUN mkdir -p $ERADIATE_CACHE_DIR $ERADIATE_DATA_DIR

## Run the asset install once at build time
## Replace this with your actual command
#RUN python -m eradiate install core gecko monotropa \
#  --cache-dir $ERADIATE_CACHE_DIR \
#  --data-dir $ERADIATE_DATA_DIR
#
## ensure runtime user can read
RUN chown -R 1000:1000 /opt/pixi/
