# Auth Ownership Table

Every aspect of authentication has a single owner. No gaps, no overlaps.

| Auth Concern | Owner |
|---|---|
| Auth strategy & model | Architect Agent |
| Auth data model (users, sessions, roles) | Architect Agent |
| Login/signup/recovery UX flows | UI/UX Agent |
| Auth component design + all states | UI/UX Agent |
| Auth implementation (code) | Full Stack Agent |
| Auth unit tests + edge cases | Full Stack Agent |
| Auth flow testing (happy + unhappy paths) | QA Agent |
| Deployment secrets management (env vars, secret rotation) | DevOps Agent |
| Auth security constraints | Security Agent |
| Auth code audit | Security Agent |
| Auth launch sign-off | Security Agent |
