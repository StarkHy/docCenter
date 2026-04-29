import request from '@/utils/request'

export function generateDocument(data) {
  return request({
    url: '/api/documents/generate',
    method: 'post',
    data
  })
}

export function getHistory(params) {
  return request({
    url: '/api/documents/history',
    method: 'get',
    params
  })
}

export function getHistoryItem(historyId) {
  return request({
    url: `/api/documents/history/${historyId}`,
    method: 'get'
  })
}

export function deleteHistory(historyId) {
  return request({
    url: `/api/documents/history/${historyId}`,
    method: 'delete'
  })
}

export function regenerateDocument(historyId) {
  return request({
    url: `/api/documents/history/${historyId}/regenerate`,
    method: 'post'
  })
}

export function previewData(dataSourceId, sql) {
  return request({
    url: '/api/documents/preview',
    method: 'get',
    params: { data_source_id: dataSourceId, sql }
  })
}

export function downloadDocument(docId) {
  return request({
    url: `/api/documents/${docId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

export function getMappingParams(mappingId) {
  return request({
    url: `/api/documents/mapping/${mappingId}/params`,
    method: 'get'
  })
}