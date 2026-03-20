# Podman Setup for Backend

## Prerequisites

The error you're seeing indicates that neither `docker-compose` nor `podman-compose` is installed. Install one of these:

### Option 1: Install podman-compose (Recommended)

```bash
pip install podman-compose
```

### Option 2: Use Podman Desktop

[Podman Desktop](https://podman-desktop.io/) includes built-in compose support.

## Running the Backend

From the project root directory:

```bash
# Using podman-compose directly
podman-compose -f backend/docker/podman/docker-compose.yml up -d

# Or using podman compose (requires compose provider installed)
podman compose -f backend/docker/podman/docker-compose.yml up -d
```

## Running Backend Only

```bash
podman-compose -f backend/docker/podman/docker-compose.yml up -d backend
```

## Stopping Services

```bash
podman-compose -f backend/docker/podman/docker-compose.yml down
```

## Viewing Logs

```bash
podman-compose -f backend/docker/podman/docker-compose.yml logs -f backend
```

## Notes

- The `:Z` suffix on volume mounts is for SELinux compatibility
- Image names use full registry paths (docker.io/) for Podman compatibility
- The `version` field is omitted as it's deprecated in newer compose specifications
