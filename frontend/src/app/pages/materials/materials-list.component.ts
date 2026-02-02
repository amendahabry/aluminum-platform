import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Material {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  unit: string;
  weight_kg: number | null;
  is_active: boolean;
}

@Component({
  selector: 'app-materials-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './materials-list.component.html',
  styleUrl: './materials-list.component.scss'
})
export class MaterialsListComponent implements OnInit {
  items: Material[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<Material[]>('/materials').subscribe({
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
