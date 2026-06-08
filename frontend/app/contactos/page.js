import ContactTable from "../../components/ContactTable";
import { prisma } from "../../lib/prisma";

export const dynamic = 'force-dynamic';

export default async function Contactos() {
  const dbContacts = await prisma.contacto.findMany({
    orderBy: { id: 'desc' }
  });

  const contacts = dbContacts.map(c => ({
    id: c.id,
    name: c.nombre,
    phone: c.numero,
    birthday: new Date(c.fecha_nacimiento).toLocaleDateString('es-ES', { timeZone: 'UTC', day: 'numeric', month: 'short' }),
    active: c.activo
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Contactos</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Gestiona las personas a las que el bot enviará mensajes.</p>
      </div>

      <ContactTable contacts={contacts} />
    </div>
  );
}
