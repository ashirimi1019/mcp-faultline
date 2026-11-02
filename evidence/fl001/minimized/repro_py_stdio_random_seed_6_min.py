#!/usr/bin/env python3
"""Standalone reproduction exported by mcp-faultline 0.1.0 (stdlib only).

Target   : python-sdk 2.3.0 over stdio, MCP protocol 2025-11-25
Scenario : random/seed-6/min
Expected : every non-cancelled request receives exactly one successful response with its own typed id
Observed : R3: request 9007199254740991 never received a response; R6: cancelling "9007199254740991" suppressed
           the response to 9007199254740991

Usage: python repro_py_stdio_random_seed_6_min.py <server command...>
   e.g. python repro_py_stdio_random_seed_6_min.py python server.py stdio
"""

import json
import queue
import subprocess
import sys
import threading
import time

# (message, wait_for_response_id) pairs, in wire order. A wait id of None means fire-and-forget.
SCRIPT = [({'jsonrpc': '2.0',
   'id': 'fl-init',
   'method': 'initialize',
   'params': {'protocolVersion': '2025-11-25',
              'capabilities': {},
              'clientInfo': {'name': 'mcp-faultline', 'version': 'mcp-faultline 0.1.0'}}},
  'fl-init'),
 ({'jsonrpc': '2.0', 'method': 'notifications/initialized'}, None),
 ({'jsonrpc': '2.0',
   'id': '9007199254740991',
   'method': 'tools/call',
   'params': {'name': 'gate', 'arguments': {'tag': 'g0'}}},
  None),
 ({'jsonrpc': '2.0',
   'id': 9007199254740991,
   'method': 'tools/call',
   'params': {'name': 'gate', 'arguments': {'tag': 'g3'}}},
  None),
 ({'jsonrpc': '2.0',
   'method': 'notifications/cancelled',
   'params': {'requestId': '9007199254740991', 'reason': 'mcp-faultline'}},
  None),
 ({'jsonrpc': '2.0',
   'id': 'fl-ctl-1',
   'method': 'tools/call',
   'params': {'name': 'release', 'arguments': {'tag': 'g0'}}},
  'fl-ctl-1'),
 ({'jsonrpc': '2.0',
   'id': 'fl-ctl-2',
   'method': 'tools/call',
   'params': {'name': 'release', 'arguments': {'tag': 'g3'}}},
  'fl-ctl-2'),
 ({'jsonrpc': '2.0', 'id': 'fl-ctl-3', 'method': 'ping'}, 'fl-ctl-3'),
 ({'jsonrpc': '2.0',
   'id': 'fl-recovery',
   'method': 'tools/call',
   'params': {'name': 'gate', 'arguments': {'tag': 'fl-recovery'}}},
  'fl-recovery'),
 ({'jsonrpc': '2.0',
   'id': 'fl-ctl-4',
   'method': 'tools/call',
   'params': {'name': 'release', 'arguments': {'tag': 'fl-recovery'}}},
  'fl-ctl-4')]
EXPECTED_RESPONSES = [9007199254740991]  # typed ids that must each receive exactly one response


def main() -> int:
    proc = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
    inbox = queue.Queue()
    threading.Thread(target=lambda: [inbox.put(line) for line in proc.stdout], daemon=True).start()
    received = []

    def drain(until, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not until():
            try:
                line = inbox.get(timeout=0.05)
            except queue.Empty:
                continue
            msg = json.loads(line)
            received.append(msg)
            print("<-", json.dumps(msg))

    def responses_to(rid):
        # Typed comparison: 7 and "7" are different JSON-RPC ids.
        return [m for m in received if "method" not in m and type(m.get("id")) is type(rid) and m.get("id") == rid]

    def answered(rid):
        return bool(responses_to(rid))

    for message, wait_id in SCRIPT:
        print("->", json.dumps(message))
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()
        if wait_id is not None:
            drain(lambda rid=wait_id: answered(rid), 10)
    drain(lambda: all(answered(r) for r in EXPECTED_RESPONSES), 5)
    drain(lambda: False, 0.5)
    proc.kill()

    failed = False
    for rid in EXPECTED_RESPONSES:
        n = len(responses_to(rid))
        if n != 1:
            failed = True
            print(f"FAIL: request id {json.dumps(rid)} received {n} responses (expected exactly 1)")
        else:
            resp = responses_to(rid)[0]
            if "error" in resp:
                failed = True
                print(f"FAIL: request id {json.dumps(rid)} was never cancelled but got error {resp['error']}")
    print("RESULT:", "defect reproduced" if failed else "no defect observed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
