import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Bot, User, CheckCheck, Calendar, DollarSign, Clock, HelpCircle,
  ExternalLink, Sparkles, ShieldCheck, RefreshCw, Terminal, Phone, CheckCircle2,
  AlertTriangle, KeyRound, Globe, ArrowRight
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator');
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: "Hello! 👋 Welcome to *Apex Solutions*.\n\nI am your AI Business Assistant. How can I assist your business today?",
      intent: 'GREETING',
      buttons: [
        { id: 'btn_services', title: '💼 Our Services' },
        { id: 'btn_pricing', title: '💰 Pricing Plans' },
        { id: 'btn_booking', title: '📅 Book a Call' }
      ],
      time: 'Just now'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [customerName, setCustomerName] = useState('Alex Rivera');
  const [customerPhone, setCustomerPhone] = useState('+1 (555) 382-9104');
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    server: 'checking',
    whatsapp_configured: false,
    gemini_configured: false,
    calendar_configured: false,
    business_name: 'Apex Solutions',
    business_hours: 'Mon - Fri: 9:00 AM - 6:00 PM EST'
  });
  const [logs, setLogs] = useState([]);
  const chatBottomRef = useRef(null);

  // Suggested test prompts
  const quickPrompts = [
    "Hi there!",
    "What are your pricing packages?",
    "Can we schedule a call tomorrow at 3 PM?",
    "What services do you provide?",
    "Where is your office located?",
    "I need to speak to a human representative"
  ];

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setSystemStatus(data);
      }
    } catch {
      setSystemStatus(prev => ({ ...prev, server: 'offline' }));
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
      }
    } catch (e) {
      // offline / mock
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchLogs();
    const interval = setInterval(() => {
      fetchLogs();
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend = null) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || loading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setLoading(true);

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: customerPhone,
          name: customerName,
          message: text
        })
      });

      if (res.ok) {
        const data = await res.json();
        const agentResp = data.agent_response;
        const botMsg = {
          id: Date.now() + 1,
          sender: 'bot',
          text: agentResp.message,
          intent: agentResp.intent,
          buttons: agentResp.buttons || [],
          calendar_event: agentResp.calendar_event,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, botMsg]);
      } else {
        throw new Error('Simulation failed');
      }
    } catch {
      // Offline fallback
      setTimeout(() => {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'bot',
            text: `Thank you for contacting *${systemStatus.business_name}*!\n\nWe received: "${text}". Start the backend server via 'python main.py' to enjoy real-time Gemini intent parsing.`,
            intent: 'GENERAL_QUERY',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }, 500);
    } finally {
      setLoading(false);
      fetchLogs();
    }
  };

  const renderFormattedText = (raw) => {
    // Basic WhatsApp style formatting (*bold*)
    const parts = raw.split(/(\*[^*]+\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('*') && part.endsWith('*')) {
        return <strong key={i} className="font-semibold text-slate-900">{part.slice(1, -1)}</strong>;
      }
      return <span key={i} className="whitespace-pre-wrap">{part}</span>;
    });
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 py-3.5 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white font-bold">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-lg tracking-tight text-white">WhatsApp Business AI Agent</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                Meta Cloud API v21
              </span>
            </div>
            <p className="text-xs text-slate-400">Intelligent Routing • Calendar Scheduling • Autonomous FAQ</p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/60 text-sm">
          <button
            onClick={() => setActiveTab('simulator')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium transition-all ${
              activeTab === 'simulator'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Phone className="w-4 h-4" />
            Live Simulator
          </button>
          <button
            onClick={() => setActiveTab('activity')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium transition-all ${
              activeTab === 'activity'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-4 h-4" />
            Activity & Webhooks
          </button>
          <button
            onClick={() => setActiveTab('credentials')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-lg font-medium transition-all ${
              activeTab === 'credentials'
                ? 'bg-emerald-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <KeyRound className="w-4 h-4" />
            Setup & Keys
          </button>
        </div>

        {/* Server State Indicator */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700">
            <span className={`w-2 h-2 rounded-full ${systemStatus.server === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            <span className="text-slate-300 font-medium capitalize">Backend: {systemStatus.server}</span>
          </div>
          <button
            onClick={fetchStatus}
            className="p-2 text-slate-400 hover:text-white rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
            title="Refresh Status"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-6">
        {/* TAB 1: LIVE SIMULATOR */}
        {activeTab === 'simulator' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left Column: WhatsApp Phone Simulation */}
            <div className="lg:col-span-7 flex justify-center">
              <div className="w-full max-w-md bg-slate-900 border-4 border-slate-800 rounded-[38px] shadow-2xl overflow-hidden flex flex-col h-[680px]">
                {/* Phone Header */}
                <div className="bg-emerald-800 px-4 py-3.5 flex items-center justify-between text-white shadow-md z-10">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 rounded-full bg-emerald-700 border border-emerald-500/50 flex items-center justify-center font-bold text-sm">
                        AS
                      </div>
                      <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 border-2 border-emerald-900 rounded-full"></span>
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="font-semibold text-sm leading-tight text-white">{systemStatus.business_name}</span>
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-300 fill-emerald-300/30" />
                      </div>
                      <span className="text-[11px] text-emerald-200">Official Business Account</span>
                    </div>
                  </div>
                  <div className="text-xs bg-emerald-950/60 text-emerald-200 px-2.5 py-1 rounded-full border border-emerald-700/50">
                    Live Bot
                  </div>
                </div>

                {/* Chat Messages Body */}
                <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-[#0b141a] bg-opacity-95 text-slate-900 text-sm">
                  <div className="flex justify-center my-1">
                    <span className="text-[10px] uppercase font-semibold tracking-wider bg-slate-900/80 text-slate-400 px-3 py-0.5 rounded-full border border-slate-800">
                      End-to-End Encrypted Simulation
                    </span>
                  </div>

                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                    >
                      {/* Intent Badge for Bot Messages */}
                      {msg.intent && (
                        <span className="text-[10px] text-emerald-400 font-mono mb-1 ml-1 flex items-center gap-1 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/40">
                          <Sparkles className="w-2.5 h-2.5" />
                          Intent: {msg.intent}
                        </span>
                      )}

                      <div
                        className={`max-w-[85%] rounded-2xl p-3 shadow-md relative ${
                          msg.sender === 'user'
                            ? 'bg-[#005c4b] text-emerald-50 rounded-tr-none'
                            : 'bg-[#202c33] text-slate-100 rounded-tl-none border border-slate-700/30'
                        }`}
                      >
                        <div className="leading-relaxed">
                          {renderFormattedText(msg.text)}
                        </div>

                        {/* Calendar Card Preview if Booked */}
                        {msg.calendar_event && (
                          <div className="mt-2.5 p-2.5 rounded-xl bg-slate-900/90 border border-emerald-500/30 text-xs">
                            <div className="flex items-center gap-2 font-semibold text-emerald-400 mb-1">
                              <Calendar className="w-4 h-4" />
                              <span>Google Calendar Event</span>
                            </div>
                            <p className="text-slate-300 font-medium">{msg.calendar_event.formatted_time}</p>
                            <a
                              href={msg.calendar_event.meet_link}
                              target="_blank"
                              rel="noreferrer"
                              className="mt-2 inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition text-[11px]"
                            >
                              Join Google Meet
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}

                        <div className="flex items-center justify-end gap-1 mt-1 text-[10px] text-slate-400">
                          <span>{msg.time}</span>
                          {msg.sender === 'user' && (
                            <CheckCheck className="w-3.5 h-3.5 text-cyan-400" />
                          )}
                        </div>
                      </div>

                      {/* Interactive Buttons (Meta Cloud API button preview) */}
                      {msg.buttons && msg.buttons.length > 0 && (
                        <div className="mt-2 space-y-1.5 w-[85%]">
                          {msg.buttons.map((btn) => (
                            <button
                              key={btn.id}
                              onClick={() => handleSendMessage(btn.title)}
                              className="w-full text-left py-2 px-3 rounded-xl bg-[#2a3942] hover:bg-[#32434d] text-cyan-300 border border-slate-700/50 text-xs font-medium flex items-center justify-between transition group shadow-sm"
                            >
                              <span>{btn.title}</span>
                              <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-300 transition" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {loading && (
                    <div className="flex items-center gap-2 p-3 bg-[#202c33] text-slate-300 rounded-2xl rounded-tl-none border border-slate-700/30 w-fit">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce"></span>
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.2s]"></span>
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce [animation-delay:0.4s]"></span>
                      <span className="text-xs text-slate-400 ml-1">AI Agent typing...</span>
                    </div>
                  )}
                  <div ref={chatBottomRef} />
                </div>

                {/* Input Bar */}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="bg-[#202c33] p-3 flex items-center gap-2 border-t border-slate-800"
                >
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type a WhatsApp message..."
                    className="flex-1 bg-[#2a3942] text-slate-100 placeholder-slate-400 text-sm px-4 py-2.5 rounded-full focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                  <button
                    type="submit"
                    disabled={!inputMessage.trim() || loading}
                    className="w-10 h-10 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white flex items-center justify-center transition shadow"
                  >
                    <Send className="w-4 h-4 ml-0.5" />
                  </button>
                </form>
              </div>
            </div>

            {/* Right Column: Interactive Test Controls & Quick Presets */}
            <div className="lg:col-span-5 space-y-6">
              {/* Presets card */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm">
                <div className="flex items-center gap-2 mb-3 text-white font-semibold">
                  <Sparkles className="w-5 h-5 text-emerald-400" />
                  <h3>Quick Test Scenarios</h3>
                </div>
                <p className="text-xs text-slate-400 mb-4 leading-relaxed">
                  Click any pre-configured customer inquiry below to test intent classification, dynamic buttons, and appointment scheduling:
                </p>
                <div className="flex flex-col gap-2">
                  {quickPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="text-left text-xs px-3.5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-750 text-slate-200 border border-slate-700/60 hover:border-emerald-500/50 transition flex items-center justify-between group"
                    >
                      <span>"{prompt}"</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-400 transition" />
                    </button>
                  ))}
                </div>
              </div>

              {/* Customer simulation metadata */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 shadow-sm">
                <h4 className="font-semibold text-sm text-white mb-3 flex items-center gap-2">
                  <User className="w-4 h-4 text-emerald-400" />
                  Customer Profile (Simulator)
                </h4>
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="text-slate-400 block mb-1">Simulated Name</label>
                    <input
                      type="text"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Simulated Phone</label>
                    <input
                      type="text"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
                    />
                  </div>
                </div>
              </div>

              {/* Capabilities checklist */}
              <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 text-xs space-y-2">
                <span className="font-semibold text-slate-300 block mb-1">Included Agent Capabilities:</span>
                <div className="flex items-center gap-2 text-slate-300">
                  <CheckCheck className="w-4 h-4 text-emerald-400" />
                  <span>Meta Webhook Signature Verification (`sha256`)</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <CheckCheck className="w-4 h-4 text-emerald-400" />
                  <span>Instant Intent Extraction (Pricing, FAQs, Hours, Booking)</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <CheckCheck className="w-4 h-4 text-emerald-400" />
                  <span>Natural Language Date Parsing & Meet Link Reservation</span>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <CheckCheck className="w-4 h-4 text-emerald-400" />
                  <span>Interactive Reply Buttons (Meta Graph API schema)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: ACTIVITY & WEBHOOK LOGS */}
        {activeTab === 'activity' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white">Live Webhook Stream & Message Activity</h2>
                <p className="text-xs text-slate-400">Real-time log of inbound payloads from Meta and outbound messages dispatched.</p>
              </div>
              <button
                onClick={fetchLogs}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-medium text-slate-300 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh Logs
              </button>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 overflow-hidden">
              {logs.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-sm">
                  <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  No message activity logged yet. Send a test message in the simulator to see live events!
                </div>
              ) : (
                <div className="divide-y divide-slate-800 font-mono text-xs max-h-[550px] overflow-y-auto">
                  {logs.map((log) => (
                    <div key={log.id} className="py-3 px-2 flex items-start justify-between gap-4 hover:bg-slate-850/50 transition">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              log.direction === 'inbound'
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            }`}
                          >
                            {log.direction}
                          </span>
                          <span className="text-slate-400">{log.phone}</span>
                          {log.meta?.intent && (
                            <span className="text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded text-[10px]">
                              {log.meta.intent}
                            </span>
                          )}
                        </div>
                        <p className="text-slate-200 text-xs font-sans whitespace-pre-wrap">{log.message}</p>
                      </div>
                      <span className="text-[10px] text-slate-500 whitespace-nowrap">
                        {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Recent'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: CREDENTIALS & SETUP GUIDE */}
        {activeTab === 'credentials' && (
          <div className="space-y-8 max-w-4xl">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">Configuration & Credentials Checklist</h2>
              <p className="text-sm text-slate-400">
                The agent is pre-configured to run out-of-the-box in full simulation mode. To connect to live Meta servers and Google Calendar, add these environment variables into your <code className="text-emerald-400">.env</code> file.
              </p>
            </div>

            {/* Step 1: Meta WhatsApp Cloud API */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">1</div>
                  <h3 className="font-semibold text-white">Meta WhatsApp Cloud API (Required for Live WhatsApp)</h3>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  systemStatus.whatsapp_configured
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                }`}>
                  {systemStatus.whatsapp_configured ? 'Configured' : 'Using Simulation Mode'}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Create a Meta App at <a href="https://developers.facebook.com" target="_blank" rel="noreferrer" className="text-emerald-400 underline">developers.facebook.com</a> &gt; Add WhatsApp product &gt; API Setup.
              </p>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 space-y-1">
                <div><span className="text-slate-500"># In your .env:</span></div>
                <div>WHATSAPP_PHONE_NUMBER_ID="your_phone_number_id"</div>
                <div>WHATSAPP_BUSINESS_ACCOUNT_ID="your_business_account_id"</div>
                <div>WHATSAPP_ACCESS_TOKEN="your_meta_system_user_access_token"</div>
                <div>WEBHOOK_VERIFY_TOKEN="{systemStatus.verify_token || 'wauto_verify_token_dev'}"</div>
              </div>
            </div>

            {/* Step 2: Google Gemini AI Key */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">2</div>
                  <h3 className="font-semibold text-white">Google Gemini API Key (Optional for Open-Ended Queries)</h3>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  systemStatus.gemini_configured
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                }`}>
                  {systemStatus.gemini_configured ? 'Connected' : 'Smart Heuristics Active'}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Grab a free API key from <a href="https://aistudio.google.com" target="_blank" rel="noreferrer" className="text-indigo-400 underline">Google AI Studio</a> to enable dynamic generative answers for general conversational questions.
              </p>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300">
                <div>GEMINI_API_KEY="AIzaSy..."</div>
              </div>
            </div>

            {/* Step 3: Google Calendar API */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center font-bold">3</div>
                  <h3 className="font-semibold text-white">Google Calendar OAuth (For Real Calendar Invitations)</h3>
                </div>
                <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  systemStatus.calendar_configured
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                }`}>
                  {systemStatus.calendar_configured ? 'Connected' : 'Meet Link Generator Active'}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Enable Google Calendar API in Google Cloud Console &gt; Create OAuth 2.0 Client Credentials.
              </p>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 font-mono text-xs text-slate-300 space-y-1">
                <div>GOOGLE_CLIENT_ID="your_client_id.apps.googleusercontent.com"</div>
                <div>GOOGLE_CLIENT_SECRET="your_client_secret"</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
