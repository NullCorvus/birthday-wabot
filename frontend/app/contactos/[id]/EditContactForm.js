"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import FormInput from "../../../components/FormInput";
import PhoneInput from "../../../components/PhoneInput";
import { updateContact } from "../../actions";

export default function EditContactForm({ contactId, initialData }) {
  const router = useRouter();
  const [formData, setFormData] = useState(initialData);

  const handleSave = async (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append("name", formData.name);
    data.append("phone", formData.phone);
    data.append("birthday", formData.birthday);
    data.append("active", formData.active.toString());

    const result = await updateContact(contactId, data);
    
    if (result.success) {
      router.push("/contactos");
    } else {
      alert("Error: " + result.error);
    }
  };

  const handleToggleActive = async () => {
    const newState = !formData.active;
    const data = new FormData();
    data.append("name", formData.name);
    data.append("phone", formData.phone);
    data.append("birthday", formData.birthday);
    data.append("active", newState.toString());

    const result = await updateContact(contactId, data);
    if (result.success) {
      setFormData({...formData, active: newState});
    }
  };

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <form onSubmit={handleSave} className="space-y-5">
        <FormInput
          id="name"
          label="Nombre Completo"
          value={formData.name}
          onChange={(e) => setFormData({...formData, name: e.target.value})}
          required
        />
        <PhoneInput
          value={formData.phone}
          onChange={(val) => setFormData({...formData, phone: val})}
          required
        />
        <FormInput
          id="birthday"
          label="Fecha de Nacimiento"
          type="date"
          value={formData.birthday}
          onChange={(e) => setFormData({...formData, birthday: e.target.value})}
          required
        />

        <div className="pt-4 flex flex-col gap-3 border-t border-zinc-200 dark:border-zinc-800">
          <button
            type="button"
            onClick={handleToggleActive}
            className={`w-full sm:w-auto rounded-xl px-4 py-2.5 text-sm font-medium transition-colors ${formData.active ? 'text-red-600 hover:bg-red-50 dark:text-red-500 dark:hover:bg-red-500/10' : 'text-green-600 hover:bg-green-50 dark:text-green-500 dark:hover:bg-green-500/10'}`}
          >
            {formData.active ? "Desactivar contacto" : "Activar contacto"}
          </button>
          <div className="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-end gap-3">
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
        </div>
      </form>
    </div>
  );
}
