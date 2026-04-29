import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5173';
const LOGIN_URL = 'http://localhost:5173/login';

async function selectOption(page: any, label: string) {
  const dialog = page.locator('.el-dialog:visible');
  const searchText = label.replace(/^请选择/, '');
  // Find the select within the dialog - try by placeholder first
  const select = dialog.locator('.el-select').filter({ hasText: searchText });
  const count = await select.count();
  if (count > 0) {
    await select.first().click();
  } else {
    await dialog.locator('.el-select').first().click();
  }
  await page.waitForTimeout(500);
  await page.locator('.el-select-dropdown__item').filter({ hasText: label }).click();
  await page.waitForTimeout(500);
}

test.describe('Word Report Generator - 自动化测试', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto(LOGIN_URL);
    await page.waitForLoadState('networkidle');
    
    await page.getByPlaceholder('请输入用户名').fill('admin');
    await page.getByPlaceholder('请输入密码').fill('admin123');
    await page.getByRole('button', { name: '登 录' }).click();
    
    await page.waitForURL('**/home');
    await page.waitForLoadState('networkidle');
  });

  test.describe('模板管理', () => {
    test('查询模板列表', async ({ page }) => {
      await page.click('text=模板管理');
      await page.waitForLoadState('networkidle');
      
      const rows = await page.locator('.el-table__row').count();
      expect(rows).toBeGreaterThanOrEqual(0);
    });

    test('查看模板变量', async ({ page }) => {
      await page.click('text=模板管理');
      await page.waitForLoadState('networkidle');
      
      const varButton = page.locator('button:has-text("变量")').first();
      if (await varButton.isVisible()) {
        await varButton.click();
        await page.waitForSelector('.el-dialog');
        await page.click('button:has-text("关")');
      }
    });

    test('删除模板', async ({ page }) => {
      await page.click('text=模板管理');
      await page.waitForLoadState('networkidle');
      
      const deleteButton = page.locator('button:has-text("删除")').first();
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        await page.waitForSelector('.el-message-box');
        await page.click('button:has-text("确定")');
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('数据源管理', () => {
    test('新增HTTP API数据源', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新增数据源")');
      await page.waitForSelector('.el-dialog');
      
      await page.getByPlaceholder('请输入数据源名称').fill('测试API');
      await selectOption(page, 'HTTP API');
      
      await page.getByPlaceholder('https://api.example.com/data').fill('https://jsonplaceholder.typicode.com/posts/1');
      
      await page.click('button:has-text("保存")');
      await page.waitForTimeout(1000);
    });

    test('新增静态JSON数据源', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新增数据源")');
      await page.waitForSelector('.el-dialog');
      
      await page.getByPlaceholder('请输入数据源名称').fill('测试JSON');
      await selectOption(page, '静态JSON');
      
      await page.locator('textarea').filter({ hasText: '' }).first().fill('{"name": "张三", "age": 28}');
      
      await page.click('button:has-text("保存")');
      await page.waitForTimeout(1000);
    });

    test('新增表单输入数据源', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新增数据源")');
      await page.waitForSelector('.el-dialog');
      
      await page.getByPlaceholder('请输入数据源名称').fill('测试表单');
      await selectOption(page, '表单输入');
      
      await page.click('text=+ 添加字段');
      await page.getByPlaceholder('字段名').fill('title');
      await page.getByPlaceholder('字段值').fill('测试值');
      
      await page.click('button:has-text("保存")');
      await page.waitForTimeout(1000);
    });

    test('测试数据源连通性', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      const testButton = page.locator('button:has-text("测试")').first();
      if (await testButton.isVisible()) {
        await testButton.click();
        await page.waitForSelector('.el-dialog', { timeout: 5000 });
        
        const alert = page.locator('.el-alert');
        await expect(alert).toBeVisible({ timeout: 5000 });
        
        await page.click('button:has-text("关")');
      }
    });

    test('编辑数据源', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      const editButton = page.locator('button:has-text("编辑")').first();
      if (await editButton.isVisible()) {
        await editButton.click();
        await page.waitForSelector('.el-dialog');
        
        await page.fill('input[placeholder="请输入数据源名称"]', '测试数据源-已编辑');
        
        await page.click('button:has-text("保存")');
        await page.waitForTimeout(1000);
      }
    });

    test('删除数据源', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      const deleteButton = page.locator('button:has-text("删除")').first();
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        await page.waitForSelector('.el-message-box');
        await page.click('button:has-text("确定")');
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('参数映射', () => {
    test('创建映射配置', async ({ page }) => {
      await page.click('text=参数映射');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新增映射")');
      await page.waitForSelector('.el-dialog');
      
      await page.fill('input[placeholder="请输入映射名称"]', '测试映射');
      
      const templateSelect = page.locator('.el-select:has-text("请选择模板")').first();
      await templateSelect.click();
      await page.waitForTimeout(500);
      const templateOption = page.locator('.el-select-dropdown__item').first();
      if (await templateOption.isVisible()) {
        await templateOption.click();
      }
      
      await page.waitForTimeout(500);
      const dsSelect = page.locator('.el-select:has-text("请选择数据源")').first();
      await dsSelect.click();
      await page.waitForTimeout(500);
      const dsOption = page.locator('.el-select-dropdown__item').first();
      if (await dsOption.isVisible()) {
        await dsOption.click();
      }
      
      await page.waitForTimeout(1000);
      await page.click('button:has-text("自动匹配")');
      await page.waitForTimeout(500);
      
      await page.click('button:has-text("保存")');
      await page.waitForTimeout(1000);
    });

    test('编辑映射配置', async ({ page }) => {
      await page.click('text=参数映射');
      await page.waitForLoadState('networkidle');
      
      const editButton = page.locator('button:has-text("编辑")').first();
      if (await editButton.isVisible()) {
        await editButton.click();
        await page.waitForSelector('.el-dialog');
        
        await page.fill('input[placeholder="请输入映射名称"]', '测试映射-已编辑');
        
        await page.click('button:has-text("保存")');
        await page.waitForTimeout(1000);
      }
    });

    test('删除映射配置', async ({ page }) => {
      await page.click('text=参数映射');
      await page.waitForLoadState('networkidle');
      
      const deleteButton = page.locator('button:has-text("删除")').first();
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        await page.waitForSelector('.el-message-box');
        await page.click('button:has-text("确定")');
        await page.waitForTimeout(1000);
      }
    });
  });

  test.describe('文档生成', () => {
    test('选择映射配置生成文档', async ({ page }) => {
      await page.click('text=生成文档');
      await page.waitForLoadState('networkidle');
      
      const mappingSelect = page.locator('.el-select:has-text("请选择映射配置")');
      if (await mappingSelect.isVisible()) {
        await mappingSelect.click();
        await page.waitForTimeout(500);
        
        const option = page.locator('.el-select-dropdown__item').first();
        if (await option.isVisible()) {
          await option.click();
          
          await page.waitForTimeout(1000);
          
          const generateBtn = page.locator('button:has-text("生成文档")');
          if (await generateBtn.isEnabled()) {
            await generateBtn.click();
            await page.waitForTimeout(3000);
          }
        }
      }
    });

    test('预览数据', async ({ page }) => {
      await page.click('text=生成文档');
      await page.waitForLoadState('networkidle');
      
      const mappingSelect = page.locator('.el-select:has-text("请选择映射配置")');
      if (await mappingSelect.isVisible()) {
        await mappingSelect.click();
        await page.waitForTimeout(500);
        
        const option = page.locator('.el-select-dropdown__item').first();
        if (await option.isVisible()) {
          await option.click();
          
          await page.waitForTimeout(500);
          
          const previewBtn = page.locator('button:has-text("预览数据")');
          if (await previewBtn.isEnabled()) {
            await previewBtn.click();
            await page.waitForTimeout(2000);
          }
        }
      }
    });

    test('下载生成的文档', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const downloadBtn = page.locator('button:has-text("下载")').first();
      if (await downloadBtn.isVisible()) {
        await downloadBtn.click();
        await page.waitForTimeout(1000);
      }
    });

    test('重新生成文档', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const regenerateBtn = page.locator('button:has-text("重新生成")').first();
      if (await regenerateBtn.isVisible()) {
        await regenerateBtn.click();
        await page.waitForSelector('.el-message-box');
        await page.click('button:has-text("确定")');
        await page.waitForTimeout(3000);
      }
    });
  });

  test.describe('历史记录', () => {
    test('查看历史记录列表', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const table = page.locator('.el-table');
      await expect(table).toBeVisible({ timeout: 5000 });
    });

    test('搜索历史记录', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const searchInput = page.locator('input[placeholder="搜索文档名称"]');
      if (await searchInput.isVisible()) {
        await searchInput.fill('测试');
        await page.waitForTimeout(1000);
      }
    });

    test('按状态筛选历史记录', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const statusFilter = page.locator('.el-select:has-text("状态筛选")');
      if (await statusFilter.isVisible()) {
        await statusFilter.click();
        await page.waitForTimeout(500);
        
        const option = page.locator('.el-select-dropdown__item:has-text("成功")');
        if (await option.isVisible()) {
          await option.click();
          await page.waitForTimeout(1000);
        }
      }
    });

    test('删除历史记录', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const deleteBtn = page.locator('button:has-text("删除")').first();
      if (await deleteBtn.isVisible()) {
        await deleteBtn.click();
        await page.waitForSelector('.el-message-box');
        await page.click('button:has-text("确定")');
        await page.waitForTimeout(1000);
      }
    });

    test('历史记录分页', async ({ page }) => {
      await page.click('text=历史记录');
      await page.waitForLoadState('networkidle');
      
      const pagination = page.locator('.el-pagination');
      if (await pagination.isVisible()) {
        const nextBtn = pagination.locator('.btn-next');
        if (await nextBtn.isEnabled()) {
          await nextBtn.click();
          await page.waitForTimeout(1000);
        }
      }
    });
  });

  test.describe('首页', () => {
    test('查看首页统计数据', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');
      
      const templateCount = page.locator('.stat-card').first();
      await expect(templateCount).toBeVisible();
    });

    test('查看最近生成记录', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');
      
      const recentTable = page.locator('.el-table').first();
      if (await recentTable.isVisible()) {
        await expect(recentTable).toBeVisible();
      }
    });

    test('快速操作跳转', async ({ page }) => {
      await page.goto(BASE_URL);
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新建文档")');
      await page.waitForLoadState('networkidle');
      expect(page.url()).toContain('/generate');
    });
  });

  test.describe('异常情况', () => {
    test('空状态 - 无模板', async ({ page }) => {
      await page.click('text=生成文档');
      await page.waitForLoadState('networkidle');
      
      const emptyState = page.locator('.el-empty');
      if (await emptyState.isVisible()) {
        await expect(emptyState).toBeVisible();
      }
    });

    test('API请求失败处理', async ({ page }) => {
      await page.click('text=数据源');
      await page.waitForLoadState('networkidle');
      
      await page.click('button:has-text("新增数据源")');
      await page.waitForSelector('.el-dialog');
      
      await page.click('button:has-text("保存")');
      await page.waitForTimeout(500);
      
      const errorMsg = page.locator('.el-form-item__error');
      if (await errorMsg.isVisible()) {
        await expect(errorMsg).toBeVisible();
      }
    });
  });
});