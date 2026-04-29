import request from '@/utils/request'

export function getTemplates(params) {
  return request({
    url: '/api/templates/',
    method: 'get',
    params
  })
}

export function getTemplate(templateId) {
  return request({
    url: `/api/templates/${templateId}`,
    method: 'get'
  })
}

export function uploadTemplate(formData) {
  return request({
    url: '/api/templates/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function deleteTemplate(templateId) {
  return request({
    url: `/api/templates/${templateId}`,
    method: 'delete'
  })
}

export function getTemplateVariables(templateId) {
  return request({
    url: `/api/templates/${templateId}/variables`,
    method: 'get'
  })
}

export function downloadTemplate(templateId) {
  return request({
    url: `/api/templates/${templateId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}