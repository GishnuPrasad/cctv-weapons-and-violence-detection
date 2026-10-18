import logo from "../assets/logo.png";
import { useNavigate } from "react-router-dom";

const Navbar = () => {
  const navigate = useNavigate();

  return (
    <nav className="glass-panel" style={styles.nav}>
      <div className="container" style={styles.inner}>
        <div style={styles.left} onClick={() => navigate("/")}>
          <img src={logo} alt="logo" style={styles.logo} />
          <span className="text-gradient" style={styles.brand}>Smart CCTV AI</span>
        </div>
        <div style={styles.right}>
          <button className="btn-secondary" onClick={() => navigate("/login")}>
            Login
          </button>
          <button className="btn-primary" onClick={() => navigate("/signup")}>
            Sign Up
          </button>
        </div>
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    position: "fixed",
    top: "1rem",
    left: "50%",
    transform: "translateX(-50%)",
    width: "calc(100% - 2rem)",
    maxWidth: "1200px",
    zIndex: 1000,
    borderRadius: "16px",
    borderTop: "1px solid rgba(255,255,255,0.1)",
  },
  inner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    height: "70px",
    padding: "0 1.5rem",
  },
  left: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    cursor: "pointer",
  },
  logo: {
    width: "40px",
    height: "40px",
    objectFit: "contain",
  },
  brand: {
    fontSize: "1.25rem",
    fontWeight: "700",
    fontFamily: "var(--font-display)",
    letterSpacing: "1px",
  },
  right: {
    display: "flex",
    gap: "1rem",
  }
};

export default Navbar;
