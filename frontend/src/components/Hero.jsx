import hero from "../assets/hero-cctv.png";
import { useNavigate } from "react-router-dom";

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section style={styles.heroWrapper}>
      <div className="container" style={styles.inner}>
        
        <div style={styles.textContainer}>
          <div style={styles.badge}>Next-Gen Security</div>
          <h1 style={styles.title}>
            AI-Powered CCTV <br />
            <span className="text-gradient">Weapon & Violence</span> Detection
          </h1>
          <p style={styles.subtitle}>
            Real-time optical surveillance combined with advanced neural networks. Detect threats instantly before they escalate and automate emergency responses.
          </p>
          <div style={styles.actions}>
            <button className="btn-primary" onClick={() => navigate("/signup")}>
              Get Started Free
            </button>
            <button className="btn-secondary" onClick={() => navigate("/login")}>
              View Dashboard
            </button>
          </div>
        </div>

        <div style={styles.imageContainer}>
          <div style={styles.glowBlob}></div>
          <img src={hero} alt="CCTV Control Room" style={styles.image} className="glass-panel" />
        </div>

      </div>
    </section>
  );
};

const styles = {
  heroWrapper: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    paddingTop: "80px", 
    position: "relative",
    overflow: "hidden",
  },
  inner: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "4rem",
    flexWrap: "wrap",
    position: "relative",
    zIndex: 10,
  },
  textContainer: {
    flex: "1 1 500px",
    maxWidth: "600px",
  },
  badge: {
    display: "inline-block",
    padding: "6px 12px",
    background: "rgba(59, 130, 246, 0.1)",
    border: "1px solid rgba(59, 130, 246, 0.3)",
    color: "#60a5fa",
    borderRadius: "var(--radius-full)",
    fontSize: "0.875rem",
    fontWeight: "600",
    marginBottom: "1.5rem",
    letterSpacing: "1px",
    textTransform: "uppercase",
  },
  title: {
    fontSize: "3.5rem",
    lineHeight: "1.1",
    marginBottom: "1.5rem",
  },
  subtitle: {
    color: "var(--text-muted)",
    fontSize: "1.125rem",
    lineHeight: "1.6",
    marginBottom: "2.5rem",
  },
  actions: {
    display: "flex",
    gap: "1rem",
  },
  imageContainer: {
    flex: "1 1 400px",
    position: "relative",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  glowBlob: {
    position: "absolute",
    width: "300px",
    height: "300px",
    background: "var(--primary)",
    filter: "blur(100px)",
    opacity: "0.3",
    borderRadius: "50%",
    zIndex: 0,
  },
  image: {
    width: "100%",
    maxWidth: "550px",
    borderRadius: "var(--radius-lg)",
    position: "relative",
    zIndex: 1,
    padding: "0.5rem",
    background: "rgba(255, 255, 255, 0.03)",
  },
};

export default Hero;
