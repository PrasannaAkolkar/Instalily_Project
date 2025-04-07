import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessageStream } from "../api/api";
import { marked } from "marked";
import partSelectLogo from "../PartSelectLogo.svg";

function ChatWindow() {
  const defaultMessage = [{
    role: "assistant",
    content: "👋 Welcome to **PartSelect Assistant**! I can help you install parts, check compatibility, and troubleshoot appliances. Just ask away!"
  }];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [hasStartedTyping, setHasStartedTyping] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendSystemMessage = async (input) => {
    const userMsg = { role: "user", content: input };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setIsThinking(true);
    setHasStartedTyping(false);

    let assistantMsg = { role: "assistant", content: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    await getAIMessageStream(input, newMessages, (streamedText) => {
      if (!hasStartedTyping) setHasStartedTyping(true);
      assistantMsg.content = streamedText;
      setMessages((prev) => [...prev.slice(0, -1), { ...assistantMsg }]);
    });

    setIsThinking(false);
    setHasStartedTyping(false);
  };

  const handleSend = async (input) => {
    if (input.trim() === "") return;
    await sendSystemMessage(input);
    setInput("");
  };

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <div className={`chat-container ${darkMode ? "dark-mode" : ""}`}>
      <div className="chat-header">
        <img src={partSelectLogo} alt="PartSelect" className="logo" />
        <h2>PartSelect Assistant</h2>
        <div className="header-buttons">
          <button onClick={toggleDarkMode}>{darkMode ? "🌞" : "🌙"}</button>
          <button onClick={() => setMessages(defaultMessage)}>🔁 Reset</button>
          <button onClick={() => sendSystemMessage("Summarize our conversation so far")}>📋 Summary</button>
        </div>
      </div>

      <div className="messages-container">
        {messages.map((msg, idx) => (
          <div key={idx} className={`${msg.role}-message-container`}>
            <div className={`message ${msg.role}-message`}>
              <div
                dangerouslySetInnerHTML={{
                  __html: marked(
                    Array.isArray(msg.content) ? msg.content.join("\n\n") : msg.content
                  ).replace(/<p>|<\/p>/g, "")
                }}
              ></div>
            </div>
          </div>
        ))}

        {(isThinking || hasStartedTyping) && (
          <div className="typing-indicator">
            {hasStartedTyping ? "Assistant is typing" : "Assistant is thinking"}
            <span className="dot">.</span><span className="dot">.</span><span className="dot">.</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about an appliance part..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend(input);
              e.preventDefault();
            }
          }}
        />
        <button className="send-button" onClick={() => handleSend(input)}>Ask</button>
      </div>
    </div>
  );
}

export default ChatWindow;
