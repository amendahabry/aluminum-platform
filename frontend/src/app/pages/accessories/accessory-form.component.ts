import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Accessory {
  id: string;
  sku: string;
  name: string;
  category: string | null;
  unit: string;
  cost: number | null;
  notes: string | null;
  is_active: boolean;
}

@Component({
  selector: 'app-accessory-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './accessory-form.component.html',
  styleUrl: './accessory-form.component.scss'
})
export class AccessoryFormComponent implements OnInit {
  id: string | null = null;
  sku = '';
  name = '';
  category = '';
  unit = 'pcs';
  cost: number | string | null = null;
  notes = '';
  isActive = true;
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
      this.api.get<Accessory>(`/accessories/${this.id}`).subscribe({
        next: (a) => {
          this.sku = a.sku;
          this.name = a.name;
          this.category = a.category ?? '';
          this.unit = a.unit ?? 'pcs';
          this.cost = a.cost != null ? Number(a.cost) : null;
          this.notes = a.notes ?? '';
          this.isActive = a.is_active;
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const costVal = this.cost === '' || this.cost === null || this.cost === undefined || (typeof this.cost === 'number' && isNaN(this.cost))
      ? null
      : Number(this.cost);
    const body = {
      sku: this.sku,
      name: this.name,
      category: this.category || null,
      unit: this.unit || 'pcs',
      cost: costVal,
      notes: this.notes || null,
      ...(this.id ? { is_active: this.isActive } : {})
    };

    if (this.id) {
      this.api.patch<Accessory>(`/accessories/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/inventory/accessories']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<Accessory>('/accessories', body).subscribe({
        next: () => this.router.navigate(['/inventory/accessories']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
