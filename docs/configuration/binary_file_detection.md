# Binary file detection

Before processing, `mklists` checks each data file for binary content. The check
reads the first 8192 bytes of the file and raises an error if a NUL byte (`\x00`)
is found.

This is the same heuristic used by ripgrep: both treat NUL-byte presence in the
leading 8192-byte window as the signal for binary content. The practical difference
is purpose — ripgrep uses the result to suppress output, while `mklists` uses it
to abort processing.

If this error occurs, the file should be removed from the data directory before
running `mklists` again.
