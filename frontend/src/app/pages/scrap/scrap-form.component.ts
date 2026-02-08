import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface ScrapRecord {
  id: string;
  material_id: string | null;
  warehouse_id: string | null;
  weight_kg: number;
  reason: string | null;
  cost_recovery: number | null;
  reported_at: string;
  notes: string | null;
}

@Component({
  selector: 'app-scrap-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './scrap-form.component.html',
  styleUrl: './scrap-form.component.scss'
})
export class ScrapFormComponent implements OnInit {
  id: string | null = null;
  materialId = '';
  warehouseId = '';
  weightKg = 0;
  reason = '';
  costRecovery: number | null = null;
  reportedAt = '';
  notes = '';
  loading = false;
  error = '';

  constructor(
    private api: ApiService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id');
    if (this.id) {
      this.api.get<ScrapRecord>(`/scrap/${this.id}`).subscribe({
        next: (s) => {
          this.materialId = s.material_id ?? '';
          this.warehouseId = s.warehouse_id ?? '';
          this.weightKg = s.weight_kg;
          this.reason = s.reason ?? '';
          this.costRecovery = s.cost_recovery;
          this.reportedAt = s.reported_at ? s.reported_at.slice(0, 16) : '';
          this.notes = s.notes ?? '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    } else {
      this.reportedAt = new Date().toISOString().slice(0, 16);
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      material_id: this.materialId || null,
      warehouse_id: this.warehouseId || null,
      weight_kg: this.weightKg,
      reason: this.reason || null,
      cost_recovery: this.costRecovery,
      reported_at: this.reportedAt || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<ScrapRecord>(`/scrap/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/inventory/scrap']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<ScrapRecord>('/scrap', body).subscribe({
        next: () => this.router.navigate(['/inventory/scrap']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
