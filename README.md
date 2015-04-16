# TrapDoor
## Scalable, Targeted, Dynamic packet capture engine in Python.

### Requiremetns
- Capture packets only for list of IP or Domain.
- IPs/Domains can change any time.
- Minimise down-time.
- Provide realtime analysis.

### Architecture

#### Startup

```
boot.py
|-> Controller
  |-> FilterManager ( Child Process)
  |-> LoggerManager ( Child Process)
  |-> NetworkManager ( Child Process)
  |-> DNSManager ( Thread)
```
