# Security policy

## Reporting a vulnerability in MCP Faultline

Please use GitHub's **private vulnerability reporting** on this repository
(Security → Report a vulnerability). Do not open a public issue. You can expect
an acknowledgement within 7 days.

## Findings about third-party MCP implementations

MCP Faultline finds interoperability and correctness defects in other projects.
If a finding could have security impact (for example, cross-session or
cross-caller response misdelivery in a multiplexing gateway), report it through
**that project's** security policy before any public discussion:

* python-sdk / typescript-sdk: see `SECURITY.md` in each repository.

Do not publish reproductions for unpatched defects that have security impact.

## Supported versions

Only the latest commit on `main` is supported.
