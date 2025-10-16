# Data Retention & Deletion

- Dataset manifest records `consent` per sample.
- To honor deletion: remove files, update manifest, and re-run dataset preparation.
- Keep audit logs (hashes) to verify removal.
- For backups (DVC/Git LFS), purge remote copies as well.

