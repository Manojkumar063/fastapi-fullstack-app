import { useState, useRef, useEffect } from "react";
import api from "../api";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleUpload(e) {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus("");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await api.post("/chat/upload", form);
      setUploadStatus(res.data.message);
    } catch (err) {
      setUploadStatus(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await api.post("/chat/message", { question });
      setMessages((prev) => [...prev, { role: "bot", text: res.data.answer }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: err.response?.data?.detail || "Error getting response" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    await api.delete("/chat/reset");
    setMessages([]);
    setUploadStatus("");
  }

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", fontFamily: "sans-serif", display: "flex", flexDirection: "column", height: "90vh" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <h2 style={{ margin: 0 }}>RAG Chatbot</h2>
        <button onClick={handleReset} style={{ background: "#e74c3c", color: "#fff", border: "none", padding: "6px 14px", borderRadius: 6, cursor: "pointer" }}>
          Reset
        </button>
      </div>

      <div style={{ marginBottom: 12 }}>
        <label style={{ cursor: "pointer", background: "#2980b9", color: "#fff", padding: "7px 16px", borderRadius: 6 }}>
          {uploading ? "Uploading…" : "📎 Upload Document (PDF / TXT)"}
          <input type="file" accept=".pdf,.txt" onChange={handleUpload} style={{ display: "none" }} disabled={uploading} />
        </label>
        {uploadStatus && <span style={{ marginLeft: 12, fontSize: 13, color: "#27ae60" }}>{uploadStatus}</span>}
      </div>

      <div style={{ flex: 1, overflowY: "auto", border: "1px solid #ddd", borderRadius: 8, padding: 16, background: "#f9f9f9" }}>
        {messages.length === 0 && (
          <p style={{ color: "#aaa", textAlign: "center", marginTop: 60 }}>Upload a document and start chatting!</p>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", marginBottom: 10 }}>
            <div style={{
              maxWidth: "75%", padding: "10px 14px", borderRadius: 12,
              background: m.role === "user" ? "#2980b9" : "#fff",
              color: m.role === "user" ? "#fff" : "#333",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              whiteSpace: "pre-wrap",
            }}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: "flex", justifyContent: "flex-start", marginBottom: 10 }}>
            <div style={{ padding: "10px 14px", borderRadius: 12, background: "#fff", color: "#999", boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}>
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask something about your document…"
          style={{ flex: 1, padding: "10px 14px", borderRadius: 8, border: "1px solid #ccc", fontSize: 15 }}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ padding: "10px 20px", borderRadius: 8, background: "#27ae60", color: "#fff", border: "none", cursor: "pointer", fontSize: 15 }}>
          Send
        </button>
      </form>
    </div>
  );
}
