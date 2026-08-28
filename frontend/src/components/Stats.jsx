function Stats({ analysis, project }) {
  const values = [
    ['Abas', analysis.workbook.sheet_count],
    ['Entidades', analysis.entities.length],
    ['Relações', analysis.relationships.length],
    ['Campos', analysis.entities.reduce((sum, entity) => sum + entity.fields.length, 0)],
    ['Registros', Object.values(project.importSummary).reduce((sum, item) => sum + item.rowsImported, 0)],
  ]

  return (
    <section className="stats">
      {values.map(([label, value]) => (
        <article className="stat" key={label}>
          <strong>{value}</strong>
          <span>{label}</span>
        </article>
      ))}
    </section>
  )
}

export default Stats
