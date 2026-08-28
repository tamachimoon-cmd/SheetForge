function UploadPanel({ file, loading, error, onFileChange, onSubmit }) {
  return (
    <section className="panel upload-panel">
      <form onSubmit={onSubmit}>
        <label className="dropzone">
          <input
            type="file"
            accept=".xlsx,.csv"
            onChange={(event) => onFileChange(event.target.files?.[0] || null)}
          />
          <span>{file ? file.name : 'Selecione ou arraste uma planilha'}</span>
          <small>.xlsx ou .csv</small>
        </label>
        <button disabled={!file || loading}>{loading ? 'Forjando…' : 'Forjar aplicação'}</button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  )
}

export default UploadPanel
