const handler: ProxyHandler<object> = { get: (_, prop: string) => prop }
export default new Proxy({}, handler)
