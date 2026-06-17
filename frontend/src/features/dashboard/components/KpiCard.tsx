interface KpiCardProps {
  label: string;
  value: string;
  subtitle?: string;
}

export function KpiCard({ label, value, subtitle }: KpiCardProps) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-4 shadow-card">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
      <p className="mt-1.5 text-2xl font-semibold text-slate-900 tracking-tight">{value}</p>
      {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
    </div>
  );
}
