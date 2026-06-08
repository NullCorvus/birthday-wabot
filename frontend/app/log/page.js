import LogTable from "../../components/LogTable";
import { prisma } from "../../lib/prisma";

export const dynamic = 'force-dynamic';

export default async function Historial() {
  const dbLogs = await prisma.log.findMany({
    include: { contacto: true },
    orderBy: { fecha_hora_envio: 'desc' },
    take: 100 // Mostrar los últimos 100
  });

  const logs = dbLogs.map(log => ({
    contact: log.contacto.nombre,
    message: log.mensaje,
    datetime: new Date(log.fecha_hora_envio).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }),
    status: log.estado
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Historial de Envíos</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Revisa todos los mensajes enviados por el bot y su estado.</p>
      </div>

      <LogTable logs={logs} />
    </div>
  );
}
