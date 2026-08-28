import { useEffect, useState } from 'react'

function inputType(type) {
  if (type === 'integer' || type === 'number') return 'number'
  if (type === 'datetime') return 'datetime-local'
  return 'text'
}

function initialValues(entity, row) {
  return Object.fromEntries(
    entity.fields.map((field) => [field.name, row?.[field.name] ?? ''])
  )
}

function RecordForm({ entity, row, saving, onSave, onCancel }) {
  const [values, setValues] = useState(() => initialValues(entity, row))

  useEffect(() => {
    setValues(initialValues(entity, row))
  }, [entity, row])

  function submit(event) {
    event.preventDefault()
    const payload = Object.fromEntries(
      entity.fields.map((field) => [field.name, values[field.name] === '' ? null : values[field.name]])
    )
    onSave(payload)
  }

  return (
    <div className="editor-backdrop">
      <section className="editor-panel">
        <div className="panel-title">
          <div>
            <span className="eyebrow">{row ? 'EDITAR' : 'NOVO REGISTRO'}</span>
            <h2>{entity.label}</h2>
          </div>
          <button className="ghost-button" onClick={onCancel}>Fechar</button>
        </div>

        <form className="record-form" onSubmit={submit}>
          <div className="form-grid">
            {entity.fields.map((field) => (
              <label key={field.name}>
                <span>{field.label}</span>
                {field.type === 'boolean' ? (
                  <select
                    value={values[field.name] ?? ''}
                    onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}
                  >
                    <option value="">Vazio</option>
                    <option value="1">Sim</option>
                    <option value="0">Não</option>
                  </select>
                ) : (
                  <input
                    type={inputType(field.type)}
                    step={field.type === 'number' ? 'any' : undefined}
                    value={values[field.name] ?? ''}
                    onChange={(event) => setValues((current) => ({ ...current, [field.name]: event.target.value }))}
                  />
                )}
                <small>{field.type}{field.nullable ? ' · opcional' : ''}</small>
              </label>
            ))}
          </div>

          <div className="form-actions">
            <button type="button" className="ghost-button" onClick={onCancel}>Cancelar</button>
            <button type="submit" disabled={saving}>{saving ? 'Salvando…' : 'Salvar registro'}</button>
          </div>
        </form>
      </section>
    </div>
  )
}

export default RecordForm
