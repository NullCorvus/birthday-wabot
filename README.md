# 🎂 Birthday WaBot

Bot automatizado de mensajes de cumpleaños por WhatsApp, con panel de administración web.

---

## 🛠 Stack

| Capa        | Tecnología                        |
|-------------|-----------------------------------|
| Frontend    | Next.js + Tailwind CSS            |
| Bot         | Node.js + whatsapp-web.js         |
| Base datos  | PostgreSQL (Docker local / Supabase prod) |
| ORM         | Prisma (compartido frontend ↔ bot)|

## 📁 Estructura del proyecto

```
birthday-wabot/
├── README.md
├── TASKS.md               ← Kanban por sprints
├── .env.example
├── docker-compose.yml      ← PostgreSQL local (puerto 5432)
│
├── prisma/
│   └── schema.prisma       ← Esquema compartido entre frontend y bot
│
├── frontend/               ← Next.js + Tailwind
│   ├── app/
│   ├── components/
│   └── package.json
│
├── bot/                    ← Node.js + whatsapp-web.js
│   ├── index.js            ← Punto de entrada del bot
│   ├── scheduler.js        ← Cron de envío diario
│   └── package.json
│
├── legacy/                 ← Código Python original (referencia)
│   ├── models/
│   └── utils/whatsapp.py
│
└── .gitignore
```

## 🚀 Cómo levantar el proyecto

### 1. Clonar y configurar variables de entorno

```bash
git clone <repo-url>
cd birthday-wabot
cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Levantar PostgreSQL con Docker

```bash
docker compose up -d
```

Esto levanta PostgreSQL en `localhost:5432` con la base de datos `birthday_wabot`.

### 3. Instalar dependencias y correr migraciones

```bash
# Prisma (raíz)
npm install
npx prisma generate
npx prisma migrate dev

# Frontend
cd frontend
npm install
cd ..

# Bot
cd bot
npm install
cd ..
```

### 4. Levantar el frontend

```bash
cd frontend
npm run dev
```

El frontend estará disponible en `http://localhost:3000`.

### 5. Levantar el bot

```bash
cd bot
node index.js
```

El bot mostrará un código QR en la terminal para vincular WhatsApp.

---

## 📋 Metodología

**Ship It Fast** — Sprints semanales con `TASKS.md` como tablero kanban.

Ver [TASKS.md](./TASKS.md) para el progreso actual.

---

## 📝 Notas

- **Frontend y bot son independientes**, se comunican únicamente a través de la base de datos vía Prisma.
- El bot **no tiene interfaz gráfica**, corre en background.
- La carpeta `legacy/` contiene el código Python original como referencia y **no debe modificarse**.
- En producción se usa **Supabase** como base de datos PostgreSQL gestionada.
