export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const ROUTES = {
  MARKETPLACE: 'marketplace',
  CHAT: 'chat',
} as const