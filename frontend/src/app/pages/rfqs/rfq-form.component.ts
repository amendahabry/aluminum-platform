import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-rfq-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './rfq-form.component.html',
  styleUrl: './rfq-form.component.scss'
})
export class RfqFormComponent {
  reference = '';
  notes = '';
  loading = false;
  error = '';

  constructor(private api: ApiService, private router: Router) {}

  submit(): void {
    this.error = '';
    this.loading = true;
    this.api.post('/rfqs', { reference: this.reference, notes: this.notes, lines: [] }).subscribe({
      next: () => this.router.navigate(['/orders/rfqs']),
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
      complete: () => this.loading = false
    });
  }
}
