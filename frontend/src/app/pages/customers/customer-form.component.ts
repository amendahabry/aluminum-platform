import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Customer {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  payment_terms: string | null;
  credit_limit: number | null;
  billing_address: string | null;
  shipping_address: string | null;
  is_active: boolean;
}

@Component({
  selector: 'app-customer-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './customer-form.component.html',
  styleUrl: './customer-form.component.scss'
})
export class CustomerFormComponent implements OnInit {
  id: string | null = null;
  name = '';
  email = '';
  phone = '';
  paymentTerms = '';
  creditLimit: number | null = null;
  billingAddress = '';
  shippingAddress = '';
  isActive = true;
  loading = false;
  error = '';

  constructor(
    private api: ApiService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id');
    if (this.id) {
      this.api.get<Customer>(`/customers/${this.id}`).subscribe({
        next: (c) => {
          this.name = c.name;
          this.email = c.email ?? '';
          this.phone = c.phone ?? '';
          this.paymentTerms = c.payment_terms ?? '';
          this.creditLimit = c.credit_limit;
          this.billingAddress = c.billing_address ?? '';
          this.shippingAddress = c.shipping_address ?? '';
          this.isActive = c.is_active;
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      name: this.name,
      email: this.email || null,
      phone: this.phone || null,
      payment_terms: this.paymentTerms || null,
      credit_limit: this.creditLimit,
      billing_address: this.billingAddress || null,
      shipping_address: this.shippingAddress || null,
      is_active: this.isActive
    };
    if (this.id) {
      this.api.patch<Customer>(`/customers/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/sales/customers']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<Customer>('/customers', body).subscribe({
        next: () => this.router.navigate(['/sales/customers']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
