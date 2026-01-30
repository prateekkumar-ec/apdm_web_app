import { useState } from "react";
import Chatbot from "./components/Chatbot";
import FileList from "./components/FileList";
import "./App.css";

export default function App() {
  const [fileId, setFileId] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [fileType, setFileType] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingError, setProcessingError] = useState<{ error: boolean; message: string }>({ error: false, message: "" });

  const handleSelectFile = (id: string, name: string, type: string, processing: boolean = false) => {
    const isNewFile = id !== fileId;
    console.log("Selected file:", { id, fileId, name, type, processing, isNewFile });

    setFileId(id);
    setFileName(name);
    setFileType(type);
    setIsProcessing(processing);

    // ✅ clear error ONLY when a new processing starts
    if (processing) {
      setProcessingError({ error: false, message: "" });
    }
  };


  return (
    <div style={{ padding: "20px", height: "100vh", display: "flex", flexDirection: "column" }}>
      <h1 style={{ marginBottom: "20px" }}>AI Document & Multimedia Q&A</h1>

      <div
        style={{
          display: "flex",
          gap: "20px",
          flex: 1,
          minHeight: 0,
        }}
      >
        {/* Left Pane - Upload and Chat */}
        <div
          style={{
            flex: "2",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            minWidth: "500px",
            height: "100%",
            overflow: "auto",
          }}
        >
          <Chatbot
            fileId={fileId}
            fileName={fileName}
            fileType={fileType}
            isProcessing={isProcessing}
            onProcessingComplete={() => setIsProcessing(false)}
            onFileSelect={handleSelectFile}
            processingError={processingError}
          />
        </div>

        {/* Right Pane - File List */}
        <div
          style={{
            flex: "1",
            minWidth: "300px",
            maxWidth: "400px",
            overflow: "hidden",
          }}
        >
          <FileList onSelectFile={handleSelectFile} currentFileId={fileId} setProcessingError={setProcessingError} />
        </div>
      </div>
    </div>
  );
}
