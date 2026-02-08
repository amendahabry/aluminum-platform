import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface PriceList {
  id: string;
  name: string;
  customer_id: string | null;
  customer_group: string | null;
  valid_from: string | null;
  valid_to: string | null;
  notes: string | null;
}

@Component({
  selector: 'app-price-list-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './price-list-form.component.html',
  styleUrl: './price-list-form.component.scss'
})
export class PriceListFormComponent implements OnInit {
  id: string | null = null;
  name = '';
  customerId = '';
  customerGroup = '';
  validFrom = '';
  validTo = '';
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
      this.api.get<PriceList>(`/price-lists/${this.id}`).subscribe({
        next: (pl) => {
          this.name = pl.name;
          this.customerId = pl.customer_id ?? '';
          this.customerGroup = pl.customer_group ?? '';
          this.validFrom = pl.valid_from ? pl.valid_from.slice(0, 10) : '';
          this.validTo = pl.valid_to ? pl.valid_to.slice(0, 10) : '';
          this.notes = pl.notes ?? '';
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
      customer_id: this.customerId || null,
      customer_group: this.customerGroup || null,
      valid_from: this.validFrom || null,
      valid_to: this.validTo || null,
      notes: this.notes || null
    };
    if (this.id) {
      this.api.patch<PriceList>(`/price-lists/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/sales/price-lists']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<PriceList>('/price-lists', { ...body, items: [] }).subscribe({
        next: () => this.router.navigate(['/sales/price-lists']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
