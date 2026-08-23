# E Paper

## Setup

1. Install dependencies:

```bash
uv sync
```

2. Create `.env` file with your API keys and location:

```bash
cp .env.example .env
```

Edit `.env` and add:

- `OPENWEATHER_API_KEY`: Get from [OpenWeatherMap](https://openweathermap.org/api)
- `LATITUDE` and `LONGITUDE`: Your location coordinates

3. (Optional) Set up authentication:

```bash
uv run python generate_password_hash.py
```

This will prompt you to enter a password and generate an Argon2 hash. Copy the generated hash and add it to `.env`:

```
AUTH_PASSWORD="$argon2id$v=19$m=65536,t=3,p=4$..."
```

Leave `AUTH_PASSWORD` empty to disable authentication.

## Run project

```bash
uv run python -m main
```

The API server starts on `http://localhost:8000`

- **Web UI**: Open `http://localhost:8000` in your browser to control the display
- **API**: Use REST endpoints to control the display programmatically

If authentication is enabled, you'll be redirected to the login page.

## Run as background service

Copy the systemd unit file and enable it:

```bash
sudo cp epaper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable epaper
sudo systemctl start epaper
```

Check status / logs:

```bash
sudo systemctl status epaper
journalctl -u epaper -f
```

Stop the service:

```bash
sudo systemctl stop epaper
```
