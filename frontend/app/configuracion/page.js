import ConfiguracionForm from "./ConfiguracionForm";
import { prisma } from "../../lib/prisma";

export const dynamic = 'force-dynamic';

export default async function Configuracion() {
  // Try to find the first template
  let template = await prisma.mensajetxt.findFirst();

  // If no template exists, create a default one
  if (!template) {
    template = await prisma.mensajetxt.create({
      data: {
        nombre: "Mensaje de cumpleaños estándar",
        texto: "¡Feliz cumpleaños {nombre}! 🎂\n\nQue pases un gran día lleno de alegrías y rodeado de tus seres queridos.\n\nTe deseamos lo mejor en este nuevo año de vida. 🎉"
      }
    });
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Configuración</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Ajusta la plantilla del mensaje de cumpleaños.</p>
      </div>

      <ConfiguracionForm 
        templateId={template.id} 
        initialName={template.nombre} 
        initialMessage={template.texto} 
      />
    </div>
  );
}
