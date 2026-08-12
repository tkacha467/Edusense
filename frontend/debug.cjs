const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  page.on('console', msg => {
    console.log('CONSOLE:', msg.type(), msg.text());
  });

  page.on('pageerror', error => {
    console.log('PAGE EXCEPTION:', error.message);
  });

  await page.goto('http://localhost:5174', { waitUntil: 'domcontentloaded' });
  
  await page.evaluate(() => {
    const user = {
      id: 'usr_student_2',
      email: 'student2@edusense.com',
      fullName: 'Demo Student 2 (New)',
      role: 'student',
      learningState: 'NEW',
      streak: 0,
      minutesToday: 0,
      completedTopics: [],
      studyPlan: [],
      alerts: [],
      predictions: []
    };
    localStorage.setItem('edu_session', JSON.stringify({ user, token: 'mock', expiresAt: Date.now() + 3600000 }));
  });

  await page.goto('http://localhost:5174/student/dashboard', { waitUntil: 'networkidle0' });
  await browser.close();
})();
