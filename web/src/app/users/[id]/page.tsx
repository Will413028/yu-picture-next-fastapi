import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

type Profile = { id: string; name: string; avatar: string | null; profile: string | null; created_at: string };
export default async function ProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^\d+$/.test(id)) notFound();
  let profile: Profile | null = null;
  try {
    const base = process.env.API_BASE_URL ?? "http://127.0.0.1:8009";
    const response = await fetch(`${base}/api/v1/users/${id}`, {
      cache: "no-store", signal: AbortSignal.timeout(4000),
    });
    if (response.status === 404) notFound();
    if (response.ok) profile = await response.json();
  } catch (error) {
    if (typeof error === "object" && error !== null && "digest" in error) throw error;
  }
  return <main><header><a className="brand" href="/">Yu Picture</a></header>
    <section className="account-panel">
      {profile ? <>
        {profile.avatar && /^https?:\/\//.test(profile.avatar) && <img src={profile.avatar} alt={`${profile.name}的頭像`} width={96} height={96} referrerPolicy="no-referrer" />}
        <h1>{profile.name}</h1><p>{profile.profile || "尚未提供簡介"}</p><p>加入日期：{new Date(profile.created_at).toLocaleDateString("zh-TW")}</p>
      </> : <p role="status">服務暫時無法使用</p>}
    </section>
  </main>;
}
