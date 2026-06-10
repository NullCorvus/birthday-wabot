const cron = require('node-cron');
const { PrismaClient } = require('@prisma/client');
const { PrismaPg } = require('@prisma/adapter-pg');
const { logOfflineEvent } = require('./utils/logger');

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL });
const prisma = new PrismaClient({ adapter });

async function processBirthdays(client, forceSend = false) {
  try {
    console.log('[SCHEDULER] Iniciando revisión de cumpleaños...');
    
    // Test DB Connection
    await prisma.$queryRaw`SELECT 1`;

    const templateRow = await prisma.mensajetxt.findFirst();
    if (!templateRow) {
      console.log('[SCHEDULER] No hay plantilla de mensaje configurada.');
      return;
    }
    const templateText = templateRow.texto;

    // Obtener fecha actual en la zona horaria local (Windows)
    const today = new Date();
    const todayMonth = today.getMonth() + 1;
    const todayDay = today.getDate();

    // Obtener contactos activos cuyo cumpleaños es hoy
    const contacts = await prisma.$queryRaw`
      SELECT * FROM "contactos" 
      WHERE "activo" = true 
        AND EXTRACT(MONTH FROM "fecha_nacimiento") = ${todayMonth} 
        AND EXTRACT(DAY FROM "fecha_nacimiento") = ${todayDay}
    `;

    if (contacts.length === 0) {
      console.log(`[SCHEDULER] No hay cumpleaños para el día de hoy (${todayDay}/${todayMonth}).`);
      return;
    }

    const startOfDay = new Date();
    startOfDay.setHours(0, 0, 0, 0);

    for (const contact of contacts) {
      try {
        const logsToday = await prisma.log.findMany({
          where: {
            contacto_id: contact.id,
            fecha_hora_envio: { gte: startOfDay }
          }
        });

        const hasSuccess = logsToday.some(l => l.estado === 'Enviado');
        const failedCount = logsToday.filter(l => l.estado === 'Fallido').length;

        if (hasSuccess) {
          console.log(`[SCHEDULER] Mensaje a ${contact.nombre} ya fue enviado exitosamente hoy.`);
          continue;
        }

        if (failedCount >= 3) {
          console.log(`[SCHEDULER] Máximo de reintentos (3) alcanzado para ${contact.nombre} hoy. Se omitirá.`);
          continue;
        }

        // Proceder a enviar
        const message = templateText.replace(/{nombre}/g, contact.nombre);
        
        // WhatsApp format is usually CountryCode+Number@c.us, e.g. 573213774603@c.us
        // Remove spaces, + and non-digits from the phone number
        const cleanNumber = contact.numero.replace(/\D/g, '');
        const chatId = `${cleanNumber}@c.us`;

        console.log(`[SCHEDULER] Intentando enviar a ${contact.nombre} (${chatId}). Intento ${failedCount + 1}/3...`);
        
        try {
          await client.sendMessage(chatId, message);
          
          await prisma.log.create({
            data: {
              contacto_id: contact.id,
              mensaje: message,
              estado: 'Enviado'
            }
          });
          console.log(`[SCHEDULER] Mensaje enviado a ${contact.nombre} con éxito.`);

        } catch (sendErr) {
          console.error(`[SCHEDULER] Error de WhatsApp enviando a ${contact.nombre}:`, sendErr.message);
          
          await prisma.log.create({
            data: {
              contacto_id: contact.id,
              mensaje: message,
              estado: 'Fallido',
              detalle: sendErr.message
            }
          });
        }

      } catch (contactErr) {
        console.error(`[SCHEDULER] Error procesando contacto ${contact.nombre}:`, contactErr);
      }
    }

    console.log('[SCHEDULER] Revisión de cumpleaños finalizada.');

  } catch (err) {
    console.error('[SCHEDULER] Error de Base de Datos:', err.message);
    logOfflineEvent(`Error de conexión a BD o ejecución general: ${err.message}`);
  }
}

// Configurar el Cron (ej. 09:00, 13:00, 17:00 todos los días)
function startScheduler(client) {
  console.log('[SCHEDULER] Tarea programada iniciada (09:00, 13:00, 17:00)');
  cron.schedule('0 9,13,17 * * *', () => {
    processBirthdays(client);
  });
}

module.exports = { startScheduler, processBirthdays };
