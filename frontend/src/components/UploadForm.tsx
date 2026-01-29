import { useState } from "react";
import backend from "../api/backend";

interface UploadFormProps {
  onUpload: (fileId: string, fileName: string, fileType: string) => void;
}

export default function UploadForm({ onUpload }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [fileId, setFileId] = useState<string>("");
  const [uploadedFileName, setUploadedFileName] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");

  const uploadFile = async () => {
    if (!file) return;
    setUploading(true);
    setMessage("");
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await backend.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setFileId(res.data.file_id);
      setUploadedFileName(res.data.file_name);
      setMessage("File uploaded! Click 'Process File' to extract content.");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setMessage("Upload error: " + (error.response?.data?.detail || error.message || "Unknown error"));
    } finally {
      setUploading(false);
    }
  };

  const processFile = async () => {
    if (!fileId || !file) return;
    setProcessing(true);
    setMessage("Processing file...");
    try {
      await backend.post(`/process/${fileId}`);
      const fileType = file.type.includes("pdf") ? "pdf" : 
                       file.type.includes("audio") ? "audio" : "video";
      onUpload(fileId, uploadedFileName, fileType);
      setMessage("File processed successfully! You can now ask questions.");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setMessage("Processing error: " + (error.response?.data?.detail || error.message || "Unknown error"));
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div style={{ 
      border: "1px solid #ccc", 
      padding: "20px", 
      borderRadius: "5px",
      backgroundColor: "#f9f9f9"
    }}>
      <h2>Upload File</h2>
      <p>Supported: PDF, MP3, WAV, MP4</p>
      
      <div style={{ display: "flex", gap: "10px", alignItems: "center", marginTop: "10px" }}>
        <input 
          type="file" 
          onChange={(e) => {
            setFile(e.target.files?.[0] || null);
            setFileId("");
            setMessage("");
          }}
          accept=".pdf,.mp3,.wav,.mp4"
        />
        <button 
          onClick={uploadFile} 
          disabled={uploading || !file}
          style={{ padding: "8px 16px", cursor: file ? "pointer" : "not-allowed" }}
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>

        {fileId && (
          <button 
            onClick={processFile} 
            disabled={processing}
            style={{ padding: "8px 16px", cursor: "pointer" }}
          >
            {processing ? "Processing..." : "Process File"}
          </button>
        )}
      </div>

      {message && (
        <p style={{ 
          marginTop: "10px", 
          padding: "10px", 
          backgroundColor: message.includes("error") ? "#ffe6e6" : "#e6ffe6",
          borderRadius: "3px"
        }}>
          {message}
        </p>
      )}
    </div>
  );
}
