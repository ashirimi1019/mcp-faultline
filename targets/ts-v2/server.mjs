// MCP Faultline target: official TypeScript SDK v2 (@modelcontextprotocol/server).
//
// Same deterministic tools as the other targets:
//   gate(tag)    blocks until release(tag) is called (or the request is cancelled), returns tag
//   release(tag) opens the gate for tag (idempotent; may precede gate)
//
// Usage:
//   node server.mjs stdio
//   node server.mjs http --port 8765 [--json-response]
//
// HTTP uses the SDK's WebStandardStreamableHTTPServerTransport behind a minimal
// node:http <-> Fetch API adapter (Node >= 20 provides Request/Response).
import { randomUUID } from 'node:crypto';
import { createServer } from 'node:http';
import { Readable } from 'node:stream';
import { McpServer, WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
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
  const server = new McpServer({ name: 'faultline-ts-v2-target', version: '0.0.0' });
  const args = z.object({ tag: z.string() });
  server.registerTool('gate', { inputSchema: args }, async ({ tag }, ctx) => {
    const signal = ctx.mcpReq.signal;
    const aborted = new Promise((_, reject) => {
      if (signal.aborted) reject(new Error('cancelled'));
      signal.addEventListener('abort', () => reject(new Error('cancelled')), { once: true });
    });
    await Promise.race([gateFor(tag).promise, aborted]);
    return { content: [{ type: 'text', text: tag }] };
  });
  server.registerTool('release', { inputSchema: args }, async ({ tag }) => {
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

async function toWebRequest(req, port) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) {
    if (v !== undefined) headers.set(k, Array.isArray(v) ? v.join(', ') : v);
  }
  const body = chunks.length && req.method !== 'GET' && req.method !== 'HEAD' ? Buffer.concat(chunks) : undefined;
  return new Request(`http://127.0.0.1:${port}${req.url}`, { method: req.method, headers, body });
}

async function sendWebResponse(webRes, res) {
  res.writeHead(webRes.status, Object.fromEntries(webRes.headers.entries()));
  if (!webRes.body) {
    res.end();
    return;
  }
  Readable.fromWeb(webRes.body).pipe(res);
}

if (mode === 'stdio') {
  await buildServer().connect(new StdioServerTransport());
} else if (mode === 'http') {
  const port = Number(option('--port', '8765'));
  const sessions = new Map();
  const http = createServer(async (req, res) => {
    try {
      const request = await toWebRequest(req, port);
      const sid = req.headers['mcp-session-id'];
      let transport = sid ? sessions.get(sid) : undefined;
      if (!transport) {
        if (sid) {
          res.writeHead(404).end();
          return;
        }
        transport = new WebStandardStreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          enableJsonResponse: flag('--json-response'),
          onsessioninitialized: (id) => sessions.set(id, transport),
        });
        await buildServer().connect(transport);
      }
      await sendWebResponse(await transport.handleRequest(request), res);
    } catch (err) {
      process.stderr.write(`adapter error: ${err?.stack ?? err}\n`);
      if (!res.headersSent) res.writeHead(500);
      res.end();
    }
  });
  http.listen(port, '127.0.0.1', () => process.stderr.write(`listening ${port}\n`));
} else {
  process.stderr.write('usage: server.mjs stdio | http --port N [--json-response]\n');
  process.exit(2);
}
