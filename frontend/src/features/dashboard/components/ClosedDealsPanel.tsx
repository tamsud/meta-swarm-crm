import type { ClosedData } from '../types';

function fmt(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
  if (v >= 1_000) return `$${(v / 1_000).toFixed(0)}K`;
  return `$${v.toLocaleString()}`;
}

export function ClosedDealsPanel({ closed }: { closed: ClosedData }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-4">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Closed Deals</p>
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 bg-green-50 rounded-lg border border-green-100">
          <p className="text-xs font-medium text-green-700">Closed Won</p>
          <p className="text-xl font-semibold text-green-800 mt-1">{closed.won.count}</p>
          <p className="text-xs text-green-600 mt-0.5">{fmt(closed.won.value)}</p>
        </div>
        <div className="p-3 bg-red-50 rounded-lg border border-red-100">
          <p className="text-xs font-medium text-red-700">Closed Lost</p>
          <p className="text-xl font-semibold text-red-800 mt-1">{closed.lost.count}</p>
          <p className="text-xs text-red-600 mt-0.5">{fmt(closed.lost.value)}</p>
        </div>
      </div>
    </div>
  );
}
