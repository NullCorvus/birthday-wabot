const { makeWASocket, useMultiFileAuthState, DisconnectReason } = require('@whiskeysockets/baileys');
const { exec } = require('child_process');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
const https = require('https');
const pino = require('pino');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

console.log('Iniciando el bot de WhatsApp...');

const AUTH_DIR = path.join(__dirname, 'auth_info_baileys');

let sock;
let birthdaysProcessed = false;

async function runBirthdayCheck(sock) {
    if (birthdaysProcessed) return;
    birthdaysProcessed = true;
    console.log('\n📋 Ejecutando revisión de cumpleaños...');
    try {
        const { processBirthdays } = require('./scheduler');
        await processBirthdays(sock);
    } catch (err) {
        console.error('Error en revisión de cumpleaños:', err);
    }
}

function downloadQrImage(qr) {
    const qrPath = path.join(__dirname, 'qr.png');
    const url = 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=' + encodeURIComponent(qr);
    https.get(url, (res) => {
        const file = fs.createWriteStream(qrPath);
        res.pipe(file);
        file.on('finish', () => {
            file.close();
            console.log('✅ QR guardado como imagen para la GUI.');
        });
    }).on('error', (err) => {
        console.error('Error al descargar el QR:', err.message);
    });
}

function setStatus(state, extra = {}) {
    const statusPath = path.join(__dirname, 'status.json');
    fs.writeFileSync(statusPath, JSON.stringify({ state, ...extra, timestamp: Date.now() }));
}

function cleanQr() {
    const qrPath = path.join(__dirname, 'qr.png');
    if (fs.existsSync(qrPath)) fs.unlinkSync(qrPath);
}

function cleanAuth() {
    if (fs.existsSync(AUTH_DIR)) fs.rmSync(AUTH_DIR, { recursive: true, force: true });
}

let reconnectAttempts = 0;
const MAX_RECONNECT = 5;

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);

    sock = makeWASocket({
        auth: state,
        browser: ['Birthday Wabot', 'Chrome', '1.0.0'],
        logger: pino({ level: 'silent' }),
        defaultQueryTimeoutMs: undefined,
        connectTimeoutMs: 60_000,
        keepAliveIntervalMs: 30_000
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            reconnectAttempts = 0;
            console.log('\n==================================================================');
            console.log('Escanea este código QR con tu aplicación de WhatsApp (Dispositivos Vinculados):');
            console.log('==================================================================\n');
            qrcode.generate(qr, { small: true });
            downloadQrImage(qr);
            setStatus('qr_ready');
        }

        if (connection === 'open') {
            console.log('\n=========================================');
            console.log('¡El cliente de WhatsApp está listo!');
            console.log('=========================================\n');

            cleanQr();
            setStatus('running');
            reconnectAttempts = 0;

            const { startScheduler } = require('./scheduler');
            startScheduler(sock);
            await runBirthdayCheck(sock);
        }

        if (connection === 'close') {
            const raw = lastDisconnect?.error;
            const statusCode = raw?.output?.statusCode || raw?.statusCode || 'N/A';
            const message = raw?.message || raw?.toString() || 'Desconocido';
            const fullError = raw ? JSON.stringify(raw, Object.getOwnPropertyNames(raw), 2) : 'sin detalles';

            console.log('\n--- Desconexión Detectada ---');
            console.log('Código:', statusCode);
            console.log('Mensaje:', message);
            console.log('Detalle completo:', fullError);
            console.log('-----------------------------\n');

            setStatus('disconnected', { reason: String(statusCode) });

            if (statusCode === DisconnectReason.loggedOut) {
                console.log('[LOGGED_OUT] Sesión cerrada. Borrando credenciales...');
                cleanAuth();
                birthdaysProcessed = false;
                reconnectAttempts = 0;

                const msgCommand = `msg * "ATENCION: La sesion de WhatsApp del bot se ha cerrado. Busca 'Birthday Wabot Manager' en tu Escritorio o Menu de Inicio, abrelo y escanea el QR nuevamente."`;
                exec(msgCommand, (error) => {
                    if (error) console.error("Error al mostrar la alerta:", error);
                });

                setTimeout(connectToWhatsApp, 3000);
                return;
            }

            if (statusCode === DisconnectReason.restartRequired) {
                console.log('[RESTART] Reinicio solicitado. Reconectando...');
                reconnectAttempts = 0;
                setTimeout(connectToWhatsApp, 3000);
                return;
            }

            if (statusCode === DisconnectReason.connectionClosed || statusCode === DisconnectReason.timedOut) {
                console.log('[NETWORK] Pérdida de conexión. Reconectando...');
                reconnectAttempts = 0;
                setTimeout(connectToWhatsApp, 5000);
                return;
            }

            reconnectAttempts++;
            if (reconnectAttempts > MAX_RECONNECT) {
                console.error(`[FATAL] ${MAX_RECONNECT} intentos fallidos. Limpiando sesión y reintentando...`);
                cleanAuth();
                birthdaysProcessed = false;
                reconnectAttempts = 0;
                setTimeout(connectToWhatsApp, 5000);
                return;
            }

            console.log(`[RETRY ${reconnectAttempts}/${MAX_RECONNECT}] Reconectando en 5s...`);
            await new Promise(resolve => setTimeout(resolve, 5000));
            connectToWhatsApp();
        }
    });
}

connectToWhatsApp().catch(err => {
    console.error('Error fatal al iniciar el bot:', err);
    process.exit(1);
});

setInterval(async () => {
    const triggerPath = path.join(__dirname, '.trigger_send');
    if (fs.existsSync(triggerPath)) {
        console.log('\n[MANUAL TRIGGER] Detectada solicitud de envío manual desde la GUI.');
        try {
            fs.unlinkSync(triggerPath);
            const { processBirthdays } = require('./scheduler');
            await processBirthdays(sock, true);
        } catch (err) {
            console.error('Error en trigger manual:', err);
        }
    }
}, 2000);
