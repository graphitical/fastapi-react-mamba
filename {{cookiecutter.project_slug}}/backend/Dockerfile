# lightweight micromamba image
FROM mambaorg/micromamba:2.3.2
ARG MAMBA_DOCKERFILE_ACTIVATE=1

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba install -y -n base -f /tmp/environment.yml && micromamba clean --all --yes

# set and create the working dir
WORKDIR /app
COPY --chown=$MAMBA_USER:$MAMBA_USER . /app

EXPOSE 8000 5678

CMD ["micromamba", "run", "-n", "base", "python", "app/main.py"]