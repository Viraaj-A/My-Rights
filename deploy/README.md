# Hetzner deployment (my-rights.info)

The site runs on a Hetzner Cloud CX23 (`myrights-test`, Falkenstein) as three Docker
containers defined in `docker-compose.yml` at the repo root:

| service | image            | role                                                        |
|---------|------------------|-------------------------------------------------------------|
| caddy   | caddy:2          | reverse proxy on :80/:443, config in `Caddyfile`            |
| web     | built from `Dockerfile` | Flask app under gunicorn (`gunicorn_hetzner.py`)     |
| db      | postgres:16      | `raw_data_db`, data in the `pgdata` volume                  |

Cutover status (6 Oct 2026): my-rights.info is still proxied by Cloudflare to the old Digital Ocean
App Platform origin. The Hetzner box is only reachable at http://167.233.22.165 until the Cloudflare
DNS record is pointed at the server and the origin has a certificate (see "Cutover" below).

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

## Cutover (still to do)

1. In Cloudflare DNS, point the A records for `my-rights.info` and `www` at 167.233.22.165 (keep the proxy on).
2. Give the origin a certificate. Caddy's default TLS-ALPN challenge cannot pass through the Cloudflare
   proxy (see `docker logs myrights-caddy-1`). Either install a Cloudflare Origin CA certificate and
   reference it in `Caddyfile` with a `tls cert key` line, or build Caddy with the Cloudflare DNS module
   and use `tls { dns cloudflare <token> }`. Set Cloudflare SSL/TLS mode to Full (strict) once done.
3. Remove the `http://167.233.22.165` preview block from `Caddyfile` and `docker compose up -d caddy`.
4. Only then shut down the Digital Ocean app and database, and rotate the old Digital Ocean database
   password (it is in this repo's git history).
