# -*- coding: utf-8 -*-
"""
Migration to add language field to UserSetting model.
Міграція для додавання поля мови до моделі UserSetting.
"""

from tortoise import fields
from tortoise.migrations import Migration


class Migration(Migration):
    """
    Add language field to UserSetting model.
    Додати поле мови до моделі UserSetting.
    """

    async def up(self):
        """Apply the migration."""
        await self.db.execute_script("""
            ALTER TABLE usersettings 
            ADD COLUMN language VARCHAR(5) DEFAULT 'uk';
        """)

    async def down(self):
        """Revert the migration."""
        await self.db.execute_script("""
            ALTER TABLE usersettings 
            DROP COLUMN language;
        """)
