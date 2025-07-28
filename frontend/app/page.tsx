"use client";
import Link from "next/link";
import {
  ColourfulText,
  CometCard,
  Boxes,
} from "../components/ui";

export default function LandingPage() {
  const heroText = "Go from Complex Documents to Clear Decisions. Instantly.";

  const howItWorksItems = [
    { title: "1. Upload Your Document", description: "Securely upload your insurance policy, contract, or any PDF/Word document you need to analyze.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-indigo-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg> },
    { title: "2. Ask Your Question", description: "Converse naturally. Ask questions like, 'Is knee surgery covered for a 46-year-old?' No complex queries needed.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-indigo-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg> },
    { title: "3. Get an Instant Answer", description: "Receive a clear decision, the reasoning behind it, and the exact clause from the document that supports the answer.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-indigo-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> },
  ];
  const features = [
      { title: "Unmatched Speed", description: "Go from hours of manual review to answers in seconds. Our AI-powered engine accelerates your workflows, enabling faster turnarounds and greater efficiency." },
      { title: "Pinpoint Accuracy", description: "Leverage sophisticated semantic understanding that goes beyond simple keywords to eliminate costly human errors and ensure consistent, unbiased analysis every time." },
      { title: "Total Transparency", description: "Build complete trust in your results. Every decision is fully auditable and backed by direct references to the specific source clauses, providing clear justification." },
      { title: "Natural Conversation", description: "No complex queries required. Simply ask questions in plain English and interact with your documents as if you're talking to a subject matter expert who knows every line by heart." },
  ];
  const useCases = [
      { title: "Insurance Claims", description: "Automate claim adjudication by instantly verifying policy coverage, checking for exclusions, and determining payout amounts. Drastically reduce manual review time and ensure consistent, auditable decisions.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> },
      { title: "Legal & Compliance", description: "Accelerate due diligence and contract review. Instantly identify risks, find non-compliant clauses, and extract key terms from thousands of pages, ensuring your organization stays ahead of regulatory requirements.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12l-1.5-1.5M21 12H3m18 0l-1.5 1.5M3 12h18M3 12l1.5-1.5M3 12l1.5 1.5M15 21l-3-3m0 0l-3 3m3-3V3m0 18l3-3m-3 3l-3-3" /></svg> },
      { title: "Human Resources", description: "Provide immediate and accurate answers to employee questions about internal policies. Empower your HR team to focus on strategic initiatives by offloading repetitive queries about benefits, leave, and company guidelines.", icon: <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mb-2 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg> },
  ];

  return (
    <>
      <div className="h-[calc(100vh-65px)] relative w-full overflow-hidden bg-gray-900 flex flex-col items-center justify-center">
        <div className="absolute inset-0 w-full h-full bg-gray-900 z-20 [mask-image:radial-gradient(transparent,white)] pointer-events-none" />
        <Boxes />
        <div className="relative z-20 text-center max-w-6xl mx-auto p-4">
          <h1 className="text-4xl md:text-7xl font-bold leading-relaxed lg:leading-snug">
            <ColourfulText text={heroText} />
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mt-6">
            Stop drowning in policy documents, contracts, and legalese. Upload your files, ask questions in plain English, and get clear answers backed by the original text.
          </p>
          <Link href="/chat" className="mt-8 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-8 rounded-lg text-lg transition-transform transform hover:scale-105 inline-block">
            Try the Demo
          </Link>
        </div>
      </div>

      <section id="what-it-is" className="py-20 bg-gray-800"><div className="container mx-auto px-6 text-center"><h3 className="text-3xl font-bold text-white mb-4">Unlock a Smarter Way to Work</h3><div className="max-w-4xl mx-auto"><p className="text-gray-300 text-lg">IntelliDoc transforms your static documents into interactive knowledge bases. Our system uses advanced Large Language Models (LLMs) to do the heavy lifting for you. We don't just search for keywords; we understand meaning, context, and logic. Stop wasting hours on manual searches and eliminate the risk of human error. Get the right information, with full context and justification, in seconds.</p></div></div></section>
      
      <section id="how-it-works" className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-white">Get Answers in Three Simple Steps</h3>
            <p className="text-gray-400 mt-2">From upload to answer in under a minute.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {howItWorksItems.map((item, i) => (
              <CometCard key={i}>
                {item.icon}
                <h4 className="text-xl font-semibold text-white mb-2">{item.title}</h4>
                <p className="text-gray-400">{item.description}</p>
              </CometCard>
            ))}
          </div>
        </div>
      </section>
      
      <section id="features" className="py-20 bg-gray-800">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-white">The Power of True Understanding</h3>
            <p className="text-gray-400 mt-2">More than just search. This is comprehension.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, i) => (
              <CometCard key={i}>
                <h4 className="text-lg font-bold text-white mb-2">{feature.title}</h4>
                <p className="text-gray-400">{feature.description}</p>
              </CometCard>
            ))}
          </div>
        </div>
      </section>
      
      <section id="use-cases" className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-white">Transforming Industries</h3>
            <p className="text-gray-400 mt-2">IntelliDoc is built to adapt to your specific industry needs.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 text-left">
            {useCases.map((useCase, i) => (
              <CometCard key={i}>
                {useCase.icon}
                <h4 className="font-bold text-xl text-white mb-2">{useCase.title}</h4>
                <p className="text-gray-400">{useCase.description}</p>
              </CometCard>
            ))}
          </div>
        </div>
      </section>

      <section id="cta" className="py-20 bg-gray-800"><div className="container mx-auto px-6 text-center"><h3 className="text-3xl font-bold text-white">Ready to Revolutionize Your Document Workflow?</h3><p className="text-gray-400 mt-2 mb-8">See our AI in action and discover how much time and money you can save.</p><Link href="/chat" className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 px-8 rounded-lg text-lg transition-transform transform hover:scale-105 inline-block">Request a Live Demo</Link></div></section>
      <footer className="bg-gray-900 border-t border-gray-700">
        <div className="container mx-auto px-6 py-4 text-center text-gray-500">
          &copy; 2024 IntelliDoc. All rights reserved.
        </div>
    </footer>
    </>
  );
}
