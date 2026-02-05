import { test, expect } from '@playwright/test';

test.describe('后台管理测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到登录页面
    await page.goto('http://localhost:5176/login');
  });

  test('登录并测试文章管理', async ({ page }) => {
    // 登录
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123456');
    await page.click('button[type="submit"]');

    // 等待导航到管理页面
    await page.waitForURL('http://localhost:5176/admin');

    // 测试文章管理
    await page.goto('http://localhost:5176/admin/posts');
    await expect(page).toHaveTitle(/Nano Banana/);

    // 检查是否有文章列表
    const articles = page.locator('table tbody tr');
    const count = await articles.count();
    console.log(`找到 ${count} 篇文章`);

    if (count > 0) {
      // 测试状态切换功能
      const firstRow = articles.first();
      const toggleButton = firstRow.locator('button[class*="inline-flex h-6 w-11"]');

      // 获取当前状态
      const statusText = await firstRow.locator('span:text("草稿"), span:text("已发布")').first().textContent();
      console.log('当前状态:', statusText);

      // 点击切换开关
      await toggleButton.click();

      // 等待更新
      await page.waitForTimeout(1000);

      // 验证状态已改变
      const newStatusText = await firstRow.locator('span:text("草稿"), span:text("已发布")').first().textContent();
      console.log('新状态:', newStatusText);
      expect(newStatusText).not.toBe(statusText);
    }
  });

  test('测试项目管理', async ({ page }) => {
    // 登录
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:5176/admin');

    // 测试项目管理
    await page.goto('http://localhost:5176/admin/projects');
    await expect(page.locator('h1:text("项目管理")')).toBeVisible();

    // 检查项目列表
    const projects = page.locator('table tbody tr');
    const count = await projects.count();
    console.log(`找到 ${count} 个项目`);

    if (count > 0) {
      // 测试滑动开关
      const firstRow = projects.first();
      const toggleSwitch = firstRow.locator('button[disabled][class*="inline-flex h-6"]');

      // 检查滑动开关是否存在
      const toggleExists = await firstRow.locator('button[class*="inline-flex h-6 w-11"]').count();
      expect(toggleExists).toBeGreaterThan(0);
      console.log('✓ 项目管理页面有滑动开关');
    }
  });

  test('测试生活记录管理', async ({ page }) => {
    // 登录
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:5176/admin');

    // 测试生活记录管理
    await page.goto('http://localhost:5176/admin/life');
    await expect(page.locator('h1:text("生活记录管理")')).toBeVisible();

    // 检查生活记录列表
    const lifePosts = page.locator('table tbody tr');
    const count = await lifePosts.count();
    console.log(`找到 ${count} 条生活记录`);

    if (count > 0) {
      // 测试滑动开关
      const firstRow = lifePosts.first();

      // 检查滑动开关是否存在
      const toggleExists = await firstRow.locator('button[class*="inline-flex h-6 w-11"]').count();
      expect(toggleExists).toBeGreaterThan(0);
      console.log('✓ 生活记录页面有滑动开关');
    }
  });

  test('测试标签保存功能', async ({ page }) => {
    // 登录
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123456');
    await page.click('button[type="submit"]');
    await page.waitForURL('http://localhost:5176/admin');

    // 进入文章编辑页面
    await page.goto('http://localhost:5176/admin/posts');

    // 找到第一篇文章并点击编辑
    const firstRow = page.locator('table tbody tr').first();
    const editButton = firstRow.locator('button[title="编辑"]');
    await editButton.click();

    // 等待编辑页面加载
    await page.waitForURL(/\/admin\/posts\/.+/);
    await page.waitForTimeout(1000);

    // 添加新标签
    const tagInput = page.locator('input[placeholder*="输入标签"]');
    await tagInput.fill('测试标签 playwright');
    await tagInput.press('Enter');
    await page.waitForTimeout(500);

    // 点击保存
    await page.click('button[type="submit"]:has-text("保存")');

    // 等待保存完成
    await page.waitForTimeout(2000);

    // 返回列表页
    await page.goto('http://localhost:5176/admin/posts');

    // 重新进入编辑页面验证标签是否保存
    const firstRow2 = page.locator('table tbody tr').first();
    const editButton2 = firstRow2.locator('button[title="编辑"]');
    await editButton2.click();

    await page.waitForURL(/\/admin\/posts\/.+/);
    await page.waitForTimeout(1000);

    // 检查标签是否存在
    const tags = page.locator('span[class*="bg-primary-from/10"]');
    const tagFound = await page.getByText('测试标签 playwright').count();
    console.log('标签保存测试结果:', tagFound > 0 ? '✓ 标签保存成功' : '✗ 标签未保存');

    expect(tagFound).toBeGreaterThan(0);
  });
});
