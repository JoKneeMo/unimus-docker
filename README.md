# Unimus Docker

Lightweight Docker container for [Unimus](https://unimus.net/), a network automation and configuration management solution.

Available on:
 - Docker Hub: [jokneemo/unimus](https://hub.docker.com/r/jokneemo/unimus)
 - GitHub Container Registry: [ghcr.io/jokneemo/unimus](https://github.com/jokneemo/unimus-docker/pkgs/container/unimus)

## Docker Compose

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

## Configuration Variables

### Unimus Properties
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

### Unimus Defaults (Advanced)
You can configure system defaults (found in `/etc/default/unimus`) using environment variables prefixed with `DEFAULT_`.
The conversion logic is the same as `PROP_` variables:
1.  Removes `DEFAULT_` prefix.
2.  Converts to lowercase.
3.  Replaces underscores `_` with dots `.`.

**Important:** For properties containing hyphens (e.g. `discovery-disabled`), you must use a hyphen in the environment variable name. This works in Docker Compose but may not be supported by all shells if running manually.

#### Disabling Features
Common use cases for disabling specific Unimus features:

| Variable | Property | Description |
|---|---|---|
| `DEFAULT_UNIMUS_CORE_DISCOVERY-DISABLED` | `unimus.core.discovery-disabled` | Disable discovery jobs. |
| `DEFAULT_UNIMUS_CORE_BACKUP-DISABLED` | `unimus.core.backup-disabled` | Disable backup jobs. |
| `DEFAULT_UNIMUS_CORE_PUSH-DISABLED` | `unimus.core.push-disabled` | Disable config push jobs. |
| `DEFAULT_UNIMUS_CORE_SCAN-DISABLED` | `unimus.core.scan-disabled` | Disable network scan jobs. |
| `DEFAULT_UNIMUS_CORE_DEVICE-CLI-DISABLED` | `unimus.core.device-cli-disabled` | Disable device CLI access. |
| `DEFAULT_UNIMUS_SERVER_CORE_LISTENER-DISABLED` | `unimus.server.core.listener-disabled` | Disable the remote core listener (port 5509). |

#### Server Address
| Variable | Property | Description |
|---|---|---|
| `DEFAULT_SERVER_ADDRESS` | `server.address` | Bind address. Default: `0.0.0.0` |
| `DEFAULT_SERVER_PORT` | `server.port` | Web UI Port. Default: `8085` |

### File Generation
The container automatically generates configuration files at startup based on your environment variables. You can disable this behavior if you prefer to mount your own configuration files.
| Variable | Default | Description |
|---|---|---|
| `MAKE_PROPERTIES` | `true` | If `true`, generates `/etc/unimus/unimus.properties` from `PROP_` variables. |
| `MAKE_DEFAULTS` | `true` | If `true`, generates `/etc/default/unimus` from `DEFAULT_` variables. |
