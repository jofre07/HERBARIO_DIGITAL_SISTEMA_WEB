from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE auth_group ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
                ALTER TABLE auth_permission ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
                ALTER TABLE auth_user_groups ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
                ALTER TABLE auth_group_permissions ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
                ALTER TABLE auth_user_user_permissions ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
                ALTER TABLE auth_user ADD COLUMN deleted BOOLEAN NOT NULL DEFAULT false;
            """,
            reverse_sql="""
                ALTER TABLE auth_group DROP COLUMN deleted;
                ALTER TABLE auth_permission DROP COLUMN deleted;
                ALTER TABLE auth_user_groups DROP COLUMN deleted;
                ALTER TABLE auth_group_permissions DROP COLUMN deleted;
                ALTER TABLE auth_user_user_permissions DROP COLUMN deleted;
                ALTER TABLE auth_user DROP COLUMN deleted;
            """,
        ),
    ]
