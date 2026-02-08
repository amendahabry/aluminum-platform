import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface Quote {
  id: string;
  rfq_id: string | null;
  reference: string | null;
  status: string;
  notes: string | null;
}

@Component({
  selector: 'app-quote-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './quote-form.component.html',
  styleUrl: './quote-form.component.scss'
})
export class QuoteFormComponent implements OnInit {
  id: string | null = null;
  rfqId = '';
  reference = '';
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
      this.api.get<Quote>(`/quotes/${this.id}`).subscribe({
        next: (q) => {
          this.rfqId = q.rfq_id ?? '';
          this.reference = q.reference ?? '';
          this.notes = q.notes ?? '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      rfq_id: this.rfqId || null,
      reference: this.reference || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<Quote>(`/quotes/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/orders/quotes']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<Quote>('/quotes', { ...body, lines: [] }).subscribe({
        next: () => this.router.navigate(['/orders/quotes']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
