from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "declarations" RENAME COLUMN "image_url" TO "xlsx_image_url";
        ALTER TABLE "declarations" ADD "xml_image_url" VARCHAR(300);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "declarations" RENAME COLUMN "xlsx_image_url" TO "image_url";
        ALTER TABLE "declarations" ADD "image_url" VARCHAR(300);
        ALTER TABLE "declarations" DROP COLUMN "xml_image_url";"""
