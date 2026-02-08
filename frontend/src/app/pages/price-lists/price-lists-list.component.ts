import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface PriceList {
  id: string;
  name: string;
  customer_id: string | null;
  customer_group: string | null;
  valid_from: string | null;
  valid_to: string | null;
}

@Component({
  selector: 'app-price-lists-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './price-lists-list.component.html',
  styleUrl: './price-lists-list.component.scss'
})
export class PriceListsListComponent implements OnInit {
  items: PriceList[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<PriceList[]>('/price-lists').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: PriceList[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
