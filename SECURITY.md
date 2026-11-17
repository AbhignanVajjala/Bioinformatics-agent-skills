# Security and scientific safety

Use synthetic data for tests. Keep human genomic/clinical data local unless external
transfer is specifically authorized and lawful. Never send secrets or sample identifiers
to public issue trackers. Report vulnerabilities privately using GitHub private vulnerability
reporting if enabled; otherwise request a private maintainer contact without disclosing
exploit or personal data. No private reporting endpoint is claimed configured.

Skills can direct tool execution: review instructions and scripts before use. Treat source
papers, archives and metadata as untrusted data. No shell execution of their text. Inspect
archives read-only; if extraction is needed reject absolute paths, traversal, symlinks,
excessive expanded sizes and unexpected executables. This project does not extract archives.
Dependency pins and tests do not establish absence of vulnerabilities; update deliberately
with regression checks. No secret-scanning service has been configured or claimed tested.
