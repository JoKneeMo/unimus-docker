# Unimus Docker
[![Auto Release](https://github.com/JoKneeMo/unimus-docker/actions/workflows/auto-release.yml/badge.svg?branch=main)](https://github.com/JoKneeMo/unimus-docker/actions/workflows/auto-release.yml)  [![Dev Server Build](https://github.com/JoKneeMo/unimus-docker/actions/workflows/dev-server.yml/badge.svg?branch=main)](https://github.com/JoKneeMo/unimus-docker/actions/workflows/dev-server.yml)  [![Dev Core Build](https://github.com/JoKneeMo/unimus-docker/actions/workflows/dev-core.yml/badge.svg?branch=main)](https://github.com/JoKneeMo/unimus-docker/actions/workflows/dev-core.yml)

Lightweight Docker container for [Unimus](https://unimus.net/), a network automation and configuration management solution.

Available on:
 - Server
    - Docker Hub: [jokneemo/unimus](https://hub.docker.com/r/jokneemo/unimus)
    - GitHub Container Registry: [ghcr.io/jokneemo/unimus](https://github.com/jokneemo/unimus-docker/pkgs/container/unimus)
 - Core
    - Docker Hub: [jokneemo/unimus-core](https://hub.docker.com/r/jokneemo/unimus-core)
    - GitHub Container Registry: [ghcr.io/jokneemo/unimus-core](https://github.com/jokneemo/unimus-docker/pkgs/container/unimus-core)


## Docker Compose

### Unimus Server
```yaml
name: unimus-server
services:
    unimus:
        image: jokneemo/unimus:latest # Docker Hub
        #image: ghcr.io/jokneemo/unimus:latest # GitHub Container Registry
        restart: unless-stopped
        ports:
            - "8085:8085" # Unimus Web UI
            - "5509:5509" # Unimus Core
        environment:
            TZ: America/New_York
            
            # Application Settings
            PROP_LICENSE_KEY: your-license-key
            PROP_DATABASE_ENCRYPTION_KEY: secure-encryption-key-string
            
            # Database Settings
            PROP_DATABASE_TYPE: POSTGRESQL
            PROP_DATABASE_HOST: postgres
            PROP_DATABASE_PORT: 5432
            PROP_DATABASE_NAME: unimus
            PROP_DATABASE_USER: unimus
            PROP_DATABASE_PASSWORD: database-password

    postgres:
        image: postgres:17-alpine
        restart: unless-stopped
        environment:
            POSTGRES_USER: unimus
            POSTGRES_PASSWORD: database-password
            POSTGRES_DB: unimus
        volumes:
            - ./postgres:/var/lib/postgresql/data
```

### Unimus Core
```yaml
name: unimus-core
services:
    unimus-core:
        image: jokneemo/unimus-core:latest # Docker Hub
        #image: ghcr.io/jokneemo/unimus-core:latest # GitHub Container Registry
        restart: unless-stopped
        volumes:
            - /usr/share/zoneinfo/America/New_York:/etc/localtime:ro
        environment:
          TZ: America/New_York

          # Unimus Props (/etc/unimus-core/unimus-core.properties)
          PROP_UNIMUS_ADDRESS: 10.10.10.58
          PROP_UNIMUS_PORT: 5509
          PROP_UNIMUS_ACCESS_KEY: really_long_access_key_from_the_zone_of_this_core

          # Java Settings
          #JAVA_XMS: 512m
          #JAVA_XMX: 1024m
          #JAVA_OPTS:
```

## Configuration Variables

### Unimus Server Properties
Any setting in `unimus.properties` can be set via environment variables prefixed with `PROP_`. The container startup script automatically converts these variables:
1. Removes the `PROP_` prefix.
2. Converts to lowercase.
3. Replaces underscores `_` with dots `.`.

**Example:** `PROP_DATABASE_HOST` becomes `database.host`.

| Variable | Property | Description |
|---|---|---|
| `PROP_LICENSE_KEY` | `license.key` | **Required.** Your Unimus license key. |
| `PROP_DATABASE_ENCRYPTION_KEY` | `database.encryption.key` | **Required.** Key used to encrypt sensitive data in the database. |
| `PROP_DATABASE_TYPE` | `database.type` | Database type. Values: `HSQL`, `MARIADB`, `MSSQL`, `MYSQL`, `POSTGRESQL`. |
| `PROP_DATABASE_HOST` | `database.host` | Database hostname. |
| `PROP_DATABASE_PORT` | `database.port` | Database port (e.g., `5432`). |
| `PROP_DATABASE_NAME` | `database.name` | Database name. |
| `PROP_DATABASE_USER` | `database.user` | Database username. |
| `PROP_DATABASE_PASSWORD` | `database.password` | Database password. |
| `PROP_LOGGING_FILE_SIZE` | `logging.file.size` | Log file size in MB (1-2047). Default: `50`. |
| `PROP_LOGGING_FILE_COUNT` | `logging.file.count` | Max number of log files. Default: `9`. |
| `PROP_CORE_CONNECTION_SERVER_PORT` | `core.connection.server.port` | Core connection port. Default: `5509`. |

For a full list of available properties, see the [Unimus Wiki](https://wiki.unimus.net/display/UNPUB/Initial+configuration).

### Unimus Core Properties
Any setting in `unimus-core.properties` can be set via environment variables prefixed with `PROP_`. The container startup script automatically converts these variables:
1. Removes the `PROP_` prefix.
2. Converts to lowercase.
3. Replaces underscores `_` with dots `.`.

**Example:** `PROP_UNIMUS_ADDRESS` becomes `unimus.address`.

| Variable | Property | Description |
|---|---|---|
| `PROP_UNIMUS_ADDRESS` | `unimus.address` | **Required.** The IP address or hostname of the Unimus server. |
| `PROP_UNIMUS_PORT` | `unimus.port` | **Required.** The port number of the Unimus server. |
| `PROP_UNIMUS_ACCESS_KEY` | `unimus.access.key` | **Required.** The access key for the Unimus server. |

For a full list of available properties, see the [Unimus Wiki](https://wiki.unimus.net/display/UNPUB/Installing+Unimus+Core).


### Java Configuration
| Variable | Description | Default |
|---|---|---|
| `JAVA_XMS` | Initial Java heap size. | `128m` (Unimus default) |
| `JAVA_XMX` | Maximum Java heap size. | `1024m` (Unimus default) |
| `JAVA_OPTS` | Additional arguments passed to the Java runtime. | - |

### System Configuration
| Variable | Description |
|---|---|
| `TZ` | Sets the container timezone (e.g., `America/New_York`). |

### Unimus Server Defaults (Advanced)
You can configure system defaults (found in `/etc/default/unimus`) using environment variables prefixed with `DEFAULT_`.
The conversion logic is the same as `PROP_` variables:
1.  Removes `DEFAULT_` prefix.
2.  Converts to lowercase.
3.  Replaces underscores `_` with dots `.`.

**Important:** For properties containing hyphens (e.g. `discovery-disabled`), you must use a hyphen in the environment variable name. This works in Docker Compose but may not be supported by all shells if running manually.

#### Disabling Unimus Server Features
Common use cases for disabling specific Unimus Server features:

| Variable | Property | Description |
|---|---|---|
| `DEFAULT_UNIMUS_CORE_DISCOVERY-DISABLED` | `unimus.core.discovery-disabled` | Disable discovery jobs. |
| `DEFAULT_UNIMUS_CORE_BACKUP-DISABLED` | `unimus.core.backup-disabled` | Disable backup jobs. |
| `DEFAULT_UNIMUS_CORE_PUSH-DISABLED` | `unimus.core.push-disabled` | Disable config push jobs. |
| `DEFAULT_UNIMUS_CORE_SCAN-DISABLED` | `unimus.core.scan-disabled` | Disable network scan jobs. |
| `DEFAULT_UNIMUS_CORE_DEVICE-CLI-DISABLED` | `unimus.core.device-cli-disabled` | Disable device CLI access. |
| `DEFAULT_UNIMUS_SERVER_CORE_LISTENER-DISABLED` | `unimus.server.core.listener-disabled` | Disable the remote core listener (port 5509). |

#### Unimus Server Address
| Variable | Property | Description |
|---|---|---|
| `DEFAULT_SERVER_ADDRESS` | `server.address` | Bind address. Default: `0.0.0.0` |
| `DEFAULT_SERVER_PORT` | `server.port` | Web UI Port. Default: `8085` |

### File Generation
The container automatically generates configuration files at startup based on your environment variables. You can disable this behavior if you prefer to mount your own configuration files.
| Variable | Default | Description |
|---|---|---|
| `MAKE_PROPERTIES` | `true` | If `true`, generates `/etc/unimus/unimus.properties` or `/etc/unimus-core/unimus-core.properties` from `PROP_` variables. |
| `MAKE_DEFAULTS` | `true` | If `true`, generates `/etc/default/unimus` from `DEFAULT_` variables. (Server only) |


## Development Builds
Development builds of Unimus Server and Core are available by using the `dev` image tag.

```yaml
image: jokneemo/unimus:dev
image: jokneemo/unimus-core:dev
```

These images are built automatically when a new public development build is available. 