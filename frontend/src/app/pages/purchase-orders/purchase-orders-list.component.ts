import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface PurchaseOrder {
  id: string;
  supplier_name: string;
  reference: string | null;
  status: string;
  order_date: string;
}

@Component({
  selector: 'app-purchase-orders-list',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './purchase-orders-list.component.html',
  styleUrl: './purchase-orders-list.component.scss'
})
export class PurchaseOrdersListComponent implements OnInit {
  items: PurchaseOrder[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<PurchaseOrder[]>('/purchase-orders').subscribe({
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
