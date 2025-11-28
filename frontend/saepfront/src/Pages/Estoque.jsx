import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Estoque.module.css";

const API_MOV = "http://localhost:8000/api/movimentacoes/";
const API_PRODUTOS = "http://localhost:8000/api/produtos/";
const REFRESH_URL = "http://localhost:8000/api/auth/refresh/";

export default function Estoque() {
  const navigate = useNavigate();

  const [movimentos, setMovimentos] = useState([]);
  const [produtos, setProdutos] = useState([]);
  const [form, setForm] = useState({
    id: null,
    produto: "",
    tipo: "entrada",
    quantidade: ""
  });

  const token = localStorage.getItem("access_token");
  const refreshToken = localStorage.getItem("refresh_token");

  const api = axios.create({
    baseURL: API_MOV,
    headers: { Authorization: `Bearer ${token}` }
  });

  // 🔄 Auto refresh do token
  api.interceptors.response.use(
    (res) => res,
    async (err) => {
      if (err.response?.status === 401 && refreshToken) {
        try {
          const res = await axios.post(REFRESH_URL, { refresh: refreshToken });
          localStorage.setItem("access_token", res.data.access);
          api.defaults.headers.Authorization = `Bearer ${res.data.access}`;
          return axios(err.config);
        } catch {
          localStorage.clear();
          navigate("/");
        }
      }
      return Promise.reject(err);
    }
  );

  useEffect(() => {
    if (!token) return navigate("/");
    carregarProdutos();
    carregarMovimentacoes();
  }, []);

  const carregarProdutos = () => {
    axios
      .get(API_PRODUTOS, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        const ordenado = [...res.data].sort((a, b) => a.nome.localeCompare(b.nome));
        setProdutos(ordenado);
      });
  };

  const carregarMovimentacoes = () => {
    api.get("/")
      .then((res) => setMovimentos(res.data))
      .catch(() => alert("Erro ao carregar movimentações!"));
  };

  const salvarMovimentacao = () => {
    if (!form.produto || !form.quantidade) {
      alert("Preencha todos os campos!");
      return;
    }

    const dados = {
      produto: form.produto,
      tipo: form.tipo,
      quantidade: Number(form.quantidade)
    };

    const request = form.id
      ? api.put(`${form.id}/`, dados)
      : api.post("/", dados);

    request
      .then(() => {
        // Atualiza lista de movimentações
        carregarMovimentacoes();
        limparForm();

        // ⚠️ Verificação de estoque mínimo após saída
        if (form.tipo === "saida") {
          const produtoAtual = produtos.find(p => p.id === Number(form.produto));
          if (produtoAtual) {
            const estoqueAtualizado = produtoAtual.quantidade_estoque - Number(form.quantidade);
            if (estoqueAtualizado <= produtoAtual.estoque_min) {
              alert(
                `⚠️ Atenção: Estoque do produto "${produtoAtual.nome}" abaixo do mínimo (${produtoAtual.estoque_min}).`
              );
            }
          }
        }
      })
      .catch(() => alert("Erro ao salvar movimentação!"));
  };

  const excluirMovimentacao = (id) => {
    if (!window.confirm("Deseja realmente excluir esta movimentação?")) return;

    api.delete(`${id}/`)
      .then(() => carregarMovimentacoes())
      .catch(() => alert("Erro ao excluir!"));
  };

  const limparForm = () => {
    setForm({
      id: null,
      produto: "",
      tipo: "entrada",
      quantidade: ""
    });
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Gestão de Estoque</h2>

      <button className={styles.backButton} onClick={() => navigate("/home")}>
        ⬅ Voltar
      </button>

      {/* Formulário */}
      <div className={styles.form}>
        <select
          className={styles.select}
          value={form.produto}
          onChange={(e) => setForm({ ...form, produto: e.target.value })}
        >
          <option value="">Selecione o produto</option>
          {produtos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nome}
            </option>
          ))}
        </select>

        <select
          className={styles.select}
          value={form.tipo}
          onChange={(e) => setForm({ ...form, tipo: e.target.value })}
        >
          <option value="entrada">Entrada</option>
          <option value="saida">Saída</option>
        </select>

        <input
          className={styles.input}
          type="number"
          placeholder="Quantidade"
          value={form.quantidade}
          onChange={(e) => setForm({ ...form, quantidade: e.target.value })}
        />

        <button className={styles.btnSave} onClick={salvarMovimentacao}>
          {form.id ? "Atualizar" : "Confirmar"}
        </button>

        {form.id && (
          <button className={styles.btnCancel} onClick={limparForm}>
            Cancelar
          </button>
        )}
      </div>

      {/* Lista de Movimentos (Cards) */}
      <div className={styles.cardsContainer}>
        {movimentos.map((mov) => (
          <div
            key={mov.id}
            className={`${styles.card} ${mov.tipo === "entrada" ? styles.entrada : styles.saida}`}
          >
            <p className={styles.cardTitle}>
              {mov.tipo === "entrada" ? "📦 Entrada" : "🚚 Saída"}
            </p>

            <p className={styles.info}><b>Produto:</b> {mov.produto_nome}</p>
            <p className={styles.info}><b>Quantidade:</b> {mov.quantidade}</p>
            <p className={styles.info}>
              <b>Data:</b> {new Date(mov.data_movimentacao).toLocaleString()}
            </p>

            <div className={styles.cardButtons}>
              <button
                className={styles.btnEdit}
                onClick={() =>
                  setForm({
                    id: mov.id,
                    produto: mov.produto,
                    tipo: mov.tipo,
                    quantidade: mov.quantidade
                  })
                }
              >
                Editar
              </button>

              <button
                className={styles.btnDelete}
                onClick={() => excluirMovimentacao(mov.id)}
              >
                Excluir
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
