import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Customer {
  id: string;
  name: string;
  email: string | null;
  payment_terms: string | null;
  credit_limit: number | null;
  is_active: boolean;
}

@Component({
  selector: 'app-customers-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './customers-list.component.html',
  styleUrl: './customers-list.component.scss'
})
export class CustomersListComponent implements OnInit {
  items: Customer[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<Customer[]>('/customers').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: Customer[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
