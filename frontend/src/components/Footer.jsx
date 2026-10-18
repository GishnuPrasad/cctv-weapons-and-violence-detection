const Footer = () => {
  return (
    <footer style={styles.footer}>
      <div className="container" style={styles.inner}>
        <div style={styles.text}>
          <span style={styles.brand}>Smart CCTV AI</span>
          <p style={styles.subText}>© 2026 Final Year Project. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

const styles = {
  footer: {
    borderTop: "1px solid var(--surface-border)",
    background: "rgba(0,0,0,0.5)",
    backdropFilter: "blur(10px)",
    padding: "2rem 0",
    marginTop: "4rem",
  },
  inner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  brand: {
    fontFamily: "var(--font-display)",
    fontWeight: "700",
    fontSize: "1.2rem",
    color: "var(--text-main)",
  },
  subText: {
    color: "var(--text-muted)",
    fontSize: "0.9rem",
    marginTop: "0.25rem",
  }
};

export default Footer;
