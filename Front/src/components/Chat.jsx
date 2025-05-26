import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function Chat() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleOptionClick = async (option) => {
    const userMessage = { text: option, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const API_URL = "http://localhost:8000/option/";

    try {
      const res = await axios.post(API_URL,
        { message: option },
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
        text: "⚠️ Error al conectar con el servidor",
        sender: "ai",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans relative">
      {/* Fondo de imagen para toda la pantalla */}
      <div className="absolute inset-0 bg-[url('src/assets/background.png')] bg-cover bg-center z-0"></div>

      {/* Header con transparencia */}
      <header className="relative z-10 bg-purple-800/50 backdrop-blur-sm text-white p-4 shadow-lg">
        <div className="container mx-auto flex items-center">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mr-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <div>
            <h1 className="text-2xl font-bold">E-Crypto</h1>
            <p className="text-base opacity-80">{isLoading ? "Typing..." : "Online"}</p>
          </div>
        </div>
      </header>

      {/* Contenedor principal */}
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        {/* Área de mensajes con transparencia - padding reducido */}
        <div className="flex-1 overflow-y-auto px-1 py-1">
          <div className="container mx-auto max-w-8/9">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex mb-2 ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[95%] rounded-2xl p-3 transition-all duration-200 ${
                    msg.sender === "user"
                      ? "bg-purple-700/30 text-white rounded-br-none shadow-md hover:shadow-lg border border-gray-200/50 backdrop-blur-sm"
                      : "bg-black/40 text-white rounded-bl-none shadow-sm hover:shadow-md border border-gray-200/50 backdrop-blur-sm"
                  }`}
                >
                  <p className="text-xl">{msg.text}</p>
                  <div className={`text-[0.65rem] mt-1 opacity-60 flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                    {msg.sender === "user" ? "You" : "AI"}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start mb-2">
                <div className="bg-black/40 text-xl backdrop-blur-sm border border-gray-50 text-gray-800 rounded-2xl rounded-bl-none p-3 shadow-sm max-w-[80%]">
                  <div className="flex space-x-2 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></div>
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse delay-100"></div>
                    <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Barra de opciones fija en la parte inferior con transparencia */}
        <div className="sticky bottom-0 bg-black/15 backdrop-blur-sm p-3">
          <div className="container mx-auto max-w-[90%] flex flex-wrap justify-center gap-2">
            <button
              onClick={() => !isLoading && handleOptionClick("Cual es tu mejor prediccion en este momento?")}
              disabled={isLoading}
              className="px-4 py-2 text-s bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 disabled:opacity-50 transition-all duration-200 backdrop-blur-sm"
            >Cual es tu mejor prediccion en este momento?</button>
            <button
              onClick={() => !isLoading && handleOptionClick("Que me recomiendas segun el comportamiendo de los ultimos 4 meses?")}
              disabled={isLoading}
              className="px-4 py-2 text-s bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 disabled:opacity-50 transition-all duration-200 backdrop-blur-sm"
            >Que me recomiendas segun el comportamiendo de los ultimos 4 meses?</button>
            <button
              onClick={() => !isLoading && handleOptionClick("Que me recomiendas en un largo plazo?")}
              disabled={isLoading}
              className="px-4 py-2 text-s bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 disabled:opacity-50 transition-all duration-200 backdrop-blur-sm"
            >Que me recomiendas en un largo plazo?</button>
            <button
              onClick={() => !isLoading && handleOptionClick("Que me recomiendas en un corto plazo?")}
              disabled={isLoading}
              className="px-4 py-2 text-s bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 disabled:opacity-50 transition-all duration-200 backdrop-blur-sm"
            >Que me recomiendas en un corto plazo?</button>
            <button
              onClick={() => !isLoading && handleOptionClick("Hablame de las cotizaciones en este momento")}
              disabled={isLoading}
              className="px-4 py-2 text-s bg-gradient-to-r from-indigo-600/90 to-purple-600/90 text-white rounded-xl flex items-center justify-center shadow-lg hover:opacity-90 disabled:opacity-50 transition-all duration-200 backdrop-blur-sm"
            >Hablame de las cotizaciones en este momento</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Chat;
