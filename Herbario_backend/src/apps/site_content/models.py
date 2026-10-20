from __future__ import annotations

from django.db import models

from apps.common.models import BaseModel


def default_impact_items() -> list[dict[str, str]]:
    return [
        {
            "title": "Conservación",
            "description": "Contribuye al conocimiento y la conservación de la flora regional y nacional.",
        },
        {
            "title": "Investigación",
            "description": "Facilita el acceso a datos organizados para la consulta científica.",
        },
        {
            "title": "Educación",
            "description": "Ofrece recursos digitales para el aprendizaje y la formación académica.",
        },
        {
            "title": "Colaboración",
            "description": "Favorece el trabajo conjunto entre estudiantes, docentes e investigadores.",
        },
    ]


def default_values() -> list[str]:
    return [
        "Rigor científico",
        "Transparencia",
        "Responsabilidad ambiental",
        "Colaboración y acceso abierto",
    ]


def default_team_members() -> list[dict[str, str]]:
    return [
        {"title": "Coordinación", "description": "Planificación y dirección del herbario"},
        {"title": "Curaduría", "description": "Gestión de colecciones botánicas"},
        {"title": "Investigación", "description": "Estudio y validación taxonómica"},
        {"title": "Gestión de datos", "description": "Administración de registros digitales"},
    ]


class AboutPageContent(BaseModel):
    introduction_title = models.CharField(max_length=160, default="¿Qué es el Herbario Digital?")
    introduction_body = models.TextField(
        max_length=2000,
        default=(
            "El Herbario Digital es una plataforma web para gestionar, consultar y difundir "
            "información sobre la diversidad vegetal. Reúne especímenes recolectados, datos "
            "taxonómicos, ubicaciones geográficas, imágenes y recursos que apoyan la "
            "investigación, la educación y la conservación."
        ),
    )
    introduction_image = models.ImageField(upload_to="site-content/about/", blank=True)
    impact_items = models.JSONField(default=default_impact_items)
    mission = models.TextField(
        max_length=1500,
        default=(
            "Gestionar y difundir información botánica de calidad mediante herramientas "
            "digitales, contribuyendo a la investigación, la educación y la conservación de "
            "la biodiversidad vegetal."
        ),
    )
    vision = models.TextField(
        max_length=1500,
        default=(
            "Ser un referente en la gestión digital de colecciones botánicas y promover el "
            "conocimiento de la flora para las futuras generaciones."
        ),
    )
    values = models.JSONField(default=default_values)
    team_title = models.CharField(max_length=160, default="Equipo institucional")
    team_subtitle = models.CharField(
        max_length=300,
        default="Funciones que sostienen la gestión científica y digital del herbario.",
    )
    team_members = models.JSONField(default=default_team_members)
    contact_address = models.CharField(
        max_length=300, default="Campus Politécnico, Calceta, Manabí"
    )
    contact_email = models.EmailField(default="herbario@espam.edu.ec")
    contact_phone = models.CharField(max_length=40, default="+593 5 268 2776")
    institution = models.CharField(max_length=160, default="ESPAM MFL")

    class Meta:
        db_table = "site_content_about_page"
        verbose_name = "contenido de la página Acerca de"
        verbose_name_plural = "contenido de la página Acerca de"

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return "Página Acerca de"
