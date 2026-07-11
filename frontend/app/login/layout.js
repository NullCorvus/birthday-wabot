import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";
import ThemeProvider from "../../components/ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Login - Birthday WaBot",
  description: "Autenticación del panel de Birthday WaBot",
};

export default function LoginLayout({ children }) {
  return (
    <html
      lang="es"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100">
        <ThemeProvider>
          <main className="flex-1 flex items-center justify-center min-h-screen p-4">
            {children}
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
