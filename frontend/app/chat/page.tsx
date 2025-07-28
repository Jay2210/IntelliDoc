"use client";
import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

// Define the structure of a chat message
interface Message {
  role: 'user' | 'bot';
  content: string;
}

// Define the structure of the Justification object from the backend
interface Justification {
  clause_id: string;
  snippet: string;
  full_text: string;
  explanation: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');
  const [insurer, setInsurer] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [uploadedInsurer, setUploadedInsurer] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const predefinedInsurers = ["HDFC Ergo", "Bajaj Allianz", "ICICI Lombard", "CholaMS", "Edelweiss"];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadStatus('Uploading...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      const newInsurerName = result.filename.split('.')[0];
      setUploadStatus(`Successfully indexed ${result.indexed_chunks} chunks from ${result.filename}.`);
      setUploadedInsurer(newInsurerName);
      setInsurer(newInsurerName);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('Upload failed. Please try again.');
    }
  };

  const handleSendMessage = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, insurer: insurer }),
      });

      if (!response.ok) {
        throw new Error('Query failed');
      }

      const result = await response.json();
      let botMessageContent: string;
      
      if (result.decision) {
          botMessageContent = `**Decision:** ${result.decision}\n\n`;
          if(result.amount) botMessageContent += `**Amount:** ${result.amount}\n\n`;
          
          // --- THIS IS THE FIX ---
          // Loop through the justification array and format it
          const formattedJustification = result.justification.map((j: Justification, index: number) => 
            `**Source Clause ${index + 1} (ID: ${j.clause_id})**\n` +
            `**Relevant Snippet:** "${j.snippet}"\n` +
            `**Explanation:** ${j.explanation}`
          ).join('\n\n---\n\n'); // Join multiple justifications with a separator

          botMessageContent += `**Justification based on the following clauses:**\n${formattedJustification}`;
          // --- END OF FIX ---

      } else {
          botMessageContent = result.answer;
      }

      const botMessage: Message = { role: 'bot', content: botMessageContent };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('Query error:', error);
      const errorMessage: Message = { role: 'bot', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-65px)] bg-gray-900 text-gray-200">
      <div className="w-1/4 bg-gray-800 p-6 border-r border-gray-700 flex flex-col">
        <h2 className="text-2xl font-bold mb-6 text-white">Controls</h2>
        <div className="mb-6">
            <button onClick={() => fileInputRef.current?.click()} className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded-lg transition-colors">
                Upload Document
            </button>
            <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.docx,.eml" />
            {uploadStatus && <p className="text-sm text-gray-400 mt-3">{uploadStatus}</p>}
        </div>
        <div className="mb-4">
            <label htmlFor="insurer" className="block text-sm font-medium text-gray-300 mb-2">Insurer</label>
            <select 
                id="insurer"
                value={insurer}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setInsurer(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-md p-2 text-gray-200 focus:ring-2 focus:ring-indigo-500"
            >
                <option value="">Select an insurer</option>
                {predefinedInsurers.map(name => (
                    <option key={name} value={name}>{name}</option>
                ))}
                {uploadedInsurer && !predefinedInsurers.includes(uploadedInsurer) && (
                    <option key={uploadedInsurer} value={uploadedInsurer}>
                        {uploadedInsurer} (Uploaded)
                    </option>
                )}
            </select>
        </div>
        <div className="mt-auto text-xs text-gray-500">
            <p>Upload a policy document to start. The insurer context will be automatically set from the filename, or you can set it manually.</p>
        </div>
      </div>
      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-6 overflow-y-auto">
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-lg px-4 py-2 rounded-xl whitespace-pre-wrap ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
                  {msg.content.split('\n').map((line, i) => (
                    <p key={i} className={line.startsWith('**') ? 'font-bold' : ''}>
                      {line.replace(/\*\*/g, '')}
                    </p>
                  ))}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <div className="p-6 border-t border-gray-700">
          <form onSubmit={handleSendMessage} className="flex items-center space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
              placeholder="Ask a question about the policy..."
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg p-3 text-gray-200 focus:ring-2 focus:ring-indigo-500"
              disabled={isLoading}
            />
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-6 rounded-lg disabled:bg-indigo-800" disabled={isLoading}>
              {isLoading ? 'Thinking...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
