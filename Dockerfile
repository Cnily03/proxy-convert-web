FROM python:3.10.13

RUN mkdir -p /app && mkdir -p /app/bin

WORKDIR /app

COPY . /app
RUN rm -rf .git .github

# COPY requirements.txt /app
# COPY install.sh /app
# COPY docker.sh /app

RUN chmod +x /app/install.sh
RUN chmod +x /app/docker.sh
RUN cp /app/docker.sh /usr/local/bin/docker.sh

RUN cat <<EOF > /usr/local/bin/docker-entrypoint.sh
#!/bin/bash
bash /app/docker.sh || {
    echo -e "\033[33mUnable to find docker.sh in /app, trying default...\033[0m" >&2
    /usr/local/bin/docker.sh || {
        echo -e "\033[31mFailed to start. Please update the version of the image or sources.\033[0m" >&2
        exit 1
    }
}
EOF
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN pip install -r requirements.txt
RUN /app/install.sh --force

ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 80