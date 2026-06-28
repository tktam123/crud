import { useState, useEffect, useCallback } from "react";

const BASE = "http://localhost:8000";

// ── API helpers ───────────────────────────────────────────────────────────────
const api = {
  login: async (username, password) => {
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${BASE}/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Login failed");
    }
    return res.json();
  },
  getItems: async (token) => {
    const res = await fetch(`${BASE}/items`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to fetch items");
    return res.json();
  },
  createItem: async (token, data) => {
    const res = await fetch(`${BASE}/items`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Create failed");
    }
    return res.json();
  },
  updateItem: async (token, id, data) => {
    const res = await fetch(`${BASE}/items/${id}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Update failed");
    }
    return res.json();
  },
  deleteItem: async (token, id) => {
    const res = await fetch(`${BASE}/items/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Delete failed");
    }
  },
};

// ── Small components ──────────────────────────────────────────────────────────
function Toast({ message, type, onDismiss }) {
  useEffect(() => {
    const t = setTimeout(onDismiss, 3500);
    return () => clearTimeout(t);
  }, [onDismiss]);

  const colors = {
    success: { bg: "var(--bg-success)", text: "var(--text-success)", border: "var(--border-success)" },
    error: { bg: "var(--bg-danger)", text: "var(--text-danger)", border: "var(--border-danger)" },
    info: { bg: "var(--bg-accent)", text: "var(--text-accent)", border: "var(--border-accent)" },
  };
  const c = colors[type] || colors.info;

  return (
    <div
      style={{
        position: "fixed",
        bottom: "1.5rem",
        right: "1.5rem",
        background: c.bg,
        color: c.text,
        border: `0.5px solid ${c.border}`,
        borderRadius: "var(--radius)",
        padding: "0.75rem 1.25rem",
        fontSize: 14,
        fontWeight: 500,
        maxWidth: 320,
        zIndex: 999,
        display: "flex",
        alignItems: "center",
        gap: 10,
        boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
      }}
    >
      <span style={{ flex: 1 }}>{message}</span>
      <button
        onClick={onDismiss}
        aria-label="Dismiss"
        style={{
          background: "none",
          border: "none",
          cursor: "pointer",
          color: c.text,
          padding: 0,
          fontSize: 16,
          lineHeight: 1,
        }}
      >
        ×
      </button>
    </div>
  );
}

function Spinner() {
  return (
    <span
      style={{
        display: "inline-block",
        width: 14,
        height: 14,
        border: "2px solid var(--border-strong)",
        borderTopColor: "var(--text-accent)",
        borderRadius: "50%",
        animation: "spin 0.7s linear infinite",
      }}
    />
  );
}

// ── Login screen ──────────────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.login(username, password);
      onLogin(data.access_token, username);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--surface-0)",
        padding: "1rem",
      }}
    >
      <div
        style={{
          background: "var(--surface-2)",
          border: "0.5px solid var(--border)",
          borderRadius: 12,
          padding: "2.5rem 2rem",
          width: "100%",
          maxWidth: 380,
        }}
      >
        <div style={{ marginBottom: "2rem" }}>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: 10,
              background: "var(--bg-accent)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "1.25rem",
            }}
          >
            <span style={{ fontSize: 20, color: "var(--text-accent)" }}>⬡</span>
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 500, margin: "0 0 4px", color: "var(--text-primary)" }}>
            Sign in
          </h1>
          <p style={{ fontSize: 14, color: "var(--text-muted)", margin: 0 }}>
            Use <code style={{ fontSize: 13 }}>jack / 111</code> or{" "}
            <code style={{ fontSize: 13 }}>admin / admin123</code>
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "1rem" }}>
            <label
              style={{ display: "block", fontSize: 13, color: "var(--text-secondary)", marginBottom: 6 }}
            >
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="jack"
              required
              autoFocus
              style={{ width: "100%", boxSizing: "border-box" }}
            />
          </div>
          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{ display: "block", fontSize: 13, color: "var(--text-secondary)", marginBottom: 6 }}
            >
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{ width: "100%", boxSizing: "border-box" }}
            />
          </div>
          {error && (
            <div
              style={{
                background: "var(--bg-danger)",
                color: "var(--text-danger)",
                border: "0.5px solid var(--border-danger)",
                borderRadius: "var(--radius)",
                padding: "0.6rem 0.875rem",
                fontSize: 13,
                marginBottom: "1rem",
              }}
            >
              {error}
            </div>
          )}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              background: "var(--fill-accent)",
              color: "var(--on-accent)",
              border: "none",
              borderRadius: "var(--radius)",
              padding: "0.6rem 1rem",
              fontSize: 14,
              fontWeight: 500,
              cursor: loading ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
            }}
          >
            {loading && <Spinner />}
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Item form (create / edit) ──────────────────────────────────────────────────
function ItemForm({ initial, onSave, onCancel, loading }) {
  const [name, setName] = useState(initial?.name || "");
  const [description, setDescription] = useState(initial?.description || "");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ name, description });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ marginBottom: "0.875rem" }}>
        <label style={{ display: "block", fontSize: 13, color: "var(--text-secondary)", marginBottom: 5 }}>
          Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Item name"
          required
          autoFocus
          style={{ width: "100%", boxSizing: "border-box" }}
        />
      </div>
      <div style={{ marginBottom: "1.25rem" }}>
        <label style={{ display: "block", fontSize: 13, color: "var(--text-secondary)", marginBottom: 5 }}>
          Description
        </label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
          rows={3}
          style={{ width: "100%", boxSizing: "border-box", resize: "vertical" }}
        />
      </div>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button type="button" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          style={{
            background: "var(--fill-accent)",
            color: "var(--on-accent)",
            border: "none",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {loading && <Spinner />}
          {initial ? "Save changes" : "Create item"}
        </button>
      </div>
    </form>
  );
}

// ── Delete confirmation ───────────────────────────────────────────────────────
function ConfirmDelete({ item, onConfirm, onCancel, loading }) {
  return (
    <div>
      <p style={{ fontSize: 14, color: "var(--text-secondary)", margin: "0 0 1.25rem" }}>
        Delete <strong style={{ color: "var(--text-primary)", fontWeight: 500 }}>{item.name}</strong>? This
        can't be undone.
      </p>
      <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
        <button onClick={onCancel}>Cancel</button>
        <button
          onClick={onConfirm}
          disabled={loading}
          style={{
            background: "var(--fill-danger)",
            color: "var(--on-danger)",
            border: "none",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          {loading && <Spinner />}
          Delete
        </button>
      </div>
    </div>
  );
}

// ── Modal wrapper ─────────────────────────────────────────────────────────────
function Modal({ title, onClose, children }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.35)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        padding: "1rem",
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div
        style={{
          background: "var(--surface-2)",
          border: "0.5px solid var(--border)",
          borderRadius: 12,
          padding: "1.5rem",
          width: "100%",
          maxWidth: 440,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.25rem",
          }}
        >
          <h2 style={{ fontSize: 16, fontWeight: 500, margin: 0 }}>{title}</h2>
          <button
            onClick={onClose}
            aria-label="Close"
            style={{ background: "none", border: "none", cursor: "pointer", padding: 4, fontSize: 18 }}
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ── Main dashboard ────────────────────────────────────────────────────────────
function Dashboard({ token, username, onLogout }) {
  const [items, setItems] = useState([]);
  const [loadingItems, setLoadingItems] = useState(true);
  const [modal, setModal] = useState(null); // null | { type: 'create' | 'edit' | 'delete', item? }
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const showToast = (message, type = "success") => setToast({ message, type });

  const fetchItems = useCallback(async () => {
    setLoadingItems(true);
    try {
      const data = await api.getItems(token);
      setItems(data);
    } catch (err) {
      if (err.message.includes("401") || err.message.toLowerCase().includes("unauthori")) {
        onLogout();
      } else {
        showToast("Couldn't load items.", "error");
      }
    } finally {
      setLoadingItems(false);
    }
  }, [token, onLogout]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const handleCreate = async (data) => {
    setActionLoading(true);
    try {
      const created = await api.createItem(token, data);
      setItems((prev) => [...prev, created]);
      setModal(null);
      showToast(`"${created.name}" created.`);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setActionLoading(false);
    }
  };

  const handleEdit = async (data) => {
    setActionLoading(true);
    try {
      const updated = await api.updateItem(token, modal.item.id, data);
      setItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)));
      setModal(null);
      showToast(`"${updated.name}" saved.`);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setActionLoading(false);
    }
  };

  const handleDelete = async () => {
    setActionLoading(true);
    try {
      await api.deleteItem(token, modal.item.id);
      setItems((prev) => prev.filter((i) => i.id !== modal.item.id));
      setModal(null);
      showToast(`"${modal.item.name}" deleted.`);
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setActionLoading(false);
    }
  };

  const myItems = items.filter((i) => i.owner === username);
  const othersItems = items.filter((i) => i.owner !== username);

  return (
    <div style={{ minHeight: "100vh", background: "var(--surface-0)" }}>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {/* Nav */}
      <header
        style={{
          background: "var(--surface-2)",
          borderBottom: "0.5px solid var(--border)",
          padding: "0 1.5rem",
          height: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 50,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 18, color: "var(--text-accent)" }}>⬡</span>
          <span style={{ fontSize: 15, fontWeight: 500, color: "var(--text-primary)" }}>Items</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              fontSize: 13,
              color: "var(--text-secondary)",
              display: "flex",
              alignItems: "center",
              gap: 7,
            }}
          >
            <div
              style={{
                width: 26,
                height: 26,
                borderRadius: "50%",
                background: "var(--bg-accent)",
                color: "var(--text-accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 500,
                fontSize: 12,
              }}
            >
              {username[0].toUpperCase()}
            </div>
            {username}
          </div>
          <button
            onClick={onLogout}
            style={{ fontSize: 13, color: "var(--text-muted)", padding: "0.3rem 0.75rem" }}
          >
            Sign out
          </button>
        </div>
      </header>

      <main style={{ maxWidth: 760, margin: "0 auto", padding: "2rem 1.5rem" }}>
        {/* Header row */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "1.75rem",
          }}
        >
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 500, margin: "0 0 2px" }}>Your items</h1>
            <p style={{ fontSize: 14, color: "var(--text-muted)", margin: 0 }}>
              {myItems.length} item{myItems.length !== 1 ? "s" : ""}
            </p>
          </div>
          <button
            onClick={() => setModal({ type: "create" })}
            style={{
              background: "var(--fill-accent)",
              color: "var(--on-accent)",
              border: "none",
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: 14,
            }}
          >
            + New item
          </button>
        </div>

        {/* Items list */}
        {loadingItems ? (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              color: "var(--text-muted)",
              fontSize: 14,
              padding: "2rem 0",
            }}
          >
            <Spinner /> Loading…
          </div>
        ) : myItems.length === 0 ? (
          <div
            style={{
              background: "var(--surface-1)",
              border: "0.5px solid var(--border)",
              borderRadius: 12,
              padding: "3rem 2rem",
              textAlign: "center",
              marginBottom: "2rem",
            }}
          >
            <p style={{ fontSize: 15, fontWeight: 500, margin: "0 0 6px", color: "var(--text-primary)" }}>
              No items yet
            </p>
            <p style={{ fontSize: 13, color: "var(--text-muted)", margin: "0 0 1.25rem" }}>
              Create your first item to get started.
            </p>
            <button
              onClick={() => setModal({ type: "create" })}
              style={{
                background: "var(--fill-accent)",
                color: "var(--on-accent)",
                border: "none",
                fontSize: 13,
              }}
            >
              + New item
            </button>
          </div>
        ) : (
          <div
            style={{
              background: "var(--surface-2)",
              border: "0.5px solid var(--border)",
              borderRadius: 12,
              overflow: "hidden",
              marginBottom: "2rem",
            }}
          >
            {myItems.map((item, idx) => (
              <div
                key={item.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "0.875rem 1.25rem",
                  borderTop: idx > 0 ? "0.5px solid var(--border)" : "none",
                }}
              >
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    background: "var(--bg-accent)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    fontSize: 14,
                    fontWeight: 500,
                    color: "var(--text-accent)",
                  }}
                >
                  {item.id}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p style={{ fontSize: 14, fontWeight: 500, margin: "0 0 2px", color: "var(--text-primary)" }}>
                    {item.name}
                  </p>
                  {item.description && (
                    <p
                      style={{
                        fontSize: 13,
                        color: "var(--text-muted)",
                        margin: 0,
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {item.description}
                    </p>
                  )}
                </div>
                <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                  <button
                    onClick={() => setModal({ type: "edit", item })}
                    style={{ fontSize: 13, padding: "0.3rem 0.75rem" }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => setModal({ type: "delete", item })}
                    style={{
                      fontSize: 13,
                      padding: "0.3rem 0.75rem",
                      color: "var(--text-danger)",
                      borderColor: "var(--border-danger)",
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Other users' items */}
        {othersItems.length > 0 && (
          <>
            <h2
              style={{
                fontSize: 14,
                fontWeight: 500,
                color: "var(--text-muted)",
                margin: "0 0 0.875rem",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Other users
            </h2>
            <div
              style={{
                background: "var(--surface-1)",
                border: "0.5px solid var(--border)",
                borderRadius: 12,
                overflow: "hidden",
              }}
            >
              {othersItems.map((item, idx) => (
                <div
                  key={item.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: "0.875rem 1.25rem",
                    borderTop: idx > 0 ? "0.5px solid var(--border)" : "none",
                    opacity: 0.7,
                  }}
                >
                  <div
                    style={{
                      width: 32,
                      height: 32,
                      borderRadius: 8,
                      background: "var(--surface-0)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      flexShrink: 0,
                      fontSize: 14,
                      fontWeight: 500,
                      color: "var(--text-muted)",
                      border: "0.5px solid var(--border)",
                    }}
                  >
                    {item.id}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 14, fontWeight: 500, margin: "0 0 2px", color: "var(--text-primary)" }}>
                      {item.name}
                    </p>
                    {item.description && (
                      <p style={{ fontSize: 13, color: "var(--text-muted)", margin: 0 }}>
                        {item.description}
                      </p>
                    )}
                  </div>
                  <span
                    style={{
                      fontSize: 12,
                      color: "var(--text-muted)",
                      background: "var(--surface-0)",
                      border: "0.5px solid var(--border)",
                      borderRadius: "var(--radius)",
                      padding: "2px 8px",
                    }}
                  >
                    {item.owner}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </main>

      {/* Modals */}
      {modal?.type === "create" && (
        <Modal title="New item" onClose={() => setModal(null)}>
          <ItemForm onSave={handleCreate} onCancel={() => setModal(null)} loading={actionLoading} />
        </Modal>
      )}
      {modal?.type === "edit" && (
        <Modal title="Edit item" onClose={() => setModal(null)}>
          <ItemForm
            initial={modal.item}
            onSave={handleEdit}
            onCancel={() => setModal(null)}
            loading={actionLoading}
          />
        </Modal>
      )}
      {modal?.type === "delete" && (
        <Modal title="Delete item" onClose={() => setModal(null)}>
          <ConfirmDelete
            item={modal.item}
            onConfirm={handleDelete}
            onCancel={() => setModal(null)}
            loading={actionLoading}
          />
        </Modal>
      )}

      {/* Toast */}
      {toast && (
        <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />
      )}
    </div>
  );
}

// ── Root ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("token") || null);
  const [username, setUsername] = useState(() => sessionStorage.getItem("username") || null);

  const handleLogin = (tok, user) => {
    sessionStorage.setItem("token", tok);
    sessionStorage.setItem("username", user);
    setToken(tok);
    setUsername(user);
  };

  const handleLogout = () => {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("username");
    setToken(null);
    setUsername(null);
  };

  if (!token) return <LoginPage onLogin={handleLogin} />;
  return <Dashboard token={token} username={username} onLogout={handleLogout} />;
}
