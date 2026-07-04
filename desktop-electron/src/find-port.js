const net = require("net");

function findFreePort(preferred = 8765, host = "127.0.0.1") {
  return new Promise((resolve, reject) => {
    const tryPort = (port) => {
      if (port > preferred + 50) {
        reject(new Error("Nessuna porta libera trovata"));
        return;
      }
      const server = net.createServer();
      server.unref();
      server.once("error", () => tryPort(port + 1));
      server.listen(port, host, () => {
        const addr = server.address();
        const bound = typeof addr === "object" && addr ? addr.port : port;
        server.close(() => resolve(bound));
      });
    };
    tryPort(preferred);
  });
}

module.exports = { findFreePort };
