# Blackfong Control Core (headless)

One daemon. Local web UI. System truth.

## Run (dev)

From the repo root:

```bash
python3 -m pip install -r requirements.txt
python3 core/main.py
```

Then open:

- `http://127.0.0.1:7331/` (monochrome dashboard)
- `http://127.0.0.1:7331/api/system/pulse` (JSON)
- `http://127.0.0.1:7331/docs` (OpenAPI)

## Config (env)

- **BLACKFONG_API_HOST**: default `127.0.0.1`
- **BLACKFONG_API_PORT**: default `7331`
- **BLACKFONG_TOKEN**: if set, require header `X-Blackfong-Token: <token>`
- **BLACKFONG_BASE_DIR / BLACKFONG_DATA_DIR / BLACKFONG_DB_PATH / BLACKFONG_LOG_DIR**
  - defaults to `/opt/blackfong/...` when writable
  - otherwise falls back to this repo’s `./data/` for unprivileged dev
- **BLACKFONG_ALLOWED_SYSTEMD_UNITS**
  - comma-separated allowlist for `/api/services/{unit}/{action}`
  - example: `ssh,nginx,blackfong-core.service`

## Install (systemd)

Copy the project to `/opt/blackfong` so paths match the service file:

```bash
sudo useradd --system --home /opt/blackfong --shell /usr/sbin/nologin blackfong || true
sudo mkdir -p /opt/blackfong
sudo rsync -a --delete ./ /opt/blackfong/
sudo python3 -m pip install -r /opt/blackfong/requirements.txt

sudo cp /opt/blackfong/systemd/blackfong-core.service /etc/systemd/system/blackfong-core.service
sudo install -m 0440 /opt/blackfong/systemd/blackfong-sudoers /etc/sudoers.d/blackfong

sudo mkdir -p /opt/blackfong/data /opt/blackfong/data/logs /opt/blackfong/data/backups
sudo chown -R blackfong:blackfong /opt/blackfong/data

sudo systemctl daemon-reload
sudo systemctl enable blackfong-core.service
sudo systemctl start blackfong-core.service
```

Check:

```bash
systemctl status blackfong-core.service --no-pager
curl -s http://127.0.0.1:7331/api/system/pulse
```

