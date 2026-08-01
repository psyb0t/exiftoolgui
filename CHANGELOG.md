# Changelog

All notable changes per release. Versions follow [semver](https://semver.org).

## 0.1.9 — 2026-08-01

Infrastructure only. No code in this repo changed — every commit since 0.1.8 touches `.github/workflows/`.

- The pipeline was split: building and publishing stay in `pipeline.yml`, and everything that leaves the host now lives beside it in `mirror-and-archive.yml`.
- The repo is mirrored to Codeberg as well as GitLab.
- It is archived to the Wayback Machine, Software Heritage and archive.org.
- Issues opened on either mirror are copied back to GitHub every six hours, and closed here when the original closes.
- Pull requests are switched off on the mirrors: they are force-pushed from GitHub, so anything merged there would be destroyed by the next sync. Issues and forking stay enabled.
