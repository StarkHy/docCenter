import request from '@/utils/request'

export function getDataSources(params) {
  return request({
    url: '/api/datasources/',
    method: 'get',
    params
  })
}

export function getDataSource(dsId) {
  return request({
    url: `/api/datasources/${dsId}`,
    method: 'get'
  })
}

export function createDataSource(data) {
  return request({
    url: '/api/datasources/',
    method: 'post',
    data
  })
}

export function updateDataSource(dsId, data) {
  return request({
    url: `/api/datasources/${dsId}`,
    method: 'put',
    data
  })
}

export function deleteDataSource(dsId) {
  return request({
    url: `/api/datasources/${dsId}`,
    method: 'delete'
  })
}

export function testDataSource(data) {
  return request({
    url: '/api/datasources/test',
    method: 'post',
    data
  })
}