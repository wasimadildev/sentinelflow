import { createServer } from 'node:http';
import { randomUUID } from 'node:crypto';

const MAX_REQUEST_BODY_BYTES = 1024;

function sendJson(res, status, payload, requestId) {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
    'Referrer-Policy': 'no-referrer',
    'X-Request-ID': requestId,
  });
  res.end(JSON.stringify(payload));
}

export function makeServer() {
  const server = createServer((req, res) => {
    const requestId = randomUUID();
    // No dynamic file paths, command execution, authentication secrets, or query reflection.
    const path = new URL(req.url ?? '/', 'http://localhost').pathname;
    const allowedPaths = new Set(['/healthz', '/readyz', '/api/v1/info']);

    if (!allowedPaths.has(path)) {
      return sendJson(res, 404, { error: 'not_found' }, requestId);
    }
    if (req.method !== 'GET') {
      res.setHeader('Allow', 'GET');
      return sendJson(res, 405, { error: 'method_not_allowed' }, requestId);
    }
    const declaredLength = Number(req.headers['content-length'] || '0');
    if (Number.isNaN(declaredLength) || declaredLength > MAX_REQUEST_BODY_BYTES) {
      return sendJson(res, 413, { error: 'request_too_large' }, requestId);
    }
    if (path === '/healthz') return sendJson(res, 200, { status: 'ok' }, requestId);
    if (path === '/readyz') return sendJson(res, 200, { ready: true }, requestId);
    return sendJson(res, 200, {
      service: 'sentinelflow-demo-api',
      version: '0.1.0',
      environment: 'demo',
    }, requestId);
  });
  server.requestTimeout = 10_000;
  server.headersTimeout = 15_000;
  server.keepAliveTimeout = 5_000;
  server.maxRequestsPerSocket = 100;
  return server;
}
