import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { createMsalAuthService } from './auth.js';
import { validateConfig } from './config.js';
import { sessionForAuthUpdate } from './session.js';
import './style.css';

type Membership = { organizationId: string; role: 'user' | 'admin' };
type AuthState = { status: string; account: { username?: string } | null };
type AuthService = ReturnType<typeof createMsalAuthService>;
type AppSession = { status: 'loading' | 'unconfigured' | 'error' | 'signedOut' | 'redirecting' | 'reauthenticationRequired' | 'noMembership' | 'signedIn'; auth?: AuthService; account?: AuthState['account']; memberships?: Membership[]; error?: string };

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
  const [session, setSession] = useState<AppSession>({ status: 'loading' });
  const [organizationId, setOrganizationId] = useState('');
  useEffect(() => {
    let active = true;
    let accessResolved = false;
    let unsubscribe: (() => void) | undefined;
    const start = async () => {
      try {
        let response: Response;
        try { response = await fetch('/config.json', { cache: 'no-store' }); }
        catch { if (active) setSession({ status: 'unconfigured' }); return; }
        if (!response.ok) throw new Error('unconfigured');
        const config = validateConfig(await response.json());
        const auth = createMsalAuthService(config);
        unsubscribe = auth.subscribe((snapshot: AuthState) => {
          if (!active) return;
          if (snapshot.status !== 'signedIn') accessResolved = false;
          setSession(current => sessionForAuthUpdate(current, snapshot, auth, accessResolved) as AppSession);
        });
        await auth.initialize();
        if (!active) return;
        const snapshot = auth.getSnapshot() as AuthState;
        if (snapshot.status !== 'signedIn') return;
        const token = await auth.getAccessToken();
        const me = await fetch(new URL('/api/me', config.apiBaseUrl), { headers: { Authorization: `Bearer ${token}` } });
        if (me.status === 401) { auth.requireSignIn(); return; }
        if (!me.ok) throw new Error('Could not load your workspace access. Try again.');
        const body = await me.json() as { memberships?: Membership[] };
        const memberships = Array.isArray(body.memberships) ? body.memberships : [];
        accessResolved = true;
        if (!memberships.length) { setSession({ status: 'noMembership', auth, account: snapshot.account, memberships }); return; }
        setOrganizationId(memberships[0].organizationId);
        setSession({ status: 'signedIn', auth, account: snapshot.account, memberships });
      } catch (error) {
        if (!active) return;
        const unconfigured = error instanceof Error && (error.message === 'unconfigured' || error.message.includes('config.json'));
        setSession({ status: unconfigured ? 'unconfigured' : 'error', error: error instanceof Error ? error.message : 'Sign-in could not be initialized.' });
      }
    };
    void start();
    return () => { active = false; unsubscribe?.(); };
  }, []);
  useEffect(() => {
    const route = () => { if (!location.hash || pages.some(item => `#${item.id}` === location.hash)) setPage(currentPage()); };
    window.addEventListener('hashchange', route);
    return () => window.removeEventListener('hashchange', route);
  }, []);

  if (session.status === 'loading' || session.status === 'redirecting') return <div className="auth-screen"><div className="auth-card"><div className="brand-icon">✳</div><span className="eyebrow">PHONEBUDDY WORKSPACE</span><h1>{session.status === 'redirecting' ? 'Opening secure sign-in…' : 'Preparing your workspace'}</h1><p>Checking your organization access.</p></div></div>;
  if (session.status === 'unconfigured' || session.status === 'error' || session.status === 'signedOut' || session.status === 'reauthenticationRequired') return <div className="auth-screen"><div className="auth-card"><div className="brand-icon">✳</div><span className="eyebrow">PHONEBUDDY WORKSPACE</span><h1>{session.status === 'unconfigured' ? 'Sign-in is not configured' : session.status === 'error' ? 'We couldn’t load your workspace' : session.status === 'reauthenticationRequired' ? 'Your session needs attention' : 'Sign in to PhoneBuddy'}</h1><p>{session.status === 'unconfigured' ? 'Add the public Entra and API settings to config.json to enable secure sign-in.' : session.status === 'error' ? session.error : session.status === 'reauthenticationRequired' ? 'Sign in again to refresh your secure session.' : 'Use your organization account to open your calling workspace.'}</p>{session.auth && session.status !== 'error' && <button type="button" onClick={() => void session.auth?.signIn()}>{session.status === 'signedOut' ? 'Sign in with Microsoft' : 'Sign in again'}</button>}</div></div>;
  if (session.status === 'noMembership') return <div className="auth-screen"><div className="auth-card"><div className="brand-icon">✳</div><span className="eyebrow">ORGANIZATION ACCESS</span><h1>No workspace access yet</h1><p>Your account is signed in, but it is not an active member of a PhoneBuddy organization. Ask your administrator to grant access.</p><button type="button" onClick={() => void session.auth?.signOut()}>Sign out</button></div></div>;
  return <div className="app">
    <a className="skip" href="#main">Skip to content</a>
    <aside className="sidebar">
      <div className="brand"><span className="brand-icon">✳</span><span>phonebuddy<small>YOUR CALLING WORKSPACE</small></span></div>
      <div className="nav-label">WORKSPACE</div>
      <nav aria-label="Main navigation">{pages.map(item => <a key={item.id} href={`#${item.id}`} aria-current={page === item.id ? 'page' : undefined}><span aria-hidden="true">{item.icon}</span>{item.label}</a>)}</nav>
      <div className="sidebar-bottom"><span className="avatar">{session.account?.username?.slice(0, 2).toUpperCase() || 'PB'}</span><span className="account-text"><span title={session.account?.username}>{session.account?.username || 'Signed in'}</span><small>{session.memberships?.find(item => item.organizationId === organizationId)?.role === 'admin' ? 'Workspace admin' : 'Workspace member'}</small></span><button className="signout" type="button" onClick={() => void session.auth?.signOut()}>Sign out</button></div>
    </aside>
    <div className="workspace">
      <header><span>Workspace <span className="crumb">/</span> <strong>{pages.find(item => item.id === page)?.label}</strong></span><span className="pilot"><span className="dot" /> Pilot workspace</span></header>
      <main id="main" tabIndex={-1}>
          {page === 'dialer' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Ready when you are.</h1><p>Preview the workspace. Calling and backend integration are not available yet.</p></div><span className="status"><span className="dot muted" /> Calling not connected</span></div>{session.memberships && session.memberships.length > 1 && <label className="organization-picker">Organization<select value={organizationId} onChange={event => setOrganizationId(event.target.value)}>{session.memberships.map(item => <option key={item.organizationId} value={item.organizationId}>{item.organizationId} · {item.role}</option>)}</select></label>}<div className="grid"><section className="card dial-card" aria-labelledby="dial-title"><div className="card-head"><div><span className="eyebrow">NEW CALL</span><h2 id="dial-title">Make a call</h2><p>Enter a number to get started.</p></div><span className="card-icon">↗</span></div><label htmlFor="number">Phone number</label><input id="number" type="tel" placeholder="+31  00  000 0000" disabled /><div className="keypad" aria-hidden="true">{['1','2','3','4','5','6','7','8','9','*','0','#'].map(n => <span key={n}>{n}</span>)}</div><button type="button" disabled>☎ &nbsp; Start call</button><p className="helper">Calling will be available once your workspace is connected.</p></section><section className="card activity"><span className="eyebrow">AT A GLANCE</span><h2>Recent activity</h2><p>Your latest calls will appear here.</p><div className="empty-icon">◷</div><h3>No calls yet</h3><p>When you make or receive a call, you’ll find it here.</p><a className="text-link" href="#history">View call history →</a></section></div></>}
          {page === 'history' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Call history</h1><p>Find your recent conversations in one place.</p></div></div><section className="card full-empty"><div className="empty-icon">◷</div><h2>No calls yet</h2><p>Your call history will appear here once calling is connected.</p><a className="text-link" href="#dialer">Go to dialer →</a></section></>}
          {page === 'settings' && <><div className="heading"><div><span className="eyebrow">YOUR WORKSPACE</span><h1>Settings</h1><p>Manage your calling preferences and workspace.</p></div></div><section className="card settings"><span className="eyebrow">CALLING SETUP</span><h2>Workspace settings</h2><p>Audio devices and calling preferences will be available when calling is connected.</p><div className="setting-row"><div><strong>Audio devices</strong><p>Choose your microphone and speaker</p></div><span>Coming soon</span></div><div className="setting-row"><div><strong>Account</strong><p>Manage your workspace connection</p></div><span>Coming soon</span></div></section></>}
      </main><footer>PhoneBuddy <span>·</span> Your conversations, made clearer.</footer>
    </div>
  </div>;
}

const root = document.getElementById('root');
if (!root) throw new Error('Missing application root');
createRoot(root).render(<React.StrictMode><App /></React.StrictMode>);
