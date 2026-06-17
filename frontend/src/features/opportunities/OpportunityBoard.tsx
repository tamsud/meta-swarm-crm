import { useDroppable } from '@dnd-kit/core';
import { DndContext, DragOverlay } from '@dnd-kit/core';
import type { DragEndEvent, DragStartEvent } from '@dnd-kit/core';
import { useState, useMemo } from 'react';
import { OpportunityCard } from './OpportunityCard';
import type { Opportunity, OpportunityStage } from './types';
import { STAGE_ORDER, STAGE_LABELS, STAGE_COLORS } from './types';
import type { Account } from '../accounts/types';

interface StageColumnProps {
  stage: OpportunityStage;
  opportunities: Opportunity[];
  accounts: Map<number, Account>;
  onOpportunityClick?: (opp: Opportunity) => void;
}

function StageColumn({ stage, opportunities, accounts, onOpportunityClick }: StageColumnProps) {
  const { setNodeRef, isOver } = useDroppable({
    id: stage,
  });

  const totalValue = useMemo(() => {
    return opportunities.reduce((sum, opp) => {
      if (opp.value) {
        return sum + parseFloat(opp.value);
      }
      return sum;
    }, 0);
  }, [opportunities]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div
      ref={setNodeRef}
      className={`flex-1 min-w-[280px] max-w-[320px] bg-slate-50 rounded-lg p-3 ${
        isOver ? 'ring-2 ring-indigo-400 ring-inset' : ''
      }`}
    >
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <span
            className={`px-2 py-0.5 rounded text-xs font-medium border ${STAGE_COLORS[stage]}`}
          >
            {STAGE_LABELS[stage]}
          </span>
          <span className="text-xs font-medium text-slate-500">{opportunities.length}</span>
        </div>
        <div className="text-sm font-semibold text-slate-700">{formatCurrency(totalValue)}</div>
      </div>

      <div className="space-y-2 min-h-[200px]">
        {opportunities.map((opp) => (
          <OpportunityCard
            key={opp.id}
            opportunity={opp}
            accountName={accounts.get(opp.account_id)?.name}
            onClick={() => onOpportunityClick?.(opp)}
          />
        ))}
      </div>
    </div>
  );
}

interface OpportunityBoardProps {
  opportunities: Opportunity[];
  accounts: Account[];
  onStageChange: (opportunityId: number, newStage: OpportunityStage) => void;
  onOpportunityClick?: (opp: Opportunity) => void;
}

export function OpportunityBoard({
  opportunities,
  accounts,
  onStageChange,
  onOpportunityClick,
}: OpportunityBoardProps) {
  const [activeId, setActiveId] = useState<number | null>(null);

  const accountsMap = useMemo(() => {
    return new Map(accounts.map((acc) => [acc.id, acc]));
  }, [accounts]);

  const opportunitiesByStage = useMemo(() => {
    const grouped: Record<OpportunityStage, Opportunity[]> = {
      prospecting: [],
      proposal: [],
      negotiation: [],
      closed_won: [],
      closed_lost: [],
    };

    opportunities.forEach((opp) => {
      grouped[opp.stage].push(opp);
    });

    return grouped;
  }, [opportunities]);

  const activeOpportunity = useMemo(() => {
    if (activeId === null) return null;
    return opportunities.find((o) => o.id === activeId) || null;
  }, [activeId, opportunities]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (over && over.id !== active.data.current?.stage) {
      onStageChange(active.id as number, over.id as OpportunityStage);
    }
  };

  return (
    <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto pb-4">
        {STAGE_ORDER.map((stage) => (
          <StageColumn
            key={stage}
            stage={stage}
            opportunities={opportunitiesByStage[stage]}
            accounts={accountsMap}
            onOpportunityClick={onOpportunityClick}
          />
        ))}
      </div>

      <DragOverlay>
        {activeOpportunity && (
          <div className="opacity-80">
            <OpportunityCard
              opportunity={activeOpportunity}
              accountName={accountsMap.get(activeOpportunity.account_id)?.name}
            />
          </div>
        )}
      </DragOverlay>
    </DndContext>
  );
}
