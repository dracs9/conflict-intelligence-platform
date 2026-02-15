import { useEffect, useState } from 'react';
import { analysisApi } from '../services/api';
import { motion } from 'framer-motion';
import { ArrowRight, Brain, AlertCircle, Heart, TrendingUp, CheckCircle } from 'lucide-react';

interface AnalysisPipelineProps {
  sessionId: number;
}

export default function AnalysisPipeline({ sessionId }: AnalysisPipelineProps) {
  const [pipeline, setPipeline] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPipeline();
  }, [sessionId]);

  const loadPipeline = async () => {
    try {
      const data = await analysisApi.getPipeline(sessionId);
      setPipeline(data);
    } catch (error) {
      console.error('Failed to load pipeline:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="analysis-card p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-300">Analyzing conversation...</p>
      </div>
    );
  }

  if (!pipeline) {
    return (
      <div className="analysis-card p-8 text-center">
        <p className="text-gray-300">No analysis available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="analysis-card p-6">
        <h2 className="text-2xl font-bold text-white mb-6">📊 Analysis Pipeline</h2>

        {pipeline.pipeline.map((turn: any, idx: number) => (
          <motion.div
            key={turn.turn_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="mb-8 last:mb-0"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium border border-white/10 ${
                turn.speaker === 'user' ? 'text-blue-300' : 'text-purple-300'
              }`}>
                {turn.speaker === 'user' ? '👤 You' : '👥 Other'}
              </span>
              <span className="text-gray-400 text-sm">Turn {turn.turn_id + 1}</span>
            </div>

            <div className="flex items-start gap-4 overflow-x-auto pb-4">
              {turn.stages.map((stage: any, stageIdx: number) => (
                <div key={stageIdx} className="flex items-center gap-4 min-w-fit">
                  <PipelineStage stage={stage} />
                  {stageIdx < turn.stages.length - 1 && (
                    <ArrowRight className="w-6 h-6 text-white/40 flex-shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recommendations */}
      {pipeline.recommendations && pipeline.recommendations.length > 0 && (
        <div className="analysis-card p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            💡 Recommendations
          </h3>
          <div className="space-y-3">
            {pipeline.recommendations.map((rec: any, idx: number) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-l-4 ${
                  rec.priority === 'high'
                    ? 'bg-red-900/20 border-red-500/40 text-red-300'
                    : rec.priority === 'medium'
                    ? 'bg-yellow-900/20 border-yellow-500/40 text-yellow-300'
                    : rec.priority === 'critical'
                    ? 'bg-purple-900/20 border-purple-500/40 text-purple-300'
                    : 'bg-green-900/20 border-green-500/40 text-green-300'
                }`}
              >
                <div className="font-medium text-white">{rec.action}</div>
                <div className="text-sm text-gray-300 mt-1">{rec.description}</div>
                <div className="text-xs text-gray-400 mt-1">
                  {rec.category} · {rec.priority} priority
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function PipelineStage({ stage }: { stage: any }) {
  const getIcon = () => {
    switch (stage.stage) {
      case 'input':
        return '💬';
      case 'emotion':
        return '😊';
      case 'bias':
        return '🧠';
      case 'nvc':
        return '❤️';
      case 'risk':
        return '⚠️';
      default:
        return '•';
    }
  };

  return (
    <div className="analysis-item min-w-[200px] max-w-[250px]">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{getIcon()}</span>
        <div className="font-medium text-white text-sm">{stage.label}</div>
      </div>
      
      <div className="text-xs text-gray-300 break-words">
        {typeof stage.content === 'string' ? (
          <div className="line-clamp-3">{stage.content}</div>
        ) : typeof stage.content === 'object' && stage.content !== null ? (
          <div className="space-y-1">
            {Object.entries(stage.content).slice(0, 3).map(([key, value]: [string, any]) => (
              <div key={key}>
                <span className="font-medium">{key}:</span>{' '}
                {typeof value === 'number' ? value.toFixed(2) : Array.isArray(value) ? value.length : String(value)}
              </div>
            ))}
          </div>
        ) : (
          <div>-</div>
        )}
      </div>
    </div>
  );
}
