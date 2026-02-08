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
      { path: 'inventory/profiles', loadComponent: () => import('./pages/profiles/profiles-list.component').then(m => m.ProfilesListComponent), canActivate: [roleGuard('inventory:profiles:read')] },
      { path: 'inventory/profiles/new', loadComponent: () => import('./pages/profiles/profile-form.component').then(m => m.ProfileFormComponent), canActivate: [roleGuard('inventory:profiles:write')] },
      { path: 'inventory/profiles/:id/edit', loadComponent: () => import('./pages/profiles/profile-form.component').then(m => m.ProfileFormComponent), canActivate: [roleGuard('inventory:profiles:write')] },
      { path: 'inventory/accessories', loadComponent: () => import('./pages/accessories/accessories-list.component').then(m => m.AccessoriesListComponent), canActivate: [roleGuard('inventory:accessories:read')] },
      { path: 'inventory/accessories/new', loadComponent: () => import('./pages/accessories/accessory-form.component').then(m => m.AccessoryFormComponent), canActivate: [roleGuard('inventory:accessories:write')] },
      { path: 'inventory/accessories/:id/edit', loadComponent: () => import('./pages/accessories/accessory-form.component').then(m => m.AccessoryFormComponent), canActivate: [roleGuard('inventory:accessories:write')] },
      { path: 'inventory/scrap', loadComponent: () => import('./pages/scrap/scrap-list.component').then(m => m.ScrapListComponent), canActivate: [roleGuard('inventory:scrap:read')] },
      { path: 'inventory/scrap/new', loadComponent: () => import('./pages/scrap/scrap-form.component').then(m => m.ScrapFormComponent), canActivate: [roleGuard('inventory:scrap:write')] },
      { path: 'inventory/scrap/:id/edit', loadComponent: () => import('./pages/scrap/scrap-form.component').then(m => m.ScrapFormComponent), canActivate: [roleGuard('inventory:scrap:write')] },
      { path: 'orders/rfqs', loadComponent: () => import('./pages/rfqs/rfqs-list.component').then(m => m.RfqsListComponent), canActivate: [roleGuard('orders:rfq:read')] },
      { path: 'orders/rfqs/new', loadComponent: () => import('./pages/rfqs/rfq-form.component').then(m => m.RfqFormComponent), canActivate: [roleGuard('orders:rfq:write')] },
      { path: 'orders/rfqs/:id/edit', loadComponent: () => import('./pages/rfqs/rfq-form.component').then(m => m.RfqFormComponent), canActivate: [roleGuard('orders:rfq:write')] },
      { path: 'orders/quotes', loadComponent: () => import('./pages/quotes/quotes-list.component').then(m => m.QuotesListComponent), canActivate: [roleGuard('orders:quotes:read')] },
      { path: 'orders/quotes/new', loadComponent: () => import('./pages/quotes/quote-form.component').then(m => m.QuoteFormComponent), canActivate: [roleGuard('orders:quotes:write')] },
      { path: 'orders/quotes/:id/edit', loadComponent: () => import('./pages/quotes/quote-form.component').then(m => m.QuoteFormComponent), canActivate: [roleGuard('orders:quotes:write')] },
      { path: 'sales/customers', loadComponent: () => import('./pages/customers/customers-list.component').then(m => m.CustomersListComponent), canActivate: [roleGuard('orders:customers:read')] },
      { path: 'sales/customers/new', loadComponent: () => import('./pages/customers/customer-form.component').then(m => m.CustomerFormComponent), canActivate: [roleGuard('orders:customers:write')] },
      { path: 'sales/customers/:id/edit', loadComponent: () => import('./pages/customers/customer-form.component').then(m => m.CustomerFormComponent), canActivate: [roleGuard('orders:customers:write')] },
      { path: 'sales/price-lists', loadComponent: () => import('./pages/price-lists/price-lists-list.component').then(m => m.PriceListsListComponent), canActivate: [roleGuard('orders:pricelists:read')] },
      { path: 'sales/price-lists/new', loadComponent: () => import('./pages/price-lists/price-list-form.component').then(m => m.PriceListFormComponent), canActivate: [roleGuard('orders:pricelists:write')] },
      { path: 'sales/price-lists/:id/edit', loadComponent: () => import('./pages/price-lists/price-list-form.component').then(m => m.PriceListFormComponent), canActivate: [roleGuard('orders:pricelists:write')] },
      { path: 'orders/sales-orders', loadComponent: () => import('./pages/sales-orders/sales-orders-list.component').then(m => m.SalesOrdersListComponent), canActivate: [roleGuard('orders:sales:read')] },
      { path: 'orders/sales-orders/new', loadComponent: () => import('./pages/sales-orders/sales-order-form.component').then(m => m.SalesOrderFormComponent), canActivate: [roleGuard('orders:sales:write')] },
      { path: 'orders/sales-orders/:id/edit', loadComponent: () => import('./pages/sales-orders/sales-order-form.component').then(m => m.SalesOrderFormComponent), canActivate: [roleGuard('orders:sales:write')] },
      { path: 'logistics/delivery-notes', loadComponent: () => import('./pages/delivery-notes/delivery-notes-list.component').then(m => m.DeliveryNotesListComponent), canActivate: [roleGuard('orders:delivery-notes:read')] },
      { path: 'logistics/delivery-notes/new', loadComponent: () => import('./pages/delivery-notes/delivery-note-form.component').then(m => m.DeliveryNoteFormComponent), canActivate: [roleGuard('orders:delivery-notes:write')] },
      { path: 'logistics/delivery-notes/:id/edit', loadComponent: () => import('./pages/delivery-notes/delivery-note-form.component').then(m => m.DeliveryNoteFormComponent), canActivate: [roleGuard('orders:delivery-notes:write')] },
      { path: 'logistics/purchase-orders', loadComponent: () => import('./pages/purchase-orders/purchase-orders-list.component').then(m => m.PurchaseOrdersListComponent), canActivate: [roleGuard('orders:purchase-orders:read')] },
      { path: 'logistics/purchase-orders/new', loadComponent: () => import('./pages/purchase-orders/purchase-order-form.component').then(m => m.PurchaseOrderFormComponent), canActivate: [roleGuard('orders:purchase-orders:write')] },
      { path: 'logistics/purchase-orders/:id/edit', loadComponent: () => import('./pages/purchase-orders/purchase-order-form.component').then(m => m.PurchaseOrderFormComponent), canActivate: [roleGuard('orders:purchase-orders:write')] },
      { path: 'production/machines', loadComponent: () => import('./pages/machines/machines-list.component').then(m => m.MachinesListComponent), canActivate: [roleGuard('production:machines:read')] },
      { path: 'production/machines/new', loadComponent: () => import('./pages/machines/machine-form.component').then(m => m.MachineFormComponent), canActivate: [roleGuard('production:machines:write')] },
      { path: 'production/machines/:id/edit', loadComponent: () => import('./pages/machines/machine-form.component').then(m => m.MachineFormComponent), canActivate: [roleGuard('production:machines:write')] },
      { path: 'production/work-orders', loadComponent: () => import('./pages/work-orders/work-orders-list.component').then(m => m.WorkOrdersListComponent), canActivate: [roleGuard('production:work-orders:read')] },
      { path: 'production/work-orders/new', loadComponent: () => import('./pages/work-orders/work-order-form.component').then(m => m.WorkOrderFormComponent), canActivate: [roleGuard('production:work-orders:write')] },
      { path: 'production/work-orders/:id/edit', loadComponent: () => import('./pages/work-orders/work-order-form.component').then(m => m.WorkOrderFormComponent), canActivate: [roleGuard('production:work-orders:write')] },
      { path: 'management/dashboard', loadComponent: () => import('./pages/management/management-dashboard.component').then(m => m.ManagementDashboardComponent), canActivate: [roleGuard('management:dashboard:read')] },
      { path: 'management/reports', loadComponent: () => import('./pages/management/management-reports.component').then(m => m.ManagementReportsComponent), canActivate: [roleGuard('management:reports:read')] },
    ]
  },
  { path: '**', redirectTo: 'login' }
];
