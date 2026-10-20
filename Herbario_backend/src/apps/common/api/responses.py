from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

RESPONSE_MESSAGES = {
    status.HTTP_200_OK: "Proceso realizado exitosamente",
    status.HTTP_201_CREATED: "Creado exitosamente",
    status.HTTP_204_NO_CONTENT: "Proceso realizado exitosamente",
    status.HTTP_400_BAD_REQUEST: "Has realizado una peticion incorrecta.",
    status.HTTP_401_UNAUTHORIZED: "Usuario no autorizado.",
    status.HTTP_403_FORBIDDEN: "No tienes permisos para realizar esta accion.",
    status.HTTP_404_NOT_FOUND: "El recurso que has intentado solicitar no existe.",
    status.HTTP_405_METHOD_NOT_ALLOWED: "Este metodo HTTP no esta permitido en el servidor.",
    status.HTTP_409_CONFLICT: "El recurso que intentas crear o actualizar ya existe.",
    status.HTTP_500_INTERNAL_SERVER_ERROR: (
        "Error en el servidor. No eres tu, soy yo. Comunicate con el administrador."
    ),
}
DEFAULT_ERROR_MESSAGE = "Error, Comunicate con el administrador."
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
ERROR_TRANSLATIONS = {
    "No active account found with the given credentials": (
        "No existe una cuenta activa con las credenciales ingresadas."
    ),
    "Given token not valid for any token type": "El token enviado no es valido.",
    "Token is invalid or expired": "El token no es valido o ha expirado.",
    "Authentication credentials were not provided.": (
        "No se enviaron credenciales de autenticacion."
    ),
    "You do not have permission to perform this action.": (
        "No tienes permisos para realizar esta accion."
    ),
    "Invalid token.": "Token invalido.",
    "User not found": "Usuario no encontrado.",
    "Invalid encoded ID.": "El identificador proporcionado no es válido.",
    "Not found.": "No se encontró el recurso solicitado.",
    "Method not allowed.": "Método no permitido.",
    "Invalid hyperlink - No URL match.": "El enlace proporcionado no es válido.",
    "Invalid hyperlink - Incorrect URL match.": "El enlace proporcionado no es válido.",
    "This field is required.": "Este campo es obligatorio.",
    "This field may not be blank.": "Este campo no puede estar vacio.",
    "This field may not be null.": "Este campo no puede ser nulo.",
    "A valid integer is required.": "Se requiere un numero entero valido.",
    "A valid number is required.": "Se requiere un número válido.",
    "Must be a valid boolean.": "Debe ser un valor booleano válido.",
    "This field must be unique.": "Este valor ya está registrado.",
    "Enter a valid email address.": "Ingresa un correo electronico valido.",
    "Invalid data. Expected a dictionary, but got {datatype}.": (
        "Datos invalidos. Se esperaba un objeto."
    ),
}


def response_message(status_code: int) -> str:
    return RESPONSE_MESSAGES.get(status_code, DEFAULT_ERROR_MESSAGE)


def is_wrapped_response(data: Any) -> bool:
    return isinstance(data, dict) and {"code", "message"}.issubset(data.keys())


def translate_error_detail(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: translate_error_detail(item) for key, item in value.items()}
    if isinstance(value, list):
        return [translate_error_detail(item) for item in value]

    text = str(value)
    return ERROR_TRANSLATIONS.get(text, value)


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context.get("response")
        view = renderer_context.get("view")

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        if getattr(view, "skip_standard_response", False) or is_wrapped_response(data):
            return super().render(data, accepted_media_type, renderer_context)

        status_code = response.status_code
        request = renderer_context.get("request")
        should_hide_data = (
            getattr(view, "suppress_write_response_data", False)
            and request is not None
            and request.method in WRITE_METHODS
            and status_code < status.HTTP_400_BAD_REQUEST
        )
        if should_hide_data:
            payload = {
                "code": status_code,
                "message": response_message(status_code),
            }
            return super().render(payload, accepted_media_type, renderer_context)

        key = "errors" if status_code >= status.HTTP_400_BAD_REQUEST else "data"
        payload = {
            "code": status_code,
            "message": response_message(status_code),
            key: data,
        }
        return super().render(payload, accepted_media_type, renderer_context)


def standard_exception_handler(exc, context):
    from rest_framework.views import exception_handler

    response = exception_handler(exc, context)
    if response is not None:
        response.data = translate_error_detail(response.data)
        return response

    return Response(
        {"detail": str(exc) or response_message(status.HTTP_500_INTERNAL_SERVER_ERROR)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
