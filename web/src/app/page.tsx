import { getServiceState } from "../lib/readiness";
import AccountLink from "./account-link";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const state = await getServiceState();
  const messages = {
    connected: "服務已就緒",
    disconnected: "資料庫暫時無法連線",
    unreachable: "服務暫時無法連線",
  };
  return (
    <main>
      <header><a href="/" className="brand">Yu Picture<span>雲端圖庫</span></a><AccountLink /></header>
      <section className="intro">
        <p className="eyebrow">你的靈感，值得好好收藏</p>
        <h1>讓每一張圖片，<br />找到它的位置。</h1>
        <p className="description">收藏、整理與分享你的視覺靈感。<br />圖片上傳與空間功能正在開發中。</p>
        <div className="status" role="status" data-testid="service-status" data-state={state}>
          <span className={`dot ${state}`} aria-hidden="true" />{messages[state]}
        </div>
      </section>
      <section className="coming" aria-label="即將提供的功能">
        <article><span>01</span><h2>收藏靈感</h2><p>搜尋與收藏圖片，建立你的素材庫。</p></article>
        <article><span>02</span><h2>整理空間</h2><p>以分類與標籤整理個人圖片。</p></article>
        <article><span>03</span><h2>一起創作</h2><p>與團隊共享素材、協作編輯。</p></article>
      </section>
      <footer>Yu Picture · 雲端圖庫</footer>
    </main>
  );
}
