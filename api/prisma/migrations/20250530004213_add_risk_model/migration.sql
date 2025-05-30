-- AlterTable
ALTER TABLE "listings" ALTER COLUMN "afs_last_run_at" SET DEFAULT '1970-01-01 00:00:00-07'::timestamp with time zone,
ALTER COLUMN "last_application_update_at" SET DEFAULT '1970-01-01 00:00:00-07'::timestamp with time zone,
ALTER COLUMN "requested_changes_date" SET DEFAULT '1970-01-01 00:00:00-07'::timestamp with time zone;

-- CreateTable
CREATE TABLE "risk" (
    "id" UUID NOT NULL DEFAULT uuid_generate_v4(),
    "application_id" UUID NOT NULL,
    "risk_probability" DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    "risk_prediction" BOOLEAN NOT NULL DEFAULT false,
    "veteran" BOOLEAN NOT NULL DEFAULT false,
    "income" DOUBLE PRECISION DEFAULT 0,
    "disabled" BOOLEAN NOT NULL DEFAULT false,
    "num_people" INTEGER DEFAULT 1,
    "age" INTEGER,
    "benefits" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(6) NOT NULL,

    CONSTRAINT "risk_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "risk_application_id_key" ON "risk"("application_id");

-- CreateIndex
CREATE INDEX "risk_application_id_idx" ON "risk"("application_id");

-- AddForeignKey
ALTER TABLE "risk" ADD CONSTRAINT "risk_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;
