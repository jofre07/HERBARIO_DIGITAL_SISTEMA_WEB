import { inject } from "@angular/core";
import { ActivatedRouteSnapshot, CanActivateFn, Router } from "@angular/router";
import { TokenService } from '../services/token.service';

export const permissionGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const tokenService = inject(TokenService);
  const router = inject(Router);
  const permission = route.data['permission'] as string;

  if (!permission || tokenService.hasPermission(permission)) return true;

  return router.createUrlTree(['/admin/dashboard']);
};
