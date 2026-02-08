import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface PurchaseOrder {
  id: string;
  supplier_name: string;
  reference: string | null;
  status: string;
  order_date: string;
  expected_date: string | null;
  notes: string | null;
}

@Component({
  selector: 'app-purchase-order-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './purchase-order-form.component.html',
  styleUrl: './purchase-order-form.component.scss'
})
export class PurchaseOrderFormComponent implements OnInit {
  id: string | null = null;
  supplierName = '';
  reference = '';
  orderDate = '';
  expectedDate = '';
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
      this.api.get<PurchaseOrder>(`/purchase-orders/${this.id}`).subscribe({
        next: (po) => {
          this.supplierName = po.supplier_name;
          this.reference = po.reference ?? '';
          this.orderDate = po.order_date ? po.order_date.slice(0, 10) : '';
          this.expectedDate = po.expected_date ? po.expected_date.slice(0, 10) : '';
          this.notes = po.notes ?? '';
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
      supplier_name: this.supplierName,
      reference: this.reference || null,
      order_date: this.orderDate || null,
      expected_date: this.expectedDate || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<PurchaseOrder>(`/purchase-orders/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/logistics/purchase-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<PurchaseOrder>('/purchase-orders', { ...body, lines: [] }).subscribe({
        next: () => this.router.navigate(['/logistics/purchase-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
