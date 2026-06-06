const fs = require('fs');
const path = require('path');

const logDir = path.join(__dirname, '..', 'logs');

// Ensure log directory exists
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const offlineLogPath = path.join(logDir, 'offline.log');

function logOfflineEvent(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(offlineLogPath, logMessage, 'utf8');
  console.log(`[OFFLINE LOG] ${message}`);
}

module.exports = { logOfflineEvent };
