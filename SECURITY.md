# Security Policy

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email **arunrajiah@gmail.com** or use [GitHub private vulnerability reporting](https://github.com/arunrajiah/speciesnet-studio/security/advisories/new).

Include:
- Description of the vulnerability and its potential impact
- Steps to reproduce
- Any suggested mitigations

We will acknowledge your report within 48 hours and aim to publish a fix within 7 days for critical issues.

## Scope

Studio processes local files on your own machine. It does not transmit data externally. The main attack surface is the FastAPI service bound to localhost — if you expose port 8000 to a network, ensure appropriate firewall rules are in place.
