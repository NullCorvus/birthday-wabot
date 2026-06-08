"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import FormInput from "../../../components/FormInput";
import PhoneInput from "../../../components/PhoneInput";
import { createContact } from "../../actions";

export default function NuevoContacto() {
  const router = useRouter();

  const handleSave = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const result = await createContact(formData);
    
    if (result.success) {
      router.push("/contactos");
    } else {
      alert("Error: " + result.error);
    }
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
        <h1 className="text-2xl font-bold text-zinc-900 dark:text-white">Nuevo Contacto</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">Añade un nuevo contacto para felicitarle el cumpleaños.</p>
      </div>

      <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <form onSubmit={handleSave} className="space-y-5">
          <FormInput
            id="name"
            name="name"
            label="Nombre Completo"
            placeholder="Ej. Juan Pérez"
            required
          />
          <PhoneInput
            name="phone"
            required
          />
          <FormInput
            id="birthday"
            name="birthday"
            label="Fecha de Nacimiento"
            type="date"
            required
          />

          <div className="pt-4 flex flex-col-reverse sm:flex-row items-center justify-end gap-3 border-t border-zinc-200 dark:border-zinc-800">
            <Link
              href="/contactos"
              className="w-full sm:w-auto text-center rounded-xl px-4 py-2.5 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-100 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Cancelar
            </Link>
            <button
              type="submit"
              className="w-full sm:w-auto text-center rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-accent/25 transition-all hover:bg-accent-light hover:shadow-accent/40 active:scale-95"
            >
              Guardar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
