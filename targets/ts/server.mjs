// MCP Faultline target: official TypeScript SDK server.
//
// Same deterministic tools as targets/python/server.py:
//   gate(tag)    blocks until release(tag) is called (or the request is cancelled), returns tag
//   release(tag) opens the gate for tag (idempotent; may precede gate)
//
// Usage:
//   node server.mjs stdio
//   node server.mjs http --port 8765 [--json-response]
import { randomUUID } from 'node:crypto';
import { createServer } from 'node:http';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { z } from 'zod';

const gates = new Map();

function gateFor(tag) {
  let g = gates.get(tag);
  if (!g) {
    let open;
    const promise = new Promise((resolve) => { open = resolve; });
    g = { promise, open };
    gates.set(tag, g);
  }
  return g;
}

function buildServer() {
  const server = new McpServer({ name: 'faultline-ts-target', version: '0.0.0' });
  server.registerTool('gate', { inputSchema: { tag: z.string() } }, async ({ tag }, extra) => {
    const aborted = new Promise((_, reject) => {
      if (extra.signal.aborted) reject(new Error('cancelled'));
      extra.signal.addEventListener('abort', () => reject(new Error('cancelled')), { once: true });
    });
    await Promise.race([gateFor(tag).promise, aborted]);
    return { content: [{ type: 'text', text: tag }] };
  });
  server.registerTool('release', { inputSchema: { tag: z.string() } }, async ({ tag }) => {
    gateFor(tag).open();
    return { content: [{ type: 'text', text: tag }] };
  });
  return server;
}

const [mode, ...rest] = process.argv.slice(2);
const flag = (name) => rest.includes(name);
const option = (name, fallback) => {
  const i = rest.indexOf(name);
  return i >= 0 ? rest[i + 1] : fallback;
};

if (mode === 'stdio') {
  await buildServer().connect(new StdioServerTransport());
} else if (mode === 'http') {
  const port = Number(option('--port', '8765'));
  const sessions = new Map();
  const http = createServer(async (req, res) => {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const raw = Buffer.concat(chunks).toString('utf8');
    const body = raw ? JSON.parse(raw) : undefined;
    const sid = req.headers['mcp-session-id'];
    let transport = sid ? sessions.get(sid) : undefined;
    if (!transport) {
      if (sid) {
        res.writeHead(404).end();
        return;
      }
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        enableJsonResponse: flag('--json-response'),
        onsessioninitialized: (id) => sessions.set(id, transport),
      });
      await buildServer().connect(transport);
    }
    await transport.handleRequest(req, res, body);
  });
  http.listen(port, '127.0.0.1', () => process.stderr.write(`listening ${port}\n`));
} else {
  process.stderr.write('usage: server.mjs stdio | http --port N [--json-response]\n');
  process.exit(2);
}
