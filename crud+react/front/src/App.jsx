import { useState, useEffect } from "react";
import "./App.css";

const BASE = "http://localhost:8000";

export default function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState("");
  const [items, setItems] = useState([]);
  const [msg, setMsg] = useState("");
  const [form, setForm] = useState(null);

  useEffect(() => {
    if (!token) return;
    fetch(`${BASE}/items`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(setItems)
      .catch(() => setMsg("Failed to load"));
  }, [token]);

  const login = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await fetch(`${BASE}/token`, {
      method: "POST",
      body: new URLSearchParams(fd),
    });
    const data = await res.json();
    if (!res.ok) return setMsg(data.detail);
    setToken(data.access_token);
    setUser(fd.get("username"));
  };

  const save = async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = {
      name:        fd.get("name"),
      description: fd.get("description"),
    };
    const url = form?.id ? `${BASE}/items/${form.id}` : `${BASE}/items`;
    await fetch(url, {
      method: form?.id ? "PUT" : "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });
    setForm(null);
    fetch(`${BASE}/items`, {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(setItems);
  };

  const del = async (id) => {
    if (!confirm("Delete?")) return;
    await fetch(`${BASE}/items/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    setItems(prev => prev.filter(i => i.id !== id));
  };

  // ── LOGIN VIEW ──────────────────────────────────────────
  if (!token) return (
    <div className="auth-wrapper">
      <div className="auth-box">
        <h2>Sign in</h2>
        {msg && <p className="msg-error">{msg}</p>}
        <form onSubmit={login}>
          <div className="field">
            <label>Username</label>
            <input name="username" placeholder="your username" />
          </div>
          <div className="field">
            <label>Password</label>
            <input name="password" type="password" placeholder="••••••••" />
          </div>
          <button className="btn-primary">Sign in</button>
        </form>
      </div>
    </div>
  );

  // ── MAIN VIEW ───────────────────────────────────────────
  return (
    <div className="app-wrapper">

      {/* Top bar */}
      <div className="topbar">
        <div className="topbar-left">
          <div className="avatar">{user.slice(0, 2)}</div>
          <h1>Items</h1>
        </div>
        <div className="topbar-right">
          <button className="btn-add" onClick={() => setForm({})}>+ New item</button>
          <button className="btn-ghost" onClick={() => setToken(null)}>Sign out</button>
        </div>
      </div>

      {msg && <p className="msg-error">{msg}</p>}

      {/* New / Edit form */}
      {form !== null && (
        <form className="item-form" onSubmit={save}>
          <input name="name" defaultValue={form.name} placeholder="Name" />
          <textarea name="description" defaultValue={form.description} placeholder="Address / description" rows={3} />
          <div className="form-actions">
            <button className="btn-save">Save</button>
            <button className="btn-cancel" type="button" onClick={() => setForm(null)}>Cancel</button>
          </div>
        </form>
      )}

      {/* Items list */}
      <div className="items-list">
        {items.map(item => (
          <div className="item-card" key={item.id}>
            <div className="item-info">
              <strong>{item.name}</strong>
              <span>owner: {item.owner}</span>
            </div>
            {item.owner === user && (
              <div className="item-actions">
                <button className="btn-edit" onClick={() => setForm(item)}>Edit</button>
                <button className="btn-delete" onClick={() => del(item.id)}>Delete</button>
              </div>
            )}
          </div>
        ))}
      </div>

    </div>
  );
}