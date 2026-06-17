import { KpiCard } from './KpiCard';
import type { KpiData } from '../types';

function formatCurrency(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
  return `$${v.toLocaleString()}`;
}

interface KpiGridProps {
  kpis: KpiData;
}

export function KpiGrid({ kpis }: KpiGridProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      <KpiCard label="Total Accounts" value={kpis.total_accounts.toLocaleString()} />
      <KpiCard label="Active Leads" value={kpis.active_leads.toLocaleString()} subtitle="New, Contacted, Qualified" />
      <KpiCard label="Open Pipeline" value={formatCurrency(kpis.open_pipeline)} />
      <KpiCard label="Weighted Value" value={formatCurrency(kpis.weighted_value)} subtitle="Value × Probability" />
      <KpiCard label="Win Rate" value={`${(kpis.win_rate * 100).toFixed(0)}%`} subtitle="Closed Won ÷ All Closed" />
    </div>
  );
}
