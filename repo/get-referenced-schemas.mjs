#!/usr/bin/env node
/**
 * Get the exact required properties for referenced schemas
 */

import WEBHOOK_SCHEMA from "@octokit/webhooks-schemas" with { type: "json" };

console.log("=== Repository Schema ===");
if (WEBHOOK_SCHEMA.definitions['repository']) {
  const repo = WEBHOOK_SCHEMA.definitions['repository'];
  console.log("Required properties:", repo.required || []);
  console.log("Additional properties:", repo.additionalProperties);
  console.log("Sample properties (first 20):");
  Object.keys(repo.properties || {}).slice(0, 20).forEach(prop => {
    console.log(`  - ${prop}`);
  });
}

console.log("\n=== User Schema (sender) ===");
if (WEBHOOK_SCHEMA.definitions['user']) {
  const user = WEBHOOK_SCHEMA.definitions['user'];
  console.log("Required properties:", user.required || []);
  console.log("Additional properties:", user.additionalProperties);
  console.log("Sample properties (first 15):");
  Object.keys(user.properties || {}).slice(0, 15).forEach(prop => {
    console.log(`  - ${prop}`);
  });
}

console.log("\n=== Pull Request Schema ===");
if (WEBHOOK_SCHEMA.definitions['pull-request']) {
  const pr = WEBHOOK_SCHEMA.definitions['pull-request'];
  console.log("Required properties:", pr.required || []);
  console.log("Additional properties:", pr.additionalProperties);
  console.log("Sample properties (first 20):");
  Object.keys(pr.properties || {}).slice(0, 20).forEach(prop => {
    console.log(`  - ${prop}`);
  });
}
