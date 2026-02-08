import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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
  selector: 'app-machines-list',
  standalone: true,
  imports: [CommonModule, TranslateModule],
  templateUrl: './machines-list.component.html',
  styleUrl: './machines-list.component.scss'
})
export class MachinesListComponent implements OnInit {
  items: Machine[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<Machine[]>('/machines').subscribe({
      next: (data) => { this.items = data; this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
