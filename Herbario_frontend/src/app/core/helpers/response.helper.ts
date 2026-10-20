import { map } from "rxjs/operators";
import { Observable } from 'rxjs';

export interface WrappedList<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export function unwrapList<T>() {
  return map((res: any) => res?.data as WrappedList<T>);
}

export function unwrapData<T>() {
  return map((res: any) => res?.data as T);
}

export function unwrapVoid() {
  // DELETE suele responder 204 y HttpClient entrega null. Normalizamos la
  // respuesta para que los callbacks puedan leer `message` y continuar con
  // la alerta y la recarga de la tabla.
  return map((res: any) => res ?? {});
}
