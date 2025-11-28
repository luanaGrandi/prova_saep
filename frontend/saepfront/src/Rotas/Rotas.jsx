import { Routes, Route } from "react-router-dom";
import Login from "../Pages/login";
import Home from "../Pages/Home";
import Produto from "../Pages/Produto";
import Estoque from "../Pages/Estoque";

export default function Rotas() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/home" element={<Home />} />
      <Route path="/produtos" element={<Produto />} />
      <Route path="/estoque" element={<Estoque />} />
    </Routes>
  );
}
