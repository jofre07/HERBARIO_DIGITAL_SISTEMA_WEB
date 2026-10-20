import { inject } from "@angular/core";
import { ActivatedRouteSnapshot, CanActivateFn, Router } from "@angular/router";
import { TokenService } from '../services/token.service';

export const roleGuard: CanActivateFn = (route: ActivatedRouteSnapshot) => {
  const tokenService = inject(TokenService);
  const router = inject(Router);

  const roles = route.data['roles'] as string[];

  if (!tokenService.hasRole(roles)) {
    router.navigate(['/admin/dashboard']);
    return false;
  }

  return true;
};
