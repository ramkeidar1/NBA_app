import { useState } from 'react';
import type { OrchestratorRecommendation } from '../../types/recommendation';

interface BetFormProps {
  rec: OrchestratorRecommendation;
}

function formatGameName(raw: string): string {
  return raw.replace(/_/g, ' ');
}

export default function BetForm({ rec }: BetFormProps) {
  const [deposit, setDeposit] = useState('');

  const parsed = parseFloat(deposit);
  const isValid = isFinite(parsed) && parsed > 0;
  const totalWin = isValid ? parsed * rec.expectedValue : null;

  return (
    <div className="pb-panel">
      <span className="pb-game-label">{formatGameName(rec.name)}</span>

      <div className="pb-divider" />

      <div className="pb-field-group">
        <span className="pb-label">Deposit Amount ($)</span>
        <input
          className="pb-input"
          type="number"
          min="0"
          step="any"
          placeholder="0.00"
          value={deposit}
          onChange={(e) => setDeposit(e.target.value)}
        />
      </div>

      <div className="pb-display-row pb-display-row--ev">
        <span className={`pb-display-value pb-display-value--ev`}>
          +{rec.expectedValue.toFixed(2)}
        </span>
        <span className="pb-display-label">Expected Value (multiplier)</span>
      </div>

      <div className="pb-display-row pb-display-row--win">
        <span className={`pb-display-value ${totalWin !== null ? 'pb-display-value--win' : 'pb-display-value--dim'}`}>
          {totalWin !== null ? `$${totalWin.toFixed(2)}` : '—'}
        </span>
        <span className="pb-display-label">Total Expected Win</span>
      </div>
    </div>
  );
}
