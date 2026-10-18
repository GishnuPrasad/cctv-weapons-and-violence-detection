import weapon from "../assets/weapon.png";
import violence from "../assets/violence.png";
import live from "../assets/live.png";
import alert from "../assets/alert.png";

const features = [
  { img: weapon, title: "Weapon Detection", desc: "Instantly recognizes firearms and knives using customized YOLO models." },
  { img: violence, title: "Violence Detection", desc: "Analyzes video sequences with PyTorch CNN-LSTM architectures." },
  { img: live, title: "Live Monitoring", desc: "View all your registered camera feeds in real-time through the dashboard." },
  { img: alert, title: "Instant Alerts", desc: "Automated WhatsApp notifications with snapshots attached within seconds." },
];

const Features = () => {
  return (
    <section style={styles.section}>
      <div className="container">
        <div style={styles.header}>
          <h2 style={styles.heading}>Intelligent Features</h2>
          <p style={styles.subText}>Everything you need to secure your premises autonomously.</p>
        </div>
        
        <div className="grid-2">
          {features.map((f, i) => (
            <div key={i} className="glass-card" style={styles.card}>
              <div style={styles.iconWrapper}>
                <img src={f.img} alt={f.title} style={styles.icon} />
              </div>
              <h3 style={styles.cardTitle}>{f.title}</h3>
              <p style={styles.cardDesc}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

const styles = {
  section: {
    padding: "6rem 0",
    position: "relative",
  },
  header: {
    textAlign: "center",
    marginBottom: "4rem",
  },
  heading: {
    fontSize: "2.5rem",
    marginBottom: "1rem",
  },
  subText: {
    color: "var(--text-muted)",
    fontSize: "1.1rem",
    maxWidth: "600px",
    margin: "0 auto",
  },
  card: {
    textAlign: "left",
    display: "flex",
    flexDirection: "column",
    gap: "1rem",
  },
  iconWrapper: {
    width: "64px",
    height: "64px",
    background: "rgba(59, 130, 246, 0.1)",
    borderRadius: "16px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: "0.5rem",
    border: "1px solid rgba(59, 130, 246, 0.2)",
  },
  icon: {
    width: "36px",
    height: "36px",
    objectFit: "contain",
    filter: "drop-shadow(0 0 8px rgba(255,255,255,0.8))",
  },
  cardTitle: {
    fontSize: "1.25rem",
    color: "#fff",
  },
  cardDesc: {
    color: "var(--text-muted)",
    fontSize: "0.95rem",
    lineHeight: "1.6",
  }
};

export default Features;
