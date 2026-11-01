export const getEnv = (n: string) => ({ RETRY: '1', TIMEOUT: '3000', NODE_ENV: 'production', DEBUG: 'false' } as Record<string,string>)[n]
export const getEnvWithFallback = (n: string, _f: string[]) => getEnv(n)
export const parseBool = (v: unknown) => v === true || v === 'true'
export const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms))
export const isObject = (o: unknown) => o !== null && typeof o === 'object' && !Array.isArray(o)
export const deepType = (o: unknown) => (isObject(o) ? 'object' : Array.isArray(o) ? 'array' : typeof o)
export const isArraylikeAccessor = (_p: unknown) => false
