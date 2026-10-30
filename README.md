# Port Scanner

A multi-threaded TCP port scanner written in Python. It tries to connect to each port on a target and reports the ones that accept a connection, with a guessed service name for common ports.

## Authorized use only

Only scan hosts you own or have written permission to test. Scanning other people's systems without permission is illegal in most places.

## Requirements

- Python 3
- `colorama` and `tqdm`

```bash
pip install colorama tqdm
```

## Usage

```bash
python3 scanner.py 192.168.1.10
```

Options:

| Flag | Description |
|------|-------------|
| `target` | Target IP address or hostname (IPv4 only) |
| `-p`, `--ports` | Ports to scan, e.g. `22,80,443` or `1-1000` (default: `1-1000`) |
| `-t`, `--threads` | Number of threads (default: 50) |
| `--timeout` | Connection timeout in seconds (default: 1) |
| `-o`, `--output` | Save open ports to a file |
| `-f`, `--format` | Output format for `-o`: `json` or `csv` (default: `json`) |

Port lists can mix single ports and ranges:

```bash
python3 scanner.py 192.168.1.10 -p 22,80,8000-8100 -o results.json
```

## Output

The scanner prints each open port as it finds it, then a summary table:

```
Port    Service
------------------------------
   22   SSH
   80   HTTP
```

JSON output looks like this:

```json
{
  "target": "192.168.1.10",
  "timestamp": "2026-10-30T14:30:00",
  "open_ports": [
    {"port": 22, "service": "SSH"},
    {"port": 80, "service": "HTTP"}
  ]
}
```

CSV output has one row per open port with `Port`, `Service`, and `Timestamp` columns.

## Service names

Service names come from a fixed list of common ports: FTP, SSH, Telnet, SMTP, DNS, HTTP, POP3, IMAP, HTTPS, MySQL, PostgreSQL, RDP, VNC, and a few HTTP alternates. Any other open port is labelled `Unknown`. The name is only a guess from the port number, not a check of what is actually running.

## Limitations

- TCP connect scan only. It does not do UDP, SYN scans, or service version detection.
- IPv4 only.
- The scanner waits for each connection attempt to time out, so large port ranges can take a while.
- Results depend on the network path. Firewalls can make ports look closed when they are not.
