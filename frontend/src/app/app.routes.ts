import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { roleGuard } from './core/guards/role.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: 'register-tenant',
    loadComponent: () => import('./pages/register-tenant/register-tenant.component').then(m => m.RegisterTenantComponent)
  },
  {
    path: '',
    loadComponent: () => import('./layout/main-layout/main-layout.component').then(m => m.MainLayoutComponent),
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'inventory/materials', pathMatch: 'full' },
      { path: 'inventory/materials', loadComponent: () => import('./pages/materials/materials-list.component').then(m => m.MaterialsListComponent), canActivate: [roleGuard('inventory:materials:read')] },
      { path: 'inventory/materials/new', loadComponent: () => import('./pages/materials/material-form.component').then(m => m.MaterialFormComponent), canActivate: [roleGuard('inventory:materials:write')] },
      { path: 'inventory/materials/:id/edit', loadComponent: () => import('./pages/materials/material-form.component').then(m => m.MaterialFormComponent), canActivate: [roleGuard('inventory:materials:write')] },
      { path: 'orders/rfqs', loadComponent: () => import('./pages/rfqs/rfqs-list.component').then(m => m.RfqsListComponent), canActivate: [roleGuard('orders:rfq:read')] },
      { path: 'orders/rfqs/new', loadComponent: () => import('./pages/rfqs/rfq-form.component').then(m => m.RfqFormComponent), canActivate: [roleGuard('orders:rfq:write')] },
      { path: 'orders/quotes', loadComponent: () => import('./pages/quotes/quotes-list.component').then(m => m.QuotesListComponent), canActivate: [roleGuard('orders:quotes:read')] },
      { path: 'orders/quotes/new', loadComponent: () => import('./pages/quotes/quote-form.component').then(m => m.QuoteFormComponent), canActivate: [roleGuard('orders:quotes:write')] },
      { path: 'orders/sales-orders', loadComponent: () => import('./pages/sales-orders/sales-orders-list.component').then(m => m.SalesOrdersListComponent), canActivate: [roleGuard('orders:sales:read')] },
    ]
  },
  { path: '**', redirectTo: 'login' }
];
