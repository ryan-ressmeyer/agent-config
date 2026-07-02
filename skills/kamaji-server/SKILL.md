---
name: kamaji-server
description: Use when interfacing with the kamaji home server — SSHing in, deploying NixOS config changes, checking service status, probing tailnet-only services, or any task that runs on or against kamaji.
---

# kamaji-server

## What kamaji is

Single-host NixOS box on Ryan's home tailnet. Fully declarative — every service is a NixOS module in the private `kamaji` flake. Runs media (Jellyfin + arr stack behind AirVPN netns), file shares (Samba/NFS on a ZFS mirror at `/tank`), Paperless-ngx, the ansa daemon, Forgejo (self-hosted private git server), `ryanressmeyer.com` (Caddy + Cloudflare Tunnel — the only public surface), and Grafana/Prometheus monitoring. Weekly restic to Backblaze B2 covers the canonical stores (`/tank/documents`, `/tank/ansa`, `/tank/forgejo`); everything else is re-derivable from the flake.

## Access

Reachable as `kamaji` via Tailscale MagicDNS. The tailnet members with keys installed are `porco` (desktop), `totoro` (laptop), and `calcifer` (work).

To run commands on the server from a keyed host, use a one-shot ssh command:

```bash
ssh kamaji '<cmd>'          # one-shot
```

Commands requiring sudo access will fail (e.g. `ssh kamaji 'sudo rebuild'). If access to a sudo command is required, bring it to the attention of the user and provide them with the commands that need to be run and an explanation of what they do and why they are required.

Tailnet-only services (no public ports): SSH 22, Jellyfin 8096, Sonarr 8989, Radarr 7878, Prowlarr 9696, Bazarr 6767, qBittorrent 8080, ansa 7327, Paperless 28981, Grafana 3000, Forgejo 3300 (web) + 2222 (git ssh). Auth on Paperless and Forgejo; tailnet is the auth boundary for the rest. Mechanism: ports open only on `interfaces.tailscale0.allowedTCPPorts` (not in the global firewall); `tailscale0` is in `firewall.trustedInterfaces`. The single public surface is `ryanressmeyer.com` via outbound Cloudflare Tunnel — zero inbound ports.

## Service registry

| Service | Port | systemd unit(s) | sops key | `/tank` dataset |
|---|---|---|---|---|
| Jellyfin | 8096 | `jellyfin` | — | `/tank/media` |
| Sonarr | 8989 | `sonarr` (+ `sonarr-webui-bridge`) | — | `/tank/media/shows`, `/tank/downloads/sonarr` |
| Radarr | 7878 | `radarr` (+ `radarr-webui-bridge`) | — | `/tank/media/movies`, `/tank/downloads/radarr` |
| Prowlarr | 9696 | `prowlarr` (+ `prowlarr-webui-bridge`) | — | — |
| Bazarr | 6767 | `bazarr` (+ `bazarr-webui-bridge`) | — | `/tank/media` |
| qBittorrent | 8080 | `qbittorrent` (+ `qbittorrent-webui-bridge`) | — | `/tank/downloads` |
| FlareSolverr | 8191 (vpn-only) | `flaresolverr` | — | — |
| AirVPN tunnel | — | `wg-airvpn` (`BindsTo` for all six above) | `airvpn.conf` | — |
| ansa | 7327 | `ansa` | — | `/tank/ansa` |
| Paperless | 28981 | `paperless-web`, `paperless-consumer`, `paperless-scheduler`, `paperless-task-queue` | `paperless-admin-password` | `/tank/paperless` |
| Forgejo | 3300 (web), 2222 (git ssh) | `forgejo` | — | `/tank/forgejo` |
| Grafana | 3000 | `grafana` | — | — |
| Prometheus | 9090 (localhost) | `prometheus` | — | — |
| Caddy + tunnel | 80 (localhost) | `caddy`, `cloudflared` | `cloudflare-tunnel-token` | — |
| Restic backup | — | `restic-backups-documents.{service,timer}`, `restic-check-documents.{service,timer}` | `restic-b2-env`, `restic-password` | `/tank/documents`, `/tank/ansa`, `/tank/forgejo` (sources) |
| Email | — | `msmtpq`, `kamaji-mail-flush.timer`, `kamaji-notify` CLI | `resend-api-key` | — |

Bouncing a service: `ssh -t kamaji 'sudo systemctl restart <unit>'`. Six arr-stack units live in the `vpn` netns and `BindsTo=wg-airvpn` — restarting `wg-airvpn` cascades to all of them.

## Forgejo (self-hosted git)

Private git server — the canonical home for personal repos (no GitHub mirroring; the point is to keep them off GitHub). Web UI + login at `http://kamaji:3300` (admin user `ryanress`). State under `/tank/forgejo` (SQLite + bare repos + LFS), backed up offsite by the restic `documents` job.

- **Clone/push:** `ssh://forgejo@kamaji:2222/ryanress/<repo>.git`. Note the SSH user is **`forgejo`**, not `git` — Forgejo's built-in SSH server runs as the `forgejo` user (port 2222, tailnet-only). Add your public key in the web UI (Settings → SSH Keys). HTTP(S) clone works too via `http://kamaji:3300/...` with a token.
- **Server admin CLI** (on kamaji, as the `forgejo` user — for users/tokens, not day-to-day):
  ```bash
  sudo -u forgejo forgejo admin user create --admin --username <u> --email <e> \
    --random-password --config /tank/forgejo/custom/conf/app.ini
  sudo -u forgejo forgejo admin user generate-access-token --username ryanress \
    --scopes write:repository,write:user --token-name <name> --raw \
    --config /tank/forgejo/custom/conf/app.ini
  ```
- **Client CLI for agents/repo ops** — `tea` (the Gitea/Forgejo API client). Installed as `tea` on kamaji (nixpkgs) and as `tea-cli` on Ubuntu hosts (apt package `tea-cli`; plain `tea` there is an unrelated editor — jiji symlinks `~/.local/bin/tea → tea-cli`). Talks to the API over the tailnet with a stored token (`~/.config/tea/`); login name is `kamaji`:
  ```bash
  tea repos ls --login kamaji
  tea repo create --login kamaji --name <repo> --private
  tea repos delete --login kamaji --owner ryanress --name <repo> --force
  ```
  Set up once per host: `tea login add --name kamaji --url http://kamaji:3300 --token <token>`. The token also lives in `~/.zshrc.local` as `FORGEJO_TOKEN` (+ `FORGEJO_URL`), distributed via the shell-secrets `secrets-pull` flow, for raw `curl` against `http://kamaji:3300/api/v1/...`.

## Deploy chain (human-in-the-loop)

The kamaji NixOS config lives in a private repo with **two checkouts that sync only via `origin/main` on GitHub**:

- `~/code/kamaji/` on the dev machine
- `~/kamaji/` on kamaji itself

Standard chain for any infrastructure change:

1. Edit `~/code/kamaji/` locally. Commit, `git push origin main`.
2. `ssh kamaji 'cd ~/kamaji && git pull --ff-only'`.
3. **Stop. Ask the user to run `rebuild` on kamaji** (alias for `sudo nixos-rebuild switch --flake .#kamaji`). Don't drive it over non-interactive ssh — sudo needs a TTY and the user is the human-in-the-loop checker for what actually applies.
4. Verify with `systemctl status`, `journalctl -u <unit>`, or a `curl` against the relevant port.

Small in-place edits on kamaji are fine (`~/kamaji/` is owned by `ryanress`), but commit-and-push from kamaji before touching the same files locally or the two checkouts diverge.

If a project flake (e.g. `ansa-kg`) is consumed as a kamaji input, bump it in its own repo first, then `nix flake update <input>` inside `~/code/kamaji/` and follow the same chain.

## Common probes

```bash
ssh kamaji systemctl status <unit> --no-pager
ssh kamaji journalctl -u <unit> -n 100 --no-pager
ssh kamaji 'zpool status; zfs list'
ssh kamaji 'systemctl list-timers --no-pager'
ssh -t kamaji 'sudo ip netns exec vpn curl -s https://ifconfig.me'   # AirVPN egress check
curl http://kamaji:<port>/...                                         # from any tailnet host
```

## Shell secrets distribution

Tailnet machines share env-var-shaped secrets (API keys, etc.) via a plain `~/.zshrc.local` on kamaji as source of truth. No sops/age — kamaji is trusted, transport is SSH over Tailscale. Each machine has a `secrets-pull` zsh function that `scp`s the file down (chmod 600) and a `reload` alias to re-source. Edit on kamaji (`ssh kamaji vim ~/.zshrc.local`), then `secrets-pull && reload` on each consumer. Upgrade to sops only if the secret set grows sensitive enough to defend against kamaji compromise.

## Constraints that bite

- **NixOS is declarative.** Never `apt`/`pip install`/`systemctl edit` to persist state — it won't survive a rebuild. Add a module to the flake.
- **Secrets are sops-nix.** Edit via `nix-shell -p sops --run 'sops ~/kamaji/secrets/secrets.yaml'` on kamaji, or anywhere with an age key at `~/.config/sops/age/keys.txt`.
- **Private flake inputs need access tokens.** Use `github:owner/repo` form; `git+https://` bypasses tokens and prompts interactively (breaks rebuilds).
- **ZFS pool `/tank`.** Per-service datasets (`/tank/media`, `/tank/documents`, `/tank/paperless`, `/tank/ansa`, `/tank/forgejo`, …), each created imperatively (`sudo zfs create tank/<name>`) before the service's first rebuild. Only the canonical stores (`/tank/documents`, `/tank/ansa`, `/tank/forgejo`) are backed up offsite.
- **Custom `dataDir` outside `/var/lib/<svc>`** requires overriding the unit's `User`/`Group` to a static system user — `DynamicUser=true` can't `chown` non-default state dirs.
- **i226-V NIC wedge.** If kamaji drops off the tailnet, suspect `enp3s0` link state first. A watchdog auto-recovers, but it's the most common cause of "kamaji is unreachable."
