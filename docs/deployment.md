# Deployment

How the website gets from GitHub to the web server. Short sentences, copy-paste commands.

## In short

- The workflow is `.github/workflows/deploy.yml`. It runs:
  - on every push (or merge) to `main`,
  - when you press **Run workflow** (Actions tab, workflow "Deploy"),
  - once a day at about 04:41 / 05:41 Frankfurt time. This removes past matches from the schedule:
    `build.py` hides them only when it runs.
- Every run builds the site with `python3 build.py` into a clean folder and checks it. If the build
  fails, the run stops. Nothing is uploaded.
- The upload is **off** until you switch it on. It happens only when the run is for `main` **and** the
  repository variable `DEPLOY_ENABLED` is `true`. Without any settings, the run only builds and is green.
- The upload uses `rsync` over SSH, with its own key and its own user on the server. The server only
  allows this key to write into one folder: `/var/www/cestlavie`.

What is uploaded (nothing else): the generated pages (`index.html`, `impressum.html`,
`datenschutz.html`, `en/`, `it/`, `kontakt/`, `spielplan/`), `robots.txt`, `sitemap.xml`, `css/`,
`js/`, `assets/`. Never uploaded: `.git` and other dotfiles, `data/`, `docs/`, `*.py`, `*.md`.
Files on the server that are not in the build are deleted, so the old `eintracht/` pages cannot come back.

If you add a new page folder in `build.py`, also add it to `GENERATED` at the top of
`.github/workflows/deploy.yml`. Until you do, the run fails on purpose.

## Names used below

Change them if you like, but then change them everywhere.

| What | Value in this guide |
|---|---|
| Deploy user on the server | `clvdeploy` |
| Site folder on the server | `/var/www/cestlavie` |
| Server name | `cestlavie-frankfurt.de` |
| Key file on your PC | `~/clv-deploy-key` (private) and `~/clv-deploy-key.pub` (public) |

## Step 1: find out a few things on the server

Log in to the server as usual (`ssh you@cestlavie-frankfurt.de`), then:

```sh
cat /etc/debian_version                  # Debian version
systemctl cat caddy                      # look for --config: usually /etc/caddy/Caddyfile
sudo cat /etc/caddy/Caddyfile            # your Caddy config: find the block for cestlavie-frankfurt.de
sudo sshd -T | grep -Ei '^(port|allowusers|allowgroups|passwordauthentication)'
sudo ufw status verbose                  # only if you use ufw
```

- **SSH port**: the `port` line. If it is not 22, you need it in step 4.
- **allowusers / allowgroups**: if one of them is shown, add `clvdeploy` to that line in
  `/etc/ssh/sshd_config` (or the file in `/etc/ssh/sshd_config.d/` that has it), then run
  `sudo sshd -t` (must print nothing) and `sudo systemctl reload ssh`.
- **passwordauthentication** should be `no`.
- **Firewall**: GitHub connects from many changing addresses. The SSH port must be reachable from
  the internet (in `ufw` and in the firewall in your hosting provider's web panel, if there is one).
  If SSH only allows your home address, the upload will fail.
- **Caddy**: note the folder after `root` in the block for the domain (the "Coming soon" page).
  It must **not** be `/var/www/cestlavie`.

## Step 2: prepare the server

Run these on the server, one by one.

```sh
# Tools (rrsync is part of the rsync package on Debian 12 and newer)
sudo apt update
sudo apt install rsync python3
ls -l /usr/bin/rrsync

# Deploy user without a password (press Enter for the questions, then Y)
sudo adduser --disabled-password clvdeploy

# The user may not change its own login settings: its home and .ssh belong to root
sudo chown root:root /home/clvdeploy
sudo chmod 755 /home/clvdeploy
sudo mkdir -p /home/clvdeploy/.ssh
sudo touch /home/clvdeploy/.ssh/authorized_keys
sudo chmod 755 /home/clvdeploy/.ssh
sudo chmod 644 /home/clvdeploy/.ssh/authorized_keys

# Site folder: only for this website. Caddy can read it, only clvdeploy can write it.
sudo mkdir -p /var/www/cestlavie
sudo chown clvdeploy:clvdeploy /var/www/cestlavie
sudo chmod 755 /var/www/cestlavie
ls -ld /var/www                          # must show drwxr-xr-x
```

If `ls -l /usr/bin/rrsync` says "No such file", stop and ask for help (older Debian).

## Step 3: make the deploy key (on your PC, not on the server)

```sh
ssh-keygen -t ed25519 -N "" -C "github-deploy-cestlavie" -f ~/clv-deploy-key
cat ~/clv-deploy-key.pub
```

- Do this in your home folder, **never inside the project folder**. The key must never be committed.
- **Never paste the private key (`~/clv-deploy-key`) into a chat**, an e-mail or an AI tool.
  It goes only into GitHub (step 4).

On the server, open the key file:

```sh
sudo nano /home/clvdeploy/.ssh/authorized_keys
```

Write **one line**: this start, then the whole content of `~/clv-deploy-key.pub`:

```text
restrict,command="/usr/bin/rrsync -wo /var/www/cestlavie" ssh-ed25519 AAAA...your-public-key... github-deploy-cestlavie
```

What this line does: the key can only upload files into `/var/www/cestlavie` with rsync. It
cannot open a shell, cannot read files, cannot forward ports. Because of this line, the workflow
uploads to the target `./`, which means `/var/www/cestlavie`.

Test from your PC (use `-p PORT` if your port is not 22):

```sh
ssh -i ~/clv-deploy-key clvdeploy@cestlavie-frankfurt.de
```

You must **not** get a shell. You should see a short error from rrsync, and the connection
closes. If you get a shell, the line above is wrong: fix it before you continue.

Still on the server, print the server's host key (GitHub uses it to make sure it talks to your
server):

```sh
cat /etc/ssh/ssh_host_ed25519_key.pub
```

## Step 4: settings in GitHub

Repository on github.com → **Settings** → **Secrets and variables** → **Actions**.

**Secrets** tab → **New repository secret**:

| Name | Value |
|---|---|
| `DEPLOY_SSH_KEY` | the whole private key: run `cat ~/clv-deploy-key` on your PC and copy everything, including the `-----BEGIN` and `-----END` lines |
| `DEPLOY_KNOWN_HOSTS` | one line: the server name, a space, then the first two parts of the host key from step 3. Port 22: `cestlavie-frankfurt.de ssh-ed25519 AAAA...`. Other port (example 2222): `[cestlavie-frankfurt.de]:2222 ssh-ed25519 AAAA...` |

After saving `DEPLOY_SSH_KEY`, delete the private key from your PC: `rm ~/clv-deploy-key`.
If you ever need it again, make a new key (step 3) and replace the old line and secret.

**Variables** tab → **New repository variable**:

| Name | Value | When |
|---|---|---|
| `DEPLOY_HOST` | `cestlavie-frankfurt.de` (same name as in `DEPLOY_KNOWN_HOSTS`) | now |
| `DEPLOY_USER` | `clvdeploy` | now |
| `DEPLOY_PORT` | your SSH port | only if it is not 22 |
| `DEPLOY_ENABLED` | `true` | when you want uploads to start (step 5) |
| `DEPLOY_CHECK_URL` | `https://cestlavie-frankfurt.de/` | only at go-live (step 6) |

Also check **Settings → Actions → General**: Actions must be allowed (at least actions created by
GitHub).

## Step 5: safe test (the "Coming soon" page stays online)

Caddy still shows "Coming soon" from its old folder, so uploading into `/var/www/cestlavie` changes
nothing for visitors.

1. The workflow must be on `main` (merge the branch that contains it).
2. Set the variable `DEPLOY_ENABLED` to `true`.
3. **Actions** tab → **Deploy** → **Run workflow** → branch `main` → **Run workflow**.
4. The run must be green. The summary shows a "Deploy record" with `Uploaded: true`.
5. On the server: `ls /var/www/cestlavie` shows `index.html`, `css`, `en`, and so on.
6. Optional preview of the uploaded files, only for you: on your PC run
   `ssh -L 8080:127.0.0.1:8080 you@cestlavie-frankfurt.de`, then in that SSH window
   `cd /var/www/cestlavie && python3 -m http.server 8080 --bind 127.0.0.1`.
   Open http://127.0.0.1:8080 on your PC. Stop with Ctrl+C.

From now on, every push to `main` and every daily run updates `/var/www/cestlavie`.

## Step 6: go live

1. In the project: set `NOINDEX = False` in `build.py`, finish the "Before going live" list in
   `TODO.md`, and merge to `main`. The run uploads the final version (still not visible).
2. On the server, back up the Caddy config:

   ```sh
   sudo cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.before-launch
   sudo nano /etc/caddy/Caddyfile
   ```

3. Replace **only** the block(s) for `cestlavie-frankfurt.de` and `www.cestlavie-frankfurt.de`
   (the "Coming soon" block) with the two blocks below. Do not touch other blocks or the global
   options block at the top. If the old block has lines you added on purpose (for example `log`),
   keep them in the new `cestlavie-frankfurt.de` block. Each domain may appear in only one block.

   ```caddyfile
   cestlavie-frankfurt.de {
   	root * /var/www/cestlavie
   	encode zstd gzip
   	file_server
   	header {
   		X-Content-Type-Options "nosniff"
   		Referrer-Policy "strict-origin-when-cross-origin"
   		-Server
   	}
   }

   www.cestlavie-frankfurt.de {
   	redir https://cestlavie-frankfurt.de{uri} permanent
   }
   ```

4. Check, then reload (reload only if the check says "Valid configuration"):

   ```sh
   sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
   sudo systemctl reload caddy
   curl -sI https://www.cestlavie-frankfurt.de/
   curl -sI https://cestlavie-frankfurt.de/
   ```

   The first `curl` must show `301` and `location: https://cestlavie-frankfurt.de/`. The second must
   show `200`.
5. In GitHub, add the variable `DEPLOY_CHECK_URL` = `https://cestlavie-frankfurt.de/`. From now on
   every run checks that the live home page is exactly the page it just built.
6. Run the workflow once by hand (as in step 5). It must be green with `Live check: success`.

Back to "Coming soon" at any time: `sudo cp /etc/caddy/Caddyfile.before-launch /etc/caddy/Caddyfile`,
then `sudo systemctl reload caddy`.

## Switch off, roll back

- **Stop all uploads**: set `DEPLOY_ENABLED` to `false` (or delete it). Builds still run, nothing is
  uploaded, the server keeps the current files.
- **Go back to an older version**: see [runbooks/rollback.md](runbooks/rollback.md).
- **Key lost or leaked**: on the server, delete the line in
  `/home/clvdeploy/.ssh/authorized_keys`. Then make a new key (step 3) and replace the secret.

## Good to know

- **Daily run**: GitHub can start scheduled runs late (sometimes an hour or more) and may skip one
  when it is very busy. In a **public** repository, GitHub switches the daily run off after 60 days
  without any activity in the repository; then turn it on again in the Actions tab. Private
  repositories pay with minutes: each run takes about 1 minute, about 30 minutes a month of the 2,000
  free minutes. Public or private: see the label next to the repository name on GitHub.
- **Who can deploy**: everyone with write access to the repository can use the deploy secrets (for
  example with a changed workflow on another branch). Give write access only to people you trust.
- **Server address**: GitHub connects over IPv4. If you ever put a proxy or CDN in front of the
  domain, set `DEPLOY_HOST` to the server's IP address and use that IP in `DEPLOY_KNOWN_HOSTS`.
- **Run history**: every run on the Actions tab has a "Deploy record" (time, trigger, commit,
  uploaded or not, live check, result). GitHub sends you an e-mail when a run fails.
