import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface ScrapRecord {
  id: string;
  material_id: string | null;
  warehouse_id: string | null;
  weight_kg: number;
  reason: string | null;
  reported_at: string;
}

@Component({
  selector: 'app-scrap-list',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './scrap-list.component.html',
  styleUrl: './scrap-list.component.scss'
})
export class ScrapListComponent implements OnInit {
  items: ScrapRecord[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<ScrapRecord[]>('/scrap').subscribe({
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
