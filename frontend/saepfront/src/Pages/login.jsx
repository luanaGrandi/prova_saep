import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./Login.module.css";

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      const resp = await axios.post("http://localhost:8000/api/auth/login/", {
        username,
        password,
      });

      const data = resp.data;
      localStorage.setItem("access_token", data.access);
      localStorage.setItem("refresh_token", data.refresh);
      localStorage.setItem("username", username);

      navigate("/home");
    } catch (err) {
      if (err.response) {
        const msg =
          (err.response.data && (err.response.data.detail || JSON.stringify(err.response.data))) ||
          `Erro do servidor: ${err.response.status}`;
        setError(msg);
      } else if (err.request) {
        setError("Sem resposta do servidor. Verifique o backend.");
      } else {
        setError("Erro ao enviar requisição: " + err.message);
      }
      setPassword("");
    }
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>SAEP - Login</h2>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className={styles.input}
          />
        </div>

        <div className={styles.formGroup}>
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className={styles.input}
          />
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button type="submit" className={styles.button}>
          Entrar
        </button>
      </form>
    </div>
  );
}
