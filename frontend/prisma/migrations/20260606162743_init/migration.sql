-- CreateTable
CREATE TABLE "contactos" (
    "id" SERIAL NOT NULL,
    "nombre" TEXT NOT NULL,
    "numero" TEXT NOT NULL,
    "fecha_nacimiento" TIMESTAMP(3) NOT NULL,
    "activo" BOOLEAN NOT NULL DEFAULT true,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "contactos_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "log" (
    "id" SERIAL NOT NULL,
    "contacto_id" INTEGER NOT NULL,
    "mensaje" TEXT NOT NULL,
    "fecha_hora_envio" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "estado" TEXT NOT NULL DEFAULT 'Abierto',
    "detalle" TEXT,

    CONSTRAINT "log_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "mensajetxt" (
    "id" SERIAL NOT NULL,
    "nombre" TEXT NOT NULL,
    "texto" TEXT NOT NULL,

    CONSTRAINT "mensajetxt_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "log" ADD CONSTRAINT "log_contacto_id_fkey" FOREIGN KEY ("contacto_id") REFERENCES "contactos"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
