"use server";

import { prisma } from "../lib/prisma";
import { revalidatePath } from "next/cache";

export async function createContact(formData) {
  const name = formData.get("name");
  const phone = formData.get("phone");
  const birthday = formData.get("birthday"); // YYYY-MM-DD

  if (!name || !phone || !birthday) return { error: "Missing fields" };

  // Parse birthday to a valid date at midnight UTC to avoid timezone issues
  const dateObj = new Date(birthday + "T00:00:00.000Z");

  await prisma.contacto.create({
    data: {
      nombre: name,
      numero: phone,
      fecha_nacimiento: dateObj,
      activo: true
    }
  });

  revalidatePath("/");
  revalidatePath("/contactos");
  return { success: true };
}

export async function updateContact(id, formData) {
  const name = formData.get("name");
  const phone = formData.get("phone");
  const birthday = formData.get("birthday");
  const active = formData.get("active") === "true";

  if (!name || !phone || !birthday) return { error: "Missing fields" };

  const dateObj = new Date(birthday + "T00:00:00.000Z");

  await prisma.contacto.update({
    where: { id: parseInt(id, 10) },
    data: {
      nombre: name,
      numero: phone,
      fecha_nacimiento: dateObj,
      activo: active
    }
  });

  revalidatePath("/");
  revalidatePath("/contactos");
  return { success: true };
}

export async function deleteContact(id) {
  // Instead of hard delete, maybe just deactivate, but we can also delete.
  // The user asked for "desactivar" so updateContact handles it. If delete is needed:
  await prisma.contacto.delete({
    where: { id: parseInt(id, 10) }
  });

  revalidatePath("/");
  revalidatePath("/contactos");
  return { success: true };
}

export async function updateMensajetxt(id, formData) {
  const texto = formData.get("texto");

  if (!texto) return { error: "Missing text" };

  await prisma.mensajetxt.update({
    where: { id: parseInt(id, 10) },
    data: {
      texto
    }
  });

  revalidatePath("/configuracion");
  return { success: true };
}
