import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { validateConfig } from './config.js';
import './style.css';

type Page = 'dialer' | 'history' | 'settings';
const pages: { id: Page; icon: string; label: string }[] = [
  { id: 'dialer', icon: '◉', label: 'Dialer' },
  { id: 'history', icon: '◷', label: 'Call history' },
  { id: 'settings', icon: '⚙', label: 'Settings' },
];
function currentPage(): Page {
  const page = location.hash.slice(1);
  return pages.some(item => item.id === page) ? page as Page : 'dialer';
}
function App() {
  const [page, setPage] = useState<Page>(currentPage);
  const [config, setConfig] = useState<'loading' | 'ready' | string>('loading');
  useEffect(() => {
    const route = () => { if (pages.some(item => `#${item.id}` === location.hash)) setPage(currentPage()); };
    window.addEventListener('hashchange', route);
    const controller = new AbortController();
    fetch(`${import.meta.env.BASE_URL}config.json`, { signal: controller.signal, cache: 'no-store' })
      .then(response => { if (!response.ok) throw new Error('Add a public config.json next to the application with an apiBaseUrl.'); return response.json(); })
      .then(value => { validateConfig(value); setConfig('ready'); })
      .catch(error => { if (!controller.signal.aborted) setConfig(error instanceof Error ? error.message : 'Unable to load configuration.'); });
    return () => { controller.abort(); window.removeEventListener('hashchange', route); };
  }, []);
  return <div className="app">
    <a className="skip" href="#main">Skip to content</a>
    <aside className="sidebar">
      <div className="brand"><span className="brand-icon">✳</span><span>phonebuddy<small>YOUR CALLING WORKSPACE</small></span></div>
      <div className="nav-label">WORKSPACE</div>
      <nav aria-label="Main navigation">{pages.map(item => <a key={item.id} href={`#${item.id}`} aria-current={page === item.id ? 'page' : undefined}><span aria-hidden="true">{item.icon}</span>{item.label}</a>)}</nav>
      <div className="sidebar-bottom"><span className="avatar">PB</span><span>Internal pilot<small>Workspace</small></span><span className="dots">···</span></div>
    </aside>
    <div className="workspace">
      <header><span>Workspace <span className="crumb">/</span> <strong>{pages.find(item => item.id === page)?.label}</strong></span><span className="pilot"><span className="dot" /> Pilot workspace</span></header>
      <main id="main" tabIndex={-1}>
        {config === 'loading' ? <div className="message" role="status"><h1>Getting things ready</h1><p>Loading workspace configuration…</p></div> : config !== 'ready' ? <div className="message" role="alert"><span className="eyebrow">SETUP REQUIRED</span><h1>We couldn’t start your workspace</h1><p>{config}</p><p>Ask your administrator to check the public configuration, then reload this page.</p><button onClick={() => location.reload()}>Try again</button></div> : <>
          {page === 'dialer' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Ready when you are.</h1><p>Make and manage your calls, all in one place.</p></div><span className="status"><span className="dot muted" /> Calling not connected</span></div><div className="grid"><section className="card dial-card" aria-labelledby="dial-title"><div className="card-head"><div><span className="eyebrow">NEW CALL</span><h2 id="dial-title">Make a call</h2><p>Enter a number to get started.</p></div><span className="card-icon">↗</span></div><label htmlFor="number">Phone number</label><input id="number" type="tel" placeholder="+31  00  000 0000" disabled /><div className="keypad" aria-hidden="true">{['1','2','3','4','5','6','7','8','9','*','0','#'].map(n => <span key={n}>{n}</span>)}</div><button disabled>☎ &nbsp; Start call</button><p className="helper">Calling will be available once your workspace is connected.</p></section><section className="card activity"><span className="eyebrow">AT A GLANCE</span><h2>Recent activity</h2><p>Your latest calls will appear here.</p><div className="empty-icon">◷</div><h3>No calls yet</h3><p>When you make or receive a call, you’ll find it here.</p><a className="text-link" href="#history">View call history →</a></section></div></>}
          {page === 'history' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Call history</h1><p>Find your recent conversations in one place.</p></div></div><section className="card full-empty"><div className="empty-icon">◷</div><h2>No calls yet</h2><p>Your call history will appear here once calling is connected.</p><a className="text-link" href="#dialer">Go to dialer →</a></section></>}
          {page === 'settings' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Settings</h1><p>Manage your calling preferences and workspace.</p></div></div><section className="card settings"><span className="eyebrow">CALLING SETUP</span><h2>Workspace settings</h2><p>Audio devices and calling preferences will be available when calling is connected.</p><div className="setting-row"><div><strong>Audio devices</strong><p>Choose your microphone and speaker</p></div><span>Coming soon</span></div><div className="setting-row"><div><strong>Account</strong><p>Manage your workspace connection</p></div><span>Coming soon</span></div></section></>}
        </>}
      </main><footer>PhoneBuddy <span>·</span> Your conversations, made clearer.</footer>
    </div>
  </div>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);
