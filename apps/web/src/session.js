/** Preserve the API's resolved access decision across silent token renewal. */
export function sessionForAuthUpdate(current, snapshot, auth, accessResolved) {
  if (snapshot.status === 'signedIn' && accessResolved) {
    return { ...current, auth, account: snapshot.account };
  }
  return {
    status: snapshot.status === 'signedIn' ? 'loading' : snapshot.status,
    auth,
    account: snapshot.account,
  };
}
