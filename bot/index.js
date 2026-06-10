const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

console.log('Iniciando el bot de WhatsApp...');

// Buscar ruta del navegador instalado en el sistema para evitar descargas corruptas de Puppeteer
const getChromePath = () => {
    const paths = [
        '/usr/bin/google-chrome-stable',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    ];
    for (const p of paths) {
        if (fs.existsSync(p)) {
            console.log(`Usando navegador del sistema encontrado en: ${p}`);
            return p;
        }
    }
    return undefined;
};

// Configuración compatible con Windows y Linux (incluyendo entornos sin sandbox)
const client = new Client({
    authStrategy: new LocalAuth({
        clientId: "birthday-wabot-session"
    }),
    webVersion: '2.2412.54',
    webVersionCache: {
        type: 'remote',
        remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html'
    },
    puppeteer: {
        headless: true,
        executablePath: getChromePath(),
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--disable-gpu'
        ]
    }
});

client.on('loading_screen', (percent, message) => {
    console.log(`Cargando WhatsApp Web: ${percent}% - ${message}`);
});

const https = require('https');

client.on('qr', (qr) => {
    console.log('\n==================================================================');
    console.log('Escanea este código QR con tu aplicación de WhatsApp (Dispositivos Vinculados):');
    console.log('==================================================================\n');
    qrcode.generate(qr, { small: true });
    
    // Guardar imagen y actualizar estado para la interfaz gráfica
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
    
    const statusPath = path.join(__dirname, 'status.json');
    fs.writeFileSync(statusPath, JSON.stringify({ state: 'qr_ready', timestamp: Date.now() }));
});

client.on('auth_failure', (msg) => {
    console.error('Fallo en la autenticación:', msg);
});

let birthdaysProcessed = false;

async function runBirthdayCheck(client) {
    if (birthdaysProcessed) return;
    birthdaysProcessed = true;
    console.log('\n📋 Ejecutando revisión de cumpleaños...');
    try {
        const { processBirthdays } = require('./scheduler');
        await processBirthdays(client);
    } catch (err) {
        console.error('Error en revisión de cumpleaños:', err);
    }
}

client.on('ready', async () => {
    console.log('\n=========================================');
    console.log('¡El cliente de WhatsApp está listo!');
    console.log('=========================================\n');
    
    // Eliminar QR viejo y actualizar estado
    const qrPath = path.join(__dirname, 'qr.png');
    if (fs.existsSync(qrPath)) fs.unlinkSync(qrPath);
    const statusPath = path.join(__dirname, 'status.json');
    fs.writeFileSync(statusPath, JSON.stringify({ state: 'running', timestamp: Date.now() }));
    
    const { startScheduler, processBirthdays } = require('./scheduler');
    startScheduler(client);
    await runBirthdayCheck(client);
});

// Fallback: si ready no se dispara, procesar igual cuando esté autenticado
client.on('authenticated', () => {
    console.log('¡Autenticado con éxito en WhatsApp!');
    
    // Eliminar QR viejo y actualizar estado
    const qrPath = path.join(__dirname, 'qr.png');
    if (fs.existsSync(qrPath)) fs.unlinkSync(qrPath);
    const statusPath = path.join(__dirname, 'status.json');
    fs.writeFileSync(statusPath, JSON.stringify({ state: 'running', timestamp: Date.now() }));
    
    setTimeout(() => {
        if (!birthdaysProcessed) {
            console.log('⚠️  ready no se disparó, ejecutando revisión igual...');
            runBirthdayCheck(client);
        }
    }, 15000);
});

client.on('disconnected', (reason) => {
    console.log('El cliente se desconectó:', reason);
    const statusPath = path.join(__dirname, 'status.json');
    fs.writeFileSync(statusPath, JSON.stringify({ state: 'disconnected', reason: reason, timestamp: Date.now() }));
});

// Matar procesos Chrome huerfanos que aun tengan el lock del userDataDir
const SESSION_DIR = path.join(__dirname, '.wwebjs_auth', 'session-birthday-wabot-session');
if (process.platform === 'win32') {
    try { require('child_process').execSync('taskkill /F /IM chrome.exe /FI "WINDOWTITLE eq birthday-wabot*" 2>nul', { stdio: 'ignore' }); } catch {}
} else {
    try { require('child_process').execSync(`pkill -f "${SESSION_DIR}" 2>/dev/null`, { stdio: 'ignore' }); } catch {}
    try { require('child_process').execSync(`pkill -f "chrome.*birthday-wabot" 2>/dev/null`, { stdio: 'ignore' }); } catch {}
}

// Watcher para trigger manual desde la GUI
setInterval(async () => {
    const triggerPath = path.join(__dirname, '.trigger_send');
    if (fs.existsSync(triggerPath)) {
        console.log('\n[MANUAL TRIGGER] Detectada solicitud de envío manual desde la GUI.');
        try {
            fs.unlinkSync(triggerPath);
            const { processBirthdays } = require('./scheduler');
            // Pasamos "true" para forzar el reenvío incluso si ya se envió hoy
            await processBirthdays(client, true);
        } catch (err) {
            console.error('Error en trigger manual:', err);
        }
    }
}, 2000);

console.log('Llamando a client.initialize()...');
client.initialize();
