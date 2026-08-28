const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options)

  if (response.status === 204) return null

  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.detail || 'Falha na comunicação com o SheetForge.')
  }
  return data
}

export async function importProject(file) {
  const body = new FormData()
  body.append('file', file)
  return request('/api/projects/import', { method: 'POST', body })
}

export function listRows(projectId, entityName, search = '') {
  const query = new URLSearchParams({ limit: '100', offset: '0' })
  if (search.trim()) query.set('search', search.trim())
  return request(`/api/projects/${projectId}/entities/${encodeURIComponent(entityName)}/rows?${query}`)
}

export function createRow(projectId, entityName, payload) {
  return request(`/api/projects/${projectId}/entities/${encodeURIComponent(entityName)}/rows`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function updateRow(projectId, entityName, rowId, payload) {
  return request(`/api/projects/${projectId}/entities/${encodeURIComponent(entityName)}/rows/${rowId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function deleteRow(projectId, entityName, rowId) {
  return request(`/api/projects/${projectId}/entities/${encodeURIComponent(entityName)}/rows/${rowId}`, {
    method: 'DELETE',
  })
}
