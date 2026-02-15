import Sidebar from "../components/Sidebar";

const AdminLayout = ({ children }) => {
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar />
      <div style={{ flex: 1, padding: "20px", background: "#f4f6f9" }}>
        {children}
      </div>
    </div>
  );
};

export default AdminLayout;
