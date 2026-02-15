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
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-xl shadow-lg p-6 border border-purple-200">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
          <ImageIcon className="w-6 h-6 text-purple-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            📸 Upload Chat Screenshot
          </h3>
          <p className="text-sm text-gray-600 mb-4">
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
            <div className={`flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-dashed border-purple-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all ${
              uploading ? 'opacity-50 cursor-not-allowed' : ''
            }`}>
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600" />
                  <span className="font-medium text-gray-700">Processing...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 text-purple-600" />
                  <span className="font-medium text-gray-700">Choose Image</span>
                </>
              )}
            </div>
          </label>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700"
            >
              {error}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
