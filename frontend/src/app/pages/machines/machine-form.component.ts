import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Machine {
  id: string;
  name: string;
  capacity_per_hour: number | null;
  constraints: string | null;
  is_active: boolean;
}

@Component({
  selector: 'app-machine-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './machine-form.component.html',
  styleUrl: './machine-form.component.scss'
})
export class MachineFormComponent implements OnInit {
  id: string | null = null;
  name = '';
  capacityPerHour: number | null = null;
  constraints = '';
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
      this.api.get<Machine>(`/machines/${this.id}`).subscribe({
        next: (m) => {
          this.name = m.name;
          this.capacityPerHour = m.capacity_per_hour;
          this.constraints = m.constraints ?? '';
          this.isActive = m.is_active;
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      name: this.name,
      capacity_per_hour: this.capacityPerHour,
      constraints: this.constraints || null,
      is_active: this.isActive
    };
    if (this.id) {
      this.api.patch<Machine>(`/machines/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/production/machines']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<Machine>('/machines', body).subscribe({
        next: () => this.router.navigate(['/production/machines']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
