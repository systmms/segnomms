#!/usr/bin/env node
/**
 * Analyze GitHub webhook schemas to understand exact property requirements
 */

import WEBHOOK_SCHEMA from "@octokit/webhooks-schemas" with { type: "json" };

console.log("=== GitHub Webhook Schema Analysis ===\n");

// Find pull_request schemas
const pullRequestSchemas = Object.keys(WEBHOOK_SCHEMA.definitions || {})
  .filter(key => key.startsWith('pull_request$'))
  .slice(0, 5); // Just show first 5

console.log("Pull Request Schema Variants:");
pullRequestSchemas.forEach(schema => {
  console.log(`- ${schema}`);
});

// Analyze pull_request$opened specifically
if (WEBHOOK_SCHEMA.definitions['pull_request$opened']) {
  const openedSchema = WEBHOOK_SCHEMA.definitions['pull_request$opened'];
  console.log("\n=== pull_request$opened Schema ===");
  console.log("Required properties:", openedSchema.required || []);
  console.log("Additional properties allowed:", openedSchema.additionalProperties !== false);
  console.log("Top-level properties:");
  Object.keys(openedSchema.properties || {}).forEach(prop => {
    console.log(`  - ${prop}: ${openedSchema.properties[prop].type || 'object'}`);
  });

  // Check pull_request object schema
  if (openedSchema.properties.pull_request && openedSchema.properties.pull_request['$ref']) {
    const prRef = openedSchema.properties.pull_request['$ref'].replace('#/definitions/', '');
    console.log(`\nPull Request object schema: ${prRef}`);
    if (WEBHOOK_SCHEMA.definitions[prRef]) {
      const prSchema = WEBHOOK_SCHEMA.definitions[prRef];
      console.log("Pull request required properties:", prSchema.required || []);
      console.log("Pull request allows additional properties:", prSchema.additionalProperties !== false);
      console.log("Pull request top-level properties:");
      Object.keys(prSchema.properties || {}).slice(0, 10).forEach(prop => {
        console.log(`  - ${prop}`);
      });
    }
  }
}

// Find push schema
console.log("\n=== Looking for Push Schema ===");
const pushRelated = WEBHOOK_SCHEMA.oneOf.find(item => {
  return item.properties && item.properties.ref && item.properties.commits && !item.properties.action;
});

if (pushRelated) {
  console.log("Found push schema in oneOf array");
  console.log("Push required properties:", pushRelated.required || []);
  console.log("Push allows additional properties:", pushRelated.additionalProperties !== false);
  console.log("Push top-level properties:");
  Object.keys(pushRelated.properties || {}).forEach(prop => {
    console.log(`  - ${prop}`);
  });
} else {
  console.log("Push schema not found in oneOf array - checking if it's handled differently");
}
