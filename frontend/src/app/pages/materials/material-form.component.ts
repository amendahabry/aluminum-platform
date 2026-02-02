import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-material-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './material-form.component.html',
  styleUrl: './material-form.component.scss'
})
export class MaterialFormComponent implements OnInit {
  id: string | null = null;
  sku = '';
  name = '';
  description = '';
  unit = 'pcs';
  weightKg: number | null = null;
  loading = false;
  error = '';

  constructor(private api: ApiService, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id');
    if (this.id) {
      this.api.get<any>(`/materials/${this.id}`).subscribe({
        next: (m) => { this.sku = m.sku; this.name = m.name; this.description = m.description || ''; this.unit = m.unit; this.weightKg = m.weight_kg; },
        error: (err) => this.error = err.error?.detail || 'errors.generic'
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = { sku: this.sku, name: this.name, description: this.description || null, unit: this.unit, weight_kg: this.weightKg };
    if (this.id) {
      this.api.patch(`/materials/${this.id}`, { name: this.name, description: this.description || null, unit: this.unit, weight_kg: this.weightKg }).subscribe({
        next: () => this.router.navigate(['/inventory/materials']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post('/materials', body).subscribe({
        next: () => this.router.navigate(['/inventory/materials']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
