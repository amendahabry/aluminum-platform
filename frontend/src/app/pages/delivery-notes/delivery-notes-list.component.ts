import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface DeliveryNote {
  id: string;
  reference: string | null;
  status: string;
  sales_order_id: string | null;
  delivered_at: string | null;
}

@Component({
  selector: 'app-delivery-notes-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './delivery-notes-list.component.html',
  styleUrl: './delivery-notes-list.component.scss'
})
export class DeliveryNotesListComponent implements OnInit {
  items: DeliveryNote[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<DeliveryNote[]>('/delivery-notes').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: DeliveryNote[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
