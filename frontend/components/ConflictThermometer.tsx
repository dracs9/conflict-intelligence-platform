import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface ConflictThermometerProps {
  conflictScore: number;
  escalationProbability: number;
  trend: string;
}

export default function ConflictThermometer({
  conflictScore,
  escalationProbability,
  trend,
}: ConflictThermometerProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'escalating':
        return <TrendingUp className="w-5 h-5 text-red-600" />;
      case 'de-escalating':
        return <TrendingDown className="w-5 h-5 text-green-600" />;
      default:
        return <Minus className="w-5 h-5 text-gray-600" />;
    }
  };

  const getWarningLevel = () => {
    if (conflictScore < 0.3) return { label: 'Safe', color: 'green' };
    if (conflictScore < 0.6) return { label: 'Caution', color: 'yellow' };
    return { label: 'Danger', color: 'red' };
  };

  const warning = getWarningLevel();

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          🌡️ Conflict Thermometer
          {getTrendIcon()}
        </h2>
        <span
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            warning.color === 'green'
              ? 'bg-green-100 text-green-800'
              : warning.color === 'yellow'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {warning.label}
        </span>
      </div>

      {/* Thermometer Bar */}
      <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
        <div className="absolute inset-0 thermometer-gradient opacity-30" />
        <motion.div
          className={`absolute left-0 top-0 h-full ${
            warning.color === 'green'
              ? 'bg-green-500'
              : warning.color === 'yellow'
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
          initial={{ width: 0 }}
          animate={{ width: `${conflictScore * 100}%` }}
          transition={{ duration: 0.5 }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-gray-900">
            {(conflictScore * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600">Conflict Intensity</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {(conflictScore * 100).toFixed(0)}%
          </div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 flex items-center gap-1">
            <AlertTriangle className="w-4 h-4" />
            Escalation Risk
          </div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {(escalationProbability * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Trend */}
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <div className="text-sm text-blue-800">
          <strong>Trend:</strong> {trend === 'escalating' ? 'Escalating ⬆️' : trend === 'de-escalating' ? 'De-escalating ⬇️' : 'Stable ➡️'}
        </div>
      </div>
    </div>
  );
}
