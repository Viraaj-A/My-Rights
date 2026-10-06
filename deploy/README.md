# Hetzner deployment (my-rights.info)

The site runs on a Hetzner Cloud CX23 (`myrights-test`, Falkenstein) as three Docker
containers defined in `docker-compose.yml` at the repo root:

| service | image            | role                                                        |
|---------|------------------|-------------------------------------------------------------|
| caddy   | caddy:2          | reverse proxy on :80/:443, config in `Caddyfile`            |
| web     | built from `Dockerfile` | Flask app under gunicorn (`gunicorn_hetzner.py`)     |
| db      | postgres:16      | `raw_data_db`, data in the `pgdata` volume                  |

Cutover done 7 Oct 2026: my-rights.info is registered at Squarespace Domains, its DNS zone is on Squarespace's
nameservers (apex A record to 167.233.22.165, `www` CNAME to the apex), and Caddy holds Let's Encrypt
certificates for both names. The IP-only preview block has been removed from `Caddyfile`.

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

## If the Digital Ocean resources are still around

Nothing on Hetzner depends on them. Full dumps of both DO databases were taken on 6 Oct 2026 into
`/root/do_final_backup/` on the server (about 6.3 GB; copy them off the server for a second copy).
The DO app `lobster-app-sj587`, the managed Postgres cluster `db-postgresql-fra1-kyr-0001` and the DO DNS
zone can be deleted. Once the cluster is deleted, the old database password in this repo's git history is dead.
