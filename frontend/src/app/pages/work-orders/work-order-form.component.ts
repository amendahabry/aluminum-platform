import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ApiService } from '../../core/services/api.service';

interface WorkOrder {
  id: string;
  bom_id: string | null;
  reference: string | null;
  status: string;
  quantity: number;
  due_date: string | null;
}

@Component({
  selector: 'app-work-order-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './work-order-form.component.html',
  styleUrl: './work-order-form.component.scss'
})
export class WorkOrderFormComponent implements OnInit {
  id: string | null = null;
  bomId = '';
  reference = '';
  quantity = 1;
  dueDate = '';
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
      this.api.get<WorkOrder>(`/work-orders/${this.id}`).subscribe({
        next: (wo) => {
          this.bomId = wo.bom_id ?? '';
          this.reference = wo.reference ?? '';
          this.quantity = wo.quantity;
          this.dueDate = wo.due_date ? wo.due_date.slice(0, 10) : '';
        },
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; }
      });
    }
  }

  submit(): void {
    this.error = '';
    this.loading = true;
    const body = {
      bom_id: this.bomId || null,
      reference: this.reference || null,
      quantity: this.quantity,
      due_date: this.dueDate || null
    };
    if (this.id) {
      this.api.patch<WorkOrder>(`/work-orders/${this.id}`, body).subscribe({
        next: () => this.router.navigate(['/production/work-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    } else {
      this.api.post<WorkOrder>('/work-orders', body).subscribe({
        next: () => this.router.navigate(['/production/work-orders']),
        error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; },
        complete: () => this.loading = false
      });
    }
  }
}
