# Hetzner deployment (my-rights.info)

The site runs on a Hetzner Cloud CX23 (`myrights-test`, Falkenstein) as three Docker
containers defined in `docker-compose.yml` at the repo root:

| service | image            | role                                                        |
|---------|------------------|-------------------------------------------------------------|
| caddy   | caddy:2          | reverse proxy on :80/:443, config in `Caddyfile`            |
| web     | built from `Dockerfile` | Flask app under gunicorn (`gunicorn_hetzner.py`)     |
| db      | postgres:16      | `raw_data_db`, data in the `pgdata` volume                  |

DNS for my-rights.info is proxied through Cloudflare to the server.

On the server the checkout lives in `/root/myrights`. Secrets live only in
`/root/myrights/.env` (see `.env.example` for the variable names).

## Deploying a change

```bash
cd /root/myrights
git fetch && git checkout <branch-or-main> && git pull
docker compose build web      # several minutes: COPY . /app invalidates the model-download layer
docker compose up -d
docker logs -f myrights-web-1  # wait for gunicorn workers to boot
```

## Backups

`deploy/pg_backup.sh` is installed at `/root/pg_backup.sh` and runs from root's crontab at
03:30 UTC daily, keeping the last 7 dumps in `/root/backups`.
