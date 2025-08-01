#!/usr/bin/env node

const axios = require('axios');
const readline = require('readline');

const MCP_ENDPOINT = process.env.MCP_ENDPOINT || 'http://localhost:3000/mcp';

async function testTool(name, arguments) {
  try {
    const response = await axios.post(MCP_ENDPOINT, {
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: {
        name,
        arguments
      }
    });
    console.log(`✅ ${name}:`, response.data.result);
    return response.data.result;
  } catch (error) {
    console.error(`❌ ${name}:`, error.response?.data || error.message);
    return null;
  }
}

function askQuestion(query) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise(resolve => rl.question(query, ans => {
    rl.close();
    resolve(ans);
  }));
}

async function runTests() {
  console.log('🧪 Starting CRDP MCP Server Tests...\n');
  console.log(`📡 Testing endpoint: ${MCP_ENDPOINT}\n`);

  // Test monitoring tools first (they don't require CRDP data)
  console.log('🔍 Testing monitoring tools...');
  await testTool('check_health', {});
  await testTool('check_liveness', {});
  await testTool('get_metrics', {});

  // Prompt for protect/reveal
  const doProtect = await askQuestion('\nDo you want to test protect/reveal operations? (y/n): ');
  if (doProtect.trim().toLowerCase() !== 'y') {
    console.log('\n🏁 Tests completed!');
    return;
  }

  // Ask for data to protect and policy name
  const data = await askQuestion('Enter data to protect: ');
  const protection_policy_name = await askQuestion('Enter protection policy name: ');

  // Protect data
  const protectResult = await testTool('protect_data', {
    data,
    protection_policy_name
  });

  if (!protectResult || !protectResult.content) {
    console.log('❌ protect_data failed. Skipping reveal_data test.');
    return;
  }

  // Extract protected_data and external_version from the response text
  const text = protectResult.content[0]?.text || '';
  const match = /Protected data: ([^\n]+)/.exec(text);
  const protected_data = match ? match[1] : null;
  const extVerMatch = /External version: ([^\n]+)/.exec(text);
  const external_version = extVerMatch ? extVerMatch[1] : undefined;

  if (!protected_data) {
    console.log('❌ Could not extract protected_data from protect_data response.');
    return;
  }

  // Ask for username for reveal
  const username = await askQuestion('Enter username for reveal: ');

  // Reveal data (include external_version if present)
  const revealArgs = {
    protected_data,
    username,
    protection_policy_name
  };
  if (external_version) {
    revealArgs.external_version = external_version;
    console.log(`(Passing external_version: ${external_version} to reveal_data)`);
  }

  await testTool('reveal_data', revealArgs);

  console.log('\n🏁 Tests completed!');
}

// Check if axios is available
try {
  require.resolve('axios');
} catch (e) {
  console.error('❌ axios is not installed. Please run: npm install axios');
  process.exit(1);
}

runTests().catch(console.error); 