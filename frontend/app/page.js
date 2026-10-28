const cards = [
  ["Pending approvals", "Review external replies and booking actions before they happen."],
  ["Inbox", "Conversations are grounded in your business documents."],
  ["Knowledge", "Upload FAQs, price lists, and operating policies."],
];

export default function Home() {
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
        <p>No pending approvals yet.</p>
      </section>
    </main>
  );
}
