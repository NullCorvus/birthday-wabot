"use client";

import { useState } from "react";
import Link from "next/link";

function Avatar({ name, size = "md" }) {
  const initials = name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const colors = [
    "bg-violet-500", "bg-blue-500", "bg-emerald-500", "bg-amber-500",
    "bg-rose-500", "bg-cyan-500", "bg-fuchsia-500", "bg-lime-500",
  ];
  const colorIndex = name.length % colors.length;
  const dims = size === "sm" ? "h-8 w-8 text-[10px]" : "h-9 w-9 text-xs";

  return (
    <div className={`flex ${dims} items-center justify-center rounded-full font-bold text-white ${colors[colorIndex]}`}>
      {initials}
    </div>
  );
}

export default function ContactTable({ contacts }) {
  const [search, setSearch] = useState("");

  const filtered = contacts.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.phone.includes(search)
  );

  return (
    <div>
      {/* Search + New button */}
      <div className="mb-5 flex items-center gap-2 sm:gap-3">
        <div className="relative flex-1 min-w-0">
          <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Buscar..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-zinc-200 bg-white py-2.5 pl-10 pr-4 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white dark:placeholder-zinc-500"
          />
        </div>
        <Link
          href="/contactos/nuevo"
          className="flex items-center justify-center rounded-xl bg-accent p-2.5 sm:px-4 sm:py-2.5 text-sm font-semibold text-white shadow-lg shadow-accent/25 transition-all duration-200 hover:bg-accent-light hover:shadow-accent/40 active:scale-95"
        >
          <svg className="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          <span className="hidden sm:inline sm:ml-2">Nuevo contacto</span>
        </Link>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-2xl border border-zinc-200 py-10 text-center text-sm text-zinc-400 dark:border-zinc-800 dark:text-zinc-500">
          No se encontraron contactos
        </div>
      ) : (
        <>
          {/* Cards — mobile */}
          <div className="space-y-3 lg:hidden">
            {filtered.map((contact) => (
              <div
                key={contact.id}
                className="rounded-2xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
              >
                <div className="flex items-start gap-3">
                  <Avatar name={contact.name} size="sm" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-zinc-900 dark:text-white truncate">
                      {contact.name}
                    </div>
                    <div className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
                      {contact.phone}
                    </div>
                  </div>
                  <span
                    className={`shrink-0 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                      contact.active
                        ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400"
                        : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500"
                    }`}
                  >
                    {contact.active ? "Activo" : "Inactivo"}
                  </span>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-zinc-400 dark:text-zinc-500">
                    🎂 {contact.birthday}
                  </span>
                  <Link
                    href={`/contactos/${contact.id}`}
                    className="rounded-lg px-3 py-1.5 text-xs font-medium text-accent transition-colors hover:bg-accent/10"
                  >
                    Editar
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Table — desktop */}
          <div className="hidden lg:block rounded-2xl border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/50">
                  <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Nombre</th>
                  <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Número</th>
                  <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Cumpleaños</th>
                  <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Estado</th>
                  <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
                {filtered.map((contact) => (
                  <tr
                    key={contact.id}
                    className="transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-800/40"
                  >
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <Avatar name={contact.name} />
                        <span className="font-medium text-zinc-900 dark:text-white">{contact.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-zinc-600 dark:text-zinc-300">{contact.phone}</td>
                    <td className="px-5 py-3.5 text-zinc-600 dark:text-zinc-300">{contact.birthday}</td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          contact.active
                            ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400"
                            : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-500"
                        }`}
                      >
                        {contact.active ? "Activo" : "Inactivo"}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <Link
                        href={`/contactos/${contact.id}`}
                        className="rounded-lg px-3 py-1.5 text-xs font-medium text-accent transition-colors hover:bg-accent/10"
                      >
                        Editar
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
