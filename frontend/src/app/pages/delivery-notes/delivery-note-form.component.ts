import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface DeliveryNote {
  id: string;
  reference: string | null;
  status: string;
  sales_order_id: string | null;
  delivered_at: string | null;
  notes: string | null;
}

@Component({
  selector: 'app-delivery-note-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './delivery-note-form.component.html',
  styleUrl: './delivery-note-form.component.scss'
})
export class DeliveryNoteFormComponent implements OnInit {
  id: string | null = null;
  salesOrderId = '';
  reference = '';
  deliveredAt = '';
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
      this.api.get<DeliveryNote>(`/delivery-notes/${this.id}`).subscribe({
        next: (note) => {
          this.salesOrderId = note.sales_order_id ?? '';
          this.reference = note.reference ?? '';
          this.deliveredAt = note.delivered_at ? note.delivered_at.slice(0, 16) : '';
          this.notes = note.notes ?? '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      sales_order_id: this.salesOrderId || null,
      reference: this.reference || null,
      delivered_at: this.deliveredAt || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<DeliveryNote>(`/delivery-notes/${this.id}`, {
        reference: body.reference,
        delivered_at: body.delivered_at,
        notes: body.notes
      }).subscribe({
        next: () => this.router.navigate(['/logistics/delivery-notes']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<DeliveryNote>('/delivery-notes', { ...body, lines: [] }).subscribe({
        next: () => this.router.navigate(['/logistics/delivery-notes']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
