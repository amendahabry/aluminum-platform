import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface SalesOrder {
  id: string;
  reference: string | null;
  status: string;
  quote_id: string | null;
  customer_id: string | null;
  order_date: string | null;
}

@Component({
  selector: 'app-sales-orders-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './sales-orders-list.component.html',
  styleUrl: './sales-orders-list.component.scss'
})
export class SalesOrdersListComponent implements OnInit {
  items: SalesOrder[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<SalesOrder[]>('/sales-orders').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: SalesOrder[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
