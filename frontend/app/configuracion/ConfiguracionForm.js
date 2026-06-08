"use client";

import { useState } from "react";
import FormInput from "../../components/FormInput";
import { updateMensajetxt } from "../actions";

export default function ConfiguracionForm({ templateId, initialName, initialMessage }) {
  const [templateName, setTemplateName] = useState(initialName);
  const [message, setMessage] = useState(initialMessage);

  const handleSave = async (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append("texto", message);
    
    // Asumimos que no se cambia el nombre de la plantilla por ahora, 
    // la tabla solo tiene 'nombre' y 'texto'.
    const result = await updateMensajetxt(templateId, data);
    if (result.success) {
      alert("Plantilla guardada correctamente.");
    } else {
      alert("Error: " + result.error);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Editor */}
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="mb-5 text-lg font-bold text-zinc-900 dark:text-white">Plantilla del Mensaje</h2>
        <form onSubmit={handleSave} className="space-y-5">
          <FormInput
            id="templateName"
            label="Nombre de la plantilla (solo lectura)"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            disabled
          />
          
          <div>
            <label htmlFor="message" className="mb-1.5 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Contenido del mensaje
            </label>
            <textarea
              id="message"
              rows={6}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full resize-none rounded-xl border border-zinc-200 bg-white p-4 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white dark:placeholder-zinc-500"
            />
            <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
              Usa <code className="rounded bg-zinc-100 px-1.5 py-0.5 font-mono text-zinc-900 dark:bg-zinc-800 dark:text-white">{`{nombre}`}</code> para que el bot lo reemplace automáticamente por el nombre del contacto.
            </p>
          </div>

          <div className="pt-4 border-t border-zinc-200 dark:border-zinc-800">
            <button
              type="submit"
              className="w-full rounded-xl bg-accent px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-accent/25 transition-all hover:bg-accent-light hover:shadow-accent/40 active:scale-95"
            >
              Guardar Plantilla
            </button>
          </div>
        </form>
      </div>

      {/* Preview */}
      <div>
        <h2 className="mb-5 text-lg font-bold text-zinc-900 dark:text-white">Vista Previa</h2>
        
        {/* WhatsApp mock bubble */}
        <div className="rounded-2xl bg-[#efeae2] p-6 dark:bg-[#0b141a]">
          <div className="mx-auto max-w-sm">
            <div className="relative rounded-2xl rounded-tl-none bg-white p-3 pr-4 shadow-sm dark:bg-[#202c33]">
              <p className="whitespace-pre-wrap text-[15px] leading-relaxed text-[#111b21] dark:text-[#e9edef]">
                {message.replace(/{nombre}/g, "Juan Pérez")}
              </p>
              <div className="mt-1 flex justify-end">
                <span className="text-[11px] text-[#667781] dark:text-[#8696a0]">
                  09:00 AM
                </span>
              </div>
              {/* Tail tail for the bubble */}
              <svg className="absolute -left-2 top-0 h-4 w-4 text-white dark:text-[#202c33]" fill="currentColor" viewBox="0 0 8 13">
                <path d="M5.188 1H0v11.156L7.984 2.195C8.822 1.35 8.196 1 7.188 1H5.188z" />
              </svg>
            </div>
          </div>
          
          <p className="mt-4 text-center text-xs text-zinc-500 dark:text-zinc-400 mix-blend-difference">
            Así se verá el mensaje en WhatsApp.
          </p>
        </div>
      </div>
    </div>
  );
}
