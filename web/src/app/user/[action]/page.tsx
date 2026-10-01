import { notFound, redirect } from "next/navigation";

export default async function LegacyAccountEntry({ params }: { params: Promise<{ action: string }> }) {
  const { action } = await params;
  if (!["login", "register", "membership"].includes(action)) notFound();
  redirect(action === "register" ? "/account?mode=register" : "/account");
}
