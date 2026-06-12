# Security Policy

## Supported versions

This is a personal open-source project. Only the latest commit on `main` is maintained.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Send a private email to **bubnovsa99@gmail.com** with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact

You will receive a response within 7 days. If the issue is confirmed, a fix will be
released as soon as reasonably possible and credited to you in the release notes
(unless you prefer to remain anonymous).

## Scope

This project is designed to run on a private local network (Mac + GPU box).
It has no authentication layer by design — exposing `server :8000` or
`model_server :8001` to the public internet is out of scope and strongly discouraged.
