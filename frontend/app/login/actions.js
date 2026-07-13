'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export async function login(formData) {
    const password = formData.get('password');
    const authPassword = process.env.AUTH_PASSWORD;

    if (!authPassword) {
        return { error: 'AUTH_PASSWORD no está configurada en el servidor.' };
    }

    if (password === authPassword) {
        const cookieStore = await cookies();
        cookieStore.set('auth_token', 'true', {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            maxAge: 60 * 60 * 24 * 7,
            path: '/',
        });
        redirect('/');
    }

    return { error: 'Contrase\u00f1a incorrecta.' };
}
