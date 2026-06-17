import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { StageBreakdown } from '../types';

const STAGE_COLORS: Record<string, string> = {
  prospecting: '#6366f1',
  proposal: '#8b5cf6',
  negotiation: '#f59e0b',
  closed_won: '#10b981',
  closed_lost: '#ef4444',
};

const STAGE_LABELS: Record<string, string> = {
  prospecting: 'Prospect',
  proposal: 'Proposal',
  negotiation: 'Negotiate',
  closed_won: 'Won',
  closed_lost: 'Lost',
};

interface PipelineBarChartProps {
  stages: StageBreakdown[];
}

export function PipelineBarChart({ stages }: PipelineBarChartProps) {
  const data = stages.map((s) => ({
    name: STAGE_LABELS[s.stage] ?? s.stage,
    count: s.count,
    color: STAGE_COLORS[s.stage] ?? '#94a3b8',
  }));

  if (data.every((d) => d.count === 0)) {
    return (
      <div className="bg-white rounded-xl border border-slate-100 p-4">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Pipeline by Stage</p>
        <div className="flex items-center justify-center h-32 text-slate-400 text-sm">No opportunities yet</div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-100 p-4">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-3">Pipeline by Stage</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barSize={28}>
          <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} width={24} />
          <Tooltip
            formatter={(v) => [v, 'Count']}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e2e8f0' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
