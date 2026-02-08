import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface WorkOrder {
  id: string;
  reference: string | null;
  status: string;
  quantity: number;
  due_date: string | null;
}

@Component({
  selector: 'app-work-orders-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './work-orders-list.component.html',
  styleUrl: './work-orders-list.component.scss'
})
export class WorkOrdersListComponent implements OnInit {
  items: WorkOrder[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.api.get<WorkOrder[]>('/work-orders').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: WorkOrder[] })?.content ?? []);
        this.items = resolved;
        this.loading = false;
      },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
