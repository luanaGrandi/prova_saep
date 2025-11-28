import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import styles from "./Produtos.module.css";

const API_URL = "http://localhost:8000/api/produtos/";
const REFRESH_URL = "http://localhost:8000/api/auth/refresh/";

export default function Produto() {
  const navigate = useNavigate();
  const [produtos, setProdutos] = useState([]);
  const [busca, setBusca] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({
    id: null,
    nome: "",
    descricao: "",
    preco: "",
    quantidade_estoque: "",
    estoque_min: ""
  });

  const token = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");

  const api = axios.create({
    baseURL: API_URL,
    headers: { Authorization: `Bearer ${token}` }
  });

  // Refresh automático do token
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      if (error.response?.status === 401 && refreshToken) {
        try {
          const res = await axios.post(REFRESH_URL, { refresh: refreshToken });
          localStorage.setItem("access_token", res.data.access);
          api.defaults.headers.Authorization = `Bearer ${res.data.access}`;
          return axios(error.config);
        } catch {
          localStorage.clear();
          navigate("/");
        }
      }
      return Promise.reject(error);
    }
  );

  useEffect(() => {
    if (!token) return navigate("/");
    carregarProdutos();
  }, []);

  const carregarProdutos = () => {
    api.get("/")
      .then((res) => setProdutos(res.data))
      .catch(() => console.log("Erro ao carregar produtos"));
  };

  const salvarProduto = () => {
    if (!form.nome || !form.preco || !form.estoque_min) {
      alert("Preencha os campos obrigatórios!");
      return;
    }

    const dados = {
      nome: form.nome,
      descricao: form.descricao,
      preco: Number(form.preco),
      quantidade_estoque: Number(form.quantidade_estoque),
      estoque_min: Number(form.estoque_min)
    };

    const request = form.id
      ? api.put(`${form.id}/`, dados)
      : api.post("/", dados);

    request
      .then(() => {
        carregarProdutos();
        fecharModal();
      })
      .catch((err) => {
        const msg = err.response?.data?.detail || "Erro ao salvar produto!";
        alert(msg);
      });
  };

  const excluirProduto = (id) => {
    if (!window.confirm("Tem certeza que deseja excluir este produto?")) return;

    api.delete(`${id}/`)
      .then(() => carregarProdutos())
      .catch((err) => {
        const msg = err.response?.data?.detail || "Erro ao excluir produto!";
        alert(msg);
      });
  };

  const filtrar = () => {
    api.get(`/?search=${busca}`)
      .then((res) => setProdutos(res.data));
  };

  const abrirModal = (produto = null) => {
    if (produto) setForm(produto);
    else limparForm();
    setIsModalOpen(true);
  };

  const fecharModal = () => {
    setIsModalOpen(false);
    limparForm();
  };

  const limparForm = () => {
    setForm({
      id: null,
      nome: "",
      descricao: "",
      preco: "",
      quantidade_estoque: "",
      estoque_min: ""
    });
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Cadastro de Produtos</h2>

      <button className={styles.backButton} onClick={() => navigate("/home")}>
        ⬅ Voltar
      </button>

      <div className={styles.searchBox}>
        <input
          className={styles.inputSearch}
          placeholder="Buscar..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
        />
        <button className={styles.btnPrimary} onClick={filtrar}>Buscar</button>
      </div>

      <button className={styles.btnSuccess} onClick={() => abrirModal()}>
        Cadastrar
      </button>

      {/* MODAL */}
      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3>{form.id ? "Editar Produto" : "Novo Produto"}</h3>

            <input
              className={styles.input}
              placeholder="Nome"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
            />
            <input
              className={styles.input}
              placeholder="Descrição"
              value={form.descricao}
              onChange={(e) => setForm({ ...form, descricao: e.target.value })}
            />
            <input
              className={styles.input}
              type="number"
              placeholder="Preço"
              value={form.preco}
              onChange={(e) => setForm({ ...form, preco: e.target.value })}
            />
            <input
              className={styles.input}
              type="number"
              placeholder="Estoque"
              value={form.quantidade_estoque}
              onChange={(e) => setForm({ ...form, quantidade_estoque: e.target.value })}
            />
            <input
              className={styles.input}
              type="number"
              placeholder="Estoque Mínimo"
              value={form.estoque_min}
              onChange={(e) => setForm({ ...form, estoque_min: e.target.value })}
            />

            <div className={styles.modalButtons}>
              <button className={styles.btnSuccess} onClick={salvarProduto}>
                {form.id ? "Salvar" : "Cadastrar"}
              </button>
              <button className={styles.btnWarning} onClick={fecharModal}>
                Fechar
              </button>
            </div>
          </div>
        </div>
      )}

      <h3 className={styles.subtitle}>Produtos Cadastrados</h3>

      <table className={styles.table}>
        <thead>
          <tr>
            <th>ID</th><th>Nome</th><th>Descrição</th><th>Preço</th>
            <th>Estoque</th><th>Min.</th><th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {produtos.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.nome}</td>
              <td>{p.descricao}</td>
              <td>R$ {p.preco}</td>
              <td>{p.quantidade_estoque}</td>
              <td className={p.quantidade_estoque <= p.estoque_min ? styles.estoqueBaixo : ""}>
                {p.estoque_min}
              </td>
              <td>
                <button className={styles.btnEdit} onClick={() => abrirModal(p)}>Editar</button>
                <button className={styles.btnDelete} onClick={() => excluirProduto(p.id)}>Excluir</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
