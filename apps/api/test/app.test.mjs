import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { request as httpRequest } from 'node:http';
import { makeServer } from '../src/app.mjs';

async function withApp(run) {
  const server = makeServer();
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  try {
    await run(`http://127.0.0.1:${server.address().port}`);
  } finally {
    server.closeAllConnections();
    await new Promise((resolve, reject) => server.close(err => err ? reject(err) : resolve()));
  }
}

test('health route returns readiness and safe headers', async () => {
  await withApp(async base => {
    const response = await fetch(`${base}/healthz`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { status: 'ok' });
    assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
    assert.equal(response.headers.get('cache-control'), 'no-store');
    assert.ok(response.headers.get('x-request-id'));
  });
});

test('ready route returns healthy', async () => {
  await withApp(async base => {
    const response = await fetch(`${base}/readyz`);
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { ready: true });
  });
});

test('info route reveals only intended public metadata', async () => {
  await withApp(async base => {
    const response = await fetch(`${base}/api/v1/info`);
    assert.equal(response.status, 200);
    const data = await response.json();
    assert.equal(data.service, 'sentinelflow-demo-api');
    assert.equal(data.environment, 'demo');
    assert.equal(Object.hasOwn(data, 'secrets'), false);
  });
});

test('unknown route produces 404', async () => {
  await withApp(async base => {
    const response = await fetch(`${base}/not-found`);
    assert.equal(response.status, 404);
  });
});

test('non-GET methods are rejected', async () => {
  await withApp(async base => {
    const response = await fetch(`${base}/healthz`, { method: 'POST' });
    assert.equal(response.status, 405);
    assert.equal(response.headers.get('allow'), 'GET');
  });
});

test('oversized Content-Length is rejected', async () => {
  await withApp(async base => {
    const status = await new Promise((resolve, reject) => {
      const req = httpRequest(`${base}/healthz`, {
        method: 'GET',
        headers: { 'Content-Length': '2000' },
      }, res => {
        res.resume();
        res.on('end', () => resolve(res.statusCode));
      });
      req.on('error', reject);
      req.end();
    });
    assert.equal(status, 413);
  });
});
