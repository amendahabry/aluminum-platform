import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface SalesOrder {
  id: string;
  reference: string | null;
  status: string;
  customer_id: string | null;
  order_date: string | null;
  notes: string | null;
}

@Component({
  selector: 'app-sales-order-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './sales-order-form.component.html',
  styleUrl: './sales-order-form.component.scss'
})
export class SalesOrderFormComponent implements OnInit {
  id: string | null = null;
  reference = '';
  customerId = '';
  orderDate = '';
  notes = '';
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
      this.api.get<SalesOrder>(`/sales-orders/${this.id}`).subscribe({
        next: (o) => {
          this.reference = o.reference ?? '';
          this.customerId = o.customer_id ?? '';
          this.orderDate = o.order_date ? o.order_date.slice(0, 10) : '';
          this.notes = o.notes ?? '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    } else {
      this.orderDate = new Date().toISOString().slice(0, 10);
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      reference: this.reference || null,
      customer_id: this.customerId || null,
      order_date: this.orderDate || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<SalesOrder>(`/sales-orders/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/orders/sales-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<SalesOrder>('/sales-orders', { ...body, lines: [] }).subscribe({
        next: () => this.router.navigate(['/orders/sales-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
