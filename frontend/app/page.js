"use client";

import { useEffect, useState } from "react";

const cards = [
  ["Pending approvals", "Review external replies and booking actions before they happen."],
  ["Inbox", "Conversations are grounded in your business documents."],
  ["Knowledge", "Upload FAQs, price lists, and operating policies."],
];

export default function Home() {
  const [businessId, setBusinessId] = useState("demo");
  const [approvals, setApprovals] = useState([]);
  const [status, setStatus] = useState("Enter a business ID to load approvals.");
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function loadApprovals() {
    setStatus("Loading approvals...");
    try {
      const response = await fetch(`${apiUrl}/approvals`, {
        headers: { "X-Business-ID": businessId },
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed (${response.status})`);
      }
      setApprovals(await response.json());
      setStatus("Approvals loaded.");
    } catch (error) {
      setApprovals([]);
      setStatus(error.message);
    }
  }

  async function decide(id, decision) {
    const response = await fetch(`${apiUrl}/approvals/${id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Business-ID": businessId },
      body: JSON.stringify({ decision }),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    await loadApprovals();
  }

  useEffect(() => {
    loadApprovals();
  }, []);

  return (
    <main style={{ maxWidth: 980, margin: "0 auto", padding: 40 }}>
      <p style={{ color: "#2563eb", fontWeight: 700 }}>ARIA OPERATIONS</p>
      <h1>Good morning. Your business is under control.</h1>
      <p style={{ color: "#475569", maxWidth: 640 }}>
        Aria handles routine customer questions and keeps risky actions in a human approval queue.
      </p>
      <section style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginTop: 32 }}>
        {cards.map(([title, text]) => (
          <article key={title} style={{ border: "1px solid #e2e8f0", borderRadius: 12, padding: 20 }}>
            <h2 style={{ fontSize: 18 }}>{title}</h2>
            <p style={{ color: "#64748b" }}>{text}</p>
          </article>
        ))}
      </section>
      <section style={{ marginTop: 40, background: "#f8fafc", borderRadius: 12, padding: 24 }}>
        <h2>Approval queue</h2>
        <form onSubmit={(event) => { event.preventDefault(); loadApprovals(); }} style={{ display: "flex", gap: 8 }}>
          <label htmlFor="business-id">Business ID</label>
          <input id="business-id" value={businessId} onChange={(event) => setBusinessId(event.target.value)} />
          <button type="submit">Load</button>
        </form>
        <p aria-live="polite">{status}</p>
        {approvals.length === 0 ? <p>No approvals found.</p> : approvals.map((approval) => (
          <article key={approval.id} style={{ borderTop: "1px solid #e2e8f0", padding: "16px 0" }}>
            <strong>{approval.action_type}</strong>
            <p>Status: {approval.status}</p>
            {approval.status === "pending" && (
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={() => decide(approval.id, "approved")}>Approve</button>
                <button onClick={() => decide(approval.id, "rejected")}>Reject</button>
              </div>
            )}
          </article>
        ))}
      </section>
    </main>
  );
}
