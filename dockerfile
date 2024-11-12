FROM python:3.8.8-slim
WORKDIR /app
EXPOSE 5000

ENV no_proxy=localhost

# Install requirements
COPY requirements.txt ./
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt
COPY app.py ./
COPY templates ./templates

# Install kafka essentials
RUN apt-get -y update; apt-get -y install curl
RUN apt-get update && apt-get install openssl libssl-dev libsasl2-modules-gssapi-mit libsasl2-dev unzip build-essential -y
ENV LIBRDKAFKA_VER=2.6.0
RUN curl -k -L -s https://github.com/edenhill/librdkafka/archive/v${LIBRDKAFKA_VER}.zip -o ./librdkafka.zip && \
unzip librdkafka.zip && \
cd librdkafka-${LIBRDKAFKA_VER} && \
./configure --reconfigure --enable-sasl | tee configure-output.txt && \
make && \
make install

# Install runtime dependencies for kerberos
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install krb5-user kstart \
    libsasl2-2 libsasl2-modules-gssapi-mit libsasl2-modules \
    && apt-get autoremove

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-binary :all: confluent-kafka


CMD [ "python", "./app.py"]