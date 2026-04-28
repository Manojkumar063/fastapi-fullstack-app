import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

export default function Items() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", description: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const fetchItems = async () => {
    try {
      const res = await api.get("/items");
      setItems(res.data);
    } catch {
      navigate("/login");
    }
  };

  useEffect(() => { fetchItems(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/items", form);
      setForm({ name: "", description: "" });
      fetchItems();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create item");
    }
  };

  const handleDelete = async (id) => {
    await api.delete(`/items/${id}`);
    fetchItems();
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="items-container">
      <div className="items-header">
        <h2>Items</h2>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </div>

      <form onSubmit={handleCreate} className="item-form">
        <input
          placeholder="Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <input
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
        {error && <p className="error">{error}</p>}
        <button type="submit">Add Item</button>
      </form>

      <ul className="item-list">
        {items.map((item) => (
          <li key={item.id} className="item-card">
            <div>
              <strong>{item.name}</strong>
              {item.description && <p>{item.description}</p>}
            </div>
            <button onClick={() => handleDelete(item.id)} className="delete-btn">Delete</button>
          </li>
        ))}
        {items.length === 0 && <p className="empty">No items yet. Add one above!</p>}
      </ul>
    </div>
  );
}
