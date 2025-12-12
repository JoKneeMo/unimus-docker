FROM alpine:3

LABEL MAINTAINER="JoKneeMo"

ARG UNIMUS_VERSION="-%20Latest"

RUN apk update && apk add --no-cache \
    curl \
    ca-certificates \
    wget \
    less \
    tzdata \
    iputils \
    tini \
    bash \
    openjdk21-jre-headless \
    && addgroup -S -g 1000 unimus \
    && adduser -S -D -u 1000 -G unimus unimus \
    && echo "UTC" > /etc/timezone

RUN if [ "${UNIMUS_VERSION}" = "dev" ]; then \
        DOWNLOAD_URL="https://download.unimus.net/unimus-dev/Unimus.jar"; \
    else \
        DOWNLOAD_URL="https://download.unimus.net/unimus/${UNIMUS_VERSION}/Unimus.jar"; \
    fi \
    && curl -L "${DOWNLOAD_URL}" --create-dirs -o /opt/unimus/Unimus.jar \
    && mkdir -p \
        /etc/unimus \
        /var/log/unimus \
        /etc/default \
    && touch \
        /etc/unimus/unimus.properties \
        /etc/default/unimus \
    && chown -R unimus:unimus \
        /opt/unimus \
        /etc/unimus \
        /var/log/unimus \
        /etc/default/unimus \
        /etc/timezone

COPY --chmod=755 docker-entrypoint.sh /docker-entrypoint.sh

EXPOSE 8085
EXPOSE 5509

WORKDIR /opt/unimus

USER unimus

ENV TZ=UTC \
    MAKE_PROPERTIES=true \
    MAKE_DEFAULTS=true

ENTRYPOINT ["tini", "-g", "--", "/docker-entrypoint.sh"]
