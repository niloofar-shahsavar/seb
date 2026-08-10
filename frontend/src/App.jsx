import { useEffect, useState } from "react";

const API = "http://localhost:8000/api/daily-run";

const STATUS_TOKEN = {
  APPROVED: "var(--gds-sys-color-dark-green-2)",
  REVIEW: "var(--gds-sys-color-dark-yellow-2)",
  REJECTED: "var(--gds-sys-color-dark-red-1)",
};

const S = {
  page: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "32px 24px 64px",
  },
  card: {
    background: "var(--gds-sys-color-background-primary, #fff)",
    border: "1px solid var(--gds-sys-color-base-300, #ddd)",
    borderRadius: 4,
    padding: 20,
    marginBottom: 24,
  },
  muted: {
    color: "var(--gds-sys-color-text-secondary, #666)",
    fontSize: 14,
    margin: "4px 0 16px",
  },
  th: {
    textAlign: "left",
    padding: "10px 8px",
    borderBottom: "2px solid var(--gds-sys-color-base-400, #ccc)",
    fontSize: 13,
    fontWeight: 600,
    color: "var(--gds-sys-color-text-secondary, #666)",
    textTransform: "uppercase",
    letterSpacing: "0.02em",
  },
  td: {
    padding: "10px 8px",
    borderBottom: "1px solid var(--gds-sys-color-base-200, #eee)",
    fontSize: 14,
    verticalAlign: "top",
  },
};

function money(n) {
  return new Intl.NumberFormat("sv-SE", {
    style: "currency",
    currency: "SEK",
    maximumFractionDigits: 0,
  }).format(n || 0);
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(API)
      .then((r) => (r.ok ? r.json() : Promise.reject(`HTTP ${r.status}`)))
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  if (error)
    return (
      <main style={S.page}>
        <p>Could not reach the API: {error}</p>
      </main>
    );
  if (!data)
    return (
      <main style={S.page}>
        <p>Loading…</p>
      </main>
    );

  const s = data.summary;
  const newHoldings = data.holdings.filter((h) => h.is_new);

  return (
    <main style={S.page}>
      <div
        style={{
          height: 4,
          background: "var(--gds-sys-color-green)",
          marginBottom: 24,
          borderRadius: 2,
        }}
      />

      <header style={{ marginBottom: 24 }}>
        <h1 style={{ margin: "0 0 4px", fontSize: 28, fontWeight: 500 }}>
          Portfolio Bond compliance monitoring
        </h1>
        <p style={{ ...S.muted, margin: 0 }}>
          Daily run {data.run_date} · policy version {data.policy_version}
        </p>
      </header>

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(5, 1fr)",
          gap: 16,
          marginBottom: 32,
        }}
      >
        <Tile label="Holdings" value={s.total_holdings} />
        <Tile label="New today" value={s.new_holdings} />
        <Tile
          label="Approved"
          value={s.approved}
          color={STATUS_TOKEN.APPROVED}
        />
        <Tile label="Review" value={s.review} color={STATUS_TOKEN.REVIEW} />
        <Tile
          label="Rejected"
          value={s.rejected}
          color={STATUS_TOKEN.REJECTED}
        />
      </section>

      <Panel
        title={`New holdings detected (${newHoldings.length})`}
        note="Instruments never held in any account on any earlier day. Newness is detected at ISIN level, not per account."
      >
        <Table
          head={["Account", "Instrument", "Type", "Value", "Status"]}
          align={[null, null, null, "right", null]}
          rows={newHoldings.map((h) => [
            h.account_id,
            h.name,
            h.asset_type,
            money(h.market_value),
            <Status key="s" value={h.status} />,
          ])}
        />
      </Panel>

      <Panel
        title="Corporate events"
        note={`${s.events_applied} applied, ${s.events_ignored} out of scope. An event matters only if it changes an input used by one of the rules.`}
      >
        <Table
          head={["Event", "Type", "ISIN", "Relevant", "Effect", "Accounts"]}
          rows={data.corporate_events.map((e) => [
            e.event_id,
            e.event_type.replace(/_/g, " ").toLowerCase(),
            e.isin,
            <span
              key="r"
              style={{
                color: e.relevant
                  ? STATUS_TOKEN.APPROVED
                  : "var(--gds-sys-color-text-secondary)",
              }}
            >
              {e.relevant ? "Yes" : "No"}
            </span>,
            e.relevant ? e.applied_change : e.reason,
            e.affected_accounts.join(", ") || "—",
          ])}
        />
      </Panel>

      <Panel
        title={`Alerts (${data.alerts.length})`}
        note="Breaches first, then largest exposure. Position size affects ordering only, never the compliance decision."
      >
        <Table
          head={[
            "Severity",
            "Rule",
            "Instrument",
            "Observed",
            "Expected",
            "Trigger",
            "Suggested action",
          ]}
          rows={data.alerts.map((a) => [
            <Status
              key="sev"
              value={a.severity === "FAIL" ? "REJECTED" : "REVIEW"}
              label={a.severity}
            />,
            <span key="r">
              <strong>{a.rule_id}</strong> {a.rule_name}
            </span>,
            a.name,
            <code key="o" style={{ fontSize: 13 }}>
              {a.observed_field} = {a.observed_value || "(empty)"}
            </code>,
            a.expected,
            a.trigger.replace(/_/g, " "),
            a.suggested_action,
          ])}
        />
      </Panel>
    </main>
  );
}

function Tile({ label, value, color }) {
  return (
    <div style={{ ...S.card, marginBottom: 0, padding: 16 }}>
      <div
        style={{
          fontSize: 12,
          color: "var(--gds-sys-color-text-secondary, #666)",
          textTransform: "uppercase",
          letterSpacing: "0.04em",
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 32,
          fontWeight: 500,
          color: color || "var(--gds-sys-color-text-primary)",
          lineHeight: 1.2,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function Panel({ title, note, children }) {
  return (
    <section style={S.card}>
      <h2 style={{ margin: 0, fontSize: 20, fontWeight: 500 }}>{title}</h2>
      <p style={S.muted}>{note}</p>
      {children}
    </section>
  );
}

function Status({ value, label }) {
  return (
    <span
      style={{
        color: STATUS_TOKEN[value],
        fontWeight: 600,
        fontSize: 13,
        letterSpacing: "0.02em",
      }}
    >
      {label || value}
    </span>
  );
}

function Table({ head, rows, align = [] }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {head.map((h, i) => (
              <th key={h} style={{ ...S.th, textAlign: align[i] || "left" }}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              {r.map((c, j) => (
                <td key={j} style={{ ...S.td, textAlign: align[j] || "left" }}>
                  {c}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
