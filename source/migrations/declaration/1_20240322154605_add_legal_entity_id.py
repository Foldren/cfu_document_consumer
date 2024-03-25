from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "declarations" ADD "legal_entity_id" VARCHAR(100);
        CREATE INDEX "idx_declaration_legal_e_93a86e" ON "declarations" ("legal_entity_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_declaration_legal_e_93a86e";
        ALTER TABLE "declarations" DROP COLUMN "legal_entity_id";"""
