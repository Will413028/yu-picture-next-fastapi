"use client";
import { useEffect, useState } from "react";
import { api, User } from "../lib/api";

export default function AccountLink() {
  const [name, setName] = useState("我的帳號");
  useEffect(() => { api<User>("/auth/me").then(user => setName(user.name)).catch(() => {}); }, []);
  return <a className="account-link" href="/account">{name}</a>;
}
