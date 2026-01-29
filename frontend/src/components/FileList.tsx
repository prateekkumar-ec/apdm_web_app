import { useState, useEffect } from "react";
import backend from "../api/backend";

interface FileItem {
  file_id: string;
  original_name: string;
  file_type: string;
  uploaded_at: string;
  status: string;
}

interface FileListProps {
  onSelectFile: (fileId: string, fileName: string, fileType: string, processing?: boolean) => void;
  currentFileId: string;
}

export default function FileList({ onSelectFile, currentFileId }: FileListProps) {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchFiles = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await backend.get("/files");
      setFiles(res.data.files);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setError("Error loading files: " + (error.response?.data?.detail || error.message || "Unknown error"));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
    // Refresh every 5 seconds
    const interval = setInterval(fetchFiles, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileClick = async (file: FileItem) => {
    // Get the stored filename from backend
    let fileName = file.original_name;
    try {
      const res = await backend.get(`/files/${file.file_id}`);
      const storedPath = res.data.stored_path;
      fileName = file.original_name || storedPath.split("/").pop();
    } catch {
      // Fallback to original name
    }

    const needsProcessing = file.status === "uploaded";

    // Immediately select the file and show processing state if needed
    onSelectFile(file.file_id, fileName, file.file_type, needsProcessing);

    // Process in background if needed
    if (needsProcessing) {
      try {
        await backend.post(`/process/${file.file_id}`);
        // Refresh the file list
        await fetchFiles();
        // Notify that processing is complete by re-selecting with processing=false
        onSelectFile(file.file_id, fileName, file.file_type, false);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } }; message?: string };
        console.error("Error processing file:", error);
        // Still notify completion even on error
        onSelectFile(file.file_id, fileName, file.file_type, false);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const getFileIcon = (fileType: string) => {
    switch (fileType) {
      case "pdf":
        return "📄";
      case "audio":
        return "🎵";
      case "video":
        return "🎬";
      default:
        return "📎";
    }
  };

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "20px",
        borderRadius: "5px",
        backgroundColor: "#f9f9f9",
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px" }}>
        <h2 style={{ margin: 0 }}>Recent Files</h2>
        <button onClick={fetchFiles} style={{ padding: "5px 10px", cursor: "pointer", fontSize: "12px" }} title="Refresh list">
          🔄
        </button>
      </div>

      {loading && files.length === 0 && <p style={{ color: "#888" }}>Loading files...</p>}

      {error && <p style={{ color: "#d00", padding: "10px", backgroundColor: "#ffe6e6", borderRadius: "3px" }}>{error}</p>}

      <div
        style={{
          flex: 1,
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        {files.length === 0 && !loading && <p style={{ color: "#888" }}>No files uploaded yet</p>}

        {files.map((file) => (
          <div
            key={file.file_id}
            onClick={() => handleFileClick(file)}
            style={{
              padding: "12px",
              backgroundColor: currentFileId === file.file_id ? "#e3f2fd" : "#fff",
              border: currentFileId === file.file_id ? "2px solid #007bff" : "1px solid #ddd",
              borderRadius: "5px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              if (currentFileId !== file.file_id) {
                e.currentTarget.style.backgroundColor = "#f5f5f5";
              }
            }}
            onMouseLeave={(e) => {
              if (currentFileId !== file.file_id) {
                e.currentTarget.style.backgroundColor = "#fff";
              }
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "5px" }}>
              <span style={{ fontSize: "20px" }}>{getFileIcon(file.file_type)}</span>
              <strong
                style={{
                  fontSize: "14px",
                  flex: 1,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {file.original_name}
              </strong>
            </div>
            <div style={{ fontSize: "11px", color: "#666", marginLeft: "28px" }}>
              <div>Type: {file.file_type.toUpperCase()}</div>
              <div>Uploaded: {formatDate(file.uploaded_at)}</div>
              <div>
                Status:
                <span
                  style={{
                    marginLeft: "5px",
                    padding: "2px 6px",
                    borderRadius: "3px",
                    backgroundColor: file.status === "uploaded" ? "#fff3cd" : "#d4edda",
                    color: file.status === "uploaded" ? "#856404" : "#155724",
                    fontSize: "10px",
                    fontWeight: "bold",
                  }}
                >
                  {file.status === "uploaded" ? "Not Processed" : "Ready"}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          marginTop: "10px",
          padding: "10px",
          backgroundColor: "#e9ecef",
          borderRadius: "3px",
          fontSize: "12px",
          color: "#555",
        }}
      >
        💡 Click on a file to use it with the chatbot
      </div>
    </div>
  );
}
