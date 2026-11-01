import http from 'http'
import { Requester } from './src/lib/modules/requester'
import { AdapterError } from './src/lib/modules/error'

const SECRET = 'TD_LIVE_KEY_abc123SECRET'
// Mock "TwelveData": unknown symbol -> HTTP 200 + {status:'error'} (the case customError is written for)
const srv = http.createServer((req, res) => {
  res.writeHead(200, { 'content-type': 'application/json' })
  res.end(JSON.stringify({ code: 400, message: '**symbol** not found: ' + new URL(req.url!, 'http://x').searchParams.get('symbol'), status: 'error' }))
}).listen(0, async () => {
  const port = (srv.address() as any).port
  // mirrors packages/sources/twelvedata/src/endpoint/price.ts
  const customError = (data: any) => data.status === 'error'
  const options = { baseURL: `http://127.0.0.1:${port}/`, url: 'price', params: { symbol: 'NOSUCHSYMBOL', apikey: SECRET } }
  try {
    await Requester.request<any>(options as any, customError)
  } catch (e: any) {
    // mirrors executeSync() in packages/core/bootstrap/src/index.ts
    const error = new AdapterError(e)
    const body = Requester.errored('1', error, error.providerStatusCode || error.statusCode)
    const json = JSON.stringify(body)
    console.log(json)
    console.log('\nAPI KEY IN HTTP RESPONSE BODY:', json.includes(SECRET))
  }
  srv.close()
})
