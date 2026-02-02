import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface RFQ {
  id: string;
  reference: string | null;
  status: string;
  customer_id: string | null;
  due_date: string | null;
  notes: string | null;
}

@Component({
  selector: 'app-rfqs-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './rfqs-list.component.html',
  styleUrl: './rfqs-list.component.scss'
})
export class RfqsListComponent implements OnInit {
  items: RFQ[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<RFQ[]>('/rfqs').subscribe({
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
