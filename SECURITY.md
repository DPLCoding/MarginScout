# Security policy

This repository is a non-operational source excerpt. It does not operate a public service, include credentials, or contain a network-capable Reddit transport.

## Reporting

Please report a suspected vulnerability privately to **dyuchuan@gmail.com**. Do not include secrets, personal data, or live third-party content in a report.

## Security boundaries demonstrated here

- Runtime tokens are provided by an injected token provider and never stored in source code.
- An approval record for the stated use, expiry date, and exact community allowlist are checked before a transport can be invoked.
- Only an exact HTTPS OAuth origin and read-only newest-post path are constructed.
- Requested items and timeouts are bounded.
- Rate-limit response headers are returned to the caller for persistent accounting.
- Deleted content, deleted authors, and expired content produce explicit redaction decisions.
- Tests use a fake transport and synthetic content.

Complete-application concerns such as authentication, secret management, TLS termination, encrypted backups, dependency scanning, and incident response live in the private development repository.
