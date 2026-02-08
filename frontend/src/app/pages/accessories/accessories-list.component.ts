import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Accessory {
  id: string;
  sku: string;
  name: string;
  category: string | null;
  unit: string;
  cost: number | null;
  is_active: boolean;
}

@Component({
  selector: 'app-accessories-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './accessories-list.component.html',
  styleUrl: './accessories-list.component.scss'
})
export class AccessoriesListComponent implements OnInit {
  items: Accessory[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<Accessory[]>('/accessories').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: Accessory[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
