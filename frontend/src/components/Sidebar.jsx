import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div
      style={{
        width: "220px",
        background: "#1f2937",
        color: "white",
        padding: "20px",
      }}
    >
      <h2>NGR Pharma</h2>

      <div
        style={{
          marginTop: "30px",
          display: "flex",
          flexDirection: "column",
          gap: "15px",
        }}
      >
        <Link to="/" style={{ color: "white", textDecoration: "none" }}>
          Dashboard
        </Link>
        <Link to="/finance" style={{ color: "white", textDecoration: "none" }}>
          Finance
        </Link>
        <Link to="/stock" style={{ color: "white", textDecoration: "none" }}>
          Stock
        </Link>
      </div>
    </div>
  );
};

export default Sidebar;
