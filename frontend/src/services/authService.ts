import type { LoginPayload, TokenResponse } from '../types/auth';

async function post<T>(path: string, body?: unknown, credentials: RequestCredentials = 'omit'): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    credentials,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((detail as { detail?: string }).detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  return post<TokenResponse>('/auth/login', payload);
}

export async function refresh(): Promise<TokenResponse> {
  return post<TokenResponse>('/auth/refresh', undefined, 'include');
}

export async function logout(): Promise<void> {
  return post<void>('/auth/logout', undefined, 'include');
}
