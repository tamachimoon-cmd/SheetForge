import { useMemo, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const stats = useMemo(() => {
    if (!result) return null
    const analysis = result.analysis
    return {
      sheets: analysis.workbook.sheet_count,
      entities: analysis.entities.length,
      relationships: analysis.relationships.length,
      fields: analysis.entities.reduce((sum, entity) => sum + entity.fields.length, 0),
      formulas: analysis.entities.reduce((sum, entity) => sum + entity.formula_count, 0),
    }
  }, [result])

  async function analyze(event) {
    event.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setResult(null)

    const body = new FormData()
    body.append('file', file)

    try {
      const response = await fetch(`${API_URL}/api/analyze`, { method: 'POST', body })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'Falha na análise.')
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <span className="eyebrow">SHEETFORGE / MVP 0.1</span>
        <h1>Da planilha nasce o sistema.</h1>
        <p>Envie um Excel ou CSV. O SheetForge identifica a estrutura dos dados e gera o primeiro schema da aplicação.</p>
      </header>

      <section className="panel upload-panel">
        <form onSubmit={analyze}>
          <label className="dropzone">
            <input
              type="file"
              accept=".xlsx,.csv"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
            <span>{file ? file.name : 'Selecione ou arraste uma planilha'}</span>
            <small>.xlsx ou .csv</small>
          </label>
          <button disabled={!file || loading}>{loading ? 'Analisando…' : 'Forjar aplicação'}</button>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      {stats && (
        <>
          <section className="stats">
            {Object.entries(stats).map(([key, value]) => (
              <article className="stat" key={key}>
                <strong>{value}</strong>
                <span>{key}</span>
              </article>
            ))}
          </section>

          <section className="panel">
            <div className="panel-title">
              <div>
                <span className="eyebrow">APP SCHEMA</span>
                <h2>Estrutura inferida</h2>
              </div>
              <span className="badge">v{result.app_schema.schemaVersion}</span>
            </div>

            <div className="entities">
              {result.app_schema.entities.map((entity) => (
                <article className="entity" key={entity.name}>
                  <h3>{entity.label}</h3>
                  <p>PK: {entity.primaryKey || 'não identificada'}</p>
                  <ul>
                    {entity.fields.map((field) => (
                      <li key={field.name}>
                        <span>{field.label}</span>
                        <code>{field.type}</code>
                      </li>
                    ))}
                  </ul>
                </article>
              ))}
            </div>
          </section>

          <section className="panel code-panel">
            <span className="eyebrow">JSON</span>
            <pre>{JSON.stringify(result.app_schema, null, 2)}</pre>
          </section>
        </>
      )}
    </main>
  )
}

export default App
