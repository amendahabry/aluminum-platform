import {
  HttpInterceptorFn,
  HttpErrorResponse,
  HttpBackend,
  HttpClient
} from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';
const API_BASE = '/api';

export const jwtInterceptor: HttpInterceptorFn = (req, next) => {
  // 🚨 NEVER intercept auth endpoints
  if (
    req.url.includes('/auth/login') ||
    req.url.includes('/auth/register') ||
    req.url.includes('/auth/register-tenant') ||
    req.url.includes('/auth/refresh')
  ) {
    return next(req);
  }

  const token = localStorage.getItem(TOKEN_KEY);

  const authReq = token
    ? req.clone({
        setHeaders: { Authorization: `Bearer ${token}` }
      })
    : req;

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      // Only handle 401
      if (err.status !== 401) {
        return throwError(() => err);
      }

      const refreshToken = localStorage.getItem(REFRESH_KEY);
      if (!refreshToken) {
        return throwError(() => err);
      }

      // Fresh HttpClient WITHOUT interceptors
      const backend = inject(HttpBackend);
      const refreshClient = new HttpClient(backend);

      return refreshClient
        .post<{ access_token: string; refresh_token: string }>(
          `${API_BASE}/auth/refresh`,
          { refresh_token: refreshToken }
        )
        .pipe(
          switchMap(res => {
            localStorage.setItem(TOKEN_KEY, res.access_token);
            localStorage.setItem(REFRESH_KEY, res.refresh_token);

            // Retry original request with new token
            return next(
              req.clone({
                setHeaders: {
                  Authorization: `Bearer ${res.access_token}`
                }
              })
            );
          }),
          catchError(() => {
            // Refresh failed → hard logout
            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(REFRESH_KEY);
            return throwError(() => err);
          })
        );
    })
  );
};
