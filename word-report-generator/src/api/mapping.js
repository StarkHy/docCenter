import request from '@/utils/request'

export function getMappings(params) {
  return request({
    url: '/api/mappings/',
    method: 'get',
    params
  })
}

export function getMapping(mappingId) {
  return request({
    url: `/api/mappings/${mappingId}`,
    method: 'get'
  })
}

export function createMapping(data) {
  return request({
    url: '/api/mappings',
    method: 'post',
    data
  })
}

export function updateMapping(mappingId, data) {
  return request({
    url: `/api/mappings/${mappingId}`,
    method: 'put',
    data
  })
}

export function deleteMapping(mappingId) {
  return request({
    url: `/api/mappings/${mappingId}`,
    method: 'delete'
  })
}