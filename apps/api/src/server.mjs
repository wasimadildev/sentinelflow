import { makeServer } from './app.mjs';

const configuredPort = Number(process.env.PORT ?? 8080);
if (!Number.isInteger(configuredPort) || configuredPort < 1 || configuredPort > 65535) {
  console.error('PORT must be an integer between 1 and 65535');
  process.exit(1);
}
const host = process.env.HOST ?? '0.0.0.0';
const server = makeServer();
server.listen(configuredPort, host, () => {
  console.log(JSON.stringify({ event: 'server_started', port: configuredPort }));
});

function shutdown(signal) {
  console.log(JSON.stringify({ event: 'shutdown', signal }));
  server.close((err) => {
    if (err) {
      console.error(err);
      process.exitCode = 1;
    }
  });
  server.closeIdleConnections();
  setTimeout(() => process.exit(1), 8000).unref();
}
process.once('SIGTERM', () => shutdown('SIGTERM'));
process.once('SIGINT', () => shutdown('SIGINT'));
