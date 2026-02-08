import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface OverviewReport {
  stock_lots: number;
  sales_orders: number;
  inventory_aging: Record<string, number>;
}

@Component({
  selector: 'app-management-reports',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './management-reports.component.html',
  styleUrl: './management-reports.component.scss'
})
export class ManagementReportsComponent implements OnInit {
  data: OverviewReport | null = null;
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<OverviewReport>('/management-reports/overview').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: OverviewReport[] })?.content ?? []);
        this.data = resolved[0] || null;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
