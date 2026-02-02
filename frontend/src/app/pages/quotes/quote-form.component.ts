import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-quote-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './quote-form.component.html',
  styleUrl: './quote-form.component.scss'
})
export class QuoteFormComponent {
  rfqId = '';
  reference = '';
  notes = '';
  loading = false;
  error = '';

  constructor(private api: ApiService, private router: Router) {}

  submit(): void {
    this.error = '';
    this.loading = true;
    this.api.post('/quotes', { rfq_id: this.rfqId || null, reference: this.reference, notes: this.notes, lines: [] }).subscribe({
      next: () => this.router.navigate(['/orders/quotes']),
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
      complete: () => this.loading = false
    });
  }
}
