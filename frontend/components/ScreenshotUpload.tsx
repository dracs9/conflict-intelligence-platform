import { useState } from 'react';
import { Upload, Image as ImageIcon } from 'lucide-react';
import { ocrApi } from '../services/api';
import { motion } from 'framer-motion';

interface ScreenshotUploadProps {
  userId: string;
  onUploadSuccess: (sessionId: number) => void;
}

export default function ScreenshotUpload({ userId, onUploadSuccess }: ScreenshotUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Please upload an image file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const result = await ocrApi.uploadScreenshot(userId, file);
      onUploadSuccess(result.session_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to process screenshot');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="analysis-card p-6">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-700 to-blue-700 flex items-center justify-center flex-shrink-0 shadow-md text-white">
          <ImageIcon className="w-6 h-6 text-white" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white mb-2">
            📸 Upload Chat Screenshot
          </h3>
          <p className="text-sm text-gray-300 mb-4">
            Upload a screenshot of your conversation and we'll extract and analyze it automatically
          </p>

          <label className="cursor-pointer">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              disabled={uploading}
              className="hidden"
            />
            <div className={`flex items-center justify-center gap-2 px-6 py-3 bg-transparent border-2 border-dashed border-purple-600 rounded-lg hover:border-purple-400 hover:bg-white/5 text-gray-200 ${
              uploading ? 'opacity-50 cursor-not-allowed' : ''
            }`}>
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                  <span className="font-medium text-gray-200">Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 text-white" />
                  <span className="font-medium text-gray-200">Choose Image</span>
                </>
              )}
            </div>
          </label>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 p-3 bg-red-900/30 border border-red-700 rounded-lg text-sm text-red-300"
            >
              {error}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
