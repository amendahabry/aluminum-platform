import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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
  imports: [CommonModule, TranslateModule],
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
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
