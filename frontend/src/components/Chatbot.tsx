import { useState, useRef, useEffect } from "react";
import backend from "../api/backend";

interface ChatbotProps {
  fileId: string;
  fileName: string;
  fileType: string;
  isProcessing: boolean;
  onProcessingComplete: () => void;
  onFileSelect: (fileId: string, fileName: string, fileType: string, processing: boolean) => void;
}

interface Message {
  type: "user" | "bot";
  text: string;
  timestamp?: number;
}

export default function Chatbot({ fileId, fileName, fileType, isProcessing, onProcessingComplete, onFileSelect }: ChatbotProps) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [summarizing, setSummarizing] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [processingMessageShown, setProcessingMessageShown] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Reset messages when file changes
    if (fileId) {
      setSummary("");
      setProcessingMessageShown(false);
    } else {
      // Show welcome message when no file is selected
      setMessages([
        {
          type: "bot",
          text: "Welcome! Upload a file using the 📎 button below or select a file from the right panel to get started.",
        },
      ]);
    }
  }, [fileId]);

  useEffect(() => {
    // Show processing message
    if (isProcessing && !processingMessageShown) {
      setMessages([
        {
          type: "bot",
          text: "Processing file... Please wait while I extract and analyze the content. This may take a moment.",
        },
      ]);
      setProcessingMessageShown(true);
    } else if (!isProcessing && processingMessageShown) {
      // Replace processing message with ready message
      setMessages([
        {
          type: "bot",
          text: "File processed successfully! You can now ask me questions about the content.",
        },
      ]);
      onProcessingComplete();
    }
  }, [isProcessing, processingMessageShown, onProcessingComplete]);

  useEffect(() => {
    // Load media file if it's audio or video
    if (fileType === "audio" || fileType === "video") {
      setAudioUrl(`http://127.0.0.1:8000/uploads/${fileName}`);
    }
  }, [fileName, fileType]);

  const askQuestion = async () => {
    if (!question.trim()) return;

    if (!fileId) {
      setMessages((prev) => [
        ...prev,
        { type: "user", text: question },
        { type: "bot", text: "Please upload a file first using the 📎 button or select one from the file list." },
      ]);
      setQuestion("");
      return;
    }

    const userMessage: Message = { type: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await backend.post("/qa", { file_id: fileId, question });
      const answer = res.data.answer;

      // Extract timestamp if present (looking for patterns like "at 1:23" or "timestamp: 1:23")
      const timestampMatch = answer.match(/(\d+):(\d+)/);
      let timestamp: number | undefined;
      if (timestampMatch) {
        const minutes = parseInt(timestampMatch[1]);
        const seconds = parseInt(timestampMatch[2]);
        timestamp = minutes * 60 + seconds;
      }

      const botMessage: Message = { type: "bot", text: answer, timestamp };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage: Message = {
        type: "bot",
        text: "Error: " + (error.response?.data?.detail || error.message || "Unknown error"),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const getSummary = async () => {
    if (!fileId) {
      alert("Please upload a file first.");
      return;
    }
    setSummarizing(true);
    try {
      const res = await backend.post("/qa", {
        file_id: fileId,
        question: "Please provide a comprehensive summary of this content.",
      });
      setSummary(res.data.answer);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setSummary("Error: " + (error.response?.data?.detail || error.message || "Unknown error"));
    } finally {
      setSummarizing(false);
    }
  };

  const playAtTimestamp = (timestamp: number) => {
    if (fileType === "audio" && audioRef.current) {
      audioRef.current.currentTime = timestamp;
      audioRef.current.play();
    } else if (fileType === "video" && videoRef.current) {
      videoRef.current.currentTime = timestamp;
      videoRef.current.play();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading) {
      askQuestion();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const uploadMessage: Message = {
      type: "bot",
      text: `Uploading ${file.name}...`,
    };
    setMessages((prev) => [...prev, uploadMessage]);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await backend.post("/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const uploadedFileId = res.data.file_id;
      const uploadedFileName = res.data.file_name;
      const fileTypeValue = file.type.includes("pdf") ? "pdf" : file.type.includes("audio") ? "audio" : "video";

      // Update message to show upload success
      setMessages((prev) => [...prev.slice(0, -1), { type: "bot", text: `File uploaded: ${file.name}. Processing...` }]);

      // Process the file
      await backend.post(`/process/${uploadedFileId}`);

      // Notify parent component
      onFileSelect(uploadedFileId, uploadedFileName, fileTypeValue, false);

      // Update message to show ready
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { type: "bot", text: `File processed successfully! You can now ask questions about ${file.name}.` },
      ]);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          type: "bot",
          text: "Upload error: " + (error.response?.data?.detail || error.message || "Unknown error"),
        },
      ]);
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "20px",
        borderRadius: "5px",
        backgroundColor: "#f9f9f9",
        display: "flex",
        flexDirection: "column",
        height: "100%",
      }}
    >
        <h2>AI Chatbot</h2>
        {fileId ? (
          <>
            <p>File: {fileName}</p>
            <p style={{ fontSize: "10px", opacity: "0.8" }}>{fileId}</p>
          </>
        ) : (
          <p style={{ color: "#888", fontSize: "14px" }}>No file selected - Upload or select a file to begin</p>
        )}

        {/* Media Player */}
        {(fileType === "audio" || fileType === "video") && (
          <div style={{ marginBottom: "20px", padding: "10px", backgroundColor: "#fff", borderRadius: "5px" }}>
            <h3>Media Player</h3>
            {fileType === "audio" && (
              <audio ref={audioRef} controls style={{ width: "100%" }}>
                <source src={audioUrl} type="audio/mpeg" />
              </audio>
            )}
            {fileType === "video" && (
              <video ref={videoRef} controls style={{ width: "100%", maxHeight: "400px" }}>
                <source src={audioUrl} type="video/mp4" />
              </video>
            )}
          </div>
        )}

        {/* Summary Section */}
        <div style={{ marginBottom: "20px" }}>
          <button onClick={getSummary} disabled={summarizing} style={{ padding: "10px 20px", cursor: "pointer" }}>
            {summarizing ? "Generating Summary..." : "Get Summary"}
          </button>
          {summary && (
            <div
              style={{
                marginTop: "10px",
                padding: "15px",
                backgroundColor: "#fff",
                borderRadius: "5px",
                border: "1px solid #ddd",
              }}
            >
              <h3>Summary:</h3>
              <p>{summary}</p>
            </div>
          )}
        </div>

        {/* Chat Messages */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            border: "1px solid #ddd",
            padding: "10px",
            backgroundColor: "#fff",
            borderRadius: "5px",
            marginBottom: "10px",
          }}
        >
          {messages.length === 0 && (
            <p style={{ color: "#888" }}>
              <p>Ask a question about the uploaded file...</p>
              <div style={{ marginTop: "10px", marginLeft: "20px", fontSize: "12px", color: "#666" }}>
                <p>Try asking:</p>
                <ul>
                  <li>"What is this document about?"</li>
                  <li>"Summarize the main points"</li>
                  {(fileType === "audio" || fileType === "video") && <li>"At what timestamp is [topic] discussed?"</li>}
                </ul>
              </div>
            </p>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                marginBottom: "15px",
                display: "flex",
                flexDirection: "column",
                alignItems: msg.type === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  padding: "10px",
                  borderRadius: "5px",
                  backgroundColor: msg.type === "user" ? "#007bff" : "#e9ecef",
                  color: msg.type === "user" ? "#fff" : "#000",
                  maxWidth: "80%",
                }}
              >
                <strong>{msg.type === "user" ? "You" : "AI"}:</strong>
                <p style={{ margin: "5px 0 0 0" }}>{msg.text}</p>
                {msg.timestamp !== undefined && (fileType === "audio" || fileType === "video") && (
                  <button
                    onClick={() => playAtTimestamp(msg.timestamp!)}
                    style={{
                      marginTop: "5px",
                      padding: "5px 10px",
                      cursor: "pointer",
                      backgroundColor: "#28a745",
                      color: "#fff",
                      border: "none",
                      borderRadius: "3px",
                    }}
                  >
                    ▶ Play at {Math.floor(msg.timestamp / 60)}:{(msg.timestamp % 60).toString().padStart(2, "0")}
                  </button>
                )}
              </div>
            </div>
          ))}
          {loading && <div style={{ color: "#888", fontStyle: "italic" }}>AI is thinking...</div>}
        </div>

      {/* Input Section */}
      <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
        <input ref={fileInputRef} type="file" onChange={handleFileUpload} accept=".pdf,.mp3,.wav,.mp4" style={{ display: "none" }} />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          style={{
            padding: "10px",
            cursor: uploading ? "not-allowed" : "pointer",
            backgroundColor: "#6c757d",
            color: "#fff",
            border: "none",
            borderRadius: "3px",
            fontSize: "16px",
          }}
          title="Upload a file"
        >
          {uploading ? "⏳" : "📎"}
        </button>
        {fileId && fileName && (
          <span
            style={{
              fontSize: "13px",
              color: "#333",
              background: "#e9ecef",
              borderRadius: "3px",
              padding: "4px 10px",
              maxWidth: "180px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={fileName}
          >
            {fileName}
          </span>
        )}
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question..."
          disabled={uploading}
          style={{
            flex: 1,
            padding: "10px",
            borderRadius: "3px",
            border: "1px solid #ddd",
          }}
        />
        <button
          onClick={askQuestion}
          disabled={loading || !question.trim() || uploading}
          style={{
            padding: "10px 20px",
            cursor: question.trim() && !uploading ? "pointer" : "not-allowed",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "3px",
          }}
        >
          {loading ? "..." : "Ask"}
        </button>
      </div>

      <div style={{ marginTop: "10px", fontSize: "12px", color: "#666" }}></div>
    </div>
  );
}
