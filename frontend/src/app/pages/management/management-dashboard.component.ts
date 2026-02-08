import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface DashboardSummary {
  profit: number;
  scrap_pct: number;
  utilization: number;
  work_orders: number;
}

@Component({
  selector: 'app-management-dashboard',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './management-dashboard.component.html',
  styleUrl: './management-dashboard.component.scss'
})
export class ManagementDashboardComponent implements OnInit {
  data: DashboardSummary | null = null;
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<DashboardSummary>('/dashboards/summary').subscribe({
      next: (data) => { this.data = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
