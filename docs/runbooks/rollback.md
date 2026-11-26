# Rollback

The site is static files. A rollback means: upload an older build. Setup: [../deployment.md](../deployment.md).

## Fast: re-run an older good run (minutes)

1. GitHub → **Actions** → **Deploy**.
2. Open the last green run **before** the bad change (branch `main`, "Uploaded: true" in its Deploy
   record).
3. **Re-run all jobs**. It builds that older commit again and uploads it. Files that the bad version
   added are deleted.
4. Open the site and check it.

This is temporary: the next push to `main` or the next daily run uploads `main` again. So also do
the next step. (GitHub allows re-runs only for about 30 days.)

## Permanent: undo the change on `main`

On your PC, in the project folder:

```sh
git switch main
git pull
git log --oneline -5          # find the bad commit
git revert <commit-id>        # makes a new commit that undoes it
```

Then push or merge to `main` as usual. That push deploys the fixed version.

## Emergency

- **Stop uploads**: set the repository variable `DEPLOY_ENABLED` to `false`. The server keeps the
  files it has.
- **Show "Coming soon" again**: on the server,
  `sudo cp /etc/caddy/Caddyfile.before-launch /etc/caddy/Caddyfile`, then
  `sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` and
  `sudo systemctl reload caddy`.
