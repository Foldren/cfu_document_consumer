from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "declarations" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "user_id" VARCHAR(100) NOT NULL,
    "file_name" VARCHAR(170) NOT NULL,
    "date" DATE NOT NULL,
    "legal_entity_inn" TEXT,
    "image_url" VARCHAR(300),
    "status" VARCHAR(7) NOT NULL  DEFAULT 'process'
);
CREATE INDEX IF NOT EXISTS "idx_declaration_user_id_014156" ON "declarations" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_declaration_file_na_9f1975" ON "declarations" ("file_name");
CREATE INDEX IF NOT EXISTS "idx_declaration_date_9dab5c" ON "declarations" ("date");
COMMENT ON COLUMN "declarations"."status" IS 'Статус декларации';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
