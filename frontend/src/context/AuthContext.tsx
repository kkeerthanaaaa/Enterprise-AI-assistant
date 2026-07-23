import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { api } from "../lib/api";
import { UserOut } from "../types";

interface AuthContextValue {
  user: UserOut | null;
  loading: boolean;
  login: (companySlug: string, email: string, password: string) => Promise<void>;
  registerCompany: (data: {
    company_name: string;
    company_slug: string;
    admin_full_name: string;
    admin_email: string;
    admin_password: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("user");
    if (stored) setUser(JSON.parse(stored));
    setLoading(false);
  }, []);

  function persist(tokens: { access_token: string; refresh_token: string }, u: UserOut) {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    localStorage.setItem("user", JSON.stringify(u));
    setUser(u);
  }

  async function login(companySlug: string, email: string, password: string) {
    const res = await api.post("/auth/login", { company_slug: companySlug, email, password });
    persist(res.data.tokens, res.data.user);
  }

  async function registerCompany(data: {
    company_name: string;
    company_slug: string;
    admin_full_name: string;
    admin_email: string;
    admin_password: string;
  }) {
    const res = await api.post("/auth/register-company", data);
    persist(res.data.tokens, res.data.user);
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, registerCompany, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
