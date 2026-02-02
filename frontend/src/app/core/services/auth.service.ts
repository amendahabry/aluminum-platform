import { Injectable, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, of } from 'rxjs';
import { TranslateService } from '@ngx-translate/core';

export interface LoginRequest {
  email: string;
  password: string;
  tenant_slug?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface MeResponse {
  id: string;
  email: string;
  full_name: string | null;
  tenant_id: string;
  tenant_name: string | null;
  roles: string[];
  permissions: string[];
  is_active: boolean;
}

export interface RegisterTenantRequest {
  name: string;
  slug: string;
  admin_email: string;
  admin_password: string;
  admin_full_name?: string;
}

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';
const API_BASE = '/api';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly accessToken = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  private readonly refreshToken = signal<string | null>(localStorage.getItem(REFRESH_KEY));
  private readonly me = signal<MeResponse | null>(null);

  readonly isAuthenticated = computed(() => !!this.accessToken());
  readonly currentUser = this.me.asReadonly();

  constructor(
    private http: HttpClient,
    private router: Router,
    private translate: TranslateService
  ) {}

  getToken(): string | null {
    return this.accessToken();
  }

  getRefreshToken(): string | null {
    return this.refreshToken();
  }

  setTokens(access: string, refresh: string): void {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
    this.accessToken.set(access);
    this.refreshToken.set(refresh);
  }

  clearTokens(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    this.accessToken.set(null);
    this.refreshToken.set(null);
    this.me.set(null);
  }

  login(body: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${API_BASE}/auth/login`, body).pipe(
      tap((res) => this.setTokens(res.access_token, res.refresh_token))
    );
  }

  registerTenant(body: RegisterTenantRequest): Observable<{ tenant_id: string; user_id: string; message: string }> {
    return this.http.post<{ tenant_id: string; user_id: string; message: string }>(`${API_BASE}/auth/register-tenant`, body);
  }

  refresh(): Observable<LoginResponse> {
    const refresh = this.refreshToken();
    if (!refresh) return of(null as any);
    return this.http.post<LoginResponse>(`${API_BASE}/auth/refresh`, { refresh_token: refresh }).pipe(
      tap((res) => this.setTokens(res.access_token, res.refresh_token)),
      catchError(() => {
        this.logout();
        return of(null as any);
      })
    );
  }

  loadMe(): Observable<MeResponse> {
    return this.http.get<MeResponse>(`${API_BASE}/auth/me`).pipe(
      tap((user) => this.me.set(user))
    );
  }

  logout(): void {
    this.clearTokens();
    this.router.navigate(['/login']);
  }

  hasPermission(perm: string): boolean {
    const user = this.me();
    if (!user?.permissions) return false;
    return user.permissions.includes(perm) || user.permissions.includes('admin:*');
  }

  setLanguage(lang: string): void {
    localStorage.setItem('lang', lang);
    this.translate.use(lang);
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === 'ar' || lang === 'he' ? 'rtl' : 'ltr';
  }
}
