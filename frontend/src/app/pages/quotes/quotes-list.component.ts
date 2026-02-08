import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Quote {
  id: string;
  reference: string | null;
  status: string;
  rfq_id: string | null;
  customer_id: string | null;
  valid_until: string | null;
}

@Component({
  selector: 'app-quotes-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './quotes-list.component.html',
  styleUrl: './quotes-list.component.scss'
})
export class QuotesListComponent implements OnInit {
  items: Quote[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.api.get<Quote[]>('/quotes').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: Quote[] })?.content ?? []);
        this.items = resolved;
        this.loading = false;
      },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }

  approve(id: string): void {
    this.api.post(`/quotes/${id}/approve`, { approved: true }).subscribe({
      next: () => this.ngOnInit(),
      error: (err) => this.error = err.error?.detail || 'errors.generic'
    });
  }
}
