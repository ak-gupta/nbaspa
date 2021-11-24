FROM python:3.8-slim

RUN apt-get -y upgrade \
 && apt-get -y update \
 && apt-get install -y \
      build-essential \
      curl \
      gcc \
      gnupg \
  && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
  && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - \
  && apt-get -y update \
  && apt-get install -y google-cloud-sdk \
  && apt-get autoremove -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
SHELL ["/bin/sh", "-c"]
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN python -m pip install --no-cache-dir -r requirements.txt .
