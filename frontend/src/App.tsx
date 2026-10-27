import { useState, type FormEvent } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ?? "Não foi possível realizar o login."
        );
      }

      // Confirmação temporária durante o desenvolvimento.
      console.log("Login realizado com sucesso!", data);
      alert("Login realizado com sucesso!");
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          "Não foi possível conectar à API. Verifique se ela está ativa."
        );
      } else {
        setError(
          err instanceof Error
            ? err.message
            : "Ocorreu um erro inesperado."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="brand">
          <img
            src="/stackflow-logo.png"
            alt="Logo do StackFlow"
            className="brand-logo"
          />
          <span className="brand-name">
            Stack<span>Flow</span>
          </span>
        </div>

        <div className="login-heading">
          <h2>Bem-vindo de volta</h2>
          <p>Entre na sua conta para continuar.</p>
        </div>

        <form className="login-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">E-mail</label>
            <input
              id="email"
              type="email"
              placeholder="voce@empresa.com"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              id="password"
              type="password"
              placeholder="Digite sua senha"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error && (
            <p className="login-error" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={loading}>
            {loading ? "Entrando..." : "Entrar na plataforma"}
          </button>
        </form>

        <p className="login-footer">
          Gestão inteligente de estoque.
        </p>
      </section>
    </main>
  );
}

export default App;
