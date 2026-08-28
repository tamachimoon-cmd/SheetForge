function EntityTable({ entity, data, loading, search, onSearchChange, onNew, onEdit, onDelete }) {
  return (
    <section className="panel data-panel">
      <div className="panel-title table-heading">
        <div>
          <span className="eyebrow">ENTIDADE</span>
          <h2>{entity.label}</h2>
          <p>{data?.total ?? 0} registros encontrados</p>
        </div>
        <button className="primary-action" onClick={onNew}>Novo registro</button>
      </div>

      <div className="table-tools">
        <input
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder={`Pesquisar em ${entity.label}...`}
        />
      </div>

      <div className="table-wrap">
        {loading ? (
          <div className="empty-state">Carregando registros…</div>
        ) : !data?.items?.length ? (
          <div className="empty-state">Nenhum registro encontrado.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                {entity.fields.map((field) => <th key={field.name}>{field.label}</th>)}
                <th className="actions-column">Ações</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((row) => (
                <tr key={row.__sf_rowid}>
                  <td className="row-id">{row.__sf_rowid}</td>
                  {entity.fields.map((field) => (
                    <td key={field.name} title={String(row[field.name] ?? '')}>
                      {row[field.name] === null || row[field.name] === '' ? <span className="muted">—</span> : String(row[field.name])}
                    </td>
                  ))}
                  <td className="row-actions">
                    <button className="ghost-button" onClick={() => onEdit(row)}>Editar</button>
                    <button className="danger-button" onClick={() => onDelete(row)}>Excluir</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  )
}

export default EntityTable
