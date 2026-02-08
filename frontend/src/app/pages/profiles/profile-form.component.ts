import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Profile {
  id: string;
  series: string;
  alloy: string;
  temper: string | null;
  weight_per_meter: number;
  cost_per_meter: number;
  description: string | null;
  is_active: boolean;
}

@Component({
  selector: 'app-profile-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './profile-form.component.html',
  styleUrl: './profile-form.component.scss'
})
export class ProfileFormComponent implements OnInit {
  id: string | null = null;
  series = '';
  alloy = '';
  temper = '';
  weightPerMeter: number | null = null;
  costPerMeter: number | null = null;
  description = '';
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
      this.api.get<Profile>(`/profiles/${this.id}`).subscribe({
        next: (p) => {
          this.series = p.series;
          this.alloy = p.alloy;
          this.temper = p.temper ?? '';
          this.weightPerMeter = p.weight_per_meter;
          this.costPerMeter = p.cost_per_meter;
          this.description = p.description ?? '';
          this.isActive = p.is_active;
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      series: this.series,
      alloy: this.alloy,
      temper: this.temper || null,
      weight_per_meter: this.weightPerMeter ?? 0,
      cost_per_meter: this.costPerMeter ?? 0,
      description: this.description || null,
      ...(this.id ? { is_active: this.isActive } : {})
    };

    if (this.id) {
      this.api.patch<Profile>(`/profiles/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/inventory/profiles']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<Profile>('/profiles', body).subscribe({
        next: () => this.router.navigate(['/inventory/profiles']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
