import request from '@/utils/request'

export function getDatabases(params) {
  return request({
    url: '/api/databases/',
    method: 'get',
    params
  })
}

export function getDatabase(dbId) {
  return request({
    url: `/api/databases/${dbId}`,
    method: 'get'
  })
}

export function createDatabase(data) {
  return request({
    url: '/api/databases/',
    method: 'post',
    data
  })
}

export function updateDatabase(dbId, data) {
  return request({
    url: `/api/databases/${dbId}`,
    method: 'put',
    data
  })
}

export function deleteDatabase(dbId) {
  return request({
    url: `/api/databases/${dbId}`,
    method: 'delete'
  })
}

export function testDatabase(dbId) {
  return request({
    url: `/api/databases/${dbId}/test`,
    method: 'post'
  })
}

export function testDatabaseConnection(data) {
  return request({
    url: '/api/databases/test',
    method: 'post',
    data
  })
}