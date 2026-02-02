import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register-tenant',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './register-tenant.component.html',
  styleUrl: './register-tenant.component.scss'
})
export class RegisterTenantComponent {
  name = '';
  slug = '';
  adminEmail = '';
  adminPassword = '';
  adminFullName = '';
  error = '';
  success = '';
  loading = false;

  constructor(private auth: AuthService, private router: Router) {}

  submit(): void {
    this.error = '';
    this.success = '';
    this.loading = true;
    this.auth.registerTenant({
      name: this.name,
      slug: this.slug,
      admin_email: this.adminEmail,
      admin_password: this.adminPassword,
      admin_full_name: this.adminFullName || undefined
    }).subscribe({
      next: () => {
        this.success = 'auth.registerSuccess';
        this.loading = false;
        setTimeout(() => this.router.navigate(['/login']), 2000);
      },
      error: (err) => {
        this.error = err.error?.detail || 'errors.generic';
        this.loading = false;
      },
      complete: () => this.loading = false
    });
  }
}
