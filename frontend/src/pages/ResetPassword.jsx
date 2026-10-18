import { useState } from "react";
import { useNavigate } from "react-router-dom";

const ResetPassword = () => {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleReset = async () => {
    setError("");
    setSuccess("");

    try {
      const res = await fetch("http://127.0.0.1:8000/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          new_password: newPassword,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Reset failed");
        return;
      }
      
      setSuccess("Success! Redirecting to login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch {
      setError("Backend not reachable");
    }
  };

  return (
    <div style={styles.container}>
      <div className="glass-panel" style={styles.card}>
        <div style={styles.header}>
          <h2 style={styles.title}>Reset Password</h2>
          <p style={styles.subtitle}>Enter your new credentials below</p>
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>Username</label>
          <input
            className="glass-input"
            placeholder="admin"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div style={styles.formGroup}>
          <label style={styles.label}>New Password</label>
          <div style={styles.passwordWrapper}>
            <input
              type={showPassword ? "text" : "password"}
              className="glass-input"
              placeholder="••••••••"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
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
        {success && <p style={styles.success}>{success}</p>}

        <button className="btn-primary" style={styles.button} onClick={handleReset}>
          Reset Password
        </button>

        <p style={styles.text}>
          Back to{" "}
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
    maxWidth: "420px",
    display: "flex",
    flexDirection: "column",
    gap: "1.5rem",
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
    marginTop: "0.5rem",
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
  success: {
    color: "var(--accent-safe)",
    fontSize: "0.9rem",
    textAlign: "center",
  }
};

export default ResetPassword;
