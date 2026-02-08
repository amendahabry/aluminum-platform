import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface RFQ {
  id: string;
  reference: string | null;
  status: string;
  notes: string | null;
}

@Component({
  selector: 'app-rfq-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './rfq-form.component.html',
  styleUrl: './rfq-form.component.scss'
})
export class RfqFormComponent implements OnInit {
  id: string | null = null;
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
      this.api.get<RFQ>(`/rfqs/${this.id}`).subscribe({
        next: (r) => {
          this.reference = r.reference ?? '';
          this.notes = r.notes ?? '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = { reference: this.reference || null, notes: this.notes || null };
    if (this.id) {
      this.api.patch<RFQ>(`/rfqs/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/orders/rfqs']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<RFQ>('/rfqs', { ...body, lines: [] }).subscribe({
        next: () => this.router.navigate(['/orders/rfqs']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
