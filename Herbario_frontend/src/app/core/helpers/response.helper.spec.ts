import { firstValueFrom, of } from 'rxjs';
import { unwrapVoid } from './response.helper';

describe('response helpers', () => {
  it('normaliza una respuesta 204 sin contenido', async () => {
    const response = await firstValueFrom(of(null).pipe(unwrapVoid()));
    expect(response).toEqual({});
  });

  it('conserva una respuesta con mensaje', async () => {
    const payload = { message: 'Eliminado correctamente' };
    const response = await firstValueFrom(of(payload).pipe(unwrapVoid()));
    expect(response).toBe(payload);
  });
});
