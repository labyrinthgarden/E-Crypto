import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { text: input, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:5000/api/chat",
        { message: input },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const aiMessage = { text: res.data.response, sender: "ai" };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        text: "⚠️ Error al conectar con la IA",
        sender: "ai",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white p-4 shadow-lg">
        <div className="container mx-auto flex items-center">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold">AI Assistant</h1>
            <p className="text-xs opacity-80">{isLoading ? "Typing..." : "Online"}</p>
          </div>
        </div>
      </header>

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="container mx-auto max-w-3xl">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex mb-4 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 transition-all duration-200 ${msg.sender === "user"
                  ? "bg-indigo-600 text-white rounded-br-none shadow-md hover:shadow-lg"
                  : "bg-white text-gray-800 rounded-bl-none shadow-sm hover:shadow-md border border-gray-100"
                  }`}
              >
                <p className="text-sm">{msg.text}</p>
                <div className={`text-xs mt-1 opacity-60 flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                  {msg.sender === "user" ? "You" : "AI"}
                </div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-white text-gray-800 rounded-2xl rounded-bl-none p-4 shadow-sm max-w-[80%]">
                <div className="flex space-x-2 items-center">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-100"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Barra de envío */}
      <form
        onSubmit={handleSubmit}
        className="bg-white border-t border-gray-200 p-4 shadow-inner"
      >
        <div className="container mx-auto max-w-3xl flex">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe un mensaje..."
            className="flex-1 p-3 rounded-l-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-5 rounded-r-xl hover:opacity-90 disabled:opacity-50 transition-all duration-200 flex items-center justify-center"
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default App;
