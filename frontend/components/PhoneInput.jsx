"use client";

import { useState, useEffect } from "react";

const COUNTRIES = [
  { code: "+57", label: "CO +57", country: "Colombia" },
  { code: "+52", label: "MX +52", country: "México" },
  { code: "+54", label: "AR +54", country: "Argentina" },
  { code: "+56", label: "CL +56", country: "Chile" },
  { code: "+51", label: "PE +51", country: "Perú" },
  { code: "+58", label: "VE +58", country: "Venezuela" },
  { code: "+593", label: "EC +593", country: "Ecuador" },
  { code: "+591", label: "BO +591", country: "Bolivia" },
  { code: "+595", label: "PY +595", country: "Paraguay" },
  { code: "+598", label: "UY +598", country: "Uruguay" },
  { code: "+506", label: "CR +506", country: "Costa Rica" },
  { code: "+507", label: "PA +507", country: "Panamá" },
  { code: "+505", label: "NI +505", country: "Nicaragua" },
  { code: "+503", label: "SV +503", country: "El Salvador" },
  { code: "+504", label: "HN +504", country: "Honduras" },
  { code: "+502", label: "GT +502", country: "Guatemala" },
  { code: "+1", label: "US +1", country: "Estados Unidos" },
  { code: "+34", label: "ES +34", country: "España" },
];

function parsePhone(full) {
  if (!full) return { code: "+57", local: "" };
  const match = COUNTRIES.find((c) => full.startsWith(c.code));
  if (match) return { code: match.code, local: full.slice(match.code.length) };
  return { code: "+57", local: full.replace(/\D/g, "") };
}

export default function PhoneInput({ value, onChange, name, required }) {
  const parsed = parsePhone(value);
  const [countryCode, setCountryCode] = useState(parsed.code);
  const [localNumber, setLocalNumber] = useState(parsed.local);

  useEffect(() => {
    const p = parsePhone(value);
    setCountryCode(p.code);
    setLocalNumber(p.local);
  }, [value]);

  const combined = countryCode + localNumber;

  const handleCountryChange = (e) => {
    const code = e.target.value;
    setCountryCode(code);
    onChange?.(code + localNumber);
  };

  const handleLocalChange = (e) => {
    const num = e.target.value.replace(/\D/g, "");
    setLocalNumber(num);
    onChange?.(countryCode + num);
  };

  return (
    <div>
      <label className="mb-1.5 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Número de WhatsApp
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>
      <div className="flex flex-col sm:flex-row gap-2">
        <select
          value={countryCode}
          onChange={handleCountryChange}
          className="w-full sm:w-28 rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white"
        >
          {COUNTRIES.map((c) => (
            <option key={c.code} value={c.code}>
              {c.label}
            </option>
          ))}
        </select>
        <input
          type="text"
          inputMode="numeric"
          placeholder="300 000 0000"
          value={localNumber}
          onChange={handleLocalChange}
          required={required}
          className="w-full rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm text-zinc-900 placeholder-zinc-400 outline-none transition-all focus:border-accent focus:ring-2 focus:ring-accent/20 dark:border-zinc-700 dark:bg-zinc-900 dark:text-white dark:placeholder-zinc-500"
        />
      </div>
      {name && (
        <input type="hidden" name={name} value={combined} />
      )}
    </div>
  );
}
