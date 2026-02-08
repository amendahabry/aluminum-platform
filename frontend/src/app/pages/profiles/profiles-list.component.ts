import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
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
  selector: 'app-profiles-list',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './profiles-list.component.html',
  styleUrl: './profiles-list.component.scss'
})
export class ProfilesListComponent implements OnInit {
  items: Profile[] = [];
  loading = true;
  error = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get<Profile[]>('/profiles').subscribe({
      next: (data) => {
        const resolved = Array.isArray(data)
          ? data
          : ((data as unknown as { content?: Profile[] })?.content ?? []);
        this.items = resolved;
        this.loading = false; },
      error: (err) => { this.error = err.error?.detail || 'errors.generic'; this.loading = false; }
    });
  }
}
