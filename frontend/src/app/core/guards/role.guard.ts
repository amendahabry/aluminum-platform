import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export function roleGuard(permission: string): CanActivateFn {
  return (route, state) => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (auth.hasPermission(permission)) {
      return true;
    }

    // Redirect safely WITHOUT causing loops
    return router.createUrlTree(['/login']);
    // or use: ['/unauthorized'] if you add that page
  };
}
