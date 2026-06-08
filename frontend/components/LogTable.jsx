"use client";

import { useState } from "react";

function Avatar({ name }) {
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

  return (
    <div className={`flex h-8 w-8 items-center justify-center rounded-full text-[10px] font-bold text-white ${colors[colorIndex]}`}>
      {initials}
    </div>
  );
}

function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        status === "Enviado"
          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400"
          : "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-400"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${status === "Enviado" ? "bg-emerald-500" : "bg-red-500"}`} />
      {status}
    </span>
  );
}

export default function LogTable({ logs }) {
  const [search, setSearch] = useState("");
  const [expandedIndex, setExpandedIndex] = useState(null);

  const filtered = logs.filter((l) =>
    l.contact.toLowerCase().includes(search.toLowerCase())
  );

  const toggleExpand = (i) => {
    setExpandedIndex(expandedIndex === i ? null : i);
  };

  if (filtered.length === 0) {
    return (
      <div>
        <div className="mb-5">
          <div className="relative max-w-md">
            <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="Buscar por nombre del contacto..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-zinc-200 bg-white py-2.5 pl-10 pr-4 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white dark:placeholder-zinc-500"
            />
          </div>
        </div>
        <div className="rounded-2xl border border-zinc-200 py-10 text-center text-sm text-zinc-400 dark:border-zinc-800 dark:text-zinc-500">
          No se encontraron registros
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Search */}
      <div className="mb-5">
        <div className="relative max-w-md">
          <svg className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por nombre del contacto..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-xl border border-zinc-200 bg-white py-2.5 pl-10 pr-4 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white dark:placeholder-zinc-500"
          />
        </div>
      </div>

      {/* Cards — mobile */}
      <div className="space-y-3 lg:hidden">
        {filtered.map((log, i) => (
          <div
            key={i}
            className="rounded-2xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <Avatar name={log.contact} />
                <span className="font-medium text-zinc-900 dark:text-white truncate">{log.contact}</span>
              </div>
              <StatusBadge status={log.status} />
            </div>
            <div
              className="mt-2 text-sm text-zinc-600 dark:text-zinc-300 cursor-pointer"
              onClick={() => toggleExpand(i)}
            >
              {expandedIndex === i ? (
                <div className="rounded-lg bg-zinc-50 p-3 text-xs leading-relaxed text-zinc-700 whitespace-pre-wrap break-words dark:bg-zinc-800 dark:text-zinc-300">
                  {log.message}
                </div>
              ) : (
                <span className="line-clamp-2">{log.message}</span>
              )}
            </div>
            <div className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
              {log.datetime}
            </div>
          </div>
        ))}
      </div>

      {/* Table — desktop */}
      <div className="hidden lg:block rounded-2xl border border-zinc-200 dark:border-zinc-800">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/50">
              <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Contacto</th>
              <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Mensaje</th>
              <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Fecha / Hora</th>
              <th className="px-5 py-3.5 font-medium text-zinc-500 dark:text-zinc-400">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-100 dark:divide-zinc-800">
            {filtered.map((log, i) => (
              <tr key={i} className="transition-colors hover:bg-zinc-50 dark:hover:bg-zinc-800/40">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-3">
                    <Avatar name={log.contact} />
                    <span className="font-medium text-zinc-900 dark:text-white">{log.contact}</span>
                  </div>
                </td>
                <td
                  className="max-w-xs px-5 py-3.5 text-zinc-600 dark:text-zinc-300 cursor-pointer"
                  onClick={() => toggleExpand(i)}
                >
                  <span className={expandedIndex === i ? "" : "truncate block"}>
                    {log.message}
                  </span>
                  {expandedIndex === i && (
                    <div className="mt-2 rounded-lg bg-zinc-100 p-3 text-xs leading-relaxed text-zinc-700 whitespace-pre-wrap break-words dark:bg-zinc-800 dark:text-zinc-300">
                      {log.message}
                    </div>
                  )}
                </td>
                <td className="px-5 py-3.5 text-zinc-500 dark:text-zinc-400 whitespace-nowrap">
                  {log.datetime}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={log.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
