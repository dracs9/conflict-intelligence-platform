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
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Analyzing conversation...</p>
      </div>
    );
  }

  if (!pipeline) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 text-center">
        <p className="text-gray-600">No analysis available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 Analysis Pipeline</h2>

        {pipeline.pipeline.map((turn: any, idx: number) => (
          <motion.div
            key={turn.turn_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="mb-8 last:mb-0"
          >
            <div className="flex items-center gap-2 mb-3">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                turn.speaker === 'user'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-purple-100 text-purple-800'
              }`}>
                {turn.speaker === 'user' ? '👤 You' : '👥 Other'}
              </span>
              <span className="text-gray-500 text-sm">Turn {turn.turn_id + 1}</span>
            </div>

            <div className="flex items-start gap-4 overflow-x-auto pb-4">
              {turn.stages.map((stage: any, stageIdx: number) => (
                <div key={stageIdx} className="flex items-center gap-4 min-w-fit">
                  <PipelineStage stage={stage} />
                  {stageIdx < turn.stages.length - 1 && (
                    <ArrowRight className="w-6 h-6 text-gray-400 flex-shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Recommendations */}
      {pipeline.recommendations && pipeline.recommendations.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            💡 Recommendations
          </h3>
          <div className="space-y-3">
            {pipeline.recommendations.map((rec: any, idx: number) => (
              <div
                key={idx}
                className={`p-4 rounded-lg border-l-4 ${
                  rec.priority === 'high'
                    ? 'bg-red-50 border-red-500'
                    : rec.priority === 'medium'
                    ? 'bg-yellow-50 border-yellow-500'
                    : rec.priority === 'critical'
                    ? 'bg-purple-50 border-purple-500'
                    : 'bg-green-50 border-green-500'
                }`}
              >
                <div className="font-medium text-gray-900">{rec.action}</div>
                <div className="text-sm text-gray-600 mt-1">{rec.description}</div>
                <div className="text-xs text-gray-500 mt-1">
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
    <div className="bg-gray-50 rounded-lg p-4 min-w-[200px] max-w-[250px]">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{getIcon()}</span>
        <div className="font-medium text-gray-900 text-sm">{stage.label}</div>
      </div>
      
      <div className="text-xs text-gray-700 break-words">
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
