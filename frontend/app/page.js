import StatCard from "../components/StatCard";
import LogTable from "../components/LogTable";
import { prisma } from "../lib/prisma";

export const dynamic = 'force-dynamic';

export default async function Dashboard() {
  const activeContactsCount = await prisma.contacto.count({
    where: { activo: true }
  });

  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const startOfNextMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1);

  const sentThisMonthCount = await prisma.log.count({
    where: {
      estado: "Enviado",
      fecha_hora_envio: {
        gte: startOfMonth,
        lt: startOfNextMonth
      }
    }
  });

  const allActiveContacts = await prisma.contacto.findMany({
    where: { activo: true }
  });

  const todayMonth = now.getUTCMonth();
  const todayDate = now.getUTCDate();

  const hoyCumple = allActiveContacts.filter(c => {
    const bday = new Date(c.fecha_nacimiento);
    return bday.getUTCMonth() === todayMonth && bday.getUTCDate() === todayDate;
  });

  // Calculate next birthday
  let nextBirthday = null;
  let minDiff = Infinity;
  const currentYear = now.getUTCFullYear();

  allActiveContacts.forEach(c => {
    const bday = new Date(c.fecha_nacimiento);
    let nextBdayThisYear = new Date(currentYear, bday.getUTCMonth(), bday.getUTCDate());
    
    // Si ya pasó este año, el próximo es el año que viene
    if (nextBdayThisYear < now && !(bday.getUTCMonth() === todayMonth && bday.getUTCDate() === todayDate)) {
      nextBdayThisYear = new Date(currentYear + 1, bday.getUTCMonth(), bday.getUTCDate());
    }

    const diff = nextBdayThisYear - now;
    if (diff > 0 && diff < minDiff) {
      minDiff = diff;
      nextBirthday = c;
    }
  });

  const nextBirthdayFormatted = nextBirthday 
    ? new Date(nextBirthday.fecha_nacimiento).toLocaleDateString('es-ES', { timeZone: 'UTC', day: 'numeric', month: 'short' })
    : "-";

  const rawLogs = await prisma.log.findMany({
    include: { contacto: true },
    orderBy: { fecha_hora_envio: 'desc' },
    take: 5
  });

  const recentLogs = rawLogs.map(log => ({
    contact: log.contacto.nombre,
    message: log.mensaje,
    datetime: new Date(log.fecha_hora_envio).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }),
    status: log.estado
  }));

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Resumen de la actividad de tu bot de cumpleaños.</p>
      </div>

      {hoyCumple.length > 0 && (
        <div className="rounded-2xl bg-gradient-to-r from-accent to-accent-light p-6 text-white shadow-lg shadow-accent/20">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 text-2xl backdrop-blur-md">
              🎂
            </div>
            <div>
              <h2 className="text-lg font-bold">¡Hoy hay cumpleaños!</h2>
              <p className="text-white/80">
                El bot tiene programado enviar mensajes a {hoyCumple.length} {hoyCumple.length === 1 ? "contacto" : "contactos"} hoy.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="grid gap-5 md:grid-cols-3">
        <StatCard
          title="Contactos Activos"
          value={activeContactsCount.toString()}
          subtitle="Total registrados"
          icon={
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          }
        />
        <StatCard
          title="Enviados este mes"
          value={sentThisMonthCount.toString()}
          subtitle="Mensajes exitosos"
          accent
          icon={
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          }
        />
        <StatCard
          title="Próximo Cumpleaños"
          value={nextBirthdayFormatted}
          subtitle={nextBirthday ? nextBirthday.nombre : "Sin contactos"}
          icon={
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          }
        />
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-zinc-900 dark:text-white">Actividad Reciente</h2>
        </div>
        <LogTable logs={recentLogs} />
      </div>
    </div>
  );
}
