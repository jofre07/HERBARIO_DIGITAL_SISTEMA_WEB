from __future__ import annotations

from django.db import connection


def replace_role_permissions(*, role_id: int, permission_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE auth_group_permissions SET deleted=TRUE WHERE group_id=%s",
            [role_id],
        )
        for perm_id in permission_ids:
            cursor.execute(
                "INSERT INTO auth_group_permissions (group_id, permission_id, deleted) "
                "VALUES (%s, %s, FALSE) "
                "ON CONFLICT (group_id, permission_id) DO UPDATE SET deleted=FALSE",
                [role_id, perm_id],
            )


def replace_user_roles(*, user_id: int, role_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE auth_user_groups SET deleted=TRUE WHERE user_id=%s",
            [user_id],
        )
        for role_id in role_ids:
            cursor.execute(
                "INSERT INTO auth_user_groups (user_id, group_id, deleted) "
                "VALUES (%s, %s, FALSE) "
                "ON CONFLICT (user_id, group_id) DO UPDATE SET deleted=FALSE",
                [user_id, role_id],
            )


def replace_user_permissions(*, user_id: int, permission_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE auth_user_user_permissions SET deleted=TRUE WHERE user_id=%s",
            [user_id],
        )
        for perm_id in permission_ids:
            cursor.execute(
                "INSERT INTO auth_user_user_permissions (user_id, permission_id, deleted) "
                "VALUES (%s, %s, FALSE) "
                "ON CONFLICT (user_id, permission_id) DO UPDATE SET deleted=FALSE",
                [user_id, perm_id],
            )


def add_user_role(*, user_id: int, role_id: int) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO auth_user_groups (user_id, group_id, deleted) "
            "VALUES (%s, %s, FALSE) "
            "ON CONFLICT (user_id, group_id) DO UPDATE SET deleted=FALSE",
            [user_id, role_id],
        )


def get_user_role_ids(*, user_id: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT ug.group_id FROM auth_user_groups ug "
            "JOIN auth_group g ON g.id = ug.group_id "
            "WHERE ug.user_id=%s AND ug.deleted=FALSE AND g.deleted=FALSE",
            [user_id],
        )
        return [row[0] for row in cursor.fetchall()]


def get_user_role_names(*, user_id: int) -> list[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT g.name FROM auth_user_groups ug "
            "JOIN auth_group g ON g.id = ug.group_id "
            "WHERE ug.user_id=%s AND ug.deleted=FALSE AND g.deleted=FALSE",
            [user_id],
        )
        return [row[0] for row in cursor.fetchall()]


def get_user_permission_ids(*, user_id: int) -> list[int]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT permission_id FROM auth_user_user_permissions "
            "WHERE user_id=%s AND deleted=FALSE",
            [user_id],
        )
        return [row[0] for row in cursor.fetchall()]


def get_user_permission_details(*, user_id: int) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT p.id, p.codename, ct.app_label "
            "FROM auth_user_user_permissions up "
            "JOIN auth_permission p ON p.id = up.permission_id "
            "JOIN django_content_type ct ON ct.id = p.content_type_id "
            "WHERE up.user_id=%s AND up.deleted=FALSE",
            [user_id],
        )
        return [
            {"id": row[0], "codename": row[1], "app_label": row[2]}
            for row in cursor.fetchall()
        ]


def get_user_effective_permission_details(*, user_id: int) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT p.id, p.codename, ct.app_label "
            "FROM auth_permission p "
            "JOIN django_content_type ct ON ct.id = p.content_type_id "
            "WHERE p.deleted=FALSE AND ("
            "EXISTS ("
            "SELECT 1 FROM auth_user_user_permissions up "
            "WHERE up.user_id=%s AND up.permission_id=p.id AND up.deleted=FALSE"
            ") OR EXISTS ("
            "SELECT 1 FROM auth_user_groups ug "
            "JOIN auth_group g ON g.id=ug.group_id "
            "JOIN auth_group_permissions gp ON gp.group_id=g.id "
            "WHERE ug.user_id=%s AND ug.deleted=FALSE AND g.deleted=FALSE "
            "AND gp.permission_id=p.id AND gp.deleted=FALSE"
            ")) ORDER BY ct.app_label, p.codename",
            [user_id, user_id],
        )
        return [
            {"id": row[0], "codename": row[1], "app_label": row[2]}
            for row in cursor.fetchall()
        ]


def user_has_permission(*, user_id: int, permission: str) -> bool:
    try:
        app_label, codename = permission.split(".", 1)
    except ValueError:
        return False

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM auth_permission p "
            "JOIN django_content_type ct ON ct.id=p.content_type_id "
            "WHERE ct.app_label=%s AND p.codename=%s AND p.deleted=FALSE AND ("
            "EXISTS ("
            "SELECT 1 FROM auth_user_user_permissions up "
            "WHERE up.user_id=%s AND up.permission_id=p.id AND up.deleted=FALSE"
            ") OR EXISTS ("
            "SELECT 1 FROM auth_user_groups ug "
            "JOIN auth_group g ON g.id=ug.group_id "
            "JOIN auth_group_permissions gp ON gp.group_id=g.id "
            "WHERE ug.user_id=%s AND ug.deleted=FALSE AND g.deleted=FALSE "
            "AND gp.permission_id=p.id AND gp.deleted=FALSE"
            ")) LIMIT 1",
            [app_label, codename, user_id, user_id],
        )
        return cursor.fetchone() is not None


def user_has_role(*, user_id: int, role_names: list[str]) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM auth_user_groups ug "
            "JOIN auth_group g ON g.id = ug.group_id "
            "WHERE ug.user_id=%s AND ug.deleted=FALSE AND g.deleted=FALSE AND g.name = ANY(%s) "
            "LIMIT 1",
            [user_id, list(role_names)],
        )
        return cursor.fetchone() is not None


def role_has_permission(*, role_id: int, permission_id: int) -> bool:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM auth_group_permissions "
            "WHERE group_id=%s AND permission_id=%s AND deleted=FALSE "
            "LIMIT 1",
            [role_id, permission_id],
        )
        return cursor.fetchone() is not None
