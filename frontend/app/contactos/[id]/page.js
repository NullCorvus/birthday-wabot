import Link from "next/link";
import EditContactForm from "./EditContactForm";
import { prisma } from "../../../lib/prisma";

export const dynamic = 'force-dynamic';

export default async function EditarContacto({ params }) {
  const { id } = await params;
  const contact = await prisma.contacto.findUnique({
    where: { id: parseInt(id, 10) }
  });

  if (!contact) {
    return (
      <div className="max-w-2xl space-y-6">
        <div>
          <Link href="/contactos" className="mb-4 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver a contactos
          </Link>
          <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Contacto no encontrado</h1>
        </div>
      </div>
    );
  }

  const initialData = {
    name: contact.nombre,
    phone: contact.numero,
    birthday: contact.fecha_nacimiento.toISOString().split('T')[0],
    active: contact.activo
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <Link href="/contactos" className="mb-4 inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white">
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a contactos
        </Link>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Editar Contacto</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Modifica los datos del contacto o desactiva sus notificaciones.</p>
      </div>

      <EditContactForm contactId={id} initialData={initialData} />
    </div>
  );
}
