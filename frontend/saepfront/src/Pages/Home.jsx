import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Home.module.css";

export default function Home() {
  const navigate = useNavigate();
  const [user, setUser] = useState("");

  useEffect(() => {
    const storedUser = localStorage.getItem("username");
    if (!storedUser) {
      navigate("/");
      return;
    }
    setUser(storedUser);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("username");
    navigate("/");
  };

  return (
    <div className={styles.containerHome}>
      <h1 className={styles.title}>Sistema de Estoque</h1>
      <p className={styles.welcome}>
        Bem-vindo(a), <strong>{user}</strong> 
      </p>

      <button className={styles.button} onClick={() => navigate("/produtos")}>
        Cadastro de Produtos
      </button>

      <button className={styles.button} onClick={() => navigate("/estoque")}>
        Gestão de Estoque
      </button>

      <button className={`${styles.button} ${styles.logout}`} onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}
