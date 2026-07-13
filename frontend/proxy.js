import { NextResponse } from 'next/server'

export function proxy(request) {
    const { pathname } = request.nextUrl

    if (
        pathname === '/login' ||
        pathname.startsWith('/_next') ||
        pathname === '/favicon.ico'
    ) {
        return NextResponse.next()
    }

    const authToken = request.cookies.get('auth_token')?.value

    if (authToken === 'true') {
        return NextResponse.next()
    }

    return NextResponse.redirect(new URL('/login', request.url))
}

export const config = {
    matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
