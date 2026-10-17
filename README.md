# Flutu

A starter project for development.

## Run the application

Configure Google credentials in `.env` (use `.env.example` as a template), then start the server:

```bash
bash start_server.sh
```

Open http://localhost:8000. The script loads variables from `.env` before starting the server. Do not run `python3 server.py` directly if you want to use Google sign-in.

## Choose a path

After signing in, the dashboard links to **Choose a path**. The decision page and its API require the usual authenticated session. Each click on **Choose for me** requests a new random permutation from ANU. The page shows only the chosen direction, not the permutation.

The decision page links to an informational page about quantum randomness and the many-worlds interpretation. This is an explanatory analogy, not evidence that a person's consciousness splits across universes.

## Check the last number in a set

The demo interface is available at http://localhost:8000/permutation-checker. The API accepts a `set` array and returns the JSON boolean `true` if its last value is greater than 1, or `false` otherwise:

```http
POST /api/check-last-number
Content-Type: application/json

{"set": [1, 2]}
```

The decision page uses `POST /api/decision`, which requests a new random permutation on each call and returns `{"go_right": true}` or `{"go_right": false}`.

## Automatic restart with Copilot

The `.github/hooks/restart-app.json` hook restarts the server when the agent changes `server.py`, `decision.html`, `quantum-info.html`, `permutation-checker.html`, or `start_server.sh`. It compares file hashes to avoid restarting when those files have not changed. The server starts in the background using `.env`; check `/tmp/flutu-server.log` if it fails to start.
