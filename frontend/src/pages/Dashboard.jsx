import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const navigate = useNavigate();
  const userId = localStorage.getItem("user_id");

  const [camera, setCamera] = useState(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("NORMAL");
  const [form, setForm] = useState({
    camera_name: "",
    ip_url: "",
  });
  const [error, setError] = useState("");

  useEffect(() => {
    if (!userId) {
      navigate("/login");
      return;
    }

    fetch(`http://127.0.0.1:8000/camera/${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error("No camera");
        return res.json();
      })
      .then((data) => {
        setCamera(data);
        setLoading(false);
      })
      .catch(() => {
        setCamera(null);
        setLoading(false);
      });
  }, [userId, navigate]);

  useEffect(() => {
    if (!camera) return;

    const interval = setInterval(() => {
      fetch(`http://127.0.0.1:8000/status/${userId}`)
        .then((res) => res.json())
        .then((data) => {
          if (data?.status) {
            setStatus(data.status);
          }
        })
        .catch(() => {});
    }, 1000);

    return () => clearInterval(interval);
  }, [camera, userId]);

  const addCamera = async () => {
    setError("");

    if (!form.camera_name || !form.ip_url) {
      setError("All fields required");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/camera/${userId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Failed to add camera");
        return;
      }

      setCamera({
        camera_name: form.camera_name,
        ip_url: form.ip_url,
      });
    } catch {
      setError("Backend not reachable");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("user_id");
    localStorage.removeItem("is_logged_in");
    navigate("/");
  };

  if (loading) {
    return (
      <div style={styles.centerContainer}>
        <div style={styles.spinner}></div>
        <p style={{ marginTop: "16px", color: "var(--text-muted)" }}>Initializing AI Core...</p>
      </div>
    );
  }

  const isThreat = status === "THREAT";

  return (
    <div style={styles.container}>
      {/* Top Bar */}
      <div className="glass-panel" style={styles.topbar}>
        <div style={styles.brand}>
          <span style={{ fontSize: "1.25rem" }}>📹</span> Smart CCTV AI Control Panel
        </div>
        <button className="btn-secondary" style={{ padding: "8px 16px", fontSize: "0.85rem" }} onClick={handleLogout}>
          Disconnect
        </button>
      </div>

      <div style={styles.main}>
        {!camera ? (
          <div className="glass-card" style={styles.setupCard}>
            <h3 style={{ marginBottom: "1rem", fontSize: "1.5rem" }}>Connect New Camera</h3>
            <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem" }}>
              Link an IP Webcam to begin real-time neural network analysis.
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <div>
                <label style={styles.label}>Camera Identity</label>
                <input
                  className="glass-input"
                  placeholder="e.g. Front Entrance"
                  onChange={(e) => setForm({ ...form, camera_name: e.target.value })}
                />
              </div>

              <div>
                <label style={styles.label}>Video Stream URL</label>
                <input
                  className="glass-input"
                  placeholder="http://192.168.x.x:8080/video"
                  onChange={(e) => setForm({ ...form, ip_url: e.target.value })}
                />
              </div>

              {error && <p style={styles.error}>{error}</p>}

              <button className="btn-primary" style={{ marginTop: "0.5rem" }} onClick={addCamera}>
                Initialize Link
              </button>
            </div>
          </div>
        ) : (
          <div className={`glass-card ${isThreat ? "threat-active" : ""}`} style={styles.dashboardCard}>
            
            {/* Header Details */}
            <div style={styles.feedHeader}>
              <div>
                <h3 style={{ fontSize: "1.4rem", margin: 0 }}>📍 Feed: {camera.camera_name}</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "4px" }}>
                  Active Neural Nodes: YOLOv8 Weapon / PyTorch CNN-LSTM Violence
                </p>
              </div>

              <div style={{ ...styles.statusBadge, ...(isThreat ? styles.badgeDanger : styles.badgeSafe) }}>
                <span style={styles.statusDot(isThreat)}></span>
                {status}
              </div>
            </div>

            {/* AI Video Feed Wrapper */}
            <div style={styles.videoWrapper}>
              <div style={styles.scanline}></div>
              <img
                src={`http://127.0.0.1:8000/stream/${userId}`}
                alt="Live CCTV"
                style={styles.video}
              />

              <div style={styles.overlayBottom}>
                <span style={{ fontWeight: 600, color: "#fff", letterSpacing: "1px" }}>
                  SYSTEM: ONLINE
                </span>
                <span style={{ color: "rgba(255,255,255,0.7)" }}>Frames: 30FPS</span>
              </div>
            </div>

            <div style={styles.footerNote}>
              <p>Automated threat alerts are being routed to WhatsApp via registered protocols.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
  },
  topbar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "1rem 2rem",
    margin: "1rem",
    marginBottom: "0",
  },
  brand: {
    fontFamily: "var(--font-display)",
    fontWeight: "700",
    color: "#fff",
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  main: {
    flex: 1,
    padding: "2rem",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
  },
  setupCard: {
    width: "100%",
    maxWidth: "500px",
    marginTop: "2rem",
  },
  dashboardCard: {
    width: "100%",
    maxWidth: "1100px",
    padding: "2rem",
    transition: "box-shadow 0.5s ease, border-color 0.5s ease",
  },
  feedHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "1.5rem",
  },
  statusBadge: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 16px",
    borderRadius: "var(--radius-full)",
    fontSize: "0.85rem",
    fontWeight: "700",
    letterSpacing: "1px",
    textTransform: "uppercase",
  },
  badgeSafe: {
    background: "rgba(16, 185, 129, 0.15)",
    color: "var(--accent-safe)",
    border: "1px solid rgba(16, 185, 129, 0.3)",
  },
  badgeDanger: {
    background: "rgba(239, 68, 68, 0.15)",
    color: "var(--accent-threat)",
    border: "1px solid rgba(239, 68, 68, 0.3)",
  },
  statusDot: (isThreat) => ({
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    background: isThreat ? "var(--accent-threat)" : "var(--accent-safe)",
    boxShadow: `0 0 10px ${isThreat ? "var(--accent-threat-glow)" : "var(--accent-safe-glow)"}`,
    animation: "pulse 1.5s infinite",
  }),
  videoWrapper: {
    position: "relative",
    width: "100%",
    borderRadius: "var(--radius-md)",
    overflow: "hidden",
    border: "1px solid var(--surface-border)",
    background: "#000",
    boxShadow: "0 10px 40px rgba(0,0,0,0.5)",
  },
  video: {
    width: "100%",
    display: "block",
    maxHeight: "70vh",
    objectFit: "contain",
  },
  scanline: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    background: "linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))",
    backgroundSize: "100% 4px, 6px 100%",
    zIndex: 10,
    pointerEvents: "none",
  },
  overlayBottom: {
    position: "absolute",
    bottom: "0",
    left: "0",
    width: "100%",
    padding: "1rem 1.5rem",
    background: "linear-gradient(to top, rgba(0,0,0,0.9), transparent)",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    zIndex: 20,
    fontSize: "0.85rem",
    fontFamily: "var(--font-display)",
  },
  footerNote: {
    marginTop: "1.5rem",
    textAlign: "center",
    color: "var(--text-muted)",
    fontSize: "0.9rem",
    borderTop: "1px solid var(--surface-border)",
    paddingTop: "1.5rem",
  },
  label: {
    display: "block",
    fontSize: "0.85rem",
    fontWeight: "600",
    color: "var(--text-muted)",
    textTransform: "uppercase",
    letterSpacing: "1px",
    marginBottom: "0.5rem",
  },
  error: {
    color: "var(--accent-threat)",
    fontSize: "0.9rem",
    marginTop: "0.5rem",
  },
  centerContainer: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
  },
  spinner: {
    width: "40px",
    height: "40px",
    border: "4px solid rgba(59, 130, 246, 0.2)",
    borderTop: "4px solid var(--primary)",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  }
};

export default Dashboard;
