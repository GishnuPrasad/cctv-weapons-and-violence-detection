import { useState } from "react";
import { useNavigate } from "react-router-dom";

const Signup = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    username: "",
    mobile_number: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleSignup = async () => {
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8000/signup", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Signup failed");
        return;
      }

      navigate("/login");
    } catch {
      setError("Backend not reachable");
    }
  };

  return (
    <div style={styles.container}>
      <div className="glass-panel" style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.title}>Create Account</h2>
          <p style={styles.subtitle}>Register to monitor your cameras with AI</p>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Full Name</label>
          <input
            className="glass-input"
            placeholder="John Doe"
            onChange={(e) => setForm({ ...form, name: e.target.value })}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Username</label>
          <input
            className="glass-input"
            placeholder="johndoe123"
            onChange={(e) => setForm({ ...form, username: e.target.value })}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Mobile Number</label>
          <input
            className="glass-input"
            placeholder="+1234567890"
            onChange={(e) => setForm({ ...form, mobile_number: e.target.value })}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Password</label>
          <div style={styles.passwordWrapper}>
            <input
              type={showPassword ? "text" : "password"}
              className="glass-input"
              placeholder="••••••••"
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            <span
              style={styles.eye}
              onClick={() => setShowPassword(!showPassword)}
            >
               {showPassword ? "🙈" : "👁️"}
            </span>
          </div>
        </div>

        {error && <p style={styles.error}>{error}</p>}

        <button className="btn-primary" style={styles.button} onClick={handleSignup}>
          Register
        </button>

        <p style={styles.text}>
          Already registered?{" "}
          <span style={styles.link} onClick={() => navigate("/login")}>
            Sign In
          </span>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    padding: "20px",
  },
  card: {
    padding: "2.5rem",
    width: "100%",
    maxWidth: "480px",
    display: "flex",
    flexDirection: "column",
    gap: "1.25rem",
  },
  header: {
    textAlign: "center",
    marginBottom: "0.5rem",
  },
  title: {
    fontSize: "1.75rem",
    marginBottom: "0.5rem",
    color: "#fff",
  },
  subtitle: {
    color: "var(--text-muted)",
    fontSize: "0.95rem",
  },
  formGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  label: {
    fontSize: "0.85rem",
    fontWeight: "600",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  passwordWrapper: {
    position: "relative",
    width: "100%",
  },
  eye: {
    position: "absolute",
    right: "12px",
    top: "50%",
    transform: "translateY(-50%)",
    cursor: "pointer",
    userSelect: "none",
  },
  button: {
    width: "100%",
    marginTop: "1rem",
    padding: "14px",
  },
  text: {
    textAlign: "center",
    fontSize: "0.9rem",
    color: "var(--text-muted)",
  },
  link: {
    color: "var(--primary)",
    cursor: "pointer",
    fontWeight: "600",
  },
  error: {
    color: "var(--accent-threat)",
    fontSize: "0.9rem",
    textAlign: "center",
  },
};

export default Signup;
