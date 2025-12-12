FROM alpine:3

ARG UNIMUS_VERSION="-%20Latest"

LABEL org.opencontainers.image.authors="JoKneeMo <https://github.com/JoKneeMo>"
LABEL org.opencontainers.image.source="https://github.com/JoKneeMo/unimus-docker"
LABEL org.opencontainers.image.title="Unimus Server"
LABEL org.opencontainers.image.version="${UNIMUS_VERSION}"

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

COPY --chmod=755 entrypoint.sh /entrypoint.sh

EXPOSE 8085
EXPOSE 5509

WORKDIR /opt/unimus

USER unimus

ENV TZ=UTC \
    MAKE_PROPERTIES=true \
    MAKE_DEFAULTS=true

ENTRYPOINT ["tini", "-g", "--", "/entrypoint.sh"]
