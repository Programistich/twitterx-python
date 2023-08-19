FROM python:3.9
#USER root
#RUN apt-get update                             \
# && apt-get install -y --no-install-recommends \
#    ca-certificates curl firefox-esr           \
# && rm -fr /var/lib/apt/lists/*                \
# && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz | tar xz -C /usr/local/bin \
# && apt-get purge -y ca-certificates curl
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT ["python", "-m", "main"]