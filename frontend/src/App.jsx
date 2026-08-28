import { useEffect, useMemo, useState } from 'react'
import { createRow, deleteRow, importProject, listRows, updateRow } from './api'
import EntityTable from './components/EntityTable'
import RecordForm from './components/RecordForm'
import Stats from './components/Stats'
import UploadPanel from './components/UploadPanel'

function App() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [activeEntityName, setActiveEntityName] = useState('')
  const [rows, setRows] = useState(null)
  const [search, setSearch] = useState('')
  const [editorRow, setEditorRow] = useState(undefined)
  const [editorOpen, setEditorOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [rowsLoading, setRowsLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const project = result?.project
  const analysis = result?.analysis
  const schema = project?.schema
  const activeEntity = useMemo(
    () => schema?.entities.find((entity) => entity.name === activeEntityName),
    [schema, activeEntityName]
  )

  useEffect(() => {
    if (!project || !activeEntityName) return

    const timer = window.setTimeout(async () => {
      setRowsLoading(true)
      setError('')
      try {
        setRows(await listRows(project.projectId, activeEntityName, search))
      } catch (err) {
        setError(err.message)
      } finally {
        setRowsLoading(false)
      }
    }, 220)

    return () => window.clearTimeout(timer)
  }, [project, activeEntityName, search])

  async function forge(event) {
    event.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setResult(null)
    setRows(null)

    try {
      const data = await importProject(file)
      setResult(data)
      setActiveEntityName(data.project.schema.entities[0]?.name || '')
      setSearch('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function refreshRows() {
    if (!project || !activeEntityName) return
    setRows(await listRows(project.projectId, activeEntityName, search))
  }

  function openNew() {
    setEditorRow(undefined)
    setEditorOpen(true)
  }

  function openEdit(row) {
    setEditorRow(row)
    setEditorOpen(true)
  }

  async function saveRecord(payload) {
    if (!project || !activeEntity) return
    setSaving(true)
    setError('')
    try {
      if (editorRow) {
        await updateRow(project.projectId, activeEntity.name, editorRow.__sf_rowid, payload)
      } else {
        await createRow(project.projectId, activeEntity.name, payload)
      }
      setEditorOpen(false)
      await refreshRows()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function removeRecord(row) {
    if (!project || !activeEntity) return
    if (!window.confirm(`Excluir o registro #${row.__sf_rowid} de ${activeEntity.label}?`)) return

    setError('')
    try {
      await deleteRow(project.projectId, activeEntity.name, row.__sf_rowid)
      await refreshRows()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="shell">
      <header className="hero">
        <span className="eyebrow">SHEETFORGE / MVP 0.2</span>
        <h1>Da planilha nasce o sistema.</h1>
        <p>Importe Excel ou CSV. O SheetForge interpreta a estrutura, cria um banco SQLite e transforma as abas em módulos utilizáveis.</p>
      </header>

      {!project && (
        <UploadPanel
          file={file}
          loading={loading}
          error={error}
          onFileChange={setFile}
          onSubmit={forge}
        />
      )}

      {project && analysis && (
        <>
          <section className="app-banner">
            <div>
              <span className="eyebrow">APLICAÇÃO GERADA</span>
              <h2>{schema.app.name}</h2>
              <p>Projeto {project.projectId} · SQLite · schema v{schema.schemaVersion}</p>
            </div>
            <button className="ghost-button" onClick={() => {
              setResult(null)
              setFile(null)
              setActiveEntityName('')
              setRows(null)
            }}>Importar outro arquivo</button>
          </section>

          <Stats analysis={analysis} project={project} />

          {error && <p className="error standalone-error">{error}</p>}

          <section className="workspace">
            <aside className="sidebar panel">
              <span className="eyebrow">MÓDULOS</span>
              <nav>
                {schema.entities.map((entity) => (
                  <button
                    key={entity.name}
                    className={entity.name === activeEntityName ? 'nav-item active' : 'nav-item'}
                    onClick={() => {
                      setActiveEntityName(entity.name)
                      setSearch('')
                      setRows(null)
                    }}
                  >
                    <span>{entity.label}</span>
                    <small>{project.importSummary[entity.name]?.rowsImported ?? 0}</small>
                  </button>
                ))}
              </nav>

              <details className="schema-details">
                <summary>Schema técnico</summary>
                <pre>{JSON.stringify(schema, null, 2)}</pre>
              </details>
            </aside>

            {activeEntity && (
              <EntityTable
                entity={activeEntity}
                data={rows}
                loading={rowsLoading}
                search={search}
                onSearchChange={setSearch}
                onNew={openNew}
                onEdit={openEdit}
                onDelete={removeRecord}
              />
            )}
          </section>
        </>
      )}

      {editorOpen && activeEntity && (
        <RecordForm
          entity={activeEntity}
          row={editorRow}
          saving={saving}
          onSave={saveRecord}
          onCancel={() => setEditorOpen(false)}
        />
      )}
    </main>
  )
}

export default App
