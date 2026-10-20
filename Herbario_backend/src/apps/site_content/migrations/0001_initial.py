from django.db import migrations, models

import apps.site_content.models


def create_initial_content(apps, schema_editor):
    AboutPageContent = apps.get_model("site_content", "AboutPageContent")
    AboutPageContent.objects.get_or_create(pk=1)


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AboutPageContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("introduction_title", models.CharField(default="¿Qué es el Herbario Digital?", max_length=160)),
                ("introduction_body", models.TextField(default="El Herbario Digital es una plataforma web para gestionar, consultar y difundir información sobre la diversidad vegetal. Reúne especímenes recolectados, datos taxonómicos, ubicaciones geográficas, imágenes y recursos que apoyan la investigación, la educación y la conservación.", max_length=2000)),
                ("introduction_image", models.ImageField(blank=True, upload_to="site-content/about/")),
                ("impact_items", models.JSONField(default=apps.site_content.models.default_impact_items)),
                ("mission", models.TextField(default="Gestionar y difundir información botánica de calidad mediante herramientas digitales, contribuyendo a la investigación, la educación y la conservación de la biodiversidad vegetal.", max_length=1500)),
                ("vision", models.TextField(default="Ser un referente en la gestión digital de colecciones botánicas y promover el conocimiento de la flora para las futuras generaciones.", max_length=1500)),
                ("values", models.JSONField(default=apps.site_content.models.default_values)),
                ("team_title", models.CharField(default="Equipo institucional", max_length=160)),
                ("team_subtitle", models.CharField(default="Funciones que sostienen la gestión científica y digital del herbario.", max_length=300)),
                ("team_members", models.JSONField(default=apps.site_content.models.default_team_members)),
                ("contact_address", models.CharField(default="Campus Politécnico, Calceta, Manabí", max_length=300)),
                ("contact_email", models.EmailField(default="herbario@espam.edu.ec", max_length=254)),
                ("contact_phone", models.CharField(default="+593 5 268 2776", max_length=40)),
                ("institution", models.CharField(default="ESPAM MFL", max_length=160)),
            ],
            options={
                "verbose_name": "contenido de la página Acerca de",
                "verbose_name_plural": "contenido de la página Acerca de",
                "db_table": "site_content_about_page",
            },
        ),
        migrations.RunPython(create_initial_content, migrations.RunPython.noop),
    ]
