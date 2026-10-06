# Hetzner deployment (my-rights.info)

The site runs on a Hetzner Cloud CX23 (`myrights-test`, Falkenstein) as three Docker
containers defined in `docker-compose.yml` at the repo root:

| service | image            | role                                                        |
|---------|------------------|-------------------------------------------------------------|
| caddy   | caddy:2          | reverse proxy on :80/:443, config in `Caddyfile`            |
| web     | built from `Dockerfile` | Flask app under gunicorn (`gunicorn_hetzner.py`)     |
| db      | postgres:16      | `raw_data_db`, data in the `pgdata` volume                  |

Cutover status (6 Oct 2026): my-rights.info is still served by the old Digital Ocean App Platform app
(`lobster-app-sj587.ondigitalocean.app`; the "cloudflare" server header is DO's own edge, not a Cloudflare
account). The domain is registered at Squarespace Domains and its DNS zone is hosted on Digital Ocean's
nameservers (ns1-3.digitalocean.com). The zone only contains the website records: apex A/AAAA to the DO
edge and `www` CNAME to the app. No MX or TXT records exist. The Hetzner box is only reachable at
http://167.233.22.165 until the steps below are done.

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

## Cutover (still to do), in this order

1. **Renew the domain at Squarespace Domains.** It expires on 2026-10-12.
2. **Move DNS off Digital Ocean.** Deleting the DO account later would delete the DNS zone and take the
   site offline, so this must come first. At Squarespace Domains switch the domain to Squarespace's own
   nameservers (or to Hetzner DNS at dns.hetzner.com, free with the Hetzner account) and create:
   - `A     @    167.233.22.165`
   - `AAAA  @    2a01:4f8:c015:7292::1` (optional; the server's IPv6 is on the Hetzner overview page)
   - `CNAME www  my-rights.info`
   Do not add a proxy/CDN in front: Caddy on the box issues its own Let's Encrypt certificate and needs
   ports 80/443 to reach it directly.
3. **Wait for the nameserver change to propagate** (minutes to a few hours; check with
   `nslookup my-rights.info` showing 167.233.22.165). Then on the server:
   ```bash
   cd /root/myrights && docker compose restart caddy
   docker logs myrights-caddy-1 2>&1 | grep -iE "certificate obtained|my-rights.info" | tail
   curl -I https://my-rights.info/
   ```
   Caddy obtains the certificate automatically once the domain resolves to the box.
4. **Remove the `http://167.233.22.165` preview block from `Caddyfile`** and `docker compose up -d caddy`,
   so the site is only served on the domain over HTTPS.
5. **Confirm the final Digital Ocean backups exist** in `/root/do_final_backup/` on the server (full
   dumps of both DO databases, about 12 GB uncompressed: the raw scraping tables were never copied into
   the Hetzner database). Copy them off the server too if you want a second copy.
6. **Only now delete on Digital Ocean:** the App Platform app, the managed Postgres cluster
   (`db-postgresql-fra1-kyr-0001`), the DNS zone, then the account. Rotating the old database password
   first is pointless once the cluster is deleted, but if the cluster is kept, rotate it: the old
   password is in this repo's git history.
