import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, Navigate } from "react-router-dom";
import Lottie from "lottie-react";
import splashAnimation from "./assets/splash.json";
import Chat from "./components/Chat";

function HomeScreen() {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-center flex-col h-screen bg-[url('assets/background.png')] bg-cover bg-center font-sans">
      <h1 className="text-2xl font-bold text-white mb-8">E-Crypto</h1>
      <p className="text-white bg-black/35 p-6 rounded-xl text-sm leading-relaxed shadow-lg mb-30 max-w-2xl text-center">
        Asistente de inversión en criptomonedas impulsado por IA, que analiza datos en tiempo real
        mediante web scraping para ofrecer recomendaciones precisas. Utilizando noticias, tendencias sociales
        y datos de mercado para identificar oportunidades y riesgos, ayudando a usuarios a tomar decisiones
        informadas con lenguaje claro y accesible.
      </p>
      <button
        className="px-8 py-4 bg-purple-800 text-white rounded-lg text-sm font-semibold shadow hover:bg-purple-700 transition border-1 border-gray-300"
        onClick={() => navigate("/chat")}
      >
        Continue
      </button>
    </div>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 1100);
    return () => clearTimeout(timer);
  }, []);

  if (showSplash) {
    return (
      <div className="flex items-center justify-center h-screen bg-black">
        <Lottie animationData={splashAnimation} loop={false} style={{ width: 300, height: 300 }} />
      </div>
    );
  }

  return (
    <>
      <Routes>
        <Route path="/" element={<HomeScreen />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </>
  );
}

export default App;
